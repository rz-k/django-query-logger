import copy
import re
import time
from collections import Counter

from django.conf import settings
from django.db import connection
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class QueryCountLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.VALUE_PATTERNS = [
            r"=\s*\d+",
            r"=\s*'[^']*'",
            r"IN\s*\([^\)]*\)",
        ]
        self.console = Console()
        self.IGNORED_QUERY_PATTERNS = ["COMMIT", "BEGIN", 'SELECT "django_session".']

    def normalize_sql(self, query: dict) -> str:
        normalized = query["sql"]
        for pattern in self.VALUE_PATTERNS:
            normalized = re.sub(pattern, "= ?", normalized, flags=re.IGNORECASE)
        return normalized

    def similar_queries(self, queries):
        counter = Counter(self.normalize_sql(q) for q in queries)
        return {sql: count for sql, count in counter.items() if count > 1}

    def duplicate_queries(self, queries):
        counter = Counter(q["sql"] for q in queries)
        return {sql: count for sql, count in counter.items() if count > 1}

    def normalize_queries(self, queries):
        for q in queries:
            for pattern in self.IGNORED_QUERY_PATTERNS:
                if pattern in q["sql"]:
                    queries.remove(q)
        return queries

    def pretty_print(self, path, duration, total, similar, duplicate):
        header = Text(" Django Query Inspector ", style="bold white on dark_green")

        summary = (
            f"[bold cyan]Path:[/] {path}\n"
            f"[bold cyan]Time:[/] {duration:.2f}s\n"
            f"[bold cyan]Total Queries:[/] [bold yellow]{total}[/]"
        )

        self.console.print(Panel(summary, title=header, expand=False))

        if similar:
            table = Table(
                title="🔥 Similar Queries (N+1 Warning)",
                header_style="bold magenta",
                show_lines=True,
            )
            table.add_column("Count", style="bold red", width=8)
            table.add_column("Normalized SQL", style="white")

            for sql, count in sorted(similar.items(), key=lambda x: -x[1]):
                table.add_row(str(count), sql)

            self.console.print(table)

        if duplicate:
            table = Table(
                title="⚠️ Duplicate Queries",
                header_style="bold yellow",
                show_lines=True,
            )
            table.add_column("Count", style="bold red", width=8)
            table.add_column("Exact SQL", style="white")

            for sql, count in sorted(duplicate.items(), key=lambda x: -x[1]):
                table.add_row(str(count), sql)
            self.console.print(table)

        if not similar and not duplicate:
            self.console.print(
                Panel(
                    "✨ No duplicate or similar queries detected!",
                    style="bold green",
                )
            )

    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)

        if not connection.queries:
            connection.queries_log.clear()

        start = time.monotonic()
        response = self.get_response(request)
        duration = (time.monotonic() - start)

        queries = copy.deepcopy(connection.queries)
        queries = self.normalize_queries(queries)

        total_queries = len(queries)
        similar = self.similar_queries(queries)
        duplicate = self.duplicate_queries(queries)
        print(queries)

        self.pretty_print(request.path,duration,total_queries,similar,duplicate)
        return response
