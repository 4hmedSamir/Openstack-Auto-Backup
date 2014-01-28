#!/usr/bin/python

import MySQLdb
import time

class Database:
 conn=None
	
 def __init__(self):
  try :
   if not Database.conn :
    Database.conn = MySQLdb.connect(host="localhost", user="root", passwd="123", db="dr")
    self.cursor = Database.conn.cursor()
  except MySQLdb.Error, e: 
    print e
    exit(1)

 def check_image_exists(self,src_tenant_id,src_instance_id):
  try :
   sql = "SELECT * FROM backup where src_tenant_id='%s' and src_instance_id='%s'" % (src_tenant_id,src_instance_id)
   self.cursor.execute(sql)
   results = self.cursor.fetchall()
   return results
  except MySQLdb.Error, e: 
    print e
    exit(1) 

 def insert_data(self,src_tenant_id,user,src_instance_id, des_tenant_id, backup_name) :
  date_time=int(time.time()+300)
  sql = "INSERT INTO backup(src_tenant_id,user,src_instance_id, des_tenant_id, backup_name,date) VALUES ('%s','%s','%s','%s', '%s', %d )" % (src_tenant_id,user,src_instance_id,des_tenant_id,backup_name,date_time) 
  self.cursor.execute(sql)
  Database.conn.commit()

 def insert_data2(self,src_instance_id,backup_id) :
 
  sql = "INSERT INTO snap(src_instance_id, backup_id) VALUES ('%s','%s')" % (src_instance_id,backup_id) 
  self.cursor.execute(sql)
  Database.conn.commit()

 def delete_data(self,src_tenant_id) :
 
  sql = "DELETE from backup  where src_tenant_id = '%s'" % (src_tenant_id) 
  self.cursor.execute(sql)
  Database.conn.commit()


 def delete_data2(self,src_instance_id) :
 
  sql = "DELETE from snap  where src_instance_id = '%s'" % (src_instance_id) 
  self.cursor.execute(sql)
  Database.conn.commit()


 def __del__(self):
  pass
    #self.cursor.close ()
    #Database.conn.close()
    

