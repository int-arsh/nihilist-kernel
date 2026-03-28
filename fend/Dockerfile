# Stage 1: Build with Bun
FROM oven/bun:1 AS builder
WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .

# Vite env at build time
ARG VITE_API_BASE_URL=http://backend:5000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN bun run build

# Stage 2: Serve with Nginx
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]