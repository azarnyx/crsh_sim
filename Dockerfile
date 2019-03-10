FROM ubuntu:16.04

MAINTAINER Dmitrii Azarnykh "d.azarnykh@tum.de"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
    && cd /usr/local/bin \
      && ln -s /usr/bin/python3 python \
        && pip3 install --upgrade pip
	
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app"]