FROM golang:1.25-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY go.mod go.sum ./
RUN go mod download

COPY . .

EXPOSE 8081

CMD ["go", "run", "llm_server.go"]
