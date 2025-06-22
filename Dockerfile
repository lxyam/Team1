FROM node:latest as frontend-builder

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY frontend/ ./frontend/
COPY backend/ ./backend/
COPY frontend/package.json ./package.json
COPY .env .env
RUN pip install -r requirements.txt


RUN cd frontend && npm config set registry http://registry.npmmirror.com && \
	npm install && npm run build

RUN npm install --production

EXPOSE 5000
EXPOSE 3000

CMD ["sh", "-c", "cd backend && python app.py & cd ../frontend && npm start"]
