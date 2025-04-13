# Naryn's Culture Website Backend

A Django-based backend system for preserving and showcasing Naryn's culture, traditions, and landmarks.

## Features

- Multi-language content support (Kyrgyz, Russian, English)
- Advanced content management system with moderation workflow
- User-generated content submission and approval process
- Dynamic QR code generation for historical sites and content
- RESTful API for frontend integration
- Role-based access control with multiple user roles
- Media upload and optimization
- JWT and OAuth authentication
- API documentation with Swagger

## Technology Stack

- **Framework**: Django 4.2
- **REST API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens), OAuth (Google, Facebook)
- **Media Processing**: Pillow, django-cleanup
- **Internationalization**: django-modeltranslation
- **QR Code Generation**: qrcode
- **API Documentation**: drf-yasg (Swagger)
- **Deployment**: Gunicorn, Whitenoise

## Project Structure

The project is organized into several Django apps:

- **accounts**: User authentication, profiles, and permissions
- **content**: Content models (Articles, Stories, Landmarks, Images, Videos)
- **moderation**: Content moderation system and workflows
- **api**: API endpoints for frontend integration
- **utils**: Utility functions (QR code generation, image compression)

## Complete Setup Guide

### 1. Clone the Repository

```bash
git clone <repository-url>
cd naryns-space
```

### 2. Set Up Python Environment

Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create a `.env` file in the project root based on `.env.example`:

```bash
cp .env.example .env
```

Then edit the `.env` file to configure your environment:

- **SECRET_KEY**: Generate a secure secret key (you can use Django's get_random_secret_key() function)
- **DEBUG**: Set to "True" for development, "False" for production
- **ALLOWED_HOSTS**: Add your domain name for production
- **DATABASE_URL**: Configure your PostgreSQL connection string
- **EMAIL_***: Set up email server credentials for notifications
- **OAUTH_***: Set up OAuth keys if using social login
- **CORS_ALLOWED_ORIGINS**: Add frontend URL for CORS

### 5. Set Up the Database

First, create a PostgreSQL database:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE naryns_space;

# Exit PostgreSQL
\q
```

Then run Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

You'll be prompted to enter an email, first name, last name, and password for the superuser.

### 7. Create Translation Files (Optional)

```bash
# Create translation files
python manage.py makemessages -l ky -l ru

# Compile translations after editing .po files
python manage.py compilemessages
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run the Development Server

```bash
python manage.py runserver
```

The site should now be available at http://localhost:8000/

### 10. Access the API Documentation

Once the server is running, you can access the Swagger documentation at:

- Swagger UI: http://localhost:8000/swagger/
- ReDoc UI: http://localhost:8000/redoc/

## Docker Setup

Alternatively, you can use Docker for a containerized setup:

### 1. Create and Configure .env File

Copy the `.env.example` to `.env` and update it as needed. For Docker, use:

```
DATABASE_URL=postgres://postgres:postgres@db:5432/naryns_space
```

### 2. Build and Start Containers

```bash
docker-compose up -d --build
```

### 3. Run Migrations and Create Superuser

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

The site will be available at http://localhost:8000/

## Environment Variables Explanation

The `.env` file contains all the configuration needed to run the application:

### Core Django Settings
- **SECRET_KEY**: Used for cryptographic signing. Must be unique and secret.
- **DEBUG**: "True" for development, "False" for production.
- **ALLOWED_HOSTS**: Comma-separated list of hosts that can serve the application.
- **BASE_URL**: Base URL for the site, used for generating absolute URLs.

### Database Settings
- **DATABASE_URL**: PostgreSQL connection URL in the format `postgres://user:password@host:port/dbname`.
- **POSTGRES_USER**: Username for PostgreSQL (used by Docker).
- **POSTGRES_PASSWORD**: Password for PostgreSQL (used by Docker).
- **POSTGRES_DB**: Database name for PostgreSQL (used by Docker).

### Email Settings
- **EMAIL_HOST**: SMTP server hostname.
- **EMAIL_PORT**: SMTP server port (usually 587 for TLS).
- **EMAIL_USE_TLS**: Whether to use TLS for email (usually True).
- **EMAIL_HOST_USER**: Email account username.
- **EMAIL_HOST_PASSWORD**: Email account password or app password.
- **DEFAULT_FROM_EMAIL**: Default sender email address.

### Frontend and Authentication
- **FRONTEND_URL**: URL of the frontend application, used for password reset links.
- **GOOGLE_OAUTH2_KEY**, **GOOGLE_OAUTH2_SECRET**: Credentials for Google OAuth.
- **FACEBOOK_KEY**, **FACEBOOK_SECRET**: Credentials for Facebook OAuth.

### CORS Settings
- **CORS_ALLOWED_ORIGINS**: Comma-separated list of origins allowed to make cross-origin requests.

## API Documentation

The API is documented using Swagger and can be accessed at `/swagger/` when the server is running.

### Authentication Endpoints

- `POST /api/auth/register/`: Register a new user
- `POST /api/auth/login/`: Log in a user
- `POST /api/token/`: Obtain JWT token
- `POST /api/token/refresh/`: Refresh JWT token
- `POST /api/token/verify/`: Verify JWT token

### Content Endpoints

- `GET /api/articles/`: List articles
- `POST /api/articles/`: Create article
- `GET /api/articles/{slug}/`: Retrieve article
- `PUT /api/articles/{slug}/`: Update article
- `DELETE /api/articles/{slug}/`: Delete article
- `POST /api/articles/{slug}/submit_for_review/`: Submit article for review

Similar endpoints exist for stories, landmarks, images, and videos.

### Moderation Endpoints

- `GET /api/moderation/pending_content/`: List all pending content
- `POST /api/moderation/approve_content/`: Approve content
- `POST /api/moderation/reject_content/`: Reject content
- `POST /api/moderation/publish_content/`: Publish approved content

## User Roles

- **Super Admin**: Full access to all system functionalities
- **Admin (Moderator)**: Can review, approve, and manage content
- **User**: Can submit content for approval and access published content

## Content Workflow

1. Users create content (articles, stories, etc.) which is saved as draft
2. Users submit content for review
3. Admins/moderators review content and either approve or reject it
4. If approved, content can be published making it visible to all users
5. Published content can be viewed by anyone

## Running Tests

To run tests:

```bash
python manage.py test
```

For specific test modules:

```bash
python manage.py test tests.test_api
```

## Database Backup and Recovery

The system uses PostgreSQL. Regular backups can be performed using Django's `dumpdata` command:

```bash
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json
```

To restore:

```bash
python manage.py loaddata backup.json
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Ensure PostgreSQL is running
   - Check DATABASE_URL in your .env file
   - Verify database user permissions

2. **Migration Errors**:
   - Try resetting migrations: `python manage.py migrate --fake-initial`

3. **Static Files Not Loading**:
   - Run `python manage.py collectstatic` again
   - Check STATIC_ROOT and STATIC_URL settings

4. **Email Sending Failures**:
   - Check email credentials in .env
   - For Gmail, ensure "Less secure app access" or App Passwords are configured

## Deployment

The application is configured to work with various deployment platforms:

- **Static files**: Served using Whitenoise
- **Media files**: Can be configured with cloud storage (AWS S3, etc.)
- **Database**: Works with any PostgreSQL database

Follow the platform-specific deployment instructions and ensure all environment variables are properly set.
