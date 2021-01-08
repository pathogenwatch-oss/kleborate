FROM ubuntu:20.04

ARG KLEBORATE
ENV KLEBORATE=${KLEBORATE:-v2.0.1}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    python3 \
    python3-setuptools \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /blast \
    && cd /blast \
    && curl ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.9.0/ncbi-blast-2.9.0+-x64-linux.tar.gz | tar -xz \
    && mv ncbi-blast-2.9.0+/bin/* /usr/bin/ \
    && cd .. \
    && rm -rf /blast

RUN curl -L https://github.com/marbl/Mash/releases/download/v2.1/mash-Linux64-v2.1.tar | tar -x \
    && mv mash-*/mash /usr/bin/ \
    && rm -rf mash-Linux*

#ENV PATH="/blast/:$PATH"

RUN git config --global core.autocrlf input \
    && echo "$KLEBORATE" \
    && git clone --recursive --depth 1 --branch $KLEBORATE https://github.com/katholt/Kleborate.git \
    && echo "$KLEBORATE" > /Kleborate/version

RUN pip3 install biopython

RUN ln -sf /usr/bin/python3.7 /usr/bin/python

WORKDIR Kleborate

#CMD python3 kleborate-runner.py -h

COPY src/cgps-kleborate.py .

COPY src/amrMap.json .

CMD cat > /tmp/query.fna && python3 cgps-kleborate.py /tmp/query.fna