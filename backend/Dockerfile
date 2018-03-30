FROM jjanzic/docker-python3-opencv

# Create backend directory
RUN mkdir /backend
COPY . /backend

RUN pip3 install -r "/backend/requirements.txt"
RUN python3 -m spacy download en

# setting environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS="/backend/.gcloud_key.json"
ENV LEXIGRAM_KEY="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdSI6Imx4ZzphcGkiLCJzYyI6WyJrZzpyZWFkIiwiZXh0cmFjdGlvbjpyZWFkIl0sImFpIjoiYXBpOjcxMjIwZjAwLTkxMjAtMWZlMC0xYTJkLTk2MWJlOGNkM2Y2MSIsInVpIjoidXNlcjoxNWJlOGE5Yy0zZDAzLTJmNmMtZjkzMS04NjE5Yjk0YzhiOGMiLCJpYXQiOjE1MjIzMDk5MDd9.FxTChifr8ARvp55Xb8Gf1odMZKfrUPueEcmOGL0Fsn8"

WORKDIR /backend
CMD ["python3","app.py"]
