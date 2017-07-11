FROM python:3.6

ARG uid=1000
ARG gid=1000

RUN getent group $gid || groupadd --gid $gid sqjobs
RUN getent passwd $uid || useradd -m -u $uid -g $gid sqjobs

RUN chown -R $uid:$gid /usr/local

USER $uid

COPY build/base/requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
