FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3 python3-pip python3-dev libsm6 libxext6 libxrender1

COPY ./requirements.txt /var/www/requirements.txt

RUN pip3 install -r /var/www/requirements.txt

WORKDIR /var/www

ENTRYPOINT ["python3"]
CMD ["main.py"]