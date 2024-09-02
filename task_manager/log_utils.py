import logging
from threading import local
import time
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)
_thread_locals = local()


class LoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        _thread_locals.request = request
        start = time.time()
        response = self.get_response(request)
        _thread_locals.request_time = time.time() - start
        return response

    def process_view(self, request: HttpRequest, view_func: Callable, *_: Any) -> None:
        _thread_locals.view = view_func


class RequestFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request = getattr(_thread_locals, "request", PlaceHolder())
        record.request = request  # type: ignore
        record.remote_addr = self.get_remote_ip(request)  # type: ignore
        record.view = getattr(_thread_locals, "view", PlaceHolder())  # type: ignore
        record.user_id = request.user.id if request.user.is_authenticated else "-"  # type: ignore
        record.request_time = getattr(_thread_locals, "request_time", PlaceHolder())
        return super().format(record)

    @staticmethod
    def get_remote_ip(request: HttpRequest) -> str:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0]
        return request.META.get("REMOTE_ADDR", PlaceHolder())


class PlaceHolder:
    def __init__(self, to_str: str = "-") -> None:
        self._to_str = to_str

    def __getattr__(self, name: str) -> "PlaceHolder":
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> "PlaceHolder":
        return self

    def __str__(self) -> str:
        return self._to_str

    def __repr__(self) -> str:
        return self._to_str

    def __bool__(self) -> bool:
        return False
