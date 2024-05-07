from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from config.config import settings
import requests
from slurm import slurm_auth
import logging


def updateUser(username, groups):
    session = requests.Session()
    newToken = slurm_auth.makejwt("root")
    headers = {
        "Content-type": "application/json",
        "X-SLURM-USER-NAME": "root",
        "X-SLURM-USER-TOKEN": newToken,
    }
    users = {"users": [{"name": username}]}
    r1 = session.post(
        headers=headers,
        json=users,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/users",
    )
    if r1.status_code == 200:
        logging.info("Succeed to add user:" + username)
    else:
        logging.error(
            "Error to add user:" + username + ", status code:" +
            str(r1.status_code) + ", reason:" + r1.content.decode("utf-8")
        )
        return
    # assign this user to default group
    associations = {
        "associations": [
            {
                "account": "default",
                "cluster": "cluster-opencsg",
                "user": username,
                "parent_account": "root",
                "partition": settings.SLURM_DEFAULT_PARTITION,
                "qos": ["default"],
            },
        ]
    }
    if groups is not None:
        for group in groups:
            associations['associations'].append({
                {
                    "account": group,
                    "cluster": "cluster-opencsg",
                    "user": username,
                    "parent_account": "root",
                    "partition": settings.SLURM_DEFAULT_PARTITION,
                    "qos": ["default"],
                }
            })
    r2 = session.post(
        headers=headers,
        json=associations,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/associations"
    )
    if r1.status_code == 200:
        logging.info("Succeed to assign default group to user:" + username)
        return JSONResponse(content="success", status_code=200)
    else:
        logging.error("Error to assign default group to user:" + username)
        return JSONResponse(content="fail", status_code=500)


def updateUsers(userGroups: list):
    session = requests.Session()
    newToken = slurm_auth.makejwt("root")
    headers = {
        "Content-type": "application/json",
        "X-SLURM-USER-NAME": "root",
        "X-SLURM-USER-TOKEN": newToken,
    }
    users = {"users": []}
    names = []
    for ug in userGroups:
        names.append(ug['name'])
        if ug['name'] == settings.ADMINISTRATOR.strip():
            users['users'].append({'name': ug['name'], "administrator_level": ["Administrator"]})
        else:
            users['users'].append({'name': ug['name']})
    r1 = session.post(
        headers=headers,
        json=users,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/users",
    )
    if r1.status_code == 200:
        logging.info("Succeed to add users:" + ' '.join(names))
    else:
        logging.error(
            "Error to add user:" + ' '.join(names) + ", status code:" +
            str(r1.status_code) + ", reason:" + r1.content.decode("utf-8")
        )
        return
    # assign this user to default group
    associations = {
        "associations": []}
    for ug in userGroups:
        associations['associations'].append({
            "account": "default",
            "cluster": "cluster-opencsg",
            "user": ug['name'],
            "parent_account": "root",
            "partition": settings.SLURM_DEFAULT_PARTITION,
            "qos": ["default"],
        })
        if ug['group'] != '':
            associations['associations'].append({
                "account": ug['group'],
                "cluster": "cluster-opencsg",
                "user": ug['name'],
                "parent_account": "root",
                "partition": settings.SLURM_DEFAULT_PARTITION,
                "qos": ["default"],
            })
    r2 = session.post(
        headers=headers,
        json=associations,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/associations"
    )
    if r1.status_code == 200:
        logging.info("Succeed to assign group to users: " + ' '.join(names))
        return JSONResponse(content="success", status_code=200)
    else:
        logging.error("Error to assign default group to user:" + ' '.join(names))
        return JSONResponse(content="fail", status_code=500)


def updateGroup(name, desc, org="opencsg"):
    session = requests.Session()
    newToken = slurm_auth.makejwt("root")
    headers = {
        "Content-type": "application/json",
        "X-SLURM-USER-NAME": "root",
        "X-SLURM-USER-TOKEN": newToken,
    }
    accounts = {
        "accounts": [{
            "name": name,
            "description": '' if desc == None else desc,
            "organization": org
        }]
    }
    r1 = session.post(
        headers=headers,
        json=accounts,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/accounts",
    )
    if r1.status_code == 200:
        logging.info("Succeed to add group:" + name)
        return JSONResponse(content="success", status_code=200)
    else:
        logging.error(
            "Error to add user:" + name + ", status code:" +
            str(r1.status_code) + ", reason:" + r1.content.decode("utf-8")
        )
        return JSONResponse(content="fail", status_code=500)


def assignUsersToGroup(message):
    session = requests.Session()
    newToken = slurm_auth.makejwt("root")
    headers = {
        "Content-type": "application/json",
        "X-SLURM-USER-NAME": "root",
        "X-SLURM-USER-TOKEN": newToken,
    }
    groupName = message['name']
    ugs = []
    for user in message['data']['users']:
        ug = {
            "account":   groupName,
            "cluster": "cluster-opencsg",
            "user": user['username'],
            "partition": settings.SLURM_DEFAULT_PARTITION,
            "qos": ["default"]
        }
        ugs.append(ug)
    print(ugs)
    associations = {
        "associations": ugs
    }
    r1 = session.post(
        headers=headers,
        json=associations,
        url=settings.SLURM_API + "/slurmdb/" + settings.SLURM_REST_VERSION + "/associations",
    )
    if r1.status_code == 200:
        logging.info("Succeed to add users to group: " + message['name'])
        return JSONResponse(content="success", status_code=200)
    else:
        logging.error(
            "Error to add user:" + message['name'] + ", status code:" +
            str(r1.status_code) + ", reason:" + r1.content.decode("utf-8")
        )
        return JSONResponse(content="fail", status_code=500)
