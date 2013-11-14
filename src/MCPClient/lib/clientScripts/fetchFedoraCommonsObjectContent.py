#!/usr/bin/python -OO

# This file is part of Archivematica.
#
# Copyright 2010-2012 Artefactual Systems Inc. <http://artefactual.com>
#
# Archivematica is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Archivematica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.  If not, see <http://www.gnu.org/licenses/>.

# @package Archivematica
# @subpackage archivematicaClientScript
# @author Mike Cantelon <mike@artefactual.com>

import os
import shutil
import sys
import urllib2
import tempfile

def _filename_from_response(response):
    info = response.info()
    if 'content-disposition' in info:
        return _parse_filename_from_content_disposition(info['content-disposition'])
    else:
        return None

def _parse_filename_from_content_disposition(header):
    filename = header.split('filename=')[1]
    if filename[0] == '"' or filename[0] == "'":
        filename = filename[1:-1]
    return filename

def download_resource(url, destination_path):
    response = urllib2.urlopen(url)
    filename = _filename_from_response(response)

    if filename == None:
        filename = os.path.basename(url)

    filepath = os.path.join(destination_path, filename)
    buffer = 16 * 1024
    with open(filepath, 'wb') as fp:
        while True:
            chunk = response.read(buffer)
            if not chunk: break
            fp.write(chunk)
    return filename

if __name__ == '__main__':
    if len(sys.argv) <> 3:
        print 'Usage: ' + sys.argv[0] + ' <resource URL> <destination directory>'
        exit(1)

    print 'Downloading started.'

    resource_url = sys.argv[1]
    destination_path = sys.argv[2]

    temp_dir = tempfile.mkdtemp()
    filename = download_resource(resource_url, temp_dir)
    shutil.move(os.path.join(temp_dir, filename), os.path.join(destination_path, filename))

    print 'Downloading complete.'
