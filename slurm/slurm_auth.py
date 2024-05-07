import json
import jwt
import time
import os
from fastapi import Request, HTTPException
from base64 import urlsafe_b64encode
from config.config import settings
from jwt.api_jwt import PyJWT
keyPath = os.path.dirname(os.path.abspath(__file__))


def b64encode(s: bytes) -> str:
    s_bin = urlsafe_b64encode(s)
    s_bin = s_bin.replace(b'=', b'')
    return s_bin.decode('ascii')


with open(keyPath + "/jwt_hs256.key", "rb") as f:
    priv_key = f.read()
dict = {"kty": "oct", "k": b64encode(priv_key)}

signing_key = jwt.algorithms.HMACAlgorithm.from_jwk(json.dumps(dict))
a = PyJWT()


def add_slurm_header(request: Request):
    if settings.ON_PREMISE is True:
        return
    newToken = makejwt(request.headers.get("x-slurm-user-name"))
    request.headers.__dict__["_list"].append(
        (
            "x-slurm-user-token".encode(),
            f"{newToken}".encode(),
        )
    )


def makejwt(username):
    message = {
        "exp": int(time.time() + 604800),
        "iat": int(time.time()),
        "sun": username,
    }
    compact_jws = a.encode(message, signing_key, algorithm="HS256")
    return compact_jws


def decode(request):
    token = request.headers.get("X-SLURM-USER-TOKEN")
    if settings.ON_PREMISE is True:
        return jwt.decode(token, key=signing_key, algorithm="HS256")
    else:
        sdk = request.app.state.CASDOOR_SDK
        userinfos = sdk.parse_jwt_token(token, options={
            "verify_iat": False, "verify_nbf": False, })
        return userinfos


async def verify(request: Request):
    token = request.headers.get("X-SLURM-USER-TOKEN")
    try:
        if settings.ON_PREMISE is True:
            userinfos = jwt.decode(token, key=signing_key, algorithm="HS256")
        else:
            sdk = request.app.state.CASDOOR_SDK
            userinfos = sdk.parse_jwt_token(token, options={
                "verify_iat": False, "verify_nbf": False, })
            print(userinfos)
        if userinfos['name'] != request.headers.get("X-SLURM-USER-NAME"):
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


if __name__ == "__main__":
    print(makejwt("test"))
