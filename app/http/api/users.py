from fastapi import APIRouter
from fastapi import Request, HTTPException
from config.config import settings
from slurm import slurm_auth
import requests
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/users"
)


@router.get("/")
def index():
    return "Users Index"


@router.post("/set_admins")
async def index(request: Request):
    userInfo = slurm_auth.decode(request)
    if userInfo['isAdmin'] is False:
        raise HTTPException(
            status_code=403,
            detail="Not authenticated"
        )
    session = requests.Session()
    slurm_auth.add_slurm_header(request)
    users = await request.json()
    print(users)
    r1 = session.post(
        headers=request.headers,
        json=users,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/users",
    )
    return JSONResponse(r1.json(), status_code=r1.status_code)
