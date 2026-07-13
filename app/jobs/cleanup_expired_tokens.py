from app.dependencies import RequiresTokenRepository
from app.jobs.scheduler import daily

@daily(id='cleanup_tokens')
async def cleanup_expired_tokens(token_repo: RequiresTokenRepository):
    token_repo.delete_all_expired()