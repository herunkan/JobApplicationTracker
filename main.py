import datetime
from enums import ApplicationStatus
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict
from models import JobApplication
from database import SessionLocal
from sqlalchemy import select
from sqlalchemy.orm import Session

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

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Job Tracker API is running"}

@app.get("/applications", response_model=list[ApplicationResponse])
def get_applications(db: Session = Depends(get_db)):
    
    result = db.execute(
        select(JobApplication)
    )
    
    jobs = result.scalars().all()
    
    return jobs
    
        
@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_specific_application(application_id:int, db: Session = Depends(get_db)):
    result = db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id
        )
    )
    
    job = result.scalar_one_or_none()
    
    
    if job is None:
        raise HTTPException(
            status_code=404,
            detail = "No application associated with this id"
        )
        
    return job

    
        
@app.post("/applications", response_model=ApplicationResponse)
def post_applications(application:ApplicationCreate, db: Session = Depends(get_db)):
    job_data = {
        "company": application.company,
        "role": application.role,
        "status": application.status,
        "job_url": str(application.job_url) if application.job_url else None,
        "location": application.location,
        "pay": application.pay,
        "job_description": application.job_description,
    }
    
    if application.apply_date is not None:
        job_data["apply_date"] = application.apply_date
    
    new_job = JobApplication(**job_data)
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job


@app.delete("/applications/{application_id}")
def delete_application(application_id:int, db: Session = Depends(get_db)):
    result = db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id
        )
    )
    
    job = result.scalar_one_or_none()
      
    if job is None:
        raise HTTPException(
            status_code=404,
            detail = "No application associated with this id"
        )
    
    db.delete(job)
    db.commit()

    return {"message": "Application has been deleted"}


@app.put("/applications/{application_id}")
def put_application(application_id:int, application:ApplicationCreate, db: Session = Depends(get_db)):
    result = db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id
        )
    )
    
    job_application = result.scalar_one_or_none()
    if job_application is None:
        raise HTTPException(
            status_code=404,
            detail = "No application associated with this id"
        )
        
    update_data = {
        "company": application.company,
        "role": application.role,
        "status": application.status,
        "location": application.location,
        "pay": application.pay,
        "job_description": application.job_description
    }
    
    for key, value in update_data.items():
        setattr(job_application, key, value)
    
    job_application.apply_date = (
        application.apply_date 
        if application.apply_date 
        else datetime.date.today()
    )
    
    job_application.job_url = (
        str(application.job_url)
        if application.job_url
        else None
    )
    
    db.commit()
    return {"message": f"Successfully updated application {application_id}."}


@app.patch("/applications/{application_id}")
def patch_application(application_id: int, application:ApplicationUpdate, db: Session = Depends(get_db)):
    result = db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id
        )
    )
    
    job_application = result.scalar_one_or_none()
    if job_application is None:
        raise HTTPException(
            status_code=404,
            detail = "No application associated with this id"
        )
    
    required_fields = {"company", "role", "status", "apply_date"}
    
    for field in application.model_fields_set:
        value = getattr(application, field)

        if field in required_fields and value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )
        
        if field == "job_url" and value is not None:
            value = str(value)
                
        setattr(job_application, field, value)
    
    db.commit()
    return {"message": f"Successfully updated application {application_id}."}

# def track_job():
#     print("Please type in your application details!")
#     company = input("Company: ")
#     role = input("Role: ")
#     statuses = list(ApplicationStatus)
#     while True:
#         try:
#             status_num = int(input("""Choose Status based on number:
                                   
#                             1. Applied
#                             2. OA
#                             3. Interview
#                             4. Final Round
#                             5. Rejected
#                             6. Offer
                            
#                             Enter number: """
#                             )) - 1
#             if 0<= status_num < len(statuses):
#                 break
#             print(f"Number has to be between 1 to {len(statuses)}\n")
        
#         except ValueError:
#             print("Choose a number, not text\n")
            
#     status = statuses[status_num]        
#     job_url = input("Job URL (optional): ") or None
#     location = input("Location (optional): ") or None
#     pay = input("Pay (optional): ") or None
#     job_description = input("Job Description (optional): ") or None
        
    
#     job = JobApplication(company= company, 
#                             role= role, 
#                             status= status, 
#                             job_url= job_url, 
#                             location= location,
#                             pay= pay,
#                             job_description= job_description) 
    
#     applications.append(job)
    
#     print("Application Saved!\n")

# def view_job() -> None:
#     if not applications:
#         print("There is no applications yet, add some now!\n")
#         return
    
#     for i, job in enumerate(applications, start=1):
#         print(f"{i}, {job}")
    
#     while True:
#         try:
#             job_num = int(input("Which job would you like to see? Type in the corresponding number to view the job.")) - 1
            
#             if 0 <= job_num <len(applications):
#                 break
            
#             print("choose a numeber from the list\n")
#         except ValueError:
#             print("Please choose a number\n")
            
#     applications[job_num].details()

# def find_job() -> None:
#     if not applications:
#         print("There is no applications yet, add some now!\n")
#         return
    
#     target_input = input("Please type in the name of the company you are looking for: \n")
#     target = target_input.strip().lower()
#     result = []
#     for application in applications:
#         if target in application.company.lower():
#             result.append(application)
    
#     if not result:
#         print(f"There are no applications for a company named {target_input}\n")
#         return
    
#     for i, job in enumerate(result, start=1):
#         print(f"{i}, {job}")
    
#     while True:
#         try:
#             job_num = int(input("Which job would you like to see? Type in the corresponding number to view the job.")) - 1
            
#             if 0 <= job_num <len(result):
#                 break
            
#             print("choose a numeber from the list\n")
#         except ValueError:
#             print("Please choose a number\n")
            
#     result[job_num].details()
    
# def delete_job() -> None:
#     if not applications:
#         print("There is no applications yet, add some now!\n")
#         return
    
#     for i, job in enumerate(applications, start=1):
#         print(f"{i}, {job}")
    
#     while True:
#         try:
#             job_num = int(input("Which job would you like to delete? Type in the corresponding number to delete the job.")) - 1
            
#             if 0 <= job_num <len(applications):
#                 break
            
#             print("choose a numeber from the list\n")
#         except ValueError:
#             print("Please choose a number\n")
            
#     removed = applications.pop(job_num)
#     print(f"{removed} is deleted\n")
    
# def main():
#     while True:
#         try:
#             action = int(input("""Welcome to the Job Application Tracker!
#                 What can I do for you today?
                
#                 1. Add application
#                 2. View applications
#                 3. Find applications
#                 4. Delete applications
#                 5. Exit
                
#                 Choose a number: \n"""
#             ))
            
#             if action == 1: 
#                 track_job()
#             elif action == 2:
#                 view_job()
#             elif action == 3:
#                 find_job()
#             elif action == 4:    
#                 delete_job()
#             elif action == 5:
#                 print("Goodbye!")
#                 sys.exit()
#             else:    
#                 print("Choose a number between 1 and 5\n")
            
#         except ValueError:
#             print("Choose a number, not text\n")
    

# if __name__ == "__main__":
#     main()