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

from django.conf.urls.defaults import *
from django.conf import settings
from components.api.models import SelectionAvailableResource
from components.api.models import SelectionAPIResource

selectionAvailable = SelectionAvailableResource()
selectionAPI = SelectionAPIResource()

urlpatterns = patterns('components.api.views',
    #(r'', include(selectionAvailable.urls)),
    #(r'', include(selectionAPI.urls)),
    (r'transfer/approve/$', 'approve_transfer'), 
    (r'transfer/unapproved/$', 'unapproved_transfers')
)

urlpatterns += patterns('components.api.views_sword',
    # v2 URLs don't require trailing slash
    (r'v2/sword$', 'service_document'),
    (r'v2/transfer/sword$', 'transfer_collection'),
    (r'v2/transfer/sword/(?P<uuid>' + settings.UUID_REGEX + ')$', 'transfer'),
    (r'v2/transfer/sword/(?P<uuid>' + settings.UUID_REGEX + ')/media$', 'transfer_files'),
    (r'v2/transfer/sword/(?P<uuid>' + settings.UUID_REGEX + ')/state$', 'transfer_state')
)

urlpatterns += patterns('components.api.views',
    (r'v2/transfer/approve$', 'approve_transfer'),
    (r'v2/transfer/unapproved$', 'unapproved_transfers')
)
