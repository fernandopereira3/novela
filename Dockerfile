FROM python
WORKDIR /app
COPY . .
EXPOSE 8000
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

FROM mongodb:latest


