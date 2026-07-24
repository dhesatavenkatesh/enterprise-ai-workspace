from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)
AI_CALLS = Counter("ai_model_calls_total", "Total AI model calls", ["model", "status"])
AI_LATENCY = Histogram("ai_model_duration_seconds", "AI response time", ["model"])
RAG_LATENCY = Histogram("rag_retrieval_duration_seconds", "RAG retrieval time")
CELERY_FAILURES = Counter("celery_task_failures_total", "Failed Celery tasks", ["task"])
