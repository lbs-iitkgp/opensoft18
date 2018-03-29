#!/bin/sh

cd backend

sudo -H pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo PIP_REQ_OK
else
    echo PIP_REQ_FAIL
fi

python3 -m nltk.downloader all

cd ..

#NODEJS_v8
#curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
#sudo apt-get install -y nodejs

#if [ $? -eq 0 ]; then
 #   echo NODE_OK
#else
 #   echo NODE_FAIL
#fi

sudo apt-get install -y build-essential

#YARN
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install yarn

if [ $? -eq 0 ]; then
    echo YARN_OK
else
    echo YARN_FAIL
fi

cd ..
