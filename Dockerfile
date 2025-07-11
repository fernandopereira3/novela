FROM fedora:latest

WORKDIR /novela

# Copy application files
COPY . .
RUN dnf update  -y
RUN dnf install python313 -y
RUN dnf install python3-pip -y
RUN cd /novela
RUN python3 -m venv .
RUN python3 -m pip install -r requirements.txt

EXPOSE  5000

# Run the application
CMD ["python3", "src/main.py"]


