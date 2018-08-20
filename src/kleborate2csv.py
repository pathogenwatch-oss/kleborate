import os
import sys
import glob
import jsonpickle

"""Given a directory of Kleborate JSON output, produces a CSV with the first column as filename"""

input_dir = sys.argv[1]
nameToKlebMap = dict()

for file in glob.glob(input_dir + '/*.jsn'):
    name = os.path.basename(file).replace('_contigs.fa.kleborate.jsn', '')
    with open(file, 'r') as kleb_out:
        nameToKlebMap[name] = jsonpickle.decode(kleb_out.read())

"""    
    "ST": "ST11",
    "virulence_score": "1",
    "Yersiniabactin": "ybt 9; ICEKp3",
    "YbST": "183",
    "Colibactin": "-",
    "CbST": "0",
    "Aerobactin": "-",
    "AbST": "0",
    "Salmochelin": "-",
    "SmST": "0",
    "hypermucoidy": "-",
    "wzi": "wzi50",
    "K_locus": "KL15",
    "K_locus_confidence": "Very high",
    "O_locus": "O4",
    "O_locus_confidence": "Good"
"""

fields = ['ST', 'virulence_score', 'Yersiniabactin', 'YbST', 'Colibactin', 'CbST', 'Aerobactin', 'AbST',
          'Salmochelin', 'SmST', 'hypermucoidy', 'wzi', 'K_locus', 'K_locus_confidence', 'O_locus',
          'O_locus_confidence']

header = ','.join(fields)

print(header, file=sys.stdout)
for name, data in nameToKlebMap.items():
    line = ','.join([data[field] for field in fields])
    print(name, line, sep=',', file=sys.stdout)
