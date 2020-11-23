import json
import sys
from subprocess import Popen, PIPE

"""Script reads a FASTA from STDIN, and then runs Kleborate over it (FASTA is temporarily written to file). 
The Kleborate results are reformatted for use by Pathogenwatch"""

with open("amrMap.json", 'r') as js_fh:
    amr_list = json.load(js_fh)

amr_dict = dict()

for record in amr_list:
    for extension in record['classes']:
        amr_dict[record['kleborateCode'] + '_' + extension] = record

with open("/Kleborate/version", 'r') as v_fh:
    version = v_fh.readline()

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
amr_profile = dict()
amr_profile['profile'] = dict()
amr_profile['classes'] = dict()

output = dict()
output['Kleborate version'] = version
output['virulence'] = dict()
output['typing'] = dict()
output['csv'] = list()
output['amr'] = dict()

for i in range(0, 4):
    output[header[i]] = result[i]
    output['csv'].append({'set': '', 'field': header[i], 'name': header[i]})

for i in range(4, 15):
    output['virulence'][header[i]] = result[i]
    output['csv'].append({'set': 'virulence', 'field': header[i], 'name': header[i]})

for i in range(15, 20):
    output['typing'][header[i]] = result[i]
    output['csv'].append({'set': 'typing', 'field': header[i], 'name': header[i]})

amr_cache = set()

for i in range(20, len(result) - 2):
    amr_profile['classes'][header[i]] = result[i]
    phenotype = amr_dict[header[i]]
    cache_index = i - 20
    tag = phenotype['key']
    if tag not in amr_profile['profile'].keys():
        amr_cache.add(tag)
        amr_profile['profile'][tag] = phenotype
        amr_profile['profile'][tag]['resistant'] = False
        amr_profile['profile'][tag]['matches'] = '-'
    if result[i] != '-':
        amr_profile['profile'][tag]['resistant'] = True
        if amr_profile['profile'][tag]['matches'] == '-':
            amr_profile['profile'][tag]['matches'] = result[i]
        else:
            amr_profile['profile'][tag]['matches'] = amr_profile['profile'][tag]['matches'] + ';' + result[i]
    output['csv'].append({'set': 'amr', 'field': header[i], 'name': header[i]})

output['amr'] = amr_profile
output['amr']['classes']['truncated_resistance_hits'] = result[len(result) - 2]
output['csv'].append({'set': 'amr', 'field': 'truncated_resistance_hits', 'name': 'truncated_resistance_hits'})

output['amr']['classes']['spurious_resistance_hits'] = result[len(result) - 1]
output['csv'].append({'set': 'amr', 'field': 'spurious_resistance_hits', 'name': 'spurious_resistance_hits'})

# print(json.dumps(OrderedDict(zip(header, result)), separators=(',', ':')), file=sys.stdout)
print(json.dumps(output, separators=(',', ':')), file=sys.stdout)
