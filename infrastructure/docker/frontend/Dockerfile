# ============================================================
# AI CareerOS — Frontend Production Dockerfile
# ============================================================
# Multi-stage build: build React app, serve via Nginx.
# ============================================================

# ---------- Stage 1: Builder ----------
FROM node:20-alpine AS builder

WORKDIR /build

# Copy package files first (cache layer)
COPY frontend/package*.json /build/

RUN npm ci

# Copy source
COPY frontend/ /build/

# Build (env passed at build time)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ---------- Stage 2: Runtime ----------
FROM nginx:1.27-alpine AS runtime

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy nginx config for SPA
COPY infrastructure/nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]