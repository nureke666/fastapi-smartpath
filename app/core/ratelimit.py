import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# Простой in-memory ограничитель
# IP -> [timestamp1, timestamp2, ...]
_requests = {}

def rate_limiter(request: Request):
    """
    Ограничивает запросы: не более 5 запросов в минуту с одного IP.
    """
    client_ip = request.client.host
    now = time.time()
    
    # Очистка старых записей
    if client_ip not in _requests:
        _requests[client_ip] = []
    
    # Оставляем только запросы за последние 60 секунд
    _requests[client_ip] = [t for t in _requests[client_ip] if now - t < 60]
    
    if len(_requests[client_ip]) >= 5:
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a moment."
        )
    
    _requests[client_ip].append(now)