cat << 'EOF' > Dockerfile

FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 7860

CMD ["python", "manage.py", "runserver", "0.0.0.0:7860"]
EOF
