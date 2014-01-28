#!/bin/bash
argv[1]=$1 #$NAME 
argv[2]=$2 #$PATH
argv[3]=$3 #$KERNEL
argv[4]=$4 #$RAM
argv[5]=$5 #$IMG_PATH
argv[6]=$6 #$USER_NAME
argv[7]=$7 #$TENANT_NAME
argv[8]=$8 #$PASSWORD
argv[9]=$9 #$AUTH_URL

export OS_AUTH_URL=$9
export OS_TENANT_NAME=$7
export OS_USERNAME=$6
export OS_PASSWORD=$8

KERNEL=`glance image-create --name=$3 --disk-format=aki --container-format=aki < $2$3 | awk '/ id / { print $4 }'`
RAM_DISK=`glance image-create --name=$4 --disk-format=ari --container-format=ari < $2$4 | awk '/ id / { print $4 }'`
glance image-create --name=$1 --disk-format=ami --container-format=ami --property kernel_id=${KERNEL} --property ramdisk_id=${RAM_DISK} < $5
