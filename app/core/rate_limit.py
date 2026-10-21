import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

WINDOW_SECONDS = 60
MAX_ATTEMPTS = 5

_attempts = defaultdict(deque)


def login_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    attempts = _attempts[client_ip]

    while attempts and now - attempts[0] >= WINDOW_SECONDS:
        attempts.popleft()

    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again in a minute.",
        )

    attempts.append(now)
