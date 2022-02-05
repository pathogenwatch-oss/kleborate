import json
import subprocess
import sys

"""Script runs Kleborate and reformats the results for use by Pathogenwatch"""

kleborate_headers = [
    "strain",
    "species",
    "species_match",
    "contig_count",
    "N50",
    "largest_contig",
    "total_size",
    "ambiguous_bases",
    "QC_warnings",
    "ST",
    "virulence_score",
    "resistance_score",
    "num_resistance_classes",
    "num_resistance_genes",
    "Yersiniabactin",
    "YbST",
    "Colibactin",
    "CbST",
    "Aerobactin",
    "AbST",
    "Salmochelin",
    "SmST",
    "RmpADC",
    "RmST",
    "rmpA2",
    "wzi",
    "K_locus",
    "K_type",
    "K_locus_problems",
    "K_locus_confidence",
    "K_locus_identity",
    "K_locus_missing_genes",
    "O_locus",
    "O_type",
    "O_locus_problems",
    "O_locus_confidence",
    "O_locus_identity",
    "O_locus_missing_genes",
    "AGly_acquired",
    "Col_acquired",
    "Fcyn_acquired",
    "Flq_acquired",
    "Gly_acquired",
    "MLS_acquired",
    "Phe_acquired",
    "Rif_acquired",
    "Sul_acquired",
    "Tet_acquired",
    "Tgc_acquired",
    "Tmt_acquired",
    "Bla_acquired",
    "Bla_inhR_acquired",
    "Bla_ESBL_acquired",
    "Bla_ESBL_inhR_acquired",
    "Bla_Carb_acquired",
    "Bla_chr",
    "SHV_mutations",
    "Omp_mutations",
    "Col_mutations",
    "Flq_mutations",
    "truncated_resistance_hits",
    "spurious_resistance_hits",
    "Chr_ST",
    "gapA",
    "infB",
    "mdh",
    "pgi",
    "phoE",
    "rpoB",
    "tonB",
    "ybtS",
    "ybtX",
    "ybtQ",
    "ybtP",
    "ybtA",
    "irp2",
    "irp1",
    "ybtU",
    "ybtT",
    "ybtE",
    "fyuA",
    "clbA",
    "clbB",
    "clbC",
    "clbD",
    "clbE",
    "clbF",
    "clbG",
    "clbH",
    "clbI",
    "clbL",
    "clbM",
    "clbN",
    "clbO",
    "clbP",
    "clbQ",
    "iucA",
    "iucB",
    "iucC",
    "iucD",
    "iutA",
    "iroB",
    "iroC",
    "iroD",
    "iroN",
    "rmpA",
    "rmpD",
    "rmpC",
    "spurious_virulence_hits"
]

top_level_fields = kleborate_headers[0:14]
virulence_fields = kleborate_headers[14:25]
classes_fields = kleborate_headers[38:60]
trunc_res_hits_field = kleborate_headers[60]
spur_res_hits_field = kleborate_headers[61]
typing_fields = kleborate_headers[25:8]
other_fields = kleborate_headers[62:]

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
complete = subprocess.run(
    [
        './kleborate-runner.py',
        '-a', str(assembly_file),
        '-o', '/tmp/tmp.out',
        '--all'
    ],
    check=True,
    capture_output=True
)

# Read result file and write as json blob
with open('/tmp/tmp.out', 'r') as result_fh:
    header = result_fh.readline().strip().split('\t')
    result = result_fh.readline().strip().split('\t')

amr_profile = dict()
amr_profile['profile'] = dict()
amr_profile['classes'] = dict()

output = dict()
output['Kleborate version'] = version
output['virulence'] = dict()
output['typing'] = dict()
output['other'] = dict()
output['csv'] = list()

for i in range(0, len(top_level_fields)):
    output[top_level_fields[i]] = result[i]
    output['csv'].append({'set': '', 'field': top_level_fields[i], 'name': top_level_fields[i]})

column_counter = len(top_level_fields) - 1

for i in range(0, len(virulence_fields)):
    output['virulence'][virulence_fields[i]] = result[column_counter]
    output['csv'].append({'set': 'virulence', 'field': virulence_fields[i], 'name': virulence_fields[i]})
    column_counter += 1

for i in range(0, len(typing_fields)):
    output['typing'][typing_fields[i]] = result[column_counter]
    output['csv'].append({'set': 'typing', 'field': typing_fields[i], 'name': typing_fields[i]})
    column_counter += 1

amr_cache = set()

for i in range(0, len(classes_fields)):
    amr_profile['classes'][classes_fields[i]] = result[column_counter]
    phenotype = amr_dict[classes_fields[i]]
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
            amr_profile['profile'][tag]['matches'] = amr_profile['profile'][tag]['matches'] + ';' + result[
                column_counter]
    output['csv'].append({'set': 'amr', 'field': classes_fields[i], 'name': classes_fields[i]})
    column_counter += 1

output['amr'] = amr_profile
output['amr']['classes']['truncated_resistance_hits'] = result[column_counter]
output['csv'].append({'set': 'amr', 'field': 'truncated_resistance_hits', 'name': 'truncated_resistance_hits'})

output['amr']['classes']['spurious_resistance_hits'] = result[column_counter + 1]
output['csv'].append({'set': 'amr', 'field': 'spurious_resistance_hits', 'name': 'spurious_resistance_hits'})
column_counter += 2

for i in range(0, len(other_fields)):
    output['other'][other_fields[i]] = result[column_counter]
    output['csv'].append({'set': 'other', 'field': other_fields[i], 'name': other_fields[i]})
    column_counter += 1

del output['strain']
print(json.dumps(output, separators=(',', ':')), file=sys.stdout)
