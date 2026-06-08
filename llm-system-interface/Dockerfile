FROM golang:1.25-alpine AS builder

# This tells Go: "If a dependency needs 1.25, go ahead and download 1.25 automatically"
ENV GOTOOLCHAIN=auto

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o llm_server llm_server.go

# --- final stage: only the binary, no Go toolchain ---
FROM alpine:3.21

RUN apk add --no-cache curl ca-certificates

COPY --from=builder /app/llm_server /llm_server

EXPOSE 8081

CMD ["/llm_server"]
