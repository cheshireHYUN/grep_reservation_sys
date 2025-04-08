from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone

# 모든 datetime 필드를 UTC-aware로 파싱
class UTCBaseModel(BaseModel):
    def model_post_init(self, __context):
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime) and field_value.tzinfo is not timezone.utc:
                self.__dict__[field_name] = field_value.astimezone(timezone.utc)