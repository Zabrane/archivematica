#!/usr/bin/python2 -OO
from __future__ import print_function
import argparse
import csv
import os
import sys
import traceback

sys.path.append("/usr/lib/archivematica/archivematicaCommon")
from executeOrRunSubProcess import executeOrRun

path = '/usr/share/archivematica/dashboard'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.common'
from fpr.models import FPCommand
from main.models import FileFormatVersion, File

def check_manual_normalization(opts):
    """ Checks for manually normalized file, returns that path or None. 

    Checks by looking for access/preservation files for a give original file.

    Check the manualNormalization/access and manualNormalization/preservation
    directories for access and preservation files.  If a nomalization.csv
    file is specified, check there first for the mapping between original
    file and access/preservation file. """

    # If normalization.csv provided, check there for mapping from original
    # to access/preservation file
    normalization_csv = os.path.join(opts.sip_path, "objects", "manualNormalization", "normalization.csv")
    dirname, bname = os.path.split(opts.file_path)
    if os.path.isfile(normalization_csv):
        found = False
        with open(normalization_csv, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            # Search the file for an original filename that matches the one provided
            try:
                for row in reader:
                    if "#" in row[0]: # ignore comments
                        continue
                    original, access_file, preservation_file = row
                    if original.lower() == bname.lower():
                        found = True
                        break
            except csv.Error:
                print >>sys.stderr, "Error reading {filename} on line {linenum}".format(
                    filename=normalization_csv, linenum=reader.line_num)
                traceback.print_exc(file=sys.stderr)
                return None

        # If we didn't find a match, let it fall through to the usual method
        if found:
            # No manually normalized file for command classification
            if "preservation" in opts.purpose and not preservation_file:
                return None
            if "access" in opts.purpose and not access_file:
                return None

            # If we found a match, verify access/preservation exists in DB
            # match and pull original location b/c sanitization
            if "preservation" in opts.purpose:
                filename = preservation_file
            elif "access" in opts.purpose:
                filename = access_file
            else:
                return None
            return File.objects.get(sipUUID=opts.sip_uuid, originallocation__endswith=filename).currentlocation #removedtime = 0

    # Assume that any access/preservation file found with the right
    # name is the correct one
    bname, _ = os.path.splitext(bname)
    path = os.path.join(dirname, bname)
    if "preservation" in opts.purpose:
        path = path.replace("%SIPDirectory%objects/",
            "%SIPDirectory%objects/manualNormalization/preservation/")
    elif "access" in opts.purpose:
        path = path.replace("%SIPDirectory%objects/",
            "%SIPDirectory%objects/manualNormalization/access/")
    else:
        return None
    try:
        return File.objects.get(sipUUID=opts.sip_uuid, originallocation__startswith=path).currentlocation #removedtime = 0
    except Exception:
        print("DEBUG EXCEPTION!")
        traceback.print_exc(file=sys.stdout)
    return None

def get_replacement_dict(opts):
    """ Generates values for all knows %var% replacement variables. """
    prefix = ""
    postfix = ""
    output_dir = ""
    #get file name and extension
    (directory, basename) = os.path.split(opts.file_path)
    directory+=os.path.sep  # All paths should have trailing /
    (filename, extension_dot) = os.path.splitext(basename)

    if "preservation" in opts.purpose:
        postfix = "-" + opts.task_uuid
        output_dir = directory
    elif "access" in opts.purpose:
        prefix = opts.file_uuid + "-"
        output_dir = os.path.join(opts.sip_path, "DIP", "objects") + os.path.sep
    elif "thumbnail" in opts.purpose:
        output_dir = os.path.join(opts.sip_path, "thumbnails") + os.path.sep
        postfix = opts.file_uuid
    else:
        print("Unsupported command purpose", opts.purpose, file=sys.stderr)
        return None

    replacement_dict = {
        "%inputFile%": opts.file_path,
        "%outputDirectory%": output_dir,
        "%fileExtensionWithDot%": extension_dot,
        "%fileFullName%": opts.file_path,
        "%fileName%":  filename,
        "%prefix%": prefix,
        "%postfix%": postfix,
        "%outputFileName%": ''.join([output_dir, prefix, filename, postfix])
    }
    return replacement_dict

def replace_vars(command, opts):
    """ Replaces all instances of %var% in command. """
    replacement_dict = get_replacement_dict(opts)
    for (replace_var, value) in replacement_dict.iteritems():
        command = command.replace(replace_var, value)
    return command

def get_output_file_path(opts):
    """ Returns the absolute filename (sans extension) of the output file. """
    replacement_dict = get_replacement_dict(opts)
    return replacement_dict['%outputFileName%']

def main(opts):
    """ Find and execute normalization commands on input file. """
    # TODO fix for maildir working only on attachments
    # TODO use existing Command class??  Take most of transcoder but update 'startup' code?
    # Replace transcoderNormalizer.executeFPRule with the setup code from here, and use transcoder.Command/CommandLinker.  Update transcoderNormalize.getReplacementDict to use this one.  Clean up usages of opts in transcoderNormalizer to use the argparse opts and stuff

    manually_normalized_file = check_manual_normalization(opts)
    if manually_normalized_file:
        print(opts.file_path, 'was already manually normalized into', manually_normalized_file)

    try:
        file_ = File.objects.get(uuid=opts.file_uuid)
    except File.DoesNotExist:
        print('File with uuid', opts.file_uuid, 'does not exist.', file=sys.stderr)
        return
    print('file', file_)
    try:
        format_id = FileFormatVersion.objects.get(file_uuid=opts.file_uuid)
    # Can't do anything if the file wasn't identified
    except FileFormatVersion.DoesNotExist, FileFormatVersion. MultipleObjectsReturned:
        print('Not normalizing ',
            os.path.basename(file_.currentlocation),
            ' - file format not identified',
            file=sys.stderr)
        return
    if format_id.format_version == None:
        print('Not normalizing',
            os.path.basename(file_.currentlocation),
            ' - file format not identified',
            file=sys.stderr)
        return
    print('format_version', format_id.format_version)
    # Normalization commands are defined in the FPR
    try:
        command = FPCommand.active.get(fprule__format=format_id.format_version,
        fprule__purpose=opts.purpose)
    except FPCommand.DoesNotExist:
        try:
            command = FPCommand.active.get(fprule__format=format_id.format_version, fprule__purpose='default_'+opts.purpose)
        except FPCommand.DoesNotExist:
            print('Not normalizing', os.path.basename(file_.currentlocation),
                ' - No rule or default rule found to normalize for', opts.purpose,
                file=sys.stderr)
            return

    print('command', command.description, command.command)
    if command.script_type == 'command' or command.script_type == 'bashScript':
        args = []
        command_to_execute = replace_vars(command.command, opts)
    else:
        command_to_execute = command.command
        args = [opts.file_path, get_output_file_path()]

    print('command_to_execute, args', command_to_execute, args, 'endargs')
    exitstatus, stdout, stderr = executeOrRun(command.script_type,
                                    command_to_execute,
                                    arguments=args,
                                    printing=True)

    if not exitstatus == 0:
        # Dang, looks like the normalization failed
        print('Command', command.description, 'failed!', file=sys.stderr)
    else:
        print('Normalized ', os.path.basename(opts.file_path), 'for', opts.purpose)

    # TODO add to DB


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Identify file formats.')
    # sip dir
    parser.add_argument('purpose', type=str, help='"preservation", "access", "thumbnail"')
    parser.add_argument('file_uuid', type=str, help='%fileUUID%')
    parser.add_argument('file_path', type=str, help='%relativeLocation%')
    parser.add_argument('sip_path', type=str, help='%SIPDirectory%')
    parser.add_argument('sip_uuid', type=str, help='%SIPUUID%')
    parser.add_argument('task_uuid', type=str, help='%taskUUID%')
    parser.add_argument('normalize_file_grp_use', type=str, help='"service", "original", "submissionDocumentation", etc')

    opts = parser.parse_args()
    sys.exit(main(opts))

