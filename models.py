import datetime
from sqlalchemy import BigInteger, ForeignKey, Text, Date, Enum, Identity, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    
    status_history:Mapped[list["JobApplicationStatusHistory"]] = relationship(
        back_populates="application",
        cascade= "all, delete-orphan",
        passive_deletes=True
    )
    
    
class JobApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"
    
    id:Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True)
    
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
    
    changed_at:Mapped[datetime.datetime] = mapped_column(
        DateTime, 
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False)
    
    application_id:Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False)
    
    application:Mapped[JobApplication] = relationship(
        back_populates="status_history"
    )
