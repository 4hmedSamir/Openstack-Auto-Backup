#!/usr/bin/env python
import os

OS_USERNAME="admin"
OS_PASSWORD=""
OS_TENANT_NAME="admin"
OS_AUTH_URL="http://172.16.16.50:5000/v2.0/"

os.environ['OS_USERNAME']=OS_USERNAME
os.environ['OS_PASSWORD']=OS_PASSWORD
os.environ['OS_AUTH_URL']=OS_AUTH_URL
os.environ['OS_TENANT_NAME']=OS_TENANT_NAME

def get_keystone_creds():
    d = {}
    d['username'] = OS_USERNAME
    d['password'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['tenant_name'] = OS_TENANT_NAME
    return d

def get_nova_creds():
    d = {}
    d['username'] = OS_USERNAME
    d['api_key'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['project_id'] = OS_TENANT_NAME
    return d
