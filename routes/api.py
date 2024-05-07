from fastapi import APIRouter, Depends
from app.http.api import demo
from app.http.api import auth
from app.http.api import users
from app.http.api import dashboard
from app.http.api import webhook
from app.http.api import nodes
from app.http.api import workloads
from app.http.api import hpcapis
from app.http.api import jobs
from slurm.slurm_auth import verify


api_router = APIRouter()

api_router.include_router(demo.router, tags=["demo"])

api_router.include_router(auth.router, tags=["auth"], prefix="/v1")

api_router.include_router(users.router, tags=["users"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(dashboard.router, tags=["dashboard"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(webhook.router, tags=["webhook"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(nodes.router, tags=["nodes"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(workloads.router, tags=["workloads"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(hpcapis.router, tags=["hpcapis"], prefix="/v1", dependencies=[Depends(verify)])

api_router.include_router(jobs.router, tags=["jobs"], prefix="/v1", dependencies=[Depends(verify)])
