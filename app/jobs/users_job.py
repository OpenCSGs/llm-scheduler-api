import datetime
import logging
import platform
import pwd
import grp
from slurm import slurm_operation

# define a global varibale
slurm_user_list = []


def sync_user_group():
    global slurm_user_list
    logging.info('[sync_user_group] running at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    system = platform.system()
    if system != "Linux":
        logging.warning("Ignore sync up task in "+system)
        return
    # create default group, create it if not exist
    slurm_operation.updateGroup('default', 'default group')
    batch_size = 20
    usergroups = []
    for p in pwd.getpwall():
        if 'nologin' in p[6] or 'false' in p[6] or p[2] < 1000:
            # ignore system user
            continue
        name = p[0]
        if name in slurm_user_list:
            # do not add it again
            continue
        else:
            slurm_user_list.append(name)
        try:
            group = grp.getgrgid(p[3])[0]
        except Exception:
            group = ''
            logging.warn("Can not find user group for "+name)
        usergroups.append({'name': name, 'group': group})
        if len(usergroups) == batch_size:
            slurm_operation.updateUsers(usergroups)
            usergroups.clear()
    if len(usergroups) > 0:
        slurm_operation.updateUsers(usergroups)
