FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# ACTIVATE ENVIRONMENT
COPY . .



# Its handy to have in case you want to run additional commands in the Dockerfile
CMD ["flask", "run", "--host", "0.0.0.0"]