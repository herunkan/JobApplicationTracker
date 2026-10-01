from database import SessionLocal
from enums import ApplicationStatus
from models import JobApplication
from sqlalchemy import select, text

db = SessionLocal()


job = JobApplication(company = "Google",
                     role = "Data Engineer",
                     status = ApplicationStatus.APPLIED)
db.add(job)
db.commit()
db.refresh(job)

print(job.id)
print(job.apply_date)
db.close()


