#!/usr/bin/env python

import os
import gzip
import shutil

class FakeTime:
    def time(self):
        return 1261130520.0

# Hack to override gzip's time implementation
# See: http://stackoverflow.com/questions/264224/setting-the-gzip-timestamp-from-python
gzip.time = FakeTime()

shutil.rmtree('gzip_media', ignore_errors=True)

for path, dirs, files in os.walk('media'):
    for filename in files:
        if filename[-3:] not in ['js', 'css', 'txt', 'html']:
            continue
    
        src_path = os.path.join(path, filename)
        dest_path = 'gzip_'+src_path
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))

        f_in = open(src_path, 'rb')
        contents = f_in.read()
        f_in.close()
        f_out = gzip.open(dest_path, 'wb')
        f_out.write(contents)
        f_out.close();
