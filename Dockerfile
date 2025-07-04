FROM python:3.12

WORKDIR /app

RUN \
    apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY frontend/ ./frontend/
COPY backend/ ./backend/
COPY .env .

RUN cd frontend && npm config set registry http://registry.npmmirror.com && \
	npm install && npm run build
RUN cd backend && pip install -r requirements.txt

EXPOSE 5000
EXPOSE 3000

CMD ["sh", "-c", "cd backend && python app.py & cd /app/frontend && npm start"]
