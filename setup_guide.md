# Naryn's Culture Website Setup Guide

This document provides detailed instructions for setting up the Naryn's Culture website backend from scratch. Follow these steps to get your development environment running.

## Prerequisites

- Python 3.9+ installed
- PostgreSQL 12+ installed
- Git installed
- Basic knowledge of Django and REST APIs

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd naryns-space
```

## Step 2: Set Up Python Environment

### Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Set Up the Environment File

Create a `.env` file in the project root by copying `.env.example`:

```bash
cp .env.example .env
```

### Configure Environment Variables

Open the `.env` file and update the following variables:

#### Core Settings
```
SECRET_KEY=<generate-a-unique-secret-key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
BASE_URL=http://localhost:8000
```

To generate a secret key, you can use Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

#### Database Settings
```
DATABASE_URL=postgres://username:password@localhost:5432/naryns_space
```

Replace `username` and `password` with your PostgreSQL credentials.

#### Email Settings
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=naryns.space@example.com
```

For Gmail, you'll need to create an App Password if you have 2FA enabled.

#### Frontend URL
```
FRONTEND_URL=http://localhost:3000
```

#### OAuth Settings (if you're using social authentication)
```
GOOGLE_OAUTH2_KEY=your-google-oauth-key
GOOGLE_OAUTH2_SECRET=your-google-oauth-secret
FACEBOOK_KEY=your-facebook-app-key
FACEBOOK_SECRET=your-facebook-app-secret
```

#### CORS Settings
```
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Step 4: Set Up PostgreSQL Database

### Create a PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create a new database
CREATE DATABASE naryns_space;

# Verify the database was created
\list

# Exit PostgreSQL
\q
```

## Step 5: Apply Migrations

Initialize the database schema:

```bash
python manage.py migrate
```

## Step 6: Create a Superuser

Create an admin account:

```bash
python manage.py createsuperuser
```

Enter an email address, first name, last name, and password when prompted.

## Step 7: Create Translation Files (Optional)

If you need to support multiple languages:

```bash
# Create message files for Kyrgyz and Russian
python manage.py makemessages -l ky -l ru

# After editing the .po files in the locale directory, compile them:
python manage.py compilemessages
```

## Step 8: Collect Static Files

```bash
python manage.py collectstatic
```

## Step 9: Run the Development Server

```bash
python manage.py runserver
```

The site should now be accessible at http://localhost:8000/

- Admin interface: http://localhost:8000/admin/
- API documentation: http://localhost:8000/swagger/

## Step 10: Testing the Setup

1. Login to the admin interface with your superuser credentials
2. Create some initial categories and tags
3. Create a test article to verify content management functionality
4. Use the API documentation to test API endpoints

## Docker Setup (Alternative)

If you prefer to use Docker:

1. Make sure Docker and Docker Compose are installed
2. Configure the `.env` file as described above, but use:
   ```
   DATABASE_URL=postgres://postgres:postgres@db:5432/naryns_space
   ```
3. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```
4. Run migrations and create a superuser:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

## Common Issues and Solutions

### Database Connection Issues
- **Error**: "could not connect to server: Connection refused"
  - **Solution**: Make sure PostgreSQL is running and check your database credentials

### Migration Issues
- **Error**: "django.db.utils.ProgrammingError: relation already exists"
  - **Solution**: Try `python manage.py migrate --fake-initial`

### Static Files Not Loading
- **Solution**: Check if `STATIC_ROOT` is set correctly and run `collectstatic` again

### Email Configuration Issues
- **Error**: "SMTPAuthenticationError"
  - **Solution**: For Gmail, create an App Password or enable "Less secure app access"

## Next Steps

1. Explore the admin interface to understand the content model
2. Review the API documentation to understand available endpoints
3. Create some sample content to test the workflow
4. Set up the frontend application (if applicable)

For more detailed information about the system, refer to the README.md file.
