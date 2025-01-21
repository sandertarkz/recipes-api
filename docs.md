# **Comprehensive Guide: Setting Up AWS RDS PostgreSQL with EC2, GitHub Actions CI/CD, Docker, and Alembic**

## **1. Creating and Configuring the AWS RDS PostgreSQL Database**

### **a. Launching the RDS PostgreSQL Instance**

1. **Navigate to the AWS RDS Console:**
   - Access the [AWS RDS Console](https://console.aws.amazon.com/rds/).

2. **Create a New Database:**
   - Click on **"Create database"**.
   - Choose **"Standard Create"**.
   - Select **"PostgreSQL"** as the engine type.

3. **Configure Database Settings:**
   - **DB Instance Identifier:** `expelliarmus`.
   - **Master Username:** `postgres`.
   - **Master Password:** Securely set (e.g., `pwd12345`).
   - **DB Instance Class:** Choose based on requirements (e.g., `db.t3.micro` for testing).

4. **Networking and Security:**
   - **Virtual Private Cloud (VPC):** Select the appropriate VPC.
   - **Public Accessibility:** Set to **"Yes"** if connecting from outside the VPC.
   - **VPC Security Groups:** Create or select a security group to control access.

5. **Additional Configuration:**
   - **Initial Database Name:** `postgres`.
   - **Storage:** Configure as needed.
   - **Backup and Maintenance:** Enable automated backups and set maintenance windows.

6. **Launch the Instance:**
   - Review settings and click **"Create database"**.
   - Wait for the status to become **"Available"**.

### **b. Configuring Security Groups and Network ACLs**

1. **Security Groups:**
   - **Inbound Rules:** Allow PostgreSQL traffic (port `5432`) from specific IPs (e.g., your local machine's IP or EC2 instance's security group).
   - **Outbound Rules:** Ensure outbound traffic is allowed to respond to requests.

2. **Network ACLs:**
   - **Inbound and Outbound Rules:** Allow traffic on port `5432` for your specific IPs.
   - **Order of Rules:** Ensure that allow rules have higher priority than any deny rules.

3. **Testing Connectivity:**
   - Use tools like `telnet` or `nc` to verify connectivity to the RDS endpoint on port `5432`.

## **2. Connecting to the RDS PostgreSQL Instance**

### **a. Using `psql` from Local Machine**

1. **Install PostgreSQL Client:**
   - Install `psql` if not already installed.
     ```bash
     sudo apt-get install postgresql-client
     ```

2. **Connect to RDS:**
   ```bash
   psql --host=db_host --port=5432 --username=postgres --dbname=postgres --password
   ```

3. **Enter Password:**
   - Provide the master password (`pwd12345`) when prompted.

### **b. Using pgAdmin**

1. **Install pgAdmin:**
   - Download and install [pgAdmin](https://www.pgadmin.org/).

2. **Configure Connection:**
   - Add a new server with the following details:
     - **Name:** `expelliarmus`
     - **Host:** `db_host`
     - **Port:** `5432`
     - **Username:** `postgres`
     - **Password:** `pwd12345`

3. **Connect and Manage Database:**
   - Access and manage your PostgreSQL databases through the pgAdmin interface.

## **3. Setting Up the EC2 Instance for the API**

### **a. Launching the EC2 Instance**

1. **Navigate to the AWS EC2 Console:**
   - Access the [AWS EC2 Console](https://console.aws.amazon.com/ec2/).

2. **Launch a New Instance:**
   - Choose an appropriate AMI (e.g., Ubuntu Server 20.04 LTS).
   - **Instance Type:** Select based on requirements (e.g., `t3.micro`).

3. **Configure Instance Details:**
   - **VPC and Subnet:** Ensure it aligns with the RDS instance's VPC.
   - **Public IP:** Assign if needing external access.

4. **Add Storage:**
   - Configure storage as needed.

5. **Configure Security Group:**
   - **Inbound Rules:**
     - SSH (port `22`) from your IP.
     - HTTP (port `80`) or HTTPS (port `443`) if hosting a web service.
   - **Outbound Rules:** Allow necessary outbound traffic.

6. **Review and Launch:**
   - Generate or use an existing SSH key pair.
   - Launch the instance and download the key pair (`your_key.pem`).

### **b. Initial EC2 Configuration**

1. **SSH into EC2:**
   ```bash
   ssh -i "your_key.pem" ubuntu@your_ec2_public_dns
   ```

2. **Update and Install Dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose git
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Clone Your API Repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

## **4. Deploying the API to EC2 Using Docker and Docker Compose**

### **a. Docker and Docker Compose Setup**

1. **Create a `Dockerfile`:**
   ```dockerfile
   FROM python:3.9-slim

   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --upgrade pip
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create a `docker-compose.yml`:**
   ```yaml
   version: '3.8'

   services:
     web:
       build: .
       container_name: recipes_api
       env_file:
         - .env
       environment:
         - DB_HOST=${DB_HOST}
         - DB_USER=${DB_USER}
         - DB_NAME=${DB_NAME}
         - DB_PASSWORD=${DB_PASSWORD}
       ports:
         - "8000:8000"
       restart: always
       depends_on:
         - db

     db:
       image: postgres:13
       container_name: postgres_db
       environment:
         - POSTGRES_USER=${DB_USER}
         - POSTGRES_PASSWORD=${DB_PASSWORD}
         - POSTGRES_DB=${DB_NAME}
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       ports:
         - "5432:5432"
       restart: always

   volumes:
     postgres_data:
   ```

3. **Create a `.env.example` File:**
   ```env
   DB_HOST=your_db_host
   DB_USER=postgres
   DB_NAME=postgres
   DB_PASSWORD=your_secure_password
   ```

4. **Build and Run Docker Containers:**
   ```bash
   docker-compose up -d --build
   ```

### **b. Verifying Deployment**

1. **Access the API:**
   - Navigate to `http://your_ec2_public_dns:8000/` in your browser.
   - Expect a response like `{"Hello": "World"}`.

2. **Check Running Containers:**
   ```bash
   docker ps
   ```

3. **Inspect Logs:**
   ```bash
   docker logs recipes_api
   ```

## **5. Managing Secrets with GitHub Actions CI/CD**

### **a. Storing Secrets in GitHub**

1. **Navigate to Repository Settings:**
   - Go to your GitHub repository.
   - Click on **"Settings"** > **"Secrets and variables"** > **"Actions"**.

2. **Add Repository Secrets:**
   - `DB_HOST`: `db_host`
   - `DB_USER`: `postgres`
   - `DB_NAME`: `postgres`
   - `DB_PASSWORD`: `pwd12345`
   - `EC2_HOST`: `your_ec2_public_dns`
   - `EC2_USER`: `ubuntu`
   - `EC2_KEY`: *(Content of `your_key.pem`)*

### **b. Configuring GitHub Actions Workflow**

1. **Create a Workflow File (`.github/workflows/deploy.yml`):**
   ```yaml
   name: CI/CD Deployment

   on:
     push:
       branches: [ main ]

   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest

       steps:
         # 1. Checkout the repository
         - name: Checkout Code
           uses: actions/checkout@v3

         # 2. Set Image Tag based on commit SHA (optional)
         - name: Set IMAGE_TAG
           run: echo "IMAGE_TAG=${GITHUB_SHA::7}" >> $GITHUB_ENV

         # 3. Login to Amazon ECR (if using Docker)
         - name: Login to Amazon ECR
           id: login-ecr
           uses: aws-actions/amazon-ecr-login@v1
           with:
             registry: 401657292421.dkr.ecr.us-east-1.amazonaws.com
           env:
             AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
             AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
             AWS_REGION: us-east-1

         # 4. Build, Tag, and Push Docker Image to ECR (if using Docker)
         - name: Build, Tag, and Push Docker Image
           run: |
             docker build -t film-recipes-api:${{ env.IMAGE_TAG }} .
             docker tag film-recipes-api:${{ env.IMAGE_TAG }} 401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api:${{ env.IMAGE_TAG }}
             docker push 401657292421.dkr.ecr.us-east-1.amazonaws.com/film-recipes/api:${{ env.IMAGE_TAG }}

         # 5. Deploy to EC2 via SSH and Update .env File
         - name: Deploy to EC2 and Update .env
           uses: appleboy/ssh-action@v0.1.3
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USER }}
             key: ${{ secrets.EC2_KEY }}
             port: 22
             script: |
               # Navigate to the application directory
               cd /home/ubuntu/app

               # Create or update the .env file with secrets
               echo "DB_HOST=${{ secrets.DB_HOST }}" > .env
               echo "DB_USER=${{ secrets.DB_USER }}" >> .env
               echo "DB_NAME=${{ secrets.DB_NAME }}" >> .env
               echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> .env

               # Pull the latest Docker image
               docker compose pull

               # Restart the Docker containers to apply new environment variables
               docker compose up -d --force-recreate

               # Optional: Remove unused Docker images to save space
               docker image prune -f

         # 6. Run Database Migrations (If Applicable)
         - name: Run Database Migrations
           uses: appleboy/ssh-action@v0.1.3
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USER }}
             key: ${{ secrets.EC2_KEY }}
             port: 22
             script: |
               cd /home/ubuntu/app
               docker compose run web alembic upgrade head
   ```

2. **Workflow Steps Explained:**
   - **Checkout Code:** Retrieves the latest code from the repository.
   - **Set Image Tag:** Generates a unique Docker image tag based on the commit SHA.
   - **Login to Amazon ECR:** Authenticates Docker to push images to AWS ECR.
   - **Build, Tag, and Push Docker Image:** Builds the Docker image, tags it, and pushes it to ECR.
   - **Deploy to EC2 and Update `.env` File:** SSHs into EC2, writes the secrets to the `.env` file, pulls the latest Docker image, and restarts the containers.
   - **Run Database Migrations:** Executes Alembic migrations within the Docker container.

### **c. Best Practices for Secret Management**

- **Exclude `.env` from Version Control:**
  - Add `.env` to `.gitignore` to prevent accidental commits.
    ```gitignore
    # .gitignore
    .env
    ```
  
- **Use `.env.example` for Reference:**
  - Provide a template for developers to set up their local `.env` files.
    ```env
    # .env.example
    DB_HOST=your_db_host
    DB_USER=postgres
    DB_NAME=postgres
    DB_PASSWORD=your_secure_password
    ```

- **Secure SSH Key Management:**
  - Ensure the `EC2_KEY` secret contains the **private SSH key** and is securely stored in GitHub Secrets.
  - Set proper permissions for the SSH key locally.
    ```bash
    chmod 600 your_key.pem
    ```

## **6. Handling Database Migrations with Alembic**

### **a. Ensuring Alembic is Installed in the Docker Image**

1. **Add Alembic to `requirements.txt`:**
   ```plaintext
   fastapi
   uvicorn
   sqlalchemy
   psycopg2-binary
   alembic
   ```

2. **Verify Installation in Dockerfile:**
   - Ensure the `RUN pip install -r requirements.txt` step includes Alembic.

3. **Rebuild Docker Image:**
   ```bash
   docker-compose build
   ```

### **b. Configuring Alembic**

1. **Initialize Alembic (If Not Already Done):**
   ```bash
   alembic init alembic
   ```

2. **Configure `alembic.ini`:**
   - Set the SQLAlchemy URL using environment variables.
     ```ini
     sqlalchemy.url = postgresql://user:password@host/table_name
     ```

3. **Create Migration Scripts:**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

### **c. Resolving Alembic Execution Errors**

- **Error Encountered:**
  ```
  Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: exec: "alembic": executable file not found in $PATH: unknown
  ```
  
- **Solution:**
  - **Ensure Alembic is Installed:** Confirm that Alembic is part of `requirements.txt` and successfully installed in the Docker image.
  - **Verify Alembic in Container's PATH:**
    - SSH into EC2 and access the container.
      ```bash
      docker exec -it recipes_api bash
      ```
    - Run `alembic --version` to verify installation.
  - **Adjust Docker Compose Commands:**
    - Ensure that migration commands reference the correct service and that Alembic is accessible.
    - Example command in GitHub Actions:
      ```bash
      docker compose run web alembic upgrade head
      ```

## **7. Finalizing and Securing the Deployment**

### **a. Securing the `.env` File on EC2**

1. **Set Proper Permissions:**
   ```bash
   sudo chown ubuntu:ubuntu /home/ubuntu/app/.env
   chmod 600 /home/ubuntu/app/.env
   ```

2. **Ensure `.env` is Not in Version Control:**
   - Already handled by adding `.env` to `.gitignore`.

### **b. Monitoring and Maintenance**

1. **Set Up AWS CloudWatch:**
   - Monitor RDS and EC2 metrics.
   - Set up alarms for unusual activities.

2. **Regular Backups:**
   - Ensure RDS automated backups are enabled.
   - Take manual snapshots before significant changes.

3. **Update and Patch Management:**
   - Regularly update Docker images and dependencies.
   - Apply security patches to EC2 instances.

### **c. Implementing a Rollback Strategy**

1. **Use Versioned Docker Images:**
   - Tag Docker images with commit SHAs or version numbers.
   - Maintain previous stable versions in ECR for quick rollback.

2. **Automate Rollbacks in GitHub Actions:**
   - Implement steps to revert to the last stable Docker image if deployments fail.

### **d. Enhancing Security with IAM Roles**

1. **Assign IAM Roles to EC2:**
   - Create an IAM role with least privilege permissions.
   - Attach the role to the EC2 instance for accessing AWS services like ECR and Secrets Manager.

2. **Avoid Using Static AWS Credentials:**
   - Utilize IAM roles instead of embedding AWS access keys in GitHub Secrets.

### **e. Utilizing AWS Secrets Manager (Optional for Enhanced Security)**

1. **Store Secrets in AWS Secrets Manager:**
   - Navigate to [AWS Secrets Manager](https://console.aws.amazon.com/secretsmanager/).
   - Store `DB_HOST`, `DB_USER`, `DB_NAME`, and `DB_PASSWORD` as secrets.

2. **Modify Application to Retrieve Secrets:**
   - Update application code to fetch secrets from Secrets Manager instead of `.env` files.
   - Example in Python:
     ```python
     import boto3
     import json

     def get_db_credentials(secret_name, region_name='us-east-1'):
         client = boto3.client('secretsmanager', region_name=region_name)
         get_secret_value_response = client.get_secret_value(SecretId=secret_name)
         secret = get_secret_value_response['SecretString']
         return json.loads(secret)
     ```

3. **Update GitHub Actions Workflow:**
   - Remove writing to `.env` and allow the application to fetch secrets directly.

## **8. Troubleshooting Common Issues**

### **a. Alembic Not Found in Container**

- **Ensure Alembic is Installed:** Verify `alembic` is in `requirements.txt` and installed during Docker build.
- **Check PATH:** Confirm `alembic` is in the container's `$PATH` by running `alembic --version` inside the container.

### **b. Database Connection Errors**

- **Verify `.env` Variables:** Ensure `DB_HOST`, `DB_USER`, `DB_NAME`, and `DB_PASSWORD` are correctly set.
- **Check Security Groups and ACLs:** Ensure EC2 can communicate with RDS on port `5432`.
- **Test Connectivity from EC2:**
  ```bash
  psql --host=db_host --port=5432 --username=postgres --dbname=postgres
  ```

### **c. SSH Connection Issues in GitHub Actions**

- **Validate SSH Keys:** Ensure the private key in `EC2_KEY` matches the public key on EC2.
- **Check Security Group Rules:** Confirm SSH access is allowed from GitHub Actions runners.
- **Verify EC2 User:** Ensure the `EC2_USER` matches the user configured on EC2 (e.g., `ubuntu`).

### **d. Deployment Failures**

- **Review GitHub Actions Logs:** Identify at which step the failure occurs.
- **Check Docker Compose Configuration:** Ensure services are correctly defined and dependencies are met.
- **Monitor EC2 Instance Resources:** Ensure sufficient CPU, memory, and disk space.

## **9. Summary of Key Steps**

1. **Launch AWS RDS PostgreSQL:**
   - Create RDS instance with appropriate configurations.
   - Configure security groups and network ACLs.

2. **Connect to RDS:**
   - Use `psql` or pgAdmin to verify connectivity.

3. **Set Up EC2 Instance:**
   - Launch and configure EC2 with necessary security and software.

4. **Deploy API Using Docker:**
   - Create `Dockerfile` and `docker-compose.yml`.
   - Build and run Docker containers on EC2.

5. **Manage Secrets with GitHub Actions:**
   - Store secrets in GitHub repository settings.
   - Configure GitHub Actions workflow to deploy and update `.env` on EC2.

6. **Handle Database Migrations with Alembic:**
   - Ensure Alembic is installed and configured in the Docker image.
   - Automate migration steps in CI/CD pipeline.

7. **Secure and Maintain Deployment:**
   - Exclude `.env` from version control.
   - Set proper permissions and monitor deployments.

8. **Troubleshoot and Optimize:**
   - Address common errors and ensure smooth operation.

---

## **Conclusion**

By following this structured approach, you successfully set up an AWS RDS PostgreSQL database, connected it to an API hosted on an EC2 instance, managed secrets securely using GitHub Actions CI/CD, deployed your application with Docker, and handled database migrations with Alembic. This comprehensive setup ensures scalability, security, and maintainability for your application.

**Best Practices Highlighted:**

- **Security First:** Always manage secrets securely using tools like GitHub Secrets, IAM roles, and AWS Secrets Manager.
- **Automation:** Utilize CI/CD pipelines to automate deployments, ensuring consistency and reducing manual errors.
- **Monitoring and Maintenance:** Implement monitoring tools and regular maintenance routines to ensure the health and security of your infrastructure.
- **Documentation:** Maintain clear and detailed documentation to facilitate team collaboration and future onboarding.

If you encounter any further challenges or need more detailed assistance on specific steps, feel free to reach out!