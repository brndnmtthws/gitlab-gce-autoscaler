FROM python:3-alpine

WORKDIR /app
COPY . /app/src

RUN cd src \
  && pip install --no-cache-dir .

ENTRYPOINT [ "gitlab-gce-autoscaler" ]
