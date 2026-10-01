import datetime
from sqlalchemy import BigInteger, Text, Date, Enum, Identity, text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from enums import ApplicationStatus

class JobApplication(Base):
    __tablename__ = "applications"
    
    id:Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True)
    
    company:Mapped[str] = mapped_column(
        Text, 
        nullable=False)
    
    role:Mapped[str] = mapped_column(
        Text,
        nullable=False)
    
    status:Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            values_callable=lambda enum_class:[
                member.value for member in enum_class
                ],
            create_constraint = False
            ),
        nullable=False) 
    apply_date:Mapped[datetime.date] = mapped_column(
        Date, 
        server_default=text("CURRENT_DATE"),
        nullable=False)
    
    job_url:Mapped[str | None] = mapped_column(
        Text,nullable=True)
    location:Mapped[str | None] = mapped_column(
        Text,nullable=True)
    pay:Mapped[str | None] = mapped_column(
        Text,nullable=True)
    job_description:Mapped[str | None] = mapped_column(
        Text,nullable=True)