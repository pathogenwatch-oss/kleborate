import json
import subprocess
import sys

"""Script reads a FASTA from STDIN, and then runs Kleborate over it (FASTA is temporarily written to file). 
The Kleborate results are reformatted for use by Pathogenwatch"""

with open("amrMap.json", 'r') as js_fh:
    amr_list = json.load(js_fh)

amr_dict = dict()

for record in amr_list:
    for extension in record['classes']:
        amr_dict[record['kleborateCode'] + '_' + extension] = record

with open("/Kleborate/version", 'r') as v_fh:
    version = v_fh.readline().strip()

assembly_file = sys.argv[1]

# Run kleborate
complete = subprocess.run(['./kleborate-runner.py', '-a', str(assembly_file), '-o', '/tmp/tmp.out', '--all'],
                          check=True,
                          capture_output=True)

# Read result file and write as json blob
with open('/tmp/tmp.out', 'r') as result_fh:
    header = result_fh.readline().strip().split('\t')[1:]
    result = result_fh.readline().strip().split('\t')[1:]

# (species, st, virulence_score, resistance_score) = result[0:4]
# (yersiniabactin, ybst, colibactin, cbst, aerobactin, abst, salmochelin, smst, rmpabd, rmST, rmpa2) = result[4:15]
# (wzi, klocus, klocus_conf, olocus, olocus_conf) = result[15:20]
# amr = result[20:]
amr_profile = dict()
amr_profile['profile'] = dict()
amr_profile['classes'] = dict()

output = dict()
output['Kleborate version'] = version
output['virulence'] = dict()
output['typing'] = dict()
output['other'] = dict()
output['csv'] = list()

for i in range(0, 13):
    output[header[i]] = result[i]
    output['csv'].append({'set': '', 'field': header[i], 'name': header[i]})

for i in range(13, 24):
    output['virulence'][header[i]] = result[i]
    output['csv'].append({'set': 'virulence', 'field': header[i], 'name': header[i]})

for i in range(24, 36):
    output['typing'][header[i]] = result[i]
    output['csv'].append({'set': 'typing', 'field': header[i], 'name': header[i]})

amr_cache = set()

for i in range(36, 58):
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
output['amr']['classes']['truncated_resistance_hits'] = result[58]
output['csv'].append({'set': 'amr', 'field': 'truncated_resistance_hits', 'name': 'truncated_resistance_hits'})

output['amr']['classes']['spurious_resistance_hits'] = result[59]
output['csv'].append({'set': 'amr', 'field': 'spurious_resistance_hits', 'name': 'spurious_resistance_hits'})

for i in range(60, len(result)):
    output['other'][header[i]] = result[i]
    output['csv'].append({'set': 'other', 'field': header[i], 'name': header[i]})

# print(json.dumps(OrderedDict(zip(header, result)), separators=(',', ':')), file=sys.stdout)
print(json.dumps(output, separators=(',', ':')), file=sys.stdout)
