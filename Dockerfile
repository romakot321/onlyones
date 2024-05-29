FROM python:3.11
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY setup.py ./
COPY ./app ./app
RUN pip3 install .

CMD init_db && \
    cd app && \
    alembic -c ./alembic.prod.ini upgrade head && \
    cd /app && \
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80
