import requests
from config.config import settings
from fastapi import APIRouter, HTTPException, Request
from slurm import slurm_auth
from itertools import groupby

router = APIRouter(prefix="/jobs")


def call_api(request: Request, path: str, context="/slurm/"):
    session = requests.Session()
    url = settings.SLURM_API + context + settings.SLURM_REST_VERSION + path
    print(url)
    slurm_auth.add_slurm_header(request)
    r1 = session.get(
        headers=request.headers,
        url=url,
    )

    if r1.status_code != 200:
        raise HTTPException(
            status_code=403,
            detail="Not authenticated"
        )

    return r1.json()


@router.get("/list")
def get_user_jobs(request: Request):
    current_user = request.headers.get("x-slurm-user-name")
    userInfo = slurm_auth.decode(request)
    param = request.url.query
    if userInfo['isAdmin'] is False:
        param = param + "&users="+current_user
    r1_json = call_api(request, "/jobs?"+param, "/slurmdb/")
    return r1_json


def find_queue(name, partitions):
    for p in partitions:
        if p.name == name:
            return p
    return None


@router.get("/queues")
def get_user_jobqueues(request: Request):
    userInfo = slurm_auth.decode(request)
    if userInfo['isAdmin']:
        ori_data = call_api(request, "/associations", "/slurmdb/")
    else:
        current_user = request.headers.get("x-slurm-user-name")
        ori_data = call_api(request, "/associations?user="+current_user, "/slurmdb/")
        return ori_data

    data = ori_data['associations']
    data.sort(key=lambda x: x["user"])  # 先按照 "name" 进行排序

    groups = groupby(data, key=lambda x: x["user"])

    # 聚合结果
    aggregated_data = []
    keys = ['cluster', 'partition', 'qos', 'account']
    for key, group in groups:
        merged_values = {}
        for item in group:
            for field, value in item.items():
                if field != "user" and field in keys:
                    if isinstance(value, list):
                        merged_values.setdefault(field, set()).add(",".join(value))
                    else:
                        merged_values.setdefault(field, set()).add(value)
        merged_values["user"] = key
        aggregated_data.append(merged_values)
    print(aggregated_data)
    return {"associations": aggregated_data}


@router.get("/queue/{name}")
def get_queue(name: str, request: Request):
    return call_api(request, "/partition/"+name)
