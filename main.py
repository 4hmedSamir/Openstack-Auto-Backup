#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep
import subprocess
import logging
import glob
import db
import keystoneclient.v2_0.client as ksclient
from novaclient import client as novaclient
import glanceclient
from credentials import get_keystone_creds
from credentials import get_nova_creds
from dest_credentials import get_dest_keystone_creds
from dest_credentials import get_dest_nova_creds

class Auth(object):

    def __init__(self):

    	self.kcreds = get_keystone_creds()
    	self.keystone = ksclient.Client(**self.kcreds)
        self.ncreds = get_nova_creds()
        self.nova = novaclient.Client("1.1",**self.ncreds)
        self.glance_endpoint = self.keystone.service_catalog.url_for(service_type='image',endpoint_type='publicURL')
        self.glance = glanceclient.Client('1',self.glance_endpoint, token=self.keystone.auth_token)

class Images(Auth):

    script_path = os.path.dirname(os.path.abspath(__file__)) 
    logfile = "{0}/dr.log".format(script_path)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%a, %d %b %Y %H:%M:%S',filename=logfile)


    def __init__(self):

    	super(Images, self).__init__()
        self.servers = self.nova.servers.list()
        self.mysql = db.Database()

    def get_property(self,id):
        property = self.glance.images.get(id)
        return property

    def backup_server(self,**kwargs):
     """Backup all running servers."""
     self.nova.servers.backup(kwargs['server_id'], kwargs['backup_name'], kwargs['backup_type'], kwargs['rotation'])
    
    def make_backup_dir(self):
      if not os.path.exists("{0}/backups".format( self.script_path )):
           os.makedirs("backups")
      else: return

    def prepared_list(self):

        get_imags = self.glance.images.list()
        get_servers = self.nova.servers.list()

        images_names_list = []
        for img in get_imags:
                images_names_list.append(img.name)

        servers_names_list = []
        for srvr in get_servers:
                servers_names_list.append(srvr.name+"_backup")

        down_list = [elem for elem in images_names_list if elem in servers_names_list]

        get_imags_casted = self.glance.images.list()
        imagss_list = list(get_imags_casted)

        result = []
        for x in xrange(0,len(down_list)):
             server_name = down_list[x]
             for y in xrange(0,len(imagss_list)):
                  imgs_name = imagss_list[y].name
                  if server_name == imgs_name:
                       imgs_id = imagss_list[y].id
                       rs_img = {}
                       rs_img['name'] = imgs_name
                       rs_img['id'] = imgs_id
                       list_imgg = [rs_img]
                       get_img = self.glance.images.get(imgs_id)
                       while get_img.status != 'active':
                            sleep(5)
                            get_imgg = self.glance.images.get(imgs_id)
                            if get_imgg.status == 'active':
                                 break
                       rs_img['disk_format'] = get_img.disk_format
                       rs_img['container_format'] = get_img.container_format
                       rs_img['is_public'] = get_img.is_public
                       rs_img['img_path'] = self.script_path+"/backups/"+imgs_name+".img"
                       rs_img['exc'] = self.script_path
                       result.append(list_imgg)
                       break
        return result


    def download_image(self,**kwargs):
     """Download images using glance client."""
     image_name = kwargs['image_name'].replace (" ", "_")
     try:
          os.chdir(kwargs['down_path'])
     except OSError as e:

        logging.warning(e)
        if kwargs['is_ami']:
            if kwargs['aki']=='aki':
                print "AKI"
                cmd = "glance image-download %s >> %s-vmlinuz" %(kwargs['kernel_id'],image_name)
                os.system(cmd)
            if kwargs['ari']=='ari':
                print "ARI"
                cmd = "glance image-download %s >> %s-loader" %(kwargs['ramdisk_id'],image_name)
                os.system(cmd)
            print "AMI"
            cmd = "glance image-download %s >> %s.img" %(kwargs['image_id'],image_name)
            os.system(cmd)
        else:
          print"Not ami"
          cmd = "glance image-download %s >> %s.img" %(kwargs['image_id'],image_name)
          os.system(cmd)

    def upload_img(self,**kwargs):
     """Upload image to destination glance."""
     with open(kwargs['img_path']) as fimage:
           self.glance.images.create(name=kwargs['img_name'], is_public=kwargs['is_public'], disk_format=kwargs['disk_format'],container_format=kwargs['container_format'], data=fimage)

    def get_backup_id(self,images):
        ids=[]
        for x in xrange(0,len(images)):
            ids.append(images[x][0]['id'])
        return ids

    def execute_backups(self,backup_list=None):
        backup_vars = {}
        if backup_list is None:
            servers_list = self.nova.servers.list()
        else:
            servers_list = backup_list

        for i in xrange(0,len(servers_list)):
            check = self.mysql.check_image_exists(self.keystone.tenant_id, servers_list[i].id)
            if not check :
                logging.info("No servers")
                if servers_list[i].status == 'ACTIVE':
                    backup_vars['server_id'] = servers_list[i].id
                    backup_vars['backup_name'] = "{0}_backup".format(servers_list[i].name) 
                    backup_vars['backup_type'] = 'daily'
                    backup_vars['rotation'] = 1
                    self.backup_server(**backup_vars)
                    self.print_format("Backing up... {0}".format(servers_list[i].name ))
                    logging.info("Backing up... {0}".format(servers_list[i].name ))
                    self.mysql.insert_data(self.keystone.tenant_id,self.keystone.username,servers_list[i].id,'',servers_list[i].name)
                else:
                    self.print_format("{0} is not active and will be ignored".format(servers_list[i].name ))
                    
            else:
                logging.info("pass")


    def update_backup(self,backup_list=None):
        backup_vars = {}

        if backup_list is None:
            servers_list = self.nova.servers.list()
        else:
            servers_list = backup_list

        for i in xrange(0,len(servers_list)):
            if servers_list[i].status == 'ACTIVE':
                    backup_vars['server_id'] = servers_list[i].id
                    backup_vars['backup_name'] = "{0}_backup".format(servers_list[i].name) 
                    backup_vars['backup_type'] = 'daily'
                    backup_vars['rotation'] = 1
                    self.backup_server(**backup_vars)
                    self.print_format("Backing up... {0}".format(servers_list[i].name ))
                    logging.info("Backing up... {0}".format(servers_list[i].name ))
                    self.mysql.insert_data(self.keystone.tenant_id,self.keystone.username,servers_list[i].id,'',servers_list[i].name)
            else:
                self.print_format("{0} is not active and will be ignored".format(servers_list[i].name ))


    def print_format(self,string):
        print "+%s+" %("-" * len(string))
        print "|%s|" % string
        print "+%s+" %("-" * len(string))

    def get_meta_and_return_servers(self):

        meta = []
        _servers = self.nova.servers.list()
        for srvrs in _servers:
            rs = {}
            gets = self.nova.servers.get(srvrs.id)
            rs['dr'] = gets.metadata.values()
            rs['id'] = srvrs.id
            meta_list = [rs]
            meta.append(meta_list)

        res = [k for k in meta if '1' in k[0]['dr']]
        servers =[]
        for i in xrange(0,len(res)):
            get_servers = self.nova.servers.get(res[i][0]['id'])
            servers.append(get_servers)

        return servers


if __name__ == "__main__":

	obj=Images()
        
       
        if not obj.prepared_list():
            obj.print_format("First backup...")
            if not obj.get_meta_and_return_servers():
                logging.info("No custom servers list")
                obj.execute_backups()
            else:
                logging.info("custom servers list with dr key")
                obj.execute_backups(obj.get_meta_and_return_servers())
                

        else:
            obj.print_format("Updating backups...")
            backup_list_index = obj.get_backup_id(obj.prepared_list())

            for x in xrange(0,len( backup_list_index )):
                obj.glance.images.delete(backup_list_index[x])
                obj.mysql.delete_data(obj.keystone.tenant_id)

            if not obj.get_meta_and_return_servers():
                logging.info("No custom servers list")
                obj.execute_backups()
            else:
                logging.info("custom servers list with dr key")
                obj.execute_backups(obj.get_meta_and_return_servers())







           

    
