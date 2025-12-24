# Casting Agency Frontend

A modern Angular 18 application for managing movies and actors in a casting agency database.

## Features

- **Movies Management**: Create, read, update, and delete movies
- **Actors Management**: Create, read, update, and delete actors
- **Real-time Age Calculation**: Automatically calculates actor ages from birth dates
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Clean UI**: Modern, intuitive interface with gradient styling

## Tech Stack

- **Angular 18**: Frontend framework
- **TypeScript**: Type-safe JavaScript
- **RxJS**: Reactive programming
- **HttpClient**: HTTP communication with backend API

## Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8080`

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

Start the development server:

```bash
npm start
```

The application will be locally available at `http://localhost:4200`


## API Integration

The frontend communicates with the backend API at `http://localhost:8080` and uses the following endpoints:

### Movies
- `GET /movies` - Fetch all movies
- `GET /movies/:id` - Fetch a specific movie
- `POST /movies` - Create a new movie
- `PATCH /movies/:id` - Update a movie
- `DELETE /movies/:id` - Delete a movie

### Actors
- `GET /actors` - Fetch all actors
- `GET /actors/:id` - Fetch a specific actor
- `POST /actors` - Create a new actor
- `PATCH /actors/:id` - Update an actor
- `DELETE /actors/:id` - Delete an actor

## Features Overview

### Movies Tab
- View all movies in a card grid
- Add new movies with title and release date
- Edit existing movies
- Delete movies with confirmation
- Displays release dates

### Actors Tab
- View all actors in a card grid
- Add new actors with name, birth date, and gender
- Edit existing actors
- Delete actors with confirmation
- Automatically calculates and displays age from birth date
- Gender selection dropdown

## Development

### Build
```bash
npm run build
```

### Watch Mode
```bash
npm run watch
```

### Testing
```bash
npm test
```

## Configuration

To change the backend API URL, edit the `apiUrl` property in `src/app/services/api.service.ts`:

```typescript
private apiUrl = 'http://localhost:8080';
```
