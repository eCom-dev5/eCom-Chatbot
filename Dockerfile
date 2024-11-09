FROM python:3.11-bullseye

RUN apt update -y && apt install awscli -y
WORKDIR /verta-chatbot

COPY . /verta-chatbot
RUN pip install -r requirements.txt

CMD ["python3", "src/serve.py"]