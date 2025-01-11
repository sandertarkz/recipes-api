# Create RDS database

---

### Steps to Set Up and Configure RDS Database with the Application

1. **Create RDS Database**
   - Log in to AWS and create an RDS instance (e.g., PostgreSQL or MySQL).
   - Configure database settings:
     - Choose engine (e.g., PostgreSQL).
     - Specify username (`DB_USER`) and password (`DB_PASSWORD`).
     - Define the database name (`DB_NAME`).
   - Note the endpoint (`DB_HOST`) provided after creation.

2. **Configure Security Group**
   - Allow inbound traffic for the database port (e.g., 5432 for PostgreSQL).
   - Restrict access to trusted IPs or link the RDS instance to your application server’s security group.

3. **Store Database Credentials in GitHub Secrets**
   - Navigate to **GitHub → Settings → Secrets and Variables → Actions**.
   - Add the following secrets for secure access:
     - `DB_HOST`
     - `DB_USER`
     - `DB_PASSWORD`
     - `DB_NAME`

4. **Update `deploy.yml` for CI/CD**
   - Modify the CI/CD pipeline to inject database credentials as environment variables:
     ```yaml
     env:
       DB_HOST: ${{ secrets.DB_HOST }}
       DB_USER: ${{ secrets.DB_USER }}
       DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
       DB_NAME: ${{ secrets.DB_NAME }}
     ```
   - Ensure the `deploy.yml` file passes these secrets to the deployment process.

5. **Create or Update `.env` File for Local Development**
   - Create a `.env` file in your project directory with the following contents:
     ```env
     DB_HOST=your-rds-endpoint.amazonaws.com
     DB_USER=your-database-user
     DB_PASSWORD=your-database-password
     DB_NAME=your-database-name
     ```
   - Add `.env` to `.gitignore` to prevent accidental commits.

6. **Update `docker-compose.yml`**
   - Modify `docker-compose.yml` to read environment variables:
     ```yaml
     services:
       app:
         build:
           context: .
         ports:
           - "3000:3000"
         environment:
           - DB_HOST=${DB_HOST}
           - DB_USER=${DB_USER}
           - DB_PASSWORD=${DB_PASSWORD}
           - DB_NAME=${DB_NAME}
     ```

---

### Outcome
- A secure RDS database is configured and integrated with your application.
- Credentials are safely stored in GitHub Secrets and `.env`.
- The application is ready for deployment using `docker-compose` with CI/CD.

Let me know if you’d like this polished further! 🚀