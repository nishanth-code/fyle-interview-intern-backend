FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=core/server.py
RUN flask db upgrade -d core/migrations/
EXPOSE 3000
CMD ["bash", "run.sh"]

