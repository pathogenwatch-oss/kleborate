import json
import sys
from subprocess import Popen, PIPE

"""Script reads a FASTA from STDIN, and then runs Kleborate over it (FASTA is temporarily written to file). 
The Kleborate results are reformatted for use by Pathogenwatch"""

with open("amrMap.json", 'r') as js_fh:
    amr_list = json.load(js_fh)

amr_dict = {record['kleborateCode']: record for record in amr_list}

assembly_file = sys.argv[1]

# Run kleborate
p = Popen(['./kleborate-runner.py', '-a', str(assembly_file), '-o', '/tmp/tmp.out', '--all'], stdout=PIPE)
return_code = p.returncode

# Read result file and write as json blob
header = p.stdout.readline().decode('UTF-8').rstrip().split('\t')[1:]
result = p.stdout.readline().decode('UTF-8').rstrip().split('\t')[1:]

# (species, st, virulence_score, resistance_score) = result[0:4]
# (yersiniabactin, ybst, colibactin, cbst, aerobactin, abst, salmochelin, smst, rmpa,rmpa2) = result[4:14]
# (wzi, klocus, klocus_conf, olocus, olocus_conf) = result[14:19]
# amr = result[19:]

output = dict()
output['amr'] = {}
output['virulence'] = {}
output['typing'] = {}
output['csv'] = []

for i in range(0, 4):
    output[header[i]] = result[i]
    output['csv'].append({'set': '', 'field': header[i], 'name': header[i]})

for i in range(4, 14):
    output['virulence'][header[i]] = result[i]
    output['csv'].append({'set': 'virulence', 'field': header[i], 'name': header[i]})

for i in range(14, 19):
    output['typing'][header[i]] = result[i]
    output['csv'].append({'set': 'typing', 'field': header[i], 'name': header[i]})

for i in range(19, len(result)):
    am_record = amr_dict[header[i]]
    am_record['match'] = result[i]
    output['amr'][am_record['key']] = am_record
    output['csv'].append({'set': 'amr', 'field': am_record['key'], 'name': am_record['kleborateCode']})

    # print(json.dumps(OrderedDict(zip(header, result)), separators=(',', ':')), file=sys.stdout)
    print(json.dumps(output, separators=(',', ':')), file=sys.stdout)
