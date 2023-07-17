FROM tiangolo/uwsgi-nginx-flask:python3.9-2023-03-20
RUN apk --update add bash nano
COPY ./requirements.txt /var/AI/requirements.txt
RUN pip install -r var/AI/requirements.txt