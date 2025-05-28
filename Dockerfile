FROM node:latest as frontend-builder
WORKDIR /app
COPY frontend/ .
RUN npm config set registry http://registry.npmmirror.com && \
	npm install && npm run build

FROM python:3.8

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/ ./backend/

COPY --from=frontend-builder /app/build ./frontend/build

COPY .env .env

WORKDIR /app/backend
RUN pip install -r requirements.txt

WORKDIR /app/frontend
COPY frontend/package.json ./package.json
RUN npm install --production

EXPOSE 5000
EXPOSE 3000

CMD ["sh", "-c", "cd backend && python app.py & cd ../frontend && npm start"]
