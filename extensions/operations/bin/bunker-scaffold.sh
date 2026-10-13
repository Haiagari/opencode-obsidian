#!/bin/bash
# bunker-scaffold.sh — Operationalize Bunker Blueprints v2026
# Usage: ./bin/bunker-scaffold.sh [project-name] --blueprint [go|react]

set -e

PROJECT_NAME=$1
BLUEPRINT=$3

if [ -z "$PROJECT_NAME" ] || [ -z "$BLUEPRINT" ]; then
    echo "Usage: ./bin/bunker-scaffold.sh [project-name] --blueprint [go|react]"
    exit 1
fi

echo "🚀 Scaffolding Bunker Project: $PROJECT_NAME (Blueprint: $BLUEPRINT)"

# --- HELPER: Create directory and keep it ---
mk_keep() {
    mkdir -p "$1"
    touch "$1/.gitkeep"
}

# --- GO BLUEPRINT ---
scaffold_go() {
    echo "🏗️ Building Go API Structure..."
    mk_keep "$PROJECT_NAME/cmd/api"
    mk_keep "$PROJECT_NAME/internal/domain"
    mk_keep "$PROJECT_NAME/internal/service"
    mk_keep "$PROJECT_NAME/internal/repository"
    mk_keep "$PROJECT_NAME/internal/handler"
    mk_keep "$PROJECT_NAME/internal/config"
    mk_keep "$PROJECT_NAME/pkg"
    mk_keep "$PROJECT_NAME/api"
    mk_keep "$PROJECT_NAME/scripts"
    mk_keep "$PROJECT_NAME/deployments"

    # main.go template
    cat <<EOF > "$PROJECT_NAME/cmd/api/main.go"
package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	slog.Info("Starting Bunker API: $PROJECT_NAME", "version", "0.1.0")

	// TODO: Initialize repository and services

	<-ctx.Done()
	slog.Info("Shutting down gracefully")
}
EOF

    # Dockerfile template
    cat <<EOF > "$PROJECT_NAME/Dockerfile"
# Stage 1: Build
FROM golang:1.26-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./cmd/api

# Stage 2: Final
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
RUN adduser -D appuser
USER appuser
CMD ["./main"]
EOF

    # Makefile template
    cat <<EOF > "$PROJECT_NAME/Makefile"
build:
	go build -o bin/main ./cmd/api

run:
	go run ./cmd/api/main.go

test:
	go test -v ./...

docker-build:
	docker build -t $PROJECT_NAME .
EOF

    echo "✅ Go API scaffolded. Next: cd $PROJECT_NAME && go mod init $PROJECT_NAME"
}

# --- REACT BLUEPRINT ---
scaffold_react() {
    echo "🏗️ Building React Web Structure (Next.js 15+)..."
    mk_keep "$PROJECT_NAME/app/(auth)"
    mk_keep "$PROJECT_NAME/app/(dashboard)"
    mk_keep "$PROJECT_NAME/app/api"
    mk_keep "$PROJECT_NAME/components/ui"
    mk_keep "$PROJECT_NAME/components/forms"
    mk_keep "$PROJECT_NAME/components/layouts"
    mk_keep "$PROJECT_NAME/lib/api"
    mk_keep "$PROJECT_NAME/lib/utils"
    mk_keep "$PROJECT_NAME/lib/hooks"
    mk_keep "$PROJECT_NAME/types"
    mk_keep "$PROJECT_NAME/styles"

    # globals.css (Tailwind 4)
    cat <<EOF > "$PROJECT_NAME/styles/globals.css"
@import "tailwindcss";

@theme {
  --color-brand-primary: oklch(0.6 0.2 250);
  --font-display: "Satoshi", "sans-serif";
}

:root {
  background: oklch(0.1 0 0); /* Bunker Dark */
  color: white;
}
EOF

    # layout.tsx
    cat <<EOF > "$PROJECT_NAME/app/layout.tsx"
import "../styles/globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased font-display bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
EOF

    # Dockerfile
    cat <<EOF > "$PROJECT_NAME/Dockerfile"
FROM node:22-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
EOF

    echo "✅ React Web scaffolded. Next: cd $PROJECT_NAME && npm init -y"
}

# --- EXECUTION ---
case "$BLUEPRINT" in
    go)
        scaffold_go
        ;;
    react)
        scaffold_react
        ;;
    *)
        echo "Error: Unknown blueprint '$BLUEPRINT'. Supported: go, react"
        exit 1
        ;;
esac

# Create Bunker Audit Checklist
cat <<EOF > "$PROJECT_NAME/BUNKER-CHECKLIST.md"
# 🛡️ Bunker Security & Quality Checklist

- [ ] Secrets: No keys in code (Scan with gitleaks).
- [ ] Provenance: SLSA Level 1 artifacts generated.
- [ ] Health: Score above 80 (Run react-doctor or linter).
- [ ] ADR: Major decisions documented in docs/adr/.
- [ ] Observability: slog/OTel configured.
EOF

echo "✨ Project '$PROJECT_NAME' is ready for action inside the Bunker."
