#!/usr/bin/env python
import os

OS_USERNAME="test_user"
OS_PASSWORD=""
OS_TENANT_NAME="test"
OS_AUTH_URL="http://172.16.17.10:5000/v2.0/"

def get_dest_keystone_creds():
    d = {}
    d['username'] = OS_USERNAME
    d['password'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['tenant_name'] = OS_TENANT_NAME
    return d

def get_dest_nova_creds():
    d = {}
    d['username'] = OS_USERNAME
    d['api_key'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['project_id'] = OS_TENANT_NAME
    return d
