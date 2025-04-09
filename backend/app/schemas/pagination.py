from app.schemas.base import BaseModel

# 예약정보 
class Pagination(BaseModel):
    page : int
    page_size : int
    total_items : int
    total_pages : int
