import glob
import os
import sys
from collections import OrderedDict

import jsonpickle

"""Given a directory of Kleborate JSON output, produces a CSV with the first column as filename"""

input_dir = sys.argv[1]
nameToKlebMap = OrderedDict()

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


header = ','.join(fields)
fields = ['species',
          'ST',
          'virulence_score',
          'resistance_score',
          'Yersiniabactin',
          'YbST',
          'Colibactin',
          'CbST',
          'Aerobactin',
          'AbST',
          'Salmochelin',
          'SmST',
          'RmpADC',
          'RmST',
          'rmpA2'
          'wzi',
          'K_locus',
          'K_locus_confidence',
          'O_locus',
          'O_locus_confidence',
          'AGly_acquired',
          'Col_acquired',
          'Fcyn_acquired',
          'Flq_acquired',
          'Gly_acquired',
          'MLS_acquired',
          'Phe_acquired',
          'Rif_acquired',
          'Sul_acquired',
          'Tet_acquired',
          'Tgc_acquired',
          'Tmt_acquired',
          'Bla_acquired',
          'Bla_inhR_acquired'
          'Bla_ESBL_acquired',
          'Bla_ESBL_inhR_acquired',
          'Bla_Carb_acquired',
          'Bla_chr',
          'SHV_mutations',
          'Omp_mutations',
          'Col_mutations',
          'truncated_resistance_hits',
          'spurious_resistance_hits'
          ]

print(header, file=sys.stdout)
for name, data in nameToKlebMap.items():
    line = ','.join([data[field] for field in fields])
    print(name, line, sep=',', file=sys.stdout)
