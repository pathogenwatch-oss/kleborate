#!/usr/bin/env bash

set -euo pipefail

# Function to report errors
error_report() {
    echo "Error: Command failed: $BASH_COMMAND" >&2
}

trap 'error_report' ERR

# Create the encoded FASTA
if ! sanitiser --store /mapping_store encode - > /tmp/query.fna; then
    echo "Error: Failed to create encoded FASTA file." >&2
    exit 1
fi

# Run Kaptive
if ! python3 cgps-kleborate.py -k /Kleborate/kleborate_version -c /Kleborate/code_version -a /Kleborate/amrMap.json /tmp/query.fna ${SPECIES}; then
    echo "Error: Failed to run." >&2
    exit 1
fi


# cat | sed 's/\t//' | sed 's/ /_/g' > /tmp/query.fna && python3 cgps-kleborate.py -k /Kleborate/kleborate_version -c /Kleborate/code_version -a /Kleborate/amrMap.json /tmp/query.fna ${SPECIES}"