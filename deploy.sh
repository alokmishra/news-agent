#!/bin/bash
# deploy.sh

# Build and push to AWS ECR
docker build -t news-agent .
docker tag news-agent:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/news-agent:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/news-agent:latest

# Deploy to EC2
ssh -i "your-key.pem" ubuntu@your-ec2-instance << 'EOF'
    cd /home/ubuntu/news-agent
    docker pull 123456789.dkr.ecr.us-east-1.amazonaws.com/news-agent:latest
    docker-compose down
    docker-compose up -d
EOF
