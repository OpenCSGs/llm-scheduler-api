from fastapi import APIRouter, Request
from config.config import settings
from fastapi.responses import JSONResponse
import logging
import json
from slurm import slurm_auth, slurm_operation

router = APIRouter(prefix="/webhook")


@router.post("/usergroup")
async def updateUserAndGroup(request: Request):
    user_agent = request.headers.get("user-agent")
    secret = request.headers.get("x-casdoor-token")
    if "casdoor-webhook" not in user_agent:
        logging.info("Invalid webhook user_agent")
        return JSONResponse(content="Invalid webhook user_agent", status_code=500)
    if settings.CASDOOR_WEBHOOK_SECRET != secret:
        logging.info("Invalid webhook secret")
        return JSONResponse(content="Invalid webhook secret", status_code=500)
    message = await request.json()
    print(json.dumps(message, indent=4))
    event_type = message["action"]
    new_object = json.loads(message['object'])

    match event_type:
        case "signup":
            logging.info("receive a signup event: " + new_object['username'])
            return slurm_operation.updateUser(new_object['username'], new_object.get('groups', None))
        case "add-user":
            logging.info("receive a add-user event: " + new_object['username'])
            return slurm_operation.updateUser(new_object['username'], new_object.get('groups', None))
        case "update-user":
            logging.info("receive a update-user event: " + new_object['username'])
            return slurm_operation.updateUser(new_object['username'], new_object.get('groups', None))
        case "add-group":
            logging.info("receive a add-group event")
            return slurm_operation.updateGroup(new_object)
        case "update-group":
            logging.info("receive a update-group event")
            slurm_operation.updateGroup(new_object)
        case _:
            # do nothing
            logging.info("Ignore event type from webhook: " + event_type)
