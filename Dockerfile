FROM python:3.10.13-alpine3.19

RUN apk add --no-cache build-base linux-headers

# -D = Don't assign a password(locked)
RUN adduser -D pystats

ADD app /home/pystats/app
ADD README.md /home/pystats/app/README.md
ADD LICENSE /home/pystats/app/LICENSE
RUN chown -R pystats:pystats /home/pystats

# add pip .requirements.txt packages to path
RUN echo "PATH=/home/pystats/.local/bin:$PATH" >> /etc/profile 

USER pystats
WORKDIR /home/pystats/app

RUN python -m pip install --no-cache-dir --upgrade pip
RUN python -m pip install --no-cache-dir -r /home/pystats/app/requirements.txt

ENTRYPOINT ["/home/pystats/app/pystat.py"]
