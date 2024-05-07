from fastapi import APIRouter, Depends

from app.http.deps import get_db
from app.models.user import User
from app.providers.database import redis_client
from app.services.auth import hashing
import requests
from fastapi import Request
from config.config import settings
from fastapi.responses import JSONResponse
import re
from slurm import slurm_auth
import logging

INVALID_STATUS = ["DOWN", "DRAINED", "FAIL", "FAILING", "INVAL", "UNKNOWN", "NOT_RESPONDING"]
pattern = r"\d+"
patternMemory = "mem=([^,}]+)"
patternCPU = "cpu=([^,}]+)"

router = APIRouter(prefix="/dashboard")


@router.get("/")
def index():
    return "Dashboard Index"


@router.get("/hpc")
def get_hpc_cluster(request: Request):
    session = requests.Session()
    result = {}
    slurm_auth.add_slurm_header(request)
    r1 = session.get(
        headers=request.headers,
        url=settings.SLURM_API + "/slurm/" + settings.SLURM_REST_VERSION + "/jobs",
    )
    jobStates = {"done": 0, "pending": 0, "suspended": 0, "running": 0, "other": 0}
    if r1.status_code != 200:
        logging.error("No jobs found, error code:" + str(r1.status_code))
    else:
        jobs = r1.json()
        for job in jobs["jobs"]:
            if job["job_state"][0].upper() == "COMPLETED":
                jobStates["done"] += 1
            elif job["job_state"][0].upper() == "PENDING":
                jobStates["pending"] += 1
            elif job["job_state"][0].upper() == "RUNNING":
                jobStates["running"] += 1
            elif job["job_state"][0].upper() == "SUSPENDED":
                jobStates["suspended"] += 1
            else:
                jobStates["other"] += 1

    session = requests.Session()
    r2 = session.get(
        headers=request.headers,
        url=settings.SLURM_API + "/slurm/" + settings.SLURM_REST_VERSION + "/nodes",
    )
    nodeStates = {"available": 0, "unavailable": 0}
    workingSates = {"busy": 0, "total": 0}
    MemStates = {"free": 0, "total": 0}
    GPUStats = {"used": 0, "total": 0}
    CPUStats = {"used": 0, "total": 0}
    if r2.status_code != 200:
        logging.error("Error to query /nodes, status code: " + str(r2.status_code))
    else:
        nodes = r2.json()

        for node in nodes["nodes"]:
            if "".join(node["state"][0]).upper() in INVALID_STATUS:
                nodeStates["unavailable"] += 1
            else:
                nodeStates["available"] += 1
                workingSates['total'] += 1
                if node['alloc_memory'] > 0:
                    workingSates['busy'] += 1
                CPUStats["total"] += node['cpus']
                CPUStats["used"] += node['alloc_cpus']
                if node["tres_used"] != None:
                    usedMemStr = re.findall(patternMemory, node["tres_used"])
                    usedMemStr = "".join(usedMemStr).replace("G", "")
                    if not usedMemStr:
                        usedMemStr = "0"
                    MemStates["free"] += (
                        int(node["real_memory"]) - int(node['alloc_memory'])
                    )
                    MemStates["total"] += node["real_memory"]
                else:
                    MemStates["free"] += node["real_memory"]
                    MemStates["total"] += node["real_memory"]
            if node["gres"] != None:
                total = re.findall(pattern, node["gres"])
                used = re.findall(pattern, node["gres_used"])
                if not total:
                    total = ["0"]
                if not used == 0:
                    used = ["0"]
                GPUStats["used"] += int("".join(used[0]))
                GPUStats["total"] += int("".join(total[0]))

    result["nodes"] = nodeStates
    result["memory"] = MemStates
    result["gpus"] = GPUStats
    result["cpus"] = CPUStats
    result["workloads"] = jobStates
    result['workingSates'] = workingSates
    return result
