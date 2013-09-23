#!/usr/bin/python2

import argparse
import os
import sys

sys.path.append("/usr/lib/archivematica/archivematicaCommon")
from executeOrRunSubProcess import executeOrRun

path = '/usr/share/archivematica/dashboard'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.common'
from fpr.models import IDCommand, IDRule
from main.models import FileFormatVersion, File


def main(id_command, file_path, file_uuid):
    print "Command UUID:", id_command
    command = IDCommand.active.get(uuid=id_command)
    _, output, _ = executeOrRun(command.script_type, command.script, arguments=[file_path], printing=False)
    output = output.strip()
    print 'Command output:', output
    try:
        idrule = IDRule.active.get(command_output=output)
    except (IDRule.DoesNotExist, IDRule.MultipleObjectsReturned) as e:
        print >>sys.stderr, 'Error:', e
        return -1
    # TODO shouldn't have to get File object - http://stackoverflow.com/questions/2846029/django-set-foreign-key-using-integer
    file_ = File.objects.get(uuid=file_uuid)
    FileFormatVersion.objects.create(file_uuid=file_, format_version=idrule.format)
    print "{} identified as a {}".format(file_path, idrule.format)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Identify file formats.')
    parser.add_argument('id_command', type=str, help='%IDCommand%')
    parser.add_argument('file_path', type=str, help='%relativeLocation%')
    parser.add_argument('file_uuid', type=str, help='%fileUUID%')

    args = parser.parse_args()
    sys.exit(main(args.id_command, args.file_path, args.file_uuid))
