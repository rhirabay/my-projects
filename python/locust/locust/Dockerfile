FROM python:3.11.0

RUN pip3 install locust

WORKDIR /locust
COPY ./locustfile.py .
COPY ./run.sh .
RUN chmod +x ./run.sh

ENTRYPOINT ["./run.sh"]