# Casting Agency API

A full-stack web application for managing actors and movies in a casting agency. Built with Flask (backend) and Angular (frontend), featuring Auth0 authentication and RBAC.

## Motivation

This project was developed as the capstone project for the Udacity Full Stack Developer Nanodegree program. 
The motivation behind this project is to demonstrate proficiency in:

- Building a complete full-stack application with separate frontend and backend
- Implementing secure authentication and authorization using Auth0
- Creating a RESTful API with proper error handling
- Designing and implementing role-based access control (RBAC)
- Managing database relationships using SQLAlchemy ORM
- Writing comprehensive test suites with proper test coverage
- Deploying a production application to a cloud platform (Render)


## Hosted Application

### Production URLs

**Frontend Application**: https://casting-agency-frontend-oj6g.onrender.com

**Backend API**: https://casting-agency-api-yjgi.onrender.com

The application is deployed on Render with the following components:
- **Frontend**: Static site hosted on Render
- **Backend**: Python web service running Gunicorn
- **Database**: PostgreSQL database on Render

## Project Dependencies

### Backend Dependencies

The backend is built with Python 3.13 and requires the following packages:

```
aiohappyeyeballs==2.6.1
aiohttp==3.13.2
aiosignal==1.4.0
alembic==1.14.0
astroid==3.3.5
attrs==25.4.0
auth0-python==4.7.2
blinker==1.9.0
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
click==8.1.7
cryptography==43.0.3
dill==0.4.0
ecdsa==0.19.0
Flask==3.1.0
Flask-Cors==5.0.0
Flask-Migrate==4.0.7
Flask-SQLAlchemy==3.1.1
frozenlist==1.8.0
idna==3.11
isort==5.13.2
itsdangerous==2.2.0
Jinja2==3.1.4
Mako==1.3.10
MarkupSafe==3.0.2
mccabe==0.7.0
multidict==6.7.0
platformdirs==4.5.1
propcache==0.4.1
pyasn1==0.6.1
pycparser==2.23
pycryptodome==3.21.0
PyJWT==2.10.1
pylint==3.3.2
python-dotenv==1.2.1
python-jose==3.3.0
requests==2.32.3
rsa==4.9
six==1.16.0
SQLAlchemy==2.0.36
tomlkit==0.13.3
typing_extensions==4.15.0
urllib3==2.6.2
Werkzeug==3.1.3
yarl==1.22.0
pylint==3.3.2
isort==5.13.2
gunicorn==20.1.0
psycopg2-binary==2.9.9
```

**Key Dependencies:**
- **Flask**: Web framework for building the API
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-CORS**: Handling Cross-Origin Resource Sharing
- **psycopg2-binary**: PostgreSQL adapter
- **python-jose**: JWT token validation for Auth0
- **gunicorn**: Production WSGI server
- **pytest**: Testing framework

### Frontend Dependencies

The frontend is built with Angular 18 and requires:

```
@angular/core: ^18.2.0
@angular/common: ^18.2.0
@angular/router: ^18.2.0
@auth0/auth0-angular: ^2.2.3
typescript: ~5.5.2
tailwindcss: ^3.4.15
```

**Key Dependencies:**
- **Angular**: Frontend framework
- **Auth0 Angular SDK**: Authentication integration
- **TailwindCSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript

## Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js 18.19 or higher
- PostgreSQL 12 or higher
- Auth0 account (for authentication)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/rabarijaona/myagency.git
cd myagency
```

#### 2. Backend Setup

Refer to the [backend README](backend/README.md) for detailed instructions on setting up and running the backend API locally.

#### 3. Frontend Setup

Refer to the [frontend README](frontend/README.md) for detailed instructions on setting up and running the frontend application locally.

## Test Users

For testing the application, you can use the following pre-configured test accounts:

### Casting Assistant
- **Email**: udacity-assistant@yopmail.com
- **Password**: Udacity123456
- **Permissions**: Read-only access to movies and actors

### Casting Director
- **Email**: udacity-director@yopmail.com
- **Password**: Udacity123456
- **Permissions**: All Assistant permissions plus ability to add/modify actors and modify movies

### Executive Producer
- **Email**: udacity-producer@yopmail.com
- **Password**: Udacity123456
- **Permissions**: Full access to all resources including creating and deleting movies

**Note**: These test accounts are configured in Auth0 with the appropriate roles and permissions. To use them, log in through the frontend application at https://casting-agency-frontend-oj6g.onrender.com

## Deployment

### Hosting Platform

The application is deployed on Render (https://render.com) with the following architecture:

- **Backend**: Web Service running Python/Gunicorn
- **Frontend**: Static Site
- **Database**: PostgreSQL database

### Deployment Configuration

The deployment is automated using `render.yaml`:

```yaml
services:
  - type: web
    name: casting-agency-api
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && gunicorn --bind 0.0.0.0:$PORT src.app:APP"

  - type: web
    name: casting-agency-frontend
    env: static
    buildCommand: "cd frontend && npm install && npm run build -- --configuration production"
    staticPublishPath: frontend/dist/myagency/browser

databases:
  - name: casting-agency-db
    databaseName: casting_agency
```

### Environment Variables (Production)

Set these in the Render dashboard:

**Backend:**
- `DATABASE_URL`: PostgreSQL connection string (automatically set by Render)
- `AUTH0_DOMAIN`: Your Auth0 domain
- `API_AUDIENCE`: Your Auth0 API identifier
- `SKIP_AUTH`: Set to `false` for production

**Frontend:**
- `NODE_VERSION`: 18.19.0

### Deployment Steps

1. Push code to GitHub
2. Connect repository to Render
3. Render automatically deploys using `render.yaml`
4. Set environment variables in Render dashboard
5. Initialize database using the `/setup-db` endpoint
