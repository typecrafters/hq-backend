from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.config.logging import get_logger

def log_exceptions(request: Request, error: Exception):
    logger = get_logger(request.url.path)
    logger.error(
        'Unhandled exception',
        extra={
            'path': request.url.path,
            'method': request.method,
            'status_code': 500,
            'request_id': request.headers.get('x-request-id'),
        },
        exc_info=error,
    )
    status_code = error.status_code if isinstance(error, HTTPException) else 500
    return JSONResponse(content={
        'message': 'An unknown error occurred. The latest operation did not complete successfully.'
    }, status_code=status_code)