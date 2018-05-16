import sys
import tempfile
from Bio import SeqIO
from subprocess import call

"""Script reads a FASTA from STDIN, and then runs Kleborate over it (FASTA is temporarily written to file). 
The Kleborate results are reformatted for use by Pathogenwatch"""

assembly = SeqIO.to_dict(SeqIO.parse(sys.stdin, 'fasta'))

with tempfile.NamedTemporaryFile() as assembly_file, tempfile.TemporaryDirectory() as temp_dir:

    # Write the temp assembly
    SeqIO.write(assembly, assembly_file, 'fasta')

    # Run kleborate
    call(['kleborate-runner.py', '-a', str(assembly_file), '-o', str(temp_dir), '-k'])

    # Read result file and write as json blob
