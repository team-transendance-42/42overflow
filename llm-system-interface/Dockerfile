FROM golang:1.25-alpine

# This tells Go: "If a dependency needs 1.25, go ahead and download 1.25 automatically"
ENV GOTOOLCHAIN=auto

WORKDIR /app

# We keep curl for your healthcheck
RUN apk add --no-cache curl

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Step 1: Actually build the binary
RUN go build -o llm_server llm_server.go

EXPOSE 8081

# Step 2: Run the compiled binary instead of "go run"
CMD ["./llm_server"]
