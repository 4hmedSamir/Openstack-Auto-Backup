#!/bin/bash
argv[1]=$1 #$NAME 
argv[2]=$2 #$username
argv[3]=$3 #$tenant_name
argv[4]=$4 #$password
argv[5]=$5 #$auth_url


export OS_AUTH_URL=$5
export OS_TENANT_NAME=$3
export OS_USERNAME=$2
export OS_PASSWORD=$4

KERNEL=`glance image-show $1 | grep "kernel_id" | cut -d"|" -f3`
RAM_DISK=`glance image-show $1 | grep "ramdisk_id" | cut -d"|" -f3`
IMG = `glance image-show $1 | grep "id" | cut -d"|" -f3`

glance image-delete $KERNEL
glance image-delete $RAM_DISK
glance image-delete $IMG
