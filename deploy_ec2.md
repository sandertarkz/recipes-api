# Deploying FastAPI to AWS EC2 with Docker

## Table of Contents

- [Deploying FastAPI to AWS EC2 with Docker](#deploying-fastapi-to-aws-ec2-with-docker)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Deployment Guide](#step-by-step-deployment-guide)
    - [1. Setup AWS Elastic Container Registry (ECR)](#1-setup-aws-elastic-container-registry-ecr)
    - [2. Configure IAM Role for EC2](#2-configure-iam-role-for-ec2)
    - [3. Launch and Configure EC2 Instance](#3-launch-and-configure-ec2-instance)
    - [4. Install Docker and Docker Compose on EC2](#4-install-docker-and-docker-compose-on-ec2)
    - [5. Prepare FastAPI Application](#5-prepare-fastapi-application)
    - [6. Configure Docker Compose](#6-configure-docker-compose)
    - [7. Set Up GitHub Actions for CI/CD](#7-set-up-github-actions-for-cicd)
    - [8. Deploy FastAPI Application](#8-deploy-fastapi-application)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)
    - [Verification Steps](#verification-steps)
  - [Best Practices](#best-practices)
  - [Conclusion](#conclusion)

---

## Introduction

Deploying a FastAPI application to an AWS EC2 instance using Docker and Docker Compose allows for scalable, maintainable, and consistent deployments. This guide walks you through setting up the necessary AWS services, configuring your EC2 instance, and automating deployments using GitHub Actions.

## Prerequisites

Before proceeding, ensure you have the following:

- **AWS Account**: Access to AWS services.
- **EC2 Instance**: An EC2 instance running a Linux distribution (e.g., Ubuntu).
- **AWS CLI**: Installed and configured on your local machine.
- **Docker**: Installed on your EC2 instance.
- **Docker Compose**: Installed on your EC2 instance.
- **GitHub Repository**: Your FastAPI application's code hosted on GitHub.
- **GitHub Actions**: Enabled for your repository for CI/CD workflows.

## Step-by-Step Deployment Guide

### 1. Setup AWS Elastic Container Registry (ECR)

**AWS ECR** is a fully managed Docker container registry that makes it easy to store, manage, and deploy Docker container images.

1. **Create an ECR Repository**:
    - Navigate to the [AWS ECR Console](https://console.aws.amazon.com/ecr/).
    - Click on **Create repository**.
    - **Repository Name**: `film-recipes/api`.
    - Configure other settings as needed.
    - Click **Create repository**.

2. **Note Repository URI**:
    - After creation, note the repository URI: `401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api`.

### 2. Configure IAM Role for EC2

Assigning an IAM role to your EC2 instance allows it to interact with AWS services securely.

1. **Create IAM Role**:
    - Go to the [AWS IAM Console](https://console.aws.amazon.com/iam/).
    - Click on **Roles** > **Create role**.
    - **Trusted Entity**: Select **AWS service** > **EC2**.
    - Click **Next: Permissions**.

2. **Attach ECR Policy**:
    - **Option 1**: Attach the managed policy `AmazonEC2ContainerRegistryFullAccess`.
    - **Option 2**: Create a custom policy with the following permissions:
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": [
              "ecr:GetAuthorizationToken",
              "ecr:BatchCheckLayerAvailability",
              "ecr:BatchGetImage",
              "ecr:GetDownloadUrlForLayer"
            ],
            "Resource": "*"
          }
        ]
      }
      ```
    - Name the role, e.g., `EC2-ECR-Access-Role`, and create it.

3. **Attach IAM Role to EC2 Instance**:
    - Navigate to the [AWS EC2 Console](https://console.aws.amazon.com/ec2/).
    - Select your EC2 instance.
    - Click **Actions** > **Security** > **Modify IAM role**.
    - Choose `EC2-ECR-Access-Role` and apply.

### 3. Launch and Configure EC2 Instance

1. **Launch EC2 Instance**:
    - Choose an appropriate AMI (e.g., Ubuntu Server 20.04 LTS).
    - Select an instance type (e.g., `t2.micro` for testing).
    - Assign the IAM role `EC2-ECR-Access-Role`.
    - Configure security groups to allow SSH (port 22), HTTP (port 80), and any other necessary ports.
    - Launch the instance and download the `.pem` key pair.

2. **Connect to EC2 Instance**:
    ```bash
    ssh -i "your_key.pem" ubuntu@your_ec2_public_dns
    ```

### 4. Install Docker and Docker Compose on EC2

1. **Update Package Lists**:
    ```bash
    sudo apt-get update
    ```

2. **Install Docker**:
    ```bash
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    ```

    - **Verify Docker Installation**:
      ```bash
      docker --version
      ```

3. **Install Docker Compose v2**:
    - **Download Docker Compose v2**:
      ```bash
      mkdir -p ~/.docker/cli-plugins/
      curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
      ```
    - **Apply Executable Permissions**:
      ```bash
      chmod +x ~/.docker/cli-plugins/docker-compose
      ```
    - **Add to PATH**:
      ```bash
      echo 'export PATH="$HOME/.docker/cli-plugins:$PATH"' >> ~/.bashrc
      source ~/.bashrc
      ```
    - **Verify Installation**:
      ```bash
      docker compose version
      ```

### 5. Prepare FastAPI Application

1. **Ensure Your FastAPI Application Has a Dockerfile**:
    - Example `Dockerfile`:
      ```dockerfile
      FROM python:3.9-slim

      WORKDIR /app

      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt

      COPY . .

      CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
      ```

2. **Ensure `requirements.txt` Includes Necessary Dependencies**:
    - Example `requirements.txt`:
      ```
      fastapi
      uvicorn
      ```

### 6. Configure Docker Compose

1. **Create `docker-compose.yml`**:
    - On EC2 instance, navigate to your project directory:
      ```bash
      mkdir -p ~/app
      cd ~/app
      ```
    - Create `docker-compose.yml`:
      ```yaml
      version: '3.8'

      services:
        web:
          image: 401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api:latest
          container_name: recipes_api
          environment:
            ENV: production
          ports:
            - "8000:8000"
          restart: always
      ```

2. **Ensure `.vscode` is Ignored in `.gitignore`**:
    ```gitignore
    .vscode/
    ```

### 7. Set Up GitHub Actions for CI/CD

1. **Configure GitHub Secrets**:
    - In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions**.
    - Add the following secrets:
        - `AWS_ACCESS_KEY_ID`
        - `AWS_SECRET_ACCESS_KEY`
        - `EC2_HOST` (EC2 public DNS or IP)
        - `EC2_KEY` (Private SSH key content)

2. **Create GitHub Actions Workflow (`.github/workflows/deploy.yml`)**:
    ```yaml
    name: CI/CD

    on:
      push:
        branches: [ main ]

    jobs:
      build-and-deploy:
        runs-on: ubuntu-latest

        steps:
          # 1. Checkout the repository
          - name: Checkout
            uses: actions/checkout@v2

          # 2. Set IMAGE_TAG based on commit SHA
          - name: Set IMAGE_TAG
            run: echo "IMAGE_TAG=${GITHUB_SHA::7}" >> $GITHUB_ENV

          # 3. Log in to Amazon ECR using the official GitHub Action
          - name: Log in to Amazon ECR
            uses: aws-actions/amazon-ecr-login@v1
            with:
              registry: 401657292421.dkr.ecr.us-east-1.amazonaws.com
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_REGION: us-east-1

          # 4. Build, tag, and push the Docker image to ECR
          - name: Build, Tag, and Push Docker Image
            run: |
              # Build the Docker image without cache to ensure all changes are included
              docker build --no-cache -t film-recipes-api:${{ env.IMAGE_TAG }} .

              # Tag the Docker image with the ECR repository URI and commit SHA tag
              docker tag film-recipes-api:${{ env.IMAGE_TAG }} 401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api:${{ env.IMAGE_TAG }}

              # Push the Docker image to ECR
              docker push 401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api:${{ env.IMAGE_TAG }}

          # 5. Deploy to EC2 via SSH
          - name: Deploy to EC2
            uses: appleboy/ssh-action@master
            with:
              host: ${{ secrets.EC2_HOST }}
              username: ubuntu
              key: ${{ secrets.EC2_KEY }}
              script: |
                cd /home/ubuntu/app

                # Log in to ECR on EC2 instance using IAM role credentials
                aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 401657292421.dkr.ecr.us-east-1.amazonaws.com

                # Update docker-compose.yml with the new IMAGE_TAG
                sed -i "s/latest/${{ env.IMAGE_TAG }}/g" docker-compose.yml

                # Pull the latest image from ECR
                docker compose pull

                # Restart the containers with the updated image
                docker compose up -d --force-recreate

                # Optional: Remove unused images to save space
                docker image prune -f
    ```

    **Notes**:
    - **Image Tagging**: Using commit SHA ensures each image is uniquely identifiable.
    - **`sed` Command**: Updates `docker-compose.yml` to use the new image tag.

### 8. Deploy FastAPI Application

1. **Push Changes to GitHub**:
    ```bash
    git add .
    git commit -m "Configure deployment workflow"
    git push origin main
    ```

2. **Monitor GitHub Actions**:
    - Navigate to the **Actions** tab in your GitHub repository.
    - Monitor the `CI/CD` workflow to ensure each step completes successfully.

3. **Verify Deployment on EC2**:
    - SSH into your EC2 instance:
      ```bash
      ssh -i "your_key.pem" ubuntu@your_ec2_public_dns
      ```
    - **Check Running Containers**:
      ```bash
      docker compose ps
      ```
    - **Access the Application**:
      - Navigate to `http://your_ec2_public_dns:8000` to verify the FastAPI application is running.

## Troubleshooting

### Common Issues

1. **ECR Authentication Errors**:
    - **Error**:
      ```
      Error response from daemon: Head "https://401657292421.dkr.ecr.us-east-1.amazonaws.com/v2/film-recipes/api/manifests/latest": no basic auth credentials
      ```
    - **Solution**:
        - Ensure the EC2 IAM role has necessary ECR permissions.
        - Verify Docker is authenticated with ECR using AWS CLI.
        - Confirm `docker-compose.yml` references the correct image URI and tag.

2. **`ContainerConfig` KeyError**:
    - **Error**:
      ```
      ERROR: for recipes_api  'ContainerConfig'
      ERROR: for web  'ContainerConfig'
      ```
    - **Solution**:
        - Upgrade Docker Compose to the latest version.
        - Ensure `docker-compose.yml` uses the `image` directive instead of `build`.
        - Validate Docker image integrity and compatibility.
        - Check for syntax errors in `docker-compose.yml`.

3. **Docker Compose Version Issues**:
    - **Solution**:
        - Upgrade to Docker Compose v2.
        - Remove any existing Docker Compose v1 installations.
        - Use Docker Compose as a Docker CLI plugin.

### Verification Steps

1. **Validate `docker-compose.yml`**:
    ```bash
    docker compose config
    ```
    - Fix any syntax or configuration errors.

2. **Manual Deployment**:
    - SSH into EC2.
    - Authenticate Docker with ECR:
      ```bash
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 401657292421.dkr.ecr.us-east-1.amazonaws.com
      ```
    - Pull and run the Docker image:
      ```bash
      docker compose pull
      docker compose up -d --force-recreate
      ```
    - Check container status:
      ```bash
      docker compose ps
      ```

## Best Practices

1. **Use Image Versioning**:
    - Avoid using the `latest` tag. Use specific tags (e.g., commit SHA) for better traceability and rollback capabilities.

2. **Secure SSH Access**:
    - Use strong SSH keys.
    - Limit SSH access to trusted IP addresses.
    - Rotate SSH keys regularly.

3. **Implement Monitoring and Logging**:
    - Use AWS CloudWatch for monitoring EC2 instances.
    - Centralize Docker logs for easier debugging.

4. **Automate Database Migrations**:
    - Integrate migration commands in the deployment script to ensure database schema consistency.

5. **Leverage Docker Health Checks**:
    - Implement health checks in `docker-compose.yml` to monitor container health.

6. **Manage Environment Variables Securely**:
    - Use GitHub Secrets for sensitive information.
    - Consider using AWS Secrets Manager for enhanced security.

## Conclusion

Deploying a FastAPI application to AWS EC2 using Docker and Docker Compose provides a scalable and maintainable solution. By following this guide, you set up a robust CI/CD pipeline using GitHub Actions, ensuring that your application is consistently built, tested, and deployed. Adhering to best practices enhances security, reliability, and efficiency in your deployment process.

For any further assistance or advanced configurations, consider consulting AWS documentation or seeking support from the community.
