FROM python:3.11-slim AS kleborate
ARG KLEBORATE_VERSION
ENV KLEBORATE_VERSION=${KLEBORATE_VERSION}
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt update && \
    apt install -y --no-install-recommends curl bzip2 &&  \
    rm -rf /var/lib/apt/lists/*

RUN curl -L "https://github.com/lh3/minimap2/releases/download/v2.28/minimap2-2.28_x64-linux.tar.bz2" | tar -jxvf - && \
    mv minimap2-2.28_x64-linux/minimap2 /usr/local/bin/ && \
    rm -rf minimap2-2.28_x64-linux

RUN curl -L https://github.com/marbl/Mash/releases/download/v2.3/mash-Linux64-v2.3.tar | tar xv \
    && mv mash-Linux64-v2.3/mash /usr/bin/ \
    && rm -rf mash-Linux64-v2.3

RUN pip --disable-pip-version-check --no-cache-dir install kleborate==${KLEBORATE_VERSION}

RUN mkdir /Kleborate

RUN echo "${KLEBORATE_VERSION}" > /Kleborate/kleborate_version

WORKDIR /Kleborate

ENTRYPOINT ["kleborate"]

FROM kleborate AS dev

ENV PYTHONDONTWRITEBYTECODE=1

RUN pip --disable-pip-version-check --no-cache-dir install typer[all]

WORKDIR /Kleborate


FROM dev AS prod

ARG SPECIES=kpsc
ARG CODE_VERSION=3
ENV SPECIES=${SPECIES}
ENV CODE_VERSION=${CODE_VERSION}

RUN echo "${CODE_VERSION}" > /Kleborate/code_version

WORKDIR /Kleborate

COPY cgps-kleborate.py .

COPY amrMap.json .

ENTRYPOINT cat > /tmp/query.fna && python3 cgps-kleborate.py -k /Kleborate/kleborate_version -c /Kleborate/code_version -a /Kleborate/amrMap.json /tmp/query.fna ${SPECIES}