from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from app.monitoring.metrics import HTTP_LATENCY, HTTP_REQUESTS

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = perf_counter()
        response = await call_next(request)
        path = request.url.path
        HTTP_REQUESTS.labels(request.method, path, response.status_code).inc()
        HTTP_LATENCY.labels(request.method, path).observe(perf_counter() - start)
        return response
