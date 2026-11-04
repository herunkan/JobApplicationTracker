import datetime
from enums import ApplicationSortBy, ApplicationStatus, SortOrder
from schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse, HistoryResponse
from fastapi import FastAPI, HTTPException, Depends, Query
from models import JobApplication, JobApplicationStatusHistory
from database import get_db
from sqlalchemy import select, func
from sqlalchemy.orm import Session


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Job Tracker API is running"}

@app.get("/applications", response_model=list[ApplicationResponse])
def get_applications(
    db: Session = Depends(get_db),
    company:str|None = None, 
    role:str|None = None, 
    location:str|None = None,
    status:ApplicationStatus|None = None,
    sort_by:ApplicationSortBy|None = None,
    order:SortOrder|None = None,
    limit:int|None = Query(default=None, ge=1),
    offset:int|None = Query(default=None, ge=0)
    ):
    statement = select(JobApplication)
    if company is not None:
        statement = statement.where(JobApplication.company.ilike(f"%{company}%"))
        
    if role is not None:
        statement = statement.where(JobApplication.role.ilike(f"%{role}%"))
    
    if status is not None:
        statement = statement.where(JobApplication.status == status)
        
    if location is not None:
        statement = statement.where(JobApplication.location.ilike(f"%{location}%"))
    
    if sort_by is not None:
        if order == SortOrder.ASC:
            statement = statement.order_by(JobApplication.apply_date.asc())
        else:
            statement = statement.order_by(JobApplication.apply_date.desc())
    
    if limit is not None:
        statement = statement.limit(limit)
    if offset is not None:
        statement = statement.offset(offset)
        
    result = db.execute(statement)
    jobs = result.scalars().all()
    
    return jobs

@app.get("/applications/stats")
def get_application_aggregation(db: Session = Depends(get_db), days: int = Query(default=7, ge=1)):
    count_by_status = db.execute(
        select(JobApplication.status,
               func.count(JobApplication.id)).group_by(
            JobApplication.status
        )
    )
    
    count_all_applications = db.execute(
        select(func.count(JobApplication.id))
    )
    
    count_by_company = db.execute(
        select(
            JobApplication.company,
            func.count(JobApplication.id)
        ).group_by(
            JobApplication.company
        )
    )
    
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days-1)
    count_recent_applications = db.execute(
        select(func.count(JobApplication.id)).where(
            JobApplication.apply_date.between(start_date, today)
        )
    )
      
    job_count_all = count_all_applications.scalar_one()
    job_by_status = count_by_status.all()
    job_by_company = count_by_company.all()
    job_count_recent = count_recent_applications.scalar_one()
    
    by_status = {}
    by_company = {}
    
    for status, count in job_by_status:
        by_status[status.value] = count
    for company, count in job_by_company:
        by_company[company] = count     
    
    return {
            "application_count" : job_count_all,
            "by_status" : by_status,
            "by_company": by_company,
            "recent_applications": job_count_recent
            }    
        
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

@app.get("/applications/{application_id}/history", response_model=list[HistoryResponse])
def get_specific_application_history(application_id:int, db:Session = Depends(get_db)):
    result = db.execute(
        select(JobApplicationStatusHistory).where(
            JobApplicationStatusHistory.application_id == application_id
        ).order_by(
            JobApplicationStatusHistory.changed_at.asc()
        )
    )
    
    history = result.scalars().all()
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail = "No application associated with this id"
        )
        
    return history
        
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
    db.flush()
    
    history_data = {
        "status": application.status,
        "application_id": new_job.id
    }
    history = JobApplicationStatusHistory(**history_data)
    db.add(history)    
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


@app.put("/applications/{application_id}", response_model=ApplicationResponse)
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
    
    if application.status != job_application.status:
        history = JobApplicationStatusHistory(
                application_id = job_application.id,
                status = application.status 
            )
        db.add(history)
        
    
    for key, value in update_data.items():
        setattr(job_application, key, value)
    
    job_application.apply_date = (
        application.apply_date 
        if application.apply_date 
        else job_application.apply_date
    )
    
    job_application.job_url = (
        str(application.job_url)
        if application.job_url
        else None
    )
    
    db.commit()
    db.refresh(job_application)
    return job_application

@app.patch("/applications/{application_id}", response_model=ApplicationResponse)
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
            
        if field == "status" and value != job_application.status:
            history = JobApplicationStatusHistory(
                application_id = job_application.id,
                status = value 
            )
            db.add(history)
                
        setattr(job_application, field, value)
    
    db.commit()
    db.refresh(job_application)
    return job_application