FROM ubuntu:latest


WORKDIR /app

COPY . .

EXPOSE 8000

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && 

CMD ["python", "app.py"]

