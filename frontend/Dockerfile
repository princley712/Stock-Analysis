# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Build Next.js
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built assets
COPY --from=builder /app/.next/static ./.next/static

# Expose port
EXPOSE 3000

# Start server
CMD ["npm", "start"]
