#!/usr/bin/env python

"""
Review the database and filesystem to identify possible orphaned files and datasets.
"""

import psycopg2
import os, os.path
from sys import argv

UPLOAD_DIRECTORY = '/var/lib/panda/uploads'
DATABASE='panda'
DB_USER='panda'
DB_PASSWORD='panda'

files = os.listdir(UPLOAD_DIRECTORY)
connection = psycopg2.connect(database=DATABASE,user=DB_USER,password=DB_PASSWORD)
cursor = connection.cursor()

cursor.execute("""select du.id, du.filename, ds.name from panda_dataupload du 
                  left outer join panda_dataset ds on (du.dataset_id = ds.id)""")

files_to_delete = []
uploads_to_delete = []
for id, filename, dataset_name in cursor:
    if dataset_name:
        files.remove(filename)
    if not dataset_name:
        print "Orphaned upload: %i" % id
        uploads_to_delete.append(id)
        try:
            files.remove(filename)
            files_to_delete.append(filename)
        except ValueError: pass
for f in files:
    print "not even a dataupload for %s" % f
    files_to_delete.append(f)

if uploads_to_delete:
    print "Data upload IDs with no corresponding dataset:"
    print "\n".join(map(str,uploads_to_delete))
    print
if files_to_delete:
    print "Files with no corresponding dataset:"
    print "\n".join(files_to_delete)
    print

if files_to_delete and uploads_to_delete:
    question = "Enter 'yes' to delete ALL of these files and data upload records: "
elif files_to_delete:
    question = "Enter 'yes' to delete ALL of these files: "
elif uploads_to_delete:
    question = "Enter 'yes' to delete ALL of these data upload records: "
else:
    question = None

if question:
    do_it = raw_input()
    if do_it == 'yes':
        for f in files_to_delete:
            os.remove(os.path.join(UPLOAD_DIRECTORY,f))
        for id in uploads_to_delete:
            cursor.execute("delete from panda_dataupload where id = %s",(id,))
        connection.commit()
        cursor.close()
        print "Cleanup complete."
    else:
        "No changes were made to the database or filesystem."
else:
    print "Everything looks pretty clean."

connection.close()

    

