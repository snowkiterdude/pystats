FROM python:3.10.13-alpine3.19

RUN apk add --no-cache build-base linux-headers
# py3-dateutil



RUN adduser -D pystats
# RUN mkdir /home/pystats/src
# RUN mkdir -p /home/pystats/src


# ADD pystat.py /home/pystats/
# ADD requirements.txt /home/pystats/
# ADD src /home/pystats/src
# ADD static /home/pystats/static
# ADD templates /home/pystats/templates
# ADD LICENSE /home/pystats/LICENSE
ADD . /home/pystats/app
RUN chown -R pystats:pystats /home/pystats


RUN echo "PATH=/home/pystats/.local/bin:$PATH" >> /etc/profile 

USER pystats
WORKDIR /home/pystats/app

RUN python -m pip  install --upgrade pip
RUN python -m pip install -r /home/pystats/app/requirements.txt


ENTRYPOINT ["/home/pystats/app/pystat.py"]
