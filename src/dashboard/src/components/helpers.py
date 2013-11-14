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

import ConfigParser
import cPickle
import logging
import mimetypes
import os
import pprint
import shutil
import sys
import urllib
import uuid
import json

from django.utils.dateformat import format
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render
from main import models

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/tmp/archivematicaDashboard.log", 
    level=logging.INFO)

# Used for debugging
def pr(object):
    return pprint.pformat(object)

# Used for raw SQL queries to return data in dictionaries instead of lists
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def keynat(string):
    r'''A natural sort helper function for sort() and sorted()
    without using regular expressions or exceptions.

    >>> items = ('Z', 'a', '10th', '1st', '9')
    >>> sorted(items)
    ['10th', '1st', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1st', '9', '10th', 'a', 'Z']    
    '''
    it = type(1)
    r = []
    for c in string:
        if c.isdigit():
            d = int(c)
            if r and type( r[-1] ) == it: 
                r[-1] = r[-1] * 10 + d
            else: 
                r.append(d)
        else:
            r.append(c.lower())
    return r

def json_response(data):
    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )

# this class wraps Pyes search results so the Django Paginator class
# can work on the results
class DjangoPaginatableListFromPyesSearchResult:
    def __init__(self, result, start, size):
        self.result = result
        self.start  = start
        self.size   = size

    def count(self):
        return self.result.count()

    def __len__(self):
        return self.count()

    def __getitem__(self, key):
        if key < self.start:
            return
        else:
            if key >= (self.start + self.size):
                return
            else:
                return self.result[key - self.start]

def pager(objects, items_per_page, current_page_number):
    page = {}

    # if a Pyes resultset, wrap it in a class so it emulates
    # a standard Python list
    if objects.__class__.__name__ == 'ResultSet':
        p = Paginator(
            DjangoPaginatableListFromPyesSearchResult(
                objects,
                (int(current_page_number) - 1) * items_per_page,
                items_per_page
            ),
            items_per_page,
        )
    else:
        p = Paginator(objects, items_per_page)

    page['current']      = 1 if current_page_number == None else int(current_page_number)

    try:
        pager = p.page(page['current'])

    except EmptyPage:
        return False

    page['has_next']     = pager.has_next()
    page['next']         = page['current'] + 1
    page['has_previous'] = pager.has_previous()
    page['previous']     = page['current'] - 1
    page['has_other']    = pager.has_other_pages()

    page['end_index']    = pager.end_index()
    page['start_index']  = pager.start_index()
    page['total_items']  = len(objects)

    # if a Pyes resultset, won't need paginator to splice it
    if objects.__class__.__name__ == 'ResultSet':
        page['objects']  = objects
    else:
        page['objects']  = pager.object_list

    page['num_pages']    = p.num_pages

    num_of_neighbors_to_show = 5
    if page['current'] > num_of_neighbors_to_show:
        page['previous_pages'] = range(
            page['current'] - num_of_neighbors_to_show,
            page['current']
        )
    else:
        page['previous_pages'] = range(1, page['current'])

    if page['current'] < (page['num_pages'] - num_of_neighbors_to_show):
        page['next_pages'] = range(
            int(page['current']) + 1,
            page['current'] + num_of_neighbors_to_show + 1
        )
    else:
        page['next_pages'] = range(
            page['current'] + 1,
            page['num_pages'] + 1
        )

    return page

def get_file_sip_uuid(fileuuid):
    file = models.File.objects.get(uuid=fileuuid)
    return file.sip.uuid

def task_duration_in_seconds(task):
    if task.endtime != None:
        duration = int(format(task.endtime, 'U')) - int(format(task.starttime, 'U'))
    else:
        duration = ''
    if duration == 0:
        duration = '< 1'
    return duration

def get_jobs_by_sipuuid(uuid):
    jobs = models.Job.objects.filter(sipuuid=uuid,subjobof='').order_by('-createdtime', 'subjobof')
    priorities = {
        'completedUnsuccessfully': 0,
        'requiresAprroval': 1,
        'requiresApproval': 1,
        'exeCommand': 2,
        'verificationCommand': 3,
        'completedSuccessfully': 4,
        'cleanupSuccessfulCommand': 5,
    }
    def get_priority(job):
        try: return priorities[job.currentstep]
        except Exception: return 0
    return sorted(jobs, key = get_priority) # key = lambda job: priorities[job.currentstep]

def get_metadata_type_id_by_description(description):
    types = models.MetadataAppliesToType.objects.filter(description=description)
    return types[0].id

def transfer_type_directories():
    return {
      'standard':     'standardTransfer',
      'unzipped bag': 'baggitDirectory',
      'zipped bag':   'baggitZippedDirectory',
      'dspace':       'Dspace',
      'maildir':      'maildir',
      'TRIM':         'TRIM'
    }

def transfer_directory_by_type(type):
    type_paths = {
      'standard':     'standardTransfer',
      'unzipped bag': 'baggitDirectory',
      'zipped bag':   'baggitZippedDirectory',
      'dspace':       'Dspace',
      'maildir':      'maildir',
      'TRIM':         'TRIM'
    }

    return transfer_type_directories()[type]

def transfer_type_by_directory(directory):
    type_directories = transfer_type_directories()

    # flip keys and values in dictionary
    directory_types = dict((value, key) for key, value in type_directories.iteritems())

    return directory_types[directory]

def get_setting(setting, default=''):
    try:
        setting = models.DashboardSetting.objects.get(name=setting)
        return setting.value
    except:
        return default

def get_boolean_setting(setting, default=''):
    setting = get_setting(setting, default)
    if setting == 'False':
       return False
    else:
       return bool(setting)

def set_setting(setting, value=''):
    try:
        setting_data = models.DashboardSetting.objects.get(name=setting)
    except:
        setting_data = models.DashboardSetting.objects.create()
        setting_data.name = setting

    setting_data.value = value
    setting_data.save()

def get_config_value(config_file, config_section, field):
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)

    try:
        return config.get(config_section, field)
    except:
        return ''

def get_client_config_value(field):
    return get_config_value(
        '/etc/archivematica/MCPClient/clientConfig.conf',
        'MCPClient',
        field
    )

def get_server_config_value(field):
    return get_config_value(
        '/etc/archivematica/MCPServer/serverConfig.conf',
        'MCPServer',
        field
    )

def redirect_with_get_params(url_name, *args, **kwargs):
    url = reverse(url_name, args = args)
    params = urllib.urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)

def send_file_or_return_error_response(request, filepath, content_type, verb='download'):
    if os.path.exists(filepath):
        return send_file(request, filepath)
    else:
        return render(request, 'not_found.html', {
            'content_type': content_type,
            'verb': verb
        })

def send_file(request, filepath):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    filename = os.path.basename(filepath)
    extension = os.path.splitext(filepath)[1].lower()

    wrapper = FileWrapper(file(filepath))
    response = HttpResponse(wrapper)

    # force download for certain filetypes
    extensions_to_download = ['.7z', '.zip']

    try:
        index = extensions_to_download.index(extension)
        response['Content-Type'] = 'application/force-download'
        response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    except:
        mimetype = mimetypes.guess_type(filename)[0]
        response['Content-type'] = mimetype

    response['Content-Length'] = os.path.getsize(filepath)
    return response

def file_is_an_archive(file):
    file = file.lower()
    return file.endswith('.zip') or file.endswith('.tgz') or file.endswith('.tar.gz')

def feature_settings():
    return {
        'atom_dip_admin':      'dashboard_administration_atom_dip_enabled',
        'contentdm_dip_admin': 'dashboard_administration_contentdm_dip_enabled',
        'dspace':              'dashboard_administration_dspace_enabled'
    }

def hidden_features():
    hide_features = {}

    short_forms = feature_settings()

    for short_form, long_form in short_forms.items():
        # hide feature if setting isn't enabled
        hide_features[short_form] = not get_boolean_setting(long_form)

    return hide_features

def copy_to_start_transfer(filepath, type='', metadata={}):
    error = check_filepath_exists(filepath)

    if 'accession' in metadata:
        accession = metadata['accession']
    else:
        accession = ''

    if error == None:
        # confine destination to subdir of originals
        basename = os.path.basename(filepath)

        active_transfer_directory = os.path.join(
            get_client_config_value('sharedDirectoryMounted'),
            'watchedDirectories/activeTransfers'
        )

        # default to standard transfer
        try:
          type_paths = transfer_type_directories()
          type_subdir = type_paths[type]
          destination = os.path.join(active_transfer_directory, type_subdir)
        except KeyError:
          destination = os.path.join(active_transfer_directory, 'standardTransfer')

        # if transfer compontent path leads to a ZIP file, treat as zipped
        # bag
        if not file_is_an_archive(filepath):
            destination = os.path.join(destination, basename)
            destination = pad_destination_filepath_if_it_already_exists(destination)

        # relay accession via DB row that MCPClient scripts will use to get
        # supplementary info from
        if 'uuid' in metadata:
            transfer = models.Transfer.objects.get(uuid=metadata['uuid'])
        else:
            temp_uuid = uuid.uuid4().__str__()
            transfer = models.Transfer.objects.create(uuid=temp_uuid)

        transfer.currentlocation = destination.replace(
            get_client_config_value('sharedDirectoryMounted'),
            '%sharedPath%'
        ) + '/'

        if accession != '':
            transfer.accessionid = accession

        transfer.save()

        try:
            shutil.move(filepath, destination)
        except:
            error = 'Error copying from ' + filepath + ' to ' + destination + '. (' + str(sys.exc_info()[0]) + ')'

    return error

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

def pad_destination_filepath_if_it_already_exists(filepath, original=None, attempt=0):
    if original == None:
        original = filepath
    attempt = attempt + 1
    if os.path.exists(filepath):
        return pad_destination_filepath_if_it_already_exists(original + '_' + str(attempt), original, attempt)
    return filepath
