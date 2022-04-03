FROM python:3.9.9

WORKDIR /usr/src/app

COPY ./requirements.txt .

VOLUME [ "/usr/src/app" ]
RUN \
    # apk add --no-cache postgresql-libs gcc g++ make python3-dev musl-dev postgresql-dev libffi && \
    # apt install musl-dev postgresql-dev libffi && \
    # python3 -m venv venv && . venv/bin/activate && \
    # pip install --upgrade pip setuptools wheel && \
    /usr/local/bin/python -m pip install --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt


EXPOSE 5000

ENTRYPOINT [ "flask","run","--host=0.0.0.0","--port=5000"  ]

# ENTRYPOINT [ "" ]
