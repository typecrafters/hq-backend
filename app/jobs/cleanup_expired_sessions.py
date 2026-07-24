from app.dependencies import RequiresSessionRepository
from app.jobs.scheduler import daily
from sqlalchemy.orm import Session
from app.db.session import engine
    
    
@daily(id='cleanup_sessions')
async def cleanup_expired_sessions():
    with Session(engine) as session_repo:
        session_repo.delete_all_expired()