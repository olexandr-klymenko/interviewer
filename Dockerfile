FROM python:3.8-slim
COPY ./requirements.txt /srv/
WORKDIR /srv
RUN pip install -r requirements.txt
COPY interviewer /srv/interviewer