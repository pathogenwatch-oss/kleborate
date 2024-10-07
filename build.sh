#!/usr/bin/env bash

set -euo pipefail
set -x

KLEBORATE_VERSION=${1:-v3.1.0}

IMAGE_BASE="registry.gitlab.com/cgps/pathogenwatch-tasks/kleborate"

CODE_VERSION="$(cat code_version)"

for i in kpsc kosc other
do
  IMAGE_NAME=${IMAGE_BASE}:${i}-${KLEBORATE_VERSION}-${CODE_VERSION}
  docker build --rm --target prod --build-arg KLEBORATE_VERSION=${KLEBORATE_VERSION} --build-arg SPECIES=${i} -t ${IMAGE_NAME} .
  docker push ${IMAGE_NAME}
done