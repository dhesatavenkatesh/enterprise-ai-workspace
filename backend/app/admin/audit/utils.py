from fastapi import Request


def get_client_ip(request: Request) -> str | None:
    """
    Return the requesting client's IP address.

    When the application is behind a trusted reverse proxy,
    X-Forwarded-For usually contains the original client IP.
    """

    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")

    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return None
