FROM python:3.11-slim AS kleborate
ARG KLEBORATE_VERSION
ENV KLEBORATE_VERSION=${KLEBORATE_VERSION} \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl bzip2 && \
    rm -rf /var/lib/apt/lists/* && \
    curl -L "https://github.com/lh3/minimap2/releases/download/v2.28/minimap2-2.28_x64-linux.tar.bz2" | tar -jxvf - && \
    mv minimap2-2.28_x64-linux/minimap2 /usr/local/bin/ && \
    rm -rf minimap2-2.28_x64-linux && \
    curl -L https://github.com/marbl/Mash/releases/download/v2.3/mash-Linux64-v2.3.tar | tar xv && \
    mv mash-Linux64-v2.3/mash /usr/bin/ && \
    rm -rf mash-Linux64-v2.3 && \
    pip --no-cache-dir install --disable-pip-version-check kleborate==${KLEBORATE_VERSION} pandas && \
    mkdir /Kleborate && \
    echo "${KLEBORATE_VERSION}" > /Kleborate/kleborate_version

RUN apt update && \
    apt install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists && \
    curl -L -o sanitiser "https://github.com/CorinYeatsCGPS/sanitise-fasta/releases/download/2/sanitiser" && \
    chmod +x ./sanitiser && \
    mv sanitiser /usr/local/bin/

WORKDIR /Kleborate

FROM kleborate AS prod

ARG SPECIES=kpsc
ARG CODE_VERSION=6
ENV SPECIES=${SPECIES} \
    CODE_VERSION=${CODE_VERSION}

RUN pip --no-cache-dir install --disable-pip-version-check typer[all] && \
    echo "${CODE_VERSION}" > /Kleborate/code_version

COPY entrypoint.sh /Kleborate/

RUN chmod +x /Kleborate/entrypoint.sh

COPY cgps-kleborate.py amrMap.json ./

ENTRYPOINT ["./entrypoint.sh"]
