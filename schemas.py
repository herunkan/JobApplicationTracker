from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict
from enums import ApplicationStatus
import datetime

class ApplicationCreate(BaseModel):
    company: str = Field(min_length = 1)
    role: str = Field(min_length = 1)
    
    @field_validator("company", "role", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value
    
    status: ApplicationStatus
    apply_date: datetime.date | None = None
    job_url: HttpUrl | None = None
    location: str | None = None
    pay: str | None = None
    job_description: str | None = None

class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length = 1)
    role: str | None = Field(default=None, min_length = 1)
    
    @field_validator("company", "role", mode="before")
    @classmethod
    def strip_required_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value
    status: ApplicationStatus | None = None
    apply_date: datetime.date | None = None
    job_url: HttpUrl | None = None
    location: str | None = None
    pay: str | None = None
    job_description: str | None = None

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    company:str
    role:str
    status:ApplicationStatus
    apply_date:datetime.date
    job_url:HttpUrl|None = None
    location:str|None = None
    pay:str|None = None
    job_description:str|None = None