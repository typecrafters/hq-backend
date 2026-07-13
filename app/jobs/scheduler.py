from datetime import timezone
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger, datetime

scheduler = AsyncIOScheduler()
daily_trigger = IntervalTrigger(days=1, start_date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
hourly_trigger = IntervalTrigger(hours=1, start_date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))

def daily(**kwargs):
    def decorator(fn: Callable):
        scheduler.add_job(fn, trigger=daily_trigger, **kwargs)
        return fn
    return decorator

def hourly(**kwargs):
    def decorator(fn: Callable):
        scheduler.add_job(fn, trigger=hourly_trigger, **kwargs)
        return fn
    return decorator