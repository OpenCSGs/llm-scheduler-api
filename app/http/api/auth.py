import logging

from config.config import settings
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pam import pam
from slurm import slurm_auth
import requests

router = APIRouter(
    prefix="/auth"
)


@router.post("/signin", response_class=JSONResponse)
async def signin(request: Request):
    if settings.ON_PREMISE is True:
        user = await request.json()
        result = authenticate(user['username'], user['password'])
        if result is True:
            isadmin = isAdmin(user['username'])
            token = slurm_auth.makejwt(user['username'], isadmin)
            return {'success': True, 'token': token, 'userinfos': {'username': user['username'], 'name': user['username'], "isAdmin": isadmin}}
        else:
            return JSONResponse({"status": 'error', 'message': 'Invalid username or password'}, status_code=403)
    else:
        sdk = request.app.state.CASDOOR_SDK
        code = request.query_params.get("code")
        if code is not None:
            try:
                token = sdk.get_oauth_token(code)
                userinfos = sdk.parse_jwt_token(token.get('access_token'), options={
                                                "verify_iat": False, "verify_nbf": False, })
            except Exception as e:
                print(e)
                return JSONResponse({"status": 'error'}, status_code=500)
            return {'success': True, 'token': token.get('access_token'), 'userinfos': userinfos}
        else:
            return JSONResponse(None, status_code=500)


def isAdmin(username, newToken=None):
    if newToken is None:
        newToken = slurm_auth.makejwt(username, False)
    headers = {
        "Content-type": "application/json",
        "X-SLURM-USER-NAME": username,
        "X-SLURM-USER-TOKEN": newToken,
    }
    session = requests.Session()
    r1 = session.get(
        headers=headers,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/user/"+username,
    )
    user = r1.json()['users']
    if "Administrator" in user[0]['administrator_level']:
        return True
    else:
        return False


def authenticate(name, password):
    """
    Returns true or false depending on the success of the name-password
    """
    try:
        success = pam().authenticate(name, password)
        if success is True:
            return success
    except Exception as e:
        logging.warning(e)

    return False
