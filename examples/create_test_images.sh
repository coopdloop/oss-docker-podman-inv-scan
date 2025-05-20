#!/bin/bash
# create_test_images.sh
# Script to create test Docker and Podman images for use with Container Inventory tool

# Create necessary files
echo "Creating files..."

# Create a directory for our test files
mkdir -p test_images
cd test_images

# Create server.js
cat > server.js << 'EOF'
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
EOF

# Create Dockerfiles
cat > Dockerfile.alpine << 'EOF'
FROM alpine:3.14
RUN apk add --no-cache python3 curl
WORKDIR /app
COPY . /app
CMD ["sh", "-c", "echo 'Alpine test container running'; sleep infinity"]
EOF

cat > Dockerfile.ubuntu << 'EOF'
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    python3 \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
CMD ["bash", "-c", "echo 'Ubuntu test container running'; sleep infinity"]
EOF

cat > Dockerfile.node << 'EOF'
FROM node:14.17.0
WORKDIR /app
COPY package.json ./
RUN echo '{\
  "name": "vulnerable-app",\
  "version": "1.0.0",\
  "dependencies": {\
    "express": "4.14.0",\
    "lodash": "4.17.0",\
    "minimist": "0.2.1"\
  }\
}' > package.json
RUN npm install
COPY . .
CMD ["node", "server.js"]
EOF

cat > Dockerfile.multistage << 'EOF'
FROM golang:1.16 AS builder
WORKDIR /app
COPY . .
RUN go mod init example.com/hello && \
    echo 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n}' > main.go && \
    CGO_ENABLED=0 go build -o hello .

FROM debian:10.7
COPY --from=builder /app/hello /usr/local/bin/
RUN apt-get update && apt-get install -y \
    curl \
    libssl1.1 \
    && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/local/bin/hello"]
EOF

# Detect which container engines are available
DOCKER_AVAILABLE=false
PODMAN_AVAILABLE=false

if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
    echo "Docker detected"
fi

if command -v podman &> /dev/null; then
    PODMAN_AVAILABLE=true
    echo "Podman detected"
fi

# Build images
echo "Building test images..."

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Building Docker images..."
    docker build -t test-alpine:latest -f Dockerfile.alpine .
    docker build -t test-ubuntu:latest -f Dockerfile.ubuntu .
    docker build -t test-node:vulnerable -f Dockerfile.node .
    docker build -t test-multistage:latest -f Dockerfile.multistage .
fi

if [ "$PODMAN_AVAILABLE" = true ]; then
    echo "Building Podman images..."
    podman build -t test-alpine:latest -f Dockerfile.alpine .
    podman build -t test-ubuntu:latest -f Dockerfile.ubuntu .
    podman build -t test-node:vulnerable -f Dockerfile.node .
    podman build -t test-multistage:latest -f Dockerfile.multistage .
fi

# Return to original directory
cd ..

echo "Test images created successfully!"
echo
echo "You can now run the container inventory tool to view and scan these images:"
echo "container-inventory --scan"
