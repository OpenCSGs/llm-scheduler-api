import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from app.providers import logging_provider
from app.jobs.users_job import sync_user_group
import datetime
from config.config import settings


def create_scheduler() -> AsyncIOScheduler:
    logging_provider.register()

    logging.info("AsyncIOScheduler initializing")

    scheduler: AsyncIOScheduler = AsyncIOScheduler()

    register_job(scheduler)

    return scheduler


def register_job(scheduler):
    """
     注册调度任务
    """
    scheduler.add_job(sync_user_group, 'interval', minutes=settings.OS_USER_SYNC_INTERVAL,
                      next_run_time=datetime.datetime.now())
