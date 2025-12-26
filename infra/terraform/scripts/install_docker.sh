#!/bin/bash
dnf update -y
dnf install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

docker run -d \
  --name aether-agent \
  --pid host \
  --restart always \
  banemen/aether-monitor:latest