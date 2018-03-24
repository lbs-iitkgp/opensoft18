# Set the base image
FROM ubuntu:16.04
# Dockerfile author / maintainer
ENV http_proxy http://172.16.2.30:8080
ENV https_proxy https://172.16.2.30:8080
MAINTAINER Name <Digicon@here>

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
RUN mkdir -p /digicon
COPY backend /digicon/backend
COPY frontend /digicon/frontend
COPY metadata-extraction /digicon/metadata-extraction
COPY spellcheck /digicon/spellcheck
COPY vision-api /digicon/vision-api

WORKDIR /digicon/backend
RUN pip3 install --upgrade pip \
&& pip3 install -r requirements.txt \
&& python3 -m nltk.downloader all \
&& apt-get clean

WORKDIR /digicon

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils

#RUN curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash - \
#&& apt-get install -y nodejs \
#&& apt-get clean

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - \
&& echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list \
&& sudo apt-get update && sudo apt-get install yarn \
&& apt-get clean

#RUN yarn config set proxy http://172.16.2.30:8080

#CMD ["yarn"]
