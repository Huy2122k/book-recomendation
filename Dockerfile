FROM python:3.9

# Cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y espeak & apt-get install -y espeak-ng
RUN apt-get -y install ffmpeg 
# Cài đặt pyttsx3 và các gói phụ thuộc
RUN pip install pyttsx3
RUN pip install pydub

# Thiết lập biến môi trường để hỗ trợ ngôn ngữ tiếng Việt
ENV ESPEAK_DATA_PATH=/usr/share/espeak-ng-data/voices/vi

# Sao chép script vào container
COPY script.py /app/script.py

# Chạy script khi container được khởi chạy
CMD ["bash"]