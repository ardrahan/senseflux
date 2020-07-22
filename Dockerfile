FROM python:3.8

ENV SF_PORT 8003
ENV INFLUX_HOST localhost
ENV INFLUX_PORT 8086
ENV INFLUX_DATABASE senseflux

RUN pip install poetry

RUN adduser --system --shell /bin/false --home /app app

USER app
COPY poetry.lock pyproject.toml /app/
COPY senseflux /app/senseflux
WORKDIR /app
RUN poetry install

CMD ["poetry", "run", "python", "-m", "senseflux.__main__"]