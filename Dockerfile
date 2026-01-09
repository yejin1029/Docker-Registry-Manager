# 베이스 이미지로 Python 3 사용
FROM python:3.8-slim

# 시스템 업데이트 및 curl 설치
RUN apt-get update && apt-get install -y curl

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt /app/

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . /app/

# Flask 앱 실행
CMD ["python", "app.py"]
