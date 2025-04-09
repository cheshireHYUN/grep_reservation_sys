from fastapi import Request
from fastapi.responses import JSONResponse

class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
