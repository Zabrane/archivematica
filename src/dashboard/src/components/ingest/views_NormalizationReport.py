#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Archivematica.    If not, see <http://www.gnu.org/licenses/>.

# @package Archivematica
# @subpackage Dashboard
# @author Joseph Perry <joseph@artefactual.com>
# @autho Justin Simpson <jsimpson@artefactual.com>
#import sys
#sys.path.append("/usr/lib/archivematica/archivematicaCommon")

#import databaseInterface
#databaseInterface.printSQL = True
from components import helpers
from django.db import connection
    
def getNormalizationReportQuery(sipUUID, idsRestriction=""):
    if idsRestriction:
        idsRestriction = 'AND (%s)' % idsRestriction  
    
    cursor = connection.cursor()
        
    # not fetching name of ID Tool, don't think we need it.
    
    sql = """
    SELECT
        CONCAT(a.currentLocation, ' ', a.fileUUID,' ', IFNULL(a.fileID, "")) AS 'pagingIndex',
        a.fileUUID, 
        a.location,
        substring(a.currentLocation,23) as fileName, 
        a.fileID, 
        a.description,
        a.already_in_access_format, 
        a.already_in_preservation_format,
        case when b.exitCode < 2 and a.fileID is not null then 1 else 0 end as access_normalization_attempted,
        case when a.fileID is not null and b.exitcode = 1 then 1 else 0 end as access_normalization_failed,
        case when c.exitCode < 2 and a.fileID is not null then 1 else 0 end as preservation_normalization_attempted,
        case when a.fileID is not null and c.exitcode = 1 then 1 else 0 end as preservation_normalization_failed,
        b.taskUUID as access_normalization_task_uuid,
        c.taskUUID as preservation_normalization_task_uuid,
        b.exitCode as access_task_exitCode,
        c.exitCode as preservation_task_exitCode
    FROM (
        SELECT
            f.fileUUID,
            f.sipUUID, 
            f.originalLocation as location,
            f.currentLocation,
            fid.uuid as 'fileID',
            fid.description, 
            f.fileGrpUse,
            fid.access_format AS 'already_in_access_format', 
            fid.preservation_format AS 'already_in_preservation_format'
        FROM
            Files f
            LEFT JOIN
            FilesIdentifiedIDs fii on f.fileUUID = fii.fileUUID
            LEFT JOIN
            fpr_formatversion fid on fii.fileID = fid.uuid
        WHERE
            f.fileGrpUse in ('original', 'service')
        ) a 
        JOIN (
        SELECT
            j.sipUUID,
            t.fileUUID,
            t.taskUUID,
            t.exitcode
        FROM
            Jobs j 
            JOIN
            Tasks t on t.jobUUID = j.jobUUID
        WHERE
            j.jobType = 'Normalize for access'
        ) b
        ON a.fileUUID = b.fileUUID AND a.sipUUID = b.sipUUID
        JOIN (
        SELECT
            j.sipUUID,
            t.fileUUID,
            t.taskUUID,
            t.exitcode
        FROM
            Jobs j 
            JOIN
            Tasks t on t.jobUUID = j.jobUUID
        WHERE
            j.jobType = 'Normalize for preservation'
        ) c
        ON a.fileUUID = c.fileUUID AND a.sipUUID = c.sipUUID
        WHERE a.sipUUID = '{0}'
        order by (access_normalization_failed + preservation_normalization_failed) desc;
    """.format(sipUUID)
    
    cursor.execute(sql)
    objects = helpers.dictfetchall(cursor)
    #objects = databaseInterface.queryAllSQL(sql)
    return objects 
    

if __name__ == '__main__':
    import sys
    uuid = "'%s'" % (sys.argv[1])
    sys.path.append("/usr/lib/archivematica/archivematicaCommon")
    #import databaseInterface
    #databaseInterface.printSQL = True
    print "testing normalization report"
    sql = getNormalizationReportQuery(sipUUID=uuid)
    print sql
    #rows = databaseInterface.queryAllSQL(sql)
    #for row in rows:
    #    print row
    #    print
