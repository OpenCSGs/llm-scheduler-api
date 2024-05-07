import logging

from fastapi import FastAPI

from app.providers import app_provider
from app.providers import logging_provider
from app.providers import handle_exception
from app.providers import route_provider
from config.config import settings


def create_app() -> FastAPI:
    app = FastAPI()

    register(app, logging_provider)
    register(app, app_provider)
    register(app, handle_exception)

    boot(app, route_provider)
    logging.info("OpenCSG scheduler Env: ON_PREMISE=%s, APPNAME=%s" % (settings.ON_PREMISE, settings.APPNAME))
    return app


def register(app, provider):
    provider.register(app)
    logging.info(provider.__name__ + ' registered')


def boot(app, provider):
    provider.boot(app)
    logging.info(provider.__name__ + ' booted')
