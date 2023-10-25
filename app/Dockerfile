FROM python:3.9

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip

RUN pip install -r /tmp/requirements.txt

RUN mkdir app

RUN mkdir server

RUN mkdir server/static

RUN mkdir server/static/saved_files

COPY . /app

WORKDIR /app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0"]
