FROM node:22-alpine AS builder

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
COPY .env.production .env.production

RUN pnpm install
COPY . .
RUN pnpm run build
RUN pnpm prune --prod

FROM node:22-alpine

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY .env.production .env.production
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY package.json .

EXPOSE 3000
ENV NODE_ENV=production

CMD ["node", "build"]
