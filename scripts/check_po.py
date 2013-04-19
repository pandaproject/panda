#!/usr/bin/env python
import os, os.path
import re

placeholder_pat = re.compile("%\((.+?)\)(\w)")
def extract_placeholders(s):
    return set(placeholder_pat.findall(s))

def check_file(fn):
    msgid = ''
    msgstr = ''
    workingon = 'msgid'
    mismatches = []
    for line in open(fn):
        if line.startswith('#'): continue
        text = ''
        if line.startswith('msg'):
            workingon, text = line.split(' ',1)
            if workingon == 'msgid':
                if msgid and msgstr:
                    id_placeholders = extract_placeholders(msgid)
                    str_placeholders = extract_placeholders(msgstr)
                    if len(id_placeholders) != len(str_placeholders) or (len(id_placeholders.difference(str_placeholders)) != 0):
                        mismatches.append((msgid,msgstr))
                    msgid = msgstr = ''
        else:
            text = line
        text = text.strip('"')
        if text:
            if workingon == 'msgid':
                msgid += text
            else:
                msgstr += text

    if mismatches:
        print "WARNING: %i mismatches in %s" % (len(mismatches),fn)
        for msgid, msgstr in mismatches:
            print 'msgid:' + msgid
            print 'msgstr:' + msgstr
            print



for path, dirs, files in os.walk('../locale'):
    for f in files:
        if f.endswith('.po'):
            check_file(os.path.join(path,f))
