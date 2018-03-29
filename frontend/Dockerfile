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

RUN mkdir /frontend
COPY . /frontend

RUN curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash - \
&& apt-get install -y nodejs \
&& apt-get clean

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
&& echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list \
&& apt-get update \
&& apt-get install yarn \
&& apt-get clean

RUN yarn config set proxy http://172.16.2.30:8080 \
&& yarn config set https-proxy http://172.16.2.30:8080

WORKDIR /frontend

RUN yarn 

#RUN yarn start

CMD ["yarn","start"]