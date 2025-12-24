# Casting Agency Backend

## Overview

The Casting Agency backend is a RESTful API built with Flask that manages movies and actors for a casting agency. The system allows executives to create, read, update, and delete movies and actors in the database.

## Tech Stack

- **Python 3.13**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Auth0** - Authentication and authorization
- **PostgreSQL** - Production database (SQLite for development)

## Getting Started

### Prerequisites

- Python 3.13 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3.13 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Server

**For Development (Skip Authentication):**
```bash
# From the backend directory
export SKIP_AUTH=true
export FLASK_APP=src/app.py
export FLASK_ENV=development
flask run --port 8080
```

**For Production (With Auth0 Authentication):**
```bash
# From the backend directory
export AUTH0_DOMAIN=dev-dzv8dgf6ff6qu41d.us.auth0.com
export API_AUDIENCE=casting-agency
export FLASK_APP=src/app.py
export FLASK_ENV=development
flask run --port 8080
```

The API will be available at `http://localhost:8080`

**Note:** Setting `SKIP_AUTH=true` bypasses authentication and is recommended for local development and testing.

### Verify the Server is Running

Open your browser and navigate to:
- `http://localhost:8080/`

You should see:
```json
{
  "success": true,
  "message": "Welcome to the Casting Agency API"
}
```

Or test with curl:
```bash
curl http://localhost:8080/
```

## Database Setup

The application uses SQLite by default for development. The database will be managed using Flask-Migrate (Alembic).

### Initialize the Database

The database will be created automatically when you start the server. To populate it with demo data:

**Option 1: Initialize with demo data (Recommended)**

Open a new terminal and run:
```bash
curl -X POST http://localhost:8080/setup-db
```

This will create the database tables and populate them with sample movies and actors.

**Option 2: Using Flask-Migrate (Advanced)**

If you want to manage migrations manually:

1. **First time setup - Initialize migrations:**
```bash
cd backend
python manage.py init
```

2. **Create initial migration:**
```bash
python manage.py migrate "Initial migration"
```

3. **Apply migrations to database:**
```bash
python manage.py upgrade
```

4. **Seed database with demo data (optional):**
```bash
python manage.py seed
```

### Common Migration Commands

```bash
# Create a new migration after model changes
python manage.py migrate "Description of changes"

# Apply pending migrations
python manage.py upgrade

# Revert last migration
python manage.py downgrade

# Seed database with 5 movies and 5 actors
python manage.py seed
```

### Production Database

For production, set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/casting_agency"
```

## API Documentation

### Base URL

Development: `http://localhost:8080`

### Authentication

The API uses Auth0 for authentication and authorization. Most endpoints require a valid JWT token in the Authorization header.

**Development Mode (SKIP_AUTH=true):**
- No authentication required
- All endpoints are accessible without tokens

**Production Mode:**
- Include the JWT token in the Authorization header:
  ```
  Authorization: Bearer <your-jwt-token>
  ```

**Public Endpoints (No Auth Required):**
- `GET /` - Welcome message
- `GET /movies` - View movies (read-only)
- `GET /actors` - View actors (read-only)

**Protected Endpoints:**
All other endpoints require authentication with appropriate permissions.

### Error Handling

Errors are returned as JSON objects in the following format:
```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

The API returns the following error codes:
- **400**: Bad Request
- **404**: Resource Not Found
- **422**: Unprocessable Entity
- **500**: Internal Server Error

### Endpoints

#### General

**GET /**
- Returns a welcome message
- No authentication required

**Response:**
```json
{
  "success": true,
  "message": "Welcome to the Casting Agency API"
}
```

---

#### Movies

**GET /movies**
- Fetches all movies from the database
- Returns a list of movies, total count, and success status

**Response:**
```json
{
  "success": true,
  "movies": [
    {
      "id": 1,
      "title": "The Matrix",
      "release_date": "1999-03-31"
    }
  ],
  "total_movies": 1
}
```

---

**GET /movies/{movie_id}**
- Fetches a specific movie by ID
- Returns the movie object and success status

**Response:**
```json
{
  "success": true,
  "movie": {
    "id": 1,
    "title": "The Matrix",
    "release_date": "1999-03-31"
  }
}
```

---

**POST /movies**
- Creates a new movie
- Request body must include `title` and `release_date` (YYYY-MM-DD format)

**Request Body:**
```json
{
  "title": "Inception",
  "release_date": "2010-07-16"
}
```

**Response:**
```json
{
  "success": true,
  "created": 2,
  "movie": {
    "id": 2,
    "title": "Inception",
    "release_date": "2010-07-16"
  }
}
```

---

**PATCH /movies/{movie_id}**
- Updates an existing movie
- Request body can include `title` and/or `release_date`

**Request Body:**
```json
{
  "title": "Inception (Director's Cut)",
  "release_date": "2010-07-16"
}
```

**Response:**
```json
{
  "success": true,
  "movie": {
    "id": 2,
    "title": "Inception (Director's Cut)",
    "release_date": "2010-07-16"
  }
}
```

---

**DELETE /movies/{movie_id}**
- Deletes a movie from the database
- Returns the ID of the deleted movie

**Response:**
```json
{
  "success": true,
  "deleted": 2
}
```

---

#### Actors

**GET /actors**
- Fetches all actors from the database
- Returns a list of actors, total count, and success status

**Response:**
```json
{
  "success": true,
  "actors": [
    {
      "id": 1,
      "name": "Keanu Reeves",
      "age": 59,
      "gender": "Male"
    }
  ],
  "total_actors": 1
}
```

---

**GET /actors/{actor_id}**
- Fetches a specific actor by ID
- Returns the actor object and success status

**Response:**
```json
{
  "success": true,
  "actor": {
    "id": 1,
    "name": "Keanu Reeves",
    "age": 59,
    "gender": "Male"
  }
}
```

---

**POST /actors**
- Creates a new actor
- Request body must include `name`, `age`, and `gender`

**Request Body:**
```json
{
  "name": "Leonardo DiCaprio",
  "age": 49,
  "gender": "Male"
}
```

**Response:**
```json
{
  "success": true,
  "created": 2,
  "actor": {
    "id": 2,
    "name": "Leonardo DiCaprio",
    "age": 49,
    "gender": "Male"
  }
}
```

---

**PATCH /actors/{actor_id}**
- Updates an existing actor
- Request body can include `name`, `age`, and/or `gender`

**Request Body:**
```json
{
  "name": "Leonardo DiCaprio",
  "age": 50,
  "gender": "Male"
}
```

**Response:**
```json
{
  "success": true,
  "actor": {
    "id": 2,
    "name": "Leonardo DiCaprio",
    "age": 50,
    "gender": "Male"
  }
}
```

---

**DELETE /actors/{actor_id}**
- Deletes an actor from the database
- Returns the ID of the deleted actor

**Response:**
```json
{
  "success": true,
  "deleted": 2
}
```

---

## Testing

### Using cURL

**Create a Movie:**
```bash
curl -X POST http://localhost:8080/movies \
  -H "Content-Type: application/json" \
  -d '{"title": "The Matrix", "release_date": "1999-03-31"}'
```

**Get All Movies:**
```bash
curl http://localhost:8080/movies
```

**Update a Movie:**
```bash
curl -X PATCH http://localhost:8080/movies/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "The Matrix Reloaded"}'
```

**Delete a Movie:**
```bash
curl -X DELETE http://localhost:8080/movies/1
```

**Create an Actor:**
```bash
curl -X POST http://localhost:8080/actors \
  -H "Content-Type: application/json" \
  -d '{"name": "Keanu Reeves", "age": 59, "gender": "Male"}'
```

**Get All Actors:**
```bash
curl http://localhost:8080/actors
```

**Update an Actor:**
```bash
curl -X PATCH http://localhost:8080/actors/1 \
  -H "Content-Type: application/json" \
  -d '{"age": 60}'
```

**Delete an Actor:**
```bash
curl -X DELETE http://localhost:8080/actors/1
```

### Unit Tests

Run the test suite:
```bash
python -m pytest test_app.py -v
```

## Data Models

### Movie

- **id** (Integer, Primary Key)
- **title** (String, Required)
- **release_date** (Date, Required)

### Actor

- **id** (Integer, Primary Key)
- **name** (String, Required)
- **age** (Integer, Required)
- **gender** (String, Required)

## Environment Variables

- `DATABASE_URL` - Database connection string (optional, defaults to SQLite)
- `FLASK_APP` - Entry point for Flask application
- `FLASK_ENV` - Environment mode (development/production)
- `AUTH0_DOMAIN` - Auth0 domain for authentication
- `API_AUDIENCE` - Auth0 API audience

## Deployment

For production deployment:

1. Set up a PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Deploy to your hosting platform (Heroku, AWS, etc.)

## Troubleshooting

Remove psycopg2-binary in requirements.txt if you encounter issues during pip install locally as it is needed 
only for production with PostgreSQL (Render).


