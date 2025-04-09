from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone

# UTC 기준
class UTCBaseModel(BaseModel):
    def model_post_init(self, __context):
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, datetime):
                # naive datetime은 UTC로 간주하고, aware는 UTC로 변환
                if field_value.tzinfo is None:
                    self.__dict__[field_name] = field_value.replace(tzinfo=timezone.utc)
                else:
                    self.__dict__[field_name] = field_value.astimezone(timezone.utc)


# KST 기준
KST = timezone(timedelta(hours=9))
class KSTBaseModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.astimezone(KST).isoformat()
        }