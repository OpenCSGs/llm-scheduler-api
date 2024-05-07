from fastapi import Request
from bootstrap.application import create_app
from config.config import settings
import uvicorn
import requests
import sched
import time
from fastapi.responses import JSONResponse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from slurm import slurm_auth
from bootstrap.scheduler import create_scheduler

app = create_app()
scheduler = create_scheduler()


# start up a timer task to sync users
@app.on_event("startup")
async def run_scheduler():
    scheduler.start()


@app.get("/")
async def root():
    return "OpenCSG starcloud API list"


async def _reverse_proxy(request: Request):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    await slurm_auth.verify(request)
    # note this is required to call slurm API
    slurm_auth.add_slurm_header(request)

    try:
        if request.method == "POST" or request.method == "PATCH":
            content = await request.json()
            r = session.request(
                request.method,
                json=content,
                headers=request.headers,
                url=settings.SLURM_API + request.url.path + "?" + request.url.query,
            )

        else:
            r = session.request(
                request.method,
                headers=request.headers,
                url=settings.SLURM_API + request.url.path + "?" + request.url.query,
            )

    except requests.exceptions.ConnectionError:
        return JSONResponse(None, status_code=500)
    return JSONResponse(r.json(), status_code=r.status_code)


# forward all slurm api to slurm server
app.add_route(
    "/slurm/{full_path:path}", _reverse_proxy, [
        "GET", "OPTIONS", "POST", "PATCH", "DELETE"]
)
# forward all slurm api to slurm server
app.add_route(
    "/slurmdb/{full_path:path}", _reverse_proxy, [
        "GET", "OPTIONS", "POST", "PATCH", "DELETE"]
)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=settings.SERVER_HOST,
                port=settings.SERVER_PORT)
