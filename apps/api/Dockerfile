FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json ./
COPY turbo.json ./
COPY tsconfig.json ./

# Copy workspace package.json files
COPY apps/api/package.json ./apps/api/package.json
COPY packages/core/package.json ./packages/core/package.json
COPY packages/db/package.json ./packages/db/package.json

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build API and dependencies
RUN npm run build --workspace=@ai-mental-health-coach/core
RUN npm run build --workspace=@ai-mental-health-coach/db
RUN npm run build --workspace=@ai-mental-health-coach/api

# Remove development dependencies
# RUN npm prune --production

FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=production

# Copy package files and built code
COPY --from=builder /app/package.json ./
COPY --from=builder /app/package-lock.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/apps/api/dist ./apps/api/dist
COPY --from=builder /app/apps/api/package.json ./apps/api/package.json
COPY --from=builder /app/packages/core/dist ./packages/core/dist
COPY --from=builder /app/packages/core/package.json ./packages/core/package.json
COPY --from=builder /app/packages/db/dist ./packages/db/dist
COPY --from=builder /app/packages/db/package.json ./packages/db/package.json
COPY --from=builder /app/packages/db/prisma ./packages/db/prisma

# Generate Prisma client
RUN cd packages/db && npx prisma generate

# Expose port
EXPOSE 3001

# Set working directory to API folder
WORKDIR /app/apps/api

# Start the API server
CMD ["node", "dist/index.js"] 