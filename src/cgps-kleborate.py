import sys
import json
from collections import OrderedDict
from subprocess import Popen, PIPE

"""Script reads a FASTA from STDIN, and then runs Kleborate over it (FASTA is temporarily written to file). 
The Kleborate results are reformatted for use by Pathogenwatch"""

assembly_file = sys.argv[1]

# Run kleborate
p = Popen(['./kleborate-runner.py', '-a', str(assembly_file), '-o', '/tmp/tmp.out', '--all'], stdout=PIPE)
return_code = p.returncode

# Read result file and write as json blob
header = p.stdout.readline().decode('UTF-8').rstrip().split('\t')[1:]
result = p.stdout.readline().decode('UTF-8').rstrip().split('\t')[1:]

print(json.dumps(OrderedDict(zip(header, result)), separators=(',', ':')), file=sys.stdout)
