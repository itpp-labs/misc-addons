# -*- coding: utf-8 -*-
import sys
import glob
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import csv
import re

files_path = sys.argv[1]

print 'files_path', files_path

files = glob.glob('%s/*.txt' % files_path)

import_options = {'separator': ';'}
csv.field_size_limit(1310720)


def get_data(file_name, find_problem_line=False):
    print file_name, find_problem_line
    with open(file_name, 'rb') as csvfile:
        fixed_file = csvfile.read().replace('\r\r\n', ' ').replace('\r\n', '<br/>').replace(';<br/>', ';\n')

        fixed_file = re.sub(r';"([0-9a-zA-Z, ]*;)', r';\1', fixed_file)

        fixed_file = StringIO(fixed_file)

    reader = csv.reader(fixed_file,
                        delimiter=import_options.get('separator'),
                        # quotechar = '"',
                        )
    if find_problem_line:
        print 'find_problem_line'
        lines = ['1', '2', '3', '4', '5']
        r = True
        while r:
            try:
                r = reader.next()
                lines.pop(0)
                lines.append(str(r))
            except:
                # print 'last lines', '\n'.join(lines)
                raise
        print 'OK', '\n'.join(lines)
    try:
        res = list(reader)
    except:
        if not find_problem_line:
            get_data(file_name, find_problem_line=True)
        raise
    return res

for file_name in files:
    data = get_data(file_name)
    print data[0]
