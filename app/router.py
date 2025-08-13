import re
from collections.abc import Callable
from typing import Any


class Router:
    def __init__(self) -> None:
        self.routes: dict[str, list[tuple[re.Pattern[str], Callable[..., Any]]]] = {}

    def add_route(self, method: str, path: str, handler: Callable[..., Any]) -> None:
        path_regex = self._convert_path_to_regex(path)
        self.routes.setdefault(method, []).append((path_regex, handler))

    def resolve(
        self, method: str, path: str
    ) -> tuple[Callable[..., Any] | None, dict[str, Any] | None]:
        routes_array = self.routes.get(method)
        if not routes_array:
            return None, None

        for path_regex, handler in routes_array:
            path_match = path_regex.fullmatch(path)
            if path_match:
                return handler, path_match.groupdict()
        return None, None

    def _convert_path_to_regex(self, path: str) -> re.Pattern[str]:
        path_regex = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', r'(?P<\1>[^/]+)', path)
        return re.compile(path_regex)
