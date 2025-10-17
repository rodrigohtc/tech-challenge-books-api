import json
import logging
import time
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("books_api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Loga todas as requisições com payload JSON estruturado."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else None

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_payload = {
                "event": "request_failed",
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_host,
                "duration_ms": round(duration_ms, 2),
            }
            logger.exception(json.dumps(log_payload))
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        log_payload = {
            "event": "request_completed",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "client_ip": client_host,
            "duration_ms": round(duration_ms, 2),
        }
        logger.info(json.dumps(log_payload))

        return response
