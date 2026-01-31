FROM --platform=linux/amd64 python:3.12-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/
COPY . /app/
WORKDIR /app/

EXPOSE 8000
ARG app_version
ENV APP_VERSION=$app_version
CMD ["gunicorn", "hello:app", "--bind", "0.0.0.0:8000", "--workers", "3"]