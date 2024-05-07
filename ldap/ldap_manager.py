from base64 import b64encode
import math
import time
import ldap
import ldap.modlist as modlist
import logging
from config.config import settings


class LDAPManager():

    def __init__(self, ldap_host=settings.LDAP_URI, base_dn=settings.BASE_DN, user=settings.BIND_DN, password=settings.BIND_DN_PWD):
        self.base_dn = base_dn
        self.ldap_host = ldap_host
        self.user = user
        self.password = password
        self.home_directory = settings.HOME_DIRECTORY
        try:
            self.ldapconn = ldap.initialize(ldap_host)
            self.ldapconn.simple_bind(user, password)
        except ldap.LDAPError as e:
            logging.error(str(e))
            print(e)

    def add_user(self, user):
        dn = 'uid=' + user['username'] + ',' + self.base_dn
        home_dir = self.home_directory + '/' + user['username']

        if str(user['id']).isnumeric():
            uidNumber = user['id']
        else:
            uidNumber = self.get_uid_number()
        lastchange = int(math.floor(time() / 86400))
        entry = []
        entry.extend([
            ('objectClass', [b"top", b"account", b"posixAccount", b"shadowAccount"]),
            ('uid', user['username'].encode()),
            ('cn', user['username'].encode()),
            ('uidNumber', uidNumber.encode()),
            ('gidNumber', uidNumber.encode()),
            ('loginShell', "/bin/sh".encode()),
            ('description', user['description'].encode()),
            ('homeDirectory', home_dir.encode()),
            ('shadowMax', b"0"),
            ('shadowWarning', b"0"),
            ('shadowLastChange', str(lastchange).encode()),
            ('userPassword', b"opencsg")
        ])
        try:
            self.ldapconn.add_s(dn, entry)
            return {"status": True}
        except ldap.LDAPError as e:
            logging.error(e)
            return {"status": False, "message": str(e)}
        finally:
            self.ldapconn.unbind_s()

    def get_uid_number(self):
        u = self.ldap_get_user("llmsystem")
        if u is None:
            iuser = {'username': 'llmsystem', 'id': '1000', 'description': "1000"}
            self.add_user(iuser)
            return "1000"
        else:
            previous_uid_number = u['description']
            new_uid_number = int(previous_uid_number)+1
            self.update_user(u, {'description': new_uid_number})
            return new_uid_number

    def ldap_get_user(self, uid=None):
        '''
        获取ldap用户详情,失败返None
        '''
        obj = self.ldapconn
        searchScope = ldap.SCOPE_SUBTREE
        searchFilter = "cn=" + uid
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, None)
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                username = result_data[0][1]['cn'][0]
                description = result_data[0][1]['description'][0]
                result = {'username': username, 'description': description}
                return result
            else:
                return None
        except ldap.LDAPError as e:
            logging.error(str(e))

    def update_user(self, new_user, old_user):
        cn = old_user['id']
        dn = 'cn={0},{1}'.format(cn, self.base_dn)
        try:
            old = {'description': [old_user['description']]}
            new = {'description': [new_user['description']]}
            mlist = modlist.modifyModlist(old, new)
            self.ldapconn.modify_s(dn, mlist)
            return {"status": True}
        except ldap.LDAPError as e:
            logging.error(str(e))
            return {"status": False}
