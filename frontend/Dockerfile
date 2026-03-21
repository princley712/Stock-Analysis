# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# Set build-time env for API URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# Production stage
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Standalone mode only needs these files
# Create public directory if missing to avoid COPY failure
RUN mkdir -p public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
# Copy public folder only if it exists in the builder
RUN if [ -d /app/public ]; then cp -r /app/public/* ./public/ || true; fi

EXPOSE 3000

# Next.js standalone server entry point
CMD ["node", "server.js"]
