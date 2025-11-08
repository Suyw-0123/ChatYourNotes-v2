# Frontend image for the ChatYourNotes React application
FROM node:20-alpine AS build

ARG VITE_API_BASE="http://localhost:8000"
ENV VITE_API_BASE=${VITE_API_BASE}

WORKDIR /app

COPY frontend/package.json ./

RUN npm install --silent

COPY frontend .
RUN npm run build

FROM nginx:1.27-alpine-slim
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
