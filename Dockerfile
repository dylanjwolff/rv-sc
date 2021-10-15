FROM ubuntu:20.04
WORKDIR /app
RUN apt update
RUN yes | apt upgrade
RUN yes | apt install python3-pip
COPY dependencies/spot.tar.gz .
RUN tar -zxvf spot.tar.gz
WORKDIR /app/spot-2.9.8
RUN ./configure
RUN make -j $(nproc)
RUN make install
WORKDIR /app
RUN rm -rf spot-2.9.8
RUN rm spot.tar.gz
RUN ldconfig
RUN cp -r /usr/local/lib/python3.8/site-packages/spot .
COPY verx-benchmarks/ verx-benchmarks

RUN yes | apt install wget
COPY rvsc/solc_vm.py rvsc/solc_vm.py
COPY config/ config
RUN python3 rvsc/solc_vm.py -M v0.4.0

COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY test/ test
COPY rvsc/ rvsc

RUN pytest

CMD pytest
