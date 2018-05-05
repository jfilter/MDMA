FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat

RUN pip install -U pip pipenv==11.9.0
ADD Pipfile* /code/
WORKDIR /code

RUN ln -sf /usr/local/bin/python /bin/python

RUN pipenv install --system --ignore-pipfile

ADD misc/dokku/CHECKS /app/
ADD misc/dokku/* /code/

COPY . /code/
RUN chmod +x /code/manage.py
RUN /code/manage.py collectstatic --noinput
