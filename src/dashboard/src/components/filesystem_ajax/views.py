# This file is part of Archivematica.
#
# Copyright 2010-2013 Artefactual Systems Inc. <http://artefactual.com>
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

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.db import connection
import os
from subprocess import call
import logging
import shutil
import MySQLdb
import tempfile
from django.core.servers.basehttp import FileWrapper
from main import models

import sys
import uuid
import mimetypes
import uuid
sys.path.append("/usr/lib/archivematica/archivematicaCommon")
import archivematicaFunctions, databaseInterface, databaseFunctions
from archivematicaCreateStructuredDirectory import createStructuredDirectory
from components import helpers
import storageService as storage_service

# for unciode sorting support
import locale
locale.setlocale(locale.LC_ALL, '')

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/tmp/archivematicaDashboard.log",
    level=logging.INFO)

SHARED_DIRECTORY_ROOT   = '/var/archivematica/sharedDirectory'
ACTIVE_TRANSFER_DIR     = SHARED_DIRECTORY_ROOT + '/watchedDirectories/activeTransfers'
STANDARD_TRANSFER_DIR   = ACTIVE_TRANSFER_DIR + '/standardTransfer'
COMPLETED_TRANSFERS_DIR = SHARED_DIRECTORY_ROOT + '/watchedDirectories/SIPCreation/completedTransfers'

def rsync_copy(source, destination):
    call([
        'rsync',
        '-r',
        '-t',
        source,
        destination
    ])

def sorted_directory_list(path):
    cleaned = []
    entries = os.listdir(archivematicaFunctions.unicodeToStr(path))
    for entry in entries:
        cleaned.append(archivematicaFunctions.unicodeToStr(entry))
    return sorted(cleaned, key=helpers.keynat)

def directory_to_dict(path, directory={}, entry=False):
    # if starting traversal, set entry to directory root
    if (entry == False):
        entry = directory
        # remove leading slash
        entry['parent'] = os.path.dirname(path)[1:]

    # set standard entry properties
    entry['name'] = os.path.basename(path)
    entry['children'] = []

    # define entries
    entries = sorted_directory_list(path)
    for file in entries:
        new_entry = None
        if file[0] != '.':
            new_entry = {}
            new_entry['name'] = file
            entry['children'].append(new_entry)

        # if entry is a directory, recurse
        child_path = os.path.join(path, file)
        if new_entry != None and os.path.isdir(child_path) and os.access(child_path, os.R_OK):
            directory_to_dict(child_path, directory, new_entry)

    # return fully traversed data
    return directory

import archivematicaFunctions

def directory_children_proxy_to_storage_server(request, location_uuid, basePath=False):
    path = ''
    if (basePath):
        path = path + basePath
    path = path + request.GET.get('base_path', '')
    path = path + request.GET.get('path', '')

    response = storage_service.browse_location(location_uuid, path)

    return helpers.json_response(response)

def directory_children(request, basePath=False):
    path = ''
    if (basePath):
        path = path + basePath
    path = path + request.GET.get('base_path', '')
    path = path + request.GET.get('path', '')

    response    = {}
    entries     = []
    directories = []

    for entry in sorted_directory_list(path):
        entry = archivematicaFunctions.strToUnicode(entry)
        if unicode(entry)[0] != '.':
            entries.append(entry)
            entry_path = os.path.join(path, entry)
            if os.path.isdir(archivematicaFunctions.unicodeToStr(entry_path)) and os.access(archivematicaFunctions.unicodeToStr(entry_path), os.R_OK):
                directories.append(entry)

    response = {
      'entries': entries,
      'directories': directories
    }

    return helpers.json_response(response)

def directory_contents(path, contents=[]):
    entries = sorted_directory_list(path)
    for entry in entries:
        contents.append(os.path.join(path, entry))
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path) and os.access(entry_path, os.R_OK):
            directory_contents(entry_path, contents)
    return contents

def contents(request):
    path = request.GET.get('path', '/home')
    response = directory_to_dict(path)
    return helpers.json_response(response)

def delete(request):
    filepath = request.POST.get('filepath', '')
    filepath = os.path.join('/', filepath)
    error = check_filepath_exists(filepath)

    if error == None:
        filepath = os.path.join(filepath)
        if os.path.isdir(filepath):
            try:
                shutil.rmtree(filepath)
            except:
                error = 'Error attempting to delete directory.'
        else:
            os.remove(filepath)

    response = {}

    if error != None:
      response['message'] = error
      response['error']   = True
    else:
      response['message'] = 'Delete successful.'

    return helpers.json_response(response)

def get_temp_directory(request):
    temp_base_dir = helpers.get_client_config_value('temp_dir')

    response = {}

    # use system temp dir if none specifically defined
    if temp_base_dir == '':
        temp_dir = tempfile.mkdtemp()
    else:
        try:
            temp_dir = tempfile.mkdtemp(dir=temp_base_dir)
        except:
            temp_dir = ''
            response['error'] = 'Unable to create temp directory.'

    #os.chmod(temp_dir, 0o777)

    response['tempDir'] = temp_dir

    return helpers.json_response(response)

def copy_transfer_component(request):
    transfer_name = archivematicaFunctions.unicodeToStr(request.POST.get('name', ''))
    path = archivematicaFunctions.unicodeToStr(request.POST.get('path', ''))
    destination = archivematicaFunctions.unicodeToStr(request.POST.get('destination', ''))

    error = None

    if transfer_name == '':
        error = 'No transfer name provided.'
    else:
        if path == '':
            error = 'No path provided.'
        else:
            # if transfer compontent path leads to an archive, treat as zipped
            # bag
            if helpers.file_is_an_archive(path):
                rsync_copy(path, destination)
                paths_copied = 1
            else:
                transfer_dir = os.path.join(destination, transfer_name)

                # Create directory before it is used, otherwise shutil.copy()
                # would that location to store a file
                if not os.path.isdir(transfer_dir):
                    os.mkdir(transfer_dir)

                paths_copied = 0

                # cycle through each path copying files/dirs inside it to transfer dir
                for entry in sorted_directory_list(path):
                    entry_path = os.path.join(path, entry)
                    rsync_copy(entry_path, transfer_dir)

                    paths_copied = paths_copied + 1

    response = {}

    if error != None:
      response['message'] = error
      response['error']   = True
    else:
      response['message'] = 'Copied ' + str(paths_copied) + ' entries.'

    return helpers.json_response(response)

def copy_to_originals(request):
    filepath = request.POST.get('filepath', '')
    error = check_filepath_exists('/' + filepath)

    if error == None:
        processingDirectory = '/var/archivematica/sharedDirectory/currentlyProcessing/'
        sipName = os.path.basename(filepath)
        autoProcessSIPDirectory = '/var/archivematica/sharedDirectory/watchedDirectories/SIPCreation/SIPsUnderConstruction/'
        tmpSIPDir = os.path.join(processingDirectory, sipName) + "/"
        destSIPDir =  os.path.join(autoProcessSIPDirectory, sipName) + "/"

        sipUUID = uuid.uuid4().__str__()

        createStructuredDirectory(tmpSIPDir)
        databaseFunctions.createSIP(destSIPDir.replace('/var/archivematica/sharedDirectory/', '%sharedPath%'), sipUUID)

        objectsDirectory = os.path.join('/', filepath, 'objects')

        #move the objects to the SIPDir
        for item in os.listdir(objectsDirectory):
            shutil.move(os.path.join(objectsDirectory, item), os.path.join(tmpSIPDir, "objects", item))

        #moveSIPTo autoProcessSIPDirectory
        shutil.move(tmpSIPDir, destSIPDir)

    response = {}

    if error != None:
        response['message'] = error
        response['error']   = True
    else:
        response['message'] = 'Copy successful.'

    return helpers.json_response(response)

def copy_to_start_transfer(request):
    filepath  = archivematicaFunctions.unicodeToStr(request.POST.get('filepath', ''))
    type      = request.POST.get('type', '')
    accession = request.POST.get('accession', '')

    error = check_filepath_exists('/' + filepath)

    if error == None:
        # confine destination to subdir of originals
        filepath = os.path.join('/', filepath)
        basename = os.path.basename(filepath)

        # default to standard transfer
        type_paths = {
          'standard':     'standardTransfer',
          'unzipped bag': 'baggitDirectory',
          'zipped bag':   'baggitZippedDirectory',
          'dspace':       'Dspace',
          'maildir':      'maildir',
          'TRIM':         'TRIM'
        }

        try:
          type_subdir = type_paths[type]
          destination = os.path.join(ACTIVE_TRANSFER_DIR, type_subdir)
        except KeyError:
          destination = os.path.join(STANDARD_TRANSFER_DIR)

        # if transfer compontent path leads to a ZIP file, treat as zipped
        # bag
        if not helpers.file_is_an_archive(filepath):
            destination = os.path.join(destination, basename)
            destination = pad_destination_filepath_if_it_already_exists(destination)

        # relay accession via DB row that MCPClient scripts will use to get
        # supplementary info from
        if accession != '':
            temp_uuid = uuid.uuid4().__str__()
            mcp_destination = destination.replace(SHARED_DIRECTORY_ROOT + '/', '%sharedPath%') + '/'
            transfer = models.Transfer.objects.create(
                uuid=temp_uuid,
                accessionid=accession,
                currentlocation=mcp_destination
            )
            transfer.save()

        try:
            shutil.move(filepath, destination)
        except:
            error = 'Error copying from ' + filepath + ' to ' + destination + '. (' + str(sys.exc_info()[0]) + ')'

    response = {}

    if error != None:
        response['message'] = error
        response['error']   = True
    else:
        response['message'] = 'Copy successful.'

    return helpers.json_response(response)

def copy_from_arrange_to_completed(request):
    filepath = '/' + request.POST.get('filepath', '')
    from components.ingest import views

    if filepath != '':
        views._initiate_sip_from_files_structured_like_a_completed_transfer(filepath)

    #return copy_to_originals(request)

def move_within_arrange(request):
    sourcepath  = request.POST.get('filepath', '')
    destination = request.POST.get('destination', '')

    error = check_filepath_exists('/' + sourcepath)

    if error == None:
        basename = os.path.basename('/' + sourcepath)
        destination_full = os.path.join('/', destination, basename)
        if (os.path.exists(destination_full)):
            error = 'A file or directory named ' + basename + ' already exists at this path.'
        else:
            shutil.move('/' + sourcepath, destination_full)

    response = {}

    if error != None:
        response['message'] = error
        response['error']   = True
    else:
        response['message'] = 'Copy successful.'

    return helpers.json_response(response)

def copy_to_arrange(request):
    # TODO: this shouldn't be hardcoded
    originals_dir = '/var/archivematica/sharedDirectory/www/AIPsStore/transferBacklog/originals'
    arrange_dir = os.path.realpath(os.path.join(
        helpers.get_client_config_value('sharedDirectoryMounted'),
        'arrange'))

    # TODO: limit sourcepath to certain allowable locations
    sourcepath  = request.POST.get('filepath', '')
    destination = request.POST.get('destination', '')

    # make source and destination path absolute
    sourcepath = os.path.join('/', sourcepath)
    destination = os.path.realpath(os.path.join('/', destination))

    # work out relative path within originals folder
    originals_subpath = sourcepath.replace(originals_dir, '')

    # work out transfer directory level and source transfer directory
    transfer_directory_level = originals_subpath.count('/')
    source_transfer_directory = originals_subpath.split('/')[1]

    error = check_filepath_exists(sourcepath)

    if error == None:
        # use lookup path to cleanly find UUID
        #lookup_path = '%sharedPath%' + sourcepath[SHARED_DIRECTORY_ROOT.__len__() + 1:sourcepath.__len__()] + '/'
        lookup_path = '%sharedPath%www/AIPsStore/transferBacklog/originals/' + source_transfer_directory + '/'
        cursor = connection.cursor()
        sql = 'SELECT unitUUID FROM transfersAndSIPs WHERE currentLocation=%s LIMIT 1'
        cursor.execute(sql, (lookup_path, ))
        possible_uuid_data = cursor.fetchone()

        # if UUID valid in system found, remove it
        if possible_uuid_data:
          uuid = possible_uuid_data[0]

          # remove UUID from destination directory name
          modified_basename = os.path.basename(sourcepath).replace('-' + uuid, '')
        else:
          # TODO: should return error?
          modified_basename = os.path.basename(sourcepath)

        # confine destination to subdir of arrange
        if arrange_dir in destination and destination.index(arrange_dir) == 0:
            full_destination = os.path.join(destination, modified_basename)
            full_destination = pad_destination_filepath_if_it_already_exists(full_destination)

            if os.path.isdir(sourcepath):
                try:
                    shutil.copytree(
                        sourcepath,
                        full_destination
                    )
                except:
                    error = 'Error copying from ' + sourcepath + ' to ' + full_destination + '.'

                if error == None:
                    # remove any metadata and logs folders
                    for path in directory_contents(full_destination):
                        basename = os.path.basename(path)
                        if basename == 'metadata' or basename == 'logs':
                            if os.path.isdir(path):
                                shutil.rmtree(path)

            else:
                shutil.copy(sourcepath, full_destination)

            # if the source path isn't a whole transfer folder, then
            # copy the source transfer's METS file into the objects
            # folder of the destination... if there is not objects
            # folder then return an error

            # an entire transfer isn't being copied... copy in METS if
            # it doesn't exist
            if transfer_directory_level != 1:
                # work out location of METS file in source transfer
                source_mets_path = os.path.join(originals_dir, source_transfer_directory, 'metadata/submissionDocumentation/METS.xml')

                # work out destination object folder
                arrange_subpath = full_destination.replace(arrange_dir, '')
                dest_transfer_directory = arrange_subpath.split('/')[1]
                objects_directory = os.path.join(arrange_dir, dest_transfer_directory, 'objects')
                destination_mets = os.path.join(objects_directory, 'METS-' + uuid + '.xml')
                if not os.path.exists(destination_mets):
                    shutil.copy(source_mets_path, destination_mets)
        else:
            error = 'The destination {} is not within the arrange directory ({}).'.format(destination, arrange_dir)

    response = {}

    if error != None:
        response['message'] = error
        response['error']   = True
    else:
        response['message'] = 'Copy successful.'

    return helpers.json_response(response)

def check_filepath_exists(filepath):
    error = None
    if filepath == '':
        error = 'No filepath provided.'

    # check if exists
    if error == None and not os.path.exists(filepath):
        error = 'Filepath ' + filepath + ' does not exist.'

    # check if is file or directory

    # check for trickery
    try:
        filepath.index('..')
        error = 'Illegal path.'
    except:
        pass

    return error

# TODO: remove and use version in helpers
def pad_destination_filepath_if_it_already_exists(filepath, original=None, attempt=0):
    if original == None:
        original = filepath
    attempt = attempt + 1
    if os.path.exists(filepath):
        return pad_destination_filepath_if_it_already_exists(original + '_' + str(attempt), original, attempt)
    return filepath

def download(request):
    shared_dir = os.path.realpath(helpers.get_client_config_value('sharedDirectoryMounted'))
    requested_filepath = os.path.realpath('/' + request.GET.get('filepath', ''))

    # respond with 404 if a non-Archivematica file is requested
    try:
        if requested_filepath.index(shared_dir) == 0:
            return helpers.send_file(request, requested_filepath)
        else:
            raise Http404
    except ValueError:
        raise Http404
