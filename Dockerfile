FROM python:3.6.9

ADD requirements-dev.txt app/
WORKDIR app 
RUN pip install -r requirements-dev.txt
