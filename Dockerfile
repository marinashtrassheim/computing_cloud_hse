FROM python:3.10-slim
WORKDIR /app
RUN pip install flask prometheus-client
COPY app.py .
RUN mkdir -p /tmp/uploads
EXPOSE 5000
CMD ["python", "app.py"]