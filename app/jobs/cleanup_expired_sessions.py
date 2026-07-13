from app.dependencies import RequiresSessionRepository
from app.jobs.scheduler import daily

@daily(id='cleanup_sessions')
async def cleanup_expired_sessions(session_repo: RequiresSessionRepository):
    session_repo.delete_all_expired()