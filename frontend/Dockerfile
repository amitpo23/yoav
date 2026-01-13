# Multi-stage build for production

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps to avoid conflicts
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build for production
RUN SKIP_PREFLIGHT_CHECK=true CI=false npm run build

# Stage 2: Production server (nginx)
FROM nginx:alpine

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy build from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy redirects file if exists
COPY --from=builder /app/public/_redirects /usr/share/nginx/html/_redirects 2>/dev/null || true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
