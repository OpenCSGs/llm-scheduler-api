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
import logging
from k8s.client import client
from k8s.nodestat import KubeResources


router = APIRouter(prefix="/k8s")


@router.get("/")
def index():
    return "Nodes Index"


@router.get("/nodes")
def get_k8s_cluster(request: Request):
    resource = KubeResources(client.CoreV1Api())
    result = {'nodes': resource.getNodes()}
    return result
