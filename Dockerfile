FROM python:alpine3.7

RUN pip install -r requirements.txt
RUN pip install -U epigrass
