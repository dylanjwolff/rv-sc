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

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:ethereum/ethereum
RUN apt update
RUN apt install -y ethereum

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY test/ test
COPY rvsc/ rvsc
COPY specs/ specs
COPY config/ config

RUN pytest

CMD pytest
