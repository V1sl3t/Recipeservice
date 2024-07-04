FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install -f
COPY . ./
RUN npm run build
CMD cp -r build result_build
