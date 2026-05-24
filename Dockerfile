cat << 'EOF' > Dockerfile
# Python ka engine uthao
FROM python:3.10

# Server mein FFMPEG install karo (Video merging ke liye)
RUN apt-get update && apt-get install -y ffmpeg

# Folder setup
WORKDIR /app
COPY . /app/

# Libraries lagao
RUN pip install -r requirements.txt

# Hugging Face Spaces hamesha port 7860 par chalti hain
EXPOSE 7860

# Engine Start Command (Port 7860 ke sath)
CMD ["python", "manage.py", "runserver", "0.0.0.0:7860"]
EOF