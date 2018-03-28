
FROM ubuntu:16.04

ENV http_proxy http://172.16.2.30:8080
ENV https_proxy https://172.16.2.30:8080

RUN apt-get update \
&& apt-get install -y \
   wget \
   curl \
   build-essential \
   sudo \
   mesa-utils \
   apt-transport-https ca-certificates \
   python3-pip \
&& apt-get clean

# Create directory
RUN mkdir /backend
COPY . /backend

WORKDIR /backend
RUN sudo -H pip3 install --upgrade pip \
&& sudo -H pip3 install -r requirements.txt \
&& apt-get clean

CMD ["python3","app.py"]