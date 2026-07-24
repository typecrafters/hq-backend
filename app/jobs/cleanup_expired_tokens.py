from app.dependencies import RequiresTokenRepository
from app.jobs.scheduler import daily
from sqlalchemy.orm import Session
from app.db.session import engine

    
@daily(id='cleanup_tokens')
async def cleanup_expired_tokens():
    with Session(engine) as token_repo:
        token_repo.delete_all_expired()