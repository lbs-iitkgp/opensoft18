# OpenSoft 2018 project - DigiCon

Our application has 2 components - Backend & Frontend

For running DigiCon, first you must run the Backend and then run the Frontend

## Backend

Change into the Backend directory  `cd backend`

Install all the requirements `pip3 install -r requirements.txt`

Install the spacy English module `python -m spacy download en`

Add the path to your Google credential .json file to your environment `export  GOOGLE_APPLICATION_CREDENTIALS="/path/to/credential/file"`

Add the Lexigram key to the environment `export LEXIGRAM_KEY="your key here"` 

Add the Spellcheck key to the environment `export SPELLCHECK_KEY="your key here"`

Add the Vision Api key to the environment `export VISION_API_KEY="your key here"`

Now run the file `python3 app.py`

## Frontend

Change into the Frontend directory `cd frontend`

- Install [nodejs (will also install npm)](https://nodejs.org/en/download/package-manager/)
- Install [yarn](https://yarnpkg.com/lang/en/docs/install/)
- Set up the proxy `yarn config set proxy "http://proxy.com:port"`  `yarn config set https-proxy "http://proxy.com:port"`
- Now initialise and download dependencies `yarn`
- Start the react server `yarn start`


