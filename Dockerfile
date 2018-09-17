FROM ubuntu:18.04

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
    && curl ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.2.30/ncbi-blast-2.2.30+-x64-linux.tar.gz | tar -xz \
    && mv ncbi-blast-2.2.30+/bin/* /usr/bin/ \
    && cd .. \
    && rm -rf /blast

#ENV PATH="/blast/:$PATH"

RUN git config --global core.autocrlf input \
    && git clone --recursive https://github.com/katholt/Kleborate.git

RUN pip3 install biopython

RUN ln -sf /usr/bin/python3.6 /usr/bin/python

WORKDIR Kleborate

#CMD python3 kleborate-runner.py -h

COPY src/cgps-kleborate.py .

CMD cat > /tmp/query.fna && python3 cgps-kleborate.py /tmp/query.fna