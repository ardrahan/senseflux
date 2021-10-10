FROM python:3.8

ENV SF_PORT 8003
ENV INFLUXDB_HOST localhost
ENV INFLUXDB_PORT 8086
ENV INFLUXDB_DATABASE senseflux

RUN pip install poetry

RUN adduser --system --shell /bin/false --home /app app

USER app
#COPY poetry.lock /app/
COPY pyproject.toml /app/
COPY senseflux /app/senseflux
WORKDIR /app
RUN poetry update 
RUN poetry install

#CMD tail -f /dev/null
CMD ["poetry", "run", "python", "-m", "senseflux.__main__"]
