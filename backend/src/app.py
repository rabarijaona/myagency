from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Movie, Actor
from .auth.auth import AuthError, requires_auth
from .auth.auth0_management import (
    Auth0ManagementError,
    get_management_api_token,
    get_auth0_users,
    get_auth0_user,
    create_auth0_user,
    update_auth0_user,
    delete_auth0_user,
    get_user_roles,
    assign_roles_to_user,
    get_all_roles
)
from .auth.role_hierarchy import (
    filter_users_by_access_level,
    get_user_role_level,
    enforce_user_management_access,
    enforce_role_assignment_access,
    get_assignable_roles
)
from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:4200",
                "http://127.0.0.1:4200",
                "https://casting-agency-frontend.onrender.com",
                "https://casting-agency-frontend-oj6g.onrender.com"
            ],
            "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    # ROUTES

    @app.route('/')
    def index():
        return jsonify({
            'success': True,
            'message': 'Welcome to the Casting Agency API'
        })

    @app.route('/setup-db', methods=['POST'])
    def setup_database():
        """Initialize the database with tables and demo data

        SECURITY NOTE: In production, this endpoint should be protected
        or removed after initial setup. For now, it's helpful for deployment.
        """
        try:
            db_drop_and_create_all()
            return jsonify({
                'success': True,
                'message': 'Database initialized successfully with demo data'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': f'Database initialization failed: {str(e)}'
            }), 500

    # MOVIE ENDPOINTS

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        """Get all movies"""
        try:
            movies = Movie.query.order_by(Movie.id).all()

            return jsonify({
                'success': True,
                'movies': [movie.format() for movie in movies],
                'total_movies': len(movies)
            })
        except Exception as e:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['GET'])
    @requires_auth('get:movies')
    def get_movie(payload, movie_id):
        """Get a specific movie by ID"""
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        # Check if actors should be included
        include_actors = request.args.get('include_actors', 'false').lower() == 'true'

        return jsonify({
            'success': True,
            'movie': movie.format(include_actors=include_actors)
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movie(payload):
        """Create a new movie"""
        body = request.get_json()

        if not body:
            abort(400)

        title = body.get('title', None)
        release_date = body.get('release_date', None)

        if not title or not release_date:
            abort(400)

        try:
            # Parse the date string to a date object
            release_date_obj = datetime.strptime(release_date, '%Y-%m-%d').date()

            movie = Movie(title=title, release_date=release_date_obj)
            movie.insert()

            return jsonify({
                'success': True,
                'created': movie.id,
                'movie': movie.format()
            }), 201
        except ValueError:
            abort(400)
        except Exception as e:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        """Update a movie"""
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        body = request.get_json()

        if not body:
            abort(400)

        try:
            if 'title' in body:
                movie.title = body['title']

            if 'release_date' in body:
                release_date_obj = datetime.strptime(body['release_date'], '%Y-%m-%d').date()
                movie.release_date = release_date_obj

            movie.update()

            return jsonify({
                'success': True,
                'movie': movie.format()
            })
        except ValueError:
            abort(400)
        except Exception as e:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        """Delete a movie"""
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        try:
            movie.delete()

            return jsonify({
                'success': True,
                'deleted': movie_id
            })
        except Exception as e:
            abort(422)

    # ACTOR ENDPOINTS

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        """Get all actors"""
        try:
            actors = Actor.query.order_by(Actor.id).all()

            return jsonify({
                'success': True,
                'actors': [actor.format() for actor in actors],
                'total_actors': len(actors)
            })
        except Exception as e:
            print(e)
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['GET'])
    @requires_auth('get:actors')
    def get_actor(payload, actor_id):
        """Get a specific actor by ID"""
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        # Check if movies should be included
        include_movies = request.args.get('include_movies', 'false').lower() == 'true'

        return jsonify({
            'success': True,
            'actor': actor.format(include_movies=include_movies)
        })

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actor(payload):
        """Create a new actor"""
        body = request.get_json()

        if not body:
            abort(400)

        name = body.get('name', None)
        birth_date = body.get('birth_date', None)
        gender = body.get('gender', None)

        if not name or not birth_date or not gender:
            abort(400)

        try:
            birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()

            actor = Actor(name=name, birth_date=birth_date_obj, gender=gender)
            actor.insert()

            return jsonify({
                'success': True,
                'created': actor.id,
                'actor': actor.format()
            }), 201
        except ValueError:
            abort(400)
        except Exception as e:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(payload, actor_id):
        """Update an actor"""
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        body = request.get_json()

        if not body:
            abort(400)

        try:
            if 'name' in body:
                actor.name = body['name']

            if 'birth_date' in body:
                birth_date_obj = datetime.strptime(body['birth_date'], '%Y-%m-%d').date()
                actor.birth_date = birth_date_obj

            if 'gender' in body:
                actor.gender = body['gender']

            actor.update()

            return jsonify({
                'success': True,
                'actor': actor.format()
            })
        except ValueError:
            abort(400)
        except Exception as e:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        """Delete an actor"""
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        try:
            actor.delete()

            return jsonify({
                'success': True,
                'deleted': actor_id
            })
        except Exception as e:
            abort(422)

    # RELATIONSHIP ENDPOINTS

    @app.route('/movies/<int:movie_id>/actors', methods=['GET'])
    @requires_auth('get:movies')
    def get_movie_actors(payload, movie_id):
        """Get all actors for a specific movie"""
        movie = Movie.query.get(movie_id)

        if movie is None:
            abort(404)

        return jsonify({
            'success': True,
            'movie_id': movie_id,
            'movie_title': movie.title,
            'actors': [actor.format() for actor in movie.actors],
            'total_actors': len(movie.actors)
        })

    @app.route('/actors/<int:actor_id>/movies', methods=['GET'])
    @requires_auth('get:actors')
    def get_actor_movies(payload, actor_id):
        """Get all movies for a specific actor"""
        actor = Actor.query.get(actor_id)

        if actor is None:
            abort(404)

        return jsonify({
            'success': True,
            'actor_id': actor_id,
            'actor_name': actor.name,
            'movies': [movie.format() for movie in actor.movies],
            'total_movies': len(actor.movies)
        })

    @app.route('/movies/<int:movie_id>/actors/<int:actor_id>', methods=['POST'])
    @requires_auth('post:casting')
    def assign_actor_to_movie(payload, movie_id, actor_id):
        """Assign an actor to a movie"""
        movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)

        if movie is None or actor is None:
            abort(404)

        try:
            # Check if actor is already in the movie
            if actor in movie.actors:
                return jsonify({
                    'success': False,
                    'message': 'Actor is already assigned to this movie'
                }), 400

            movie.actors.append(actor)
            from src.database.models import db
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'{actor.name} assigned to {movie.title}',
                'movie': movie.format(include_actors=True)
            }), 201
        except Exception as e:
            from src.database.models import db
            db.session.rollback()
            abort(422)

    @app.route('/movies/<int:movie_id>/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:casting')
    def remove_actor_from_movie(payload, movie_id, actor_id):
        """Remove an actor from a movie"""
        movie = Movie.query.get(movie_id)
        actor = Actor.query.get(actor_id)

        if movie is None or actor is None:
            abort(404)

        try:
            # Check if actor is in the movie
            if actor not in movie.actors:
                return jsonify({
                    'success': False,
                    'message': 'Actor is not assigned to this movie'
                }), 400

            movie.actors.remove(actor)
            from src.database.models import db
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'{actor.name} removed from {movie.title}',
                'movie': movie.format(include_actors=True)
            })
        except Exception as e:
            from src.database.models import db
            db.session.rollback()
            abort(422)

    # USER MANAGEMENT ENDPOINTS
    @app.route('/users', methods=['GET'])
    @requires_auth('get:users')
    def get_users(payload):

        try:
            mgmt_token = get_management_api_token()

            page = request.args.get('page', 0, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            search = request.args.get('search', None)

            result = get_auth0_users(mgmt_token, page, per_page, search)
            users = result.get('users', [])

            manager_permissions = payload.get('permissions', [])
            filtered_users = filter_users_by_access_level(users, manager_permissions)

            return jsonify({
                'success': True,
                'users': filtered_users,
                'total': len(filtered_users),
                'page': page,
                'per_page': per_page,
                'your_role_level': get_user_role_level(manager_permissions)
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users/<user_id>', methods=['GET'])
    @requires_auth('get:users')
    def get_user(payload, user_id):
        try:
            mgmt_token = get_management_api_token()
            user = get_auth0_user(mgmt_token, user_id)

            user_roles = get_user_roles(mgmt_token, user_id)
            manager_permissions = payload.get('permissions', [])

            enforce_user_management_access(manager_permissions, user_roles)

            return jsonify({
                'success': True,
                'user': user
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users', methods=['POST'])
    @requires_auth('post:users')
    def create_user(payload):
        try:
            body = request.get_json()

            if not body:
                abort(400)

            email = body.get('email')
            password = body.get('password')
            name = body.get('name')
            role_name = body.get('role', 'Casting Assistant')

            if not email or not password:
                return jsonify({
                    'success': False,
                    'error': 400,
                    'message': 'Email and password are required'
                }), 400

            manager_permissions = payload.get('permissions', [])
            enforce_role_assignment_access(manager_permissions, role_name)

            mgmt_token = get_management_api_token()
            user = create_auth0_user(mgmt_token, email, password, name)

            if role_name:
                all_roles = get_all_roles(mgmt_token)
                role_id = None
                for role in all_roles:
                    if role.get('name') == role_name:
                        role_id = role.get('id')
                        break

                if role_id:
                    assign_roles_to_user(mgmt_token, user['user_id'], [role_id])

            return jsonify({
                'success': True,
                'user': user,
                'role_assigned': role_name
            }), 201
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users/<user_id>', methods=['PATCH'])
    @requires_auth('patch:users')
    def update_user(payload, user_id):
        try:
            body = request.get_json()

            if not body:
                abort(400)

            mgmt_token = get_management_api_token()

            user_roles = get_user_roles(mgmt_token, user_id)
            manager_permissions = payload.get('permissions', [])
            enforce_user_management_access(manager_permissions, user_roles)

            user = update_auth0_user(mgmt_token, user_id, body)

            return jsonify({
                'success': True,
                'user': user
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users/<user_id>', methods=['DELETE'])
    @requires_auth('delete:users')
    def delete_user(payload, user_id):
        try:
            mgmt_token = get_management_api_token()

            user_roles = get_user_roles(mgmt_token, user_id)
            manager_permissions = payload.get('permissions', [])
            enforce_user_management_access(manager_permissions, user_roles)

            delete_auth0_user(mgmt_token, user_id)

            return jsonify({
                'success': True,
                'deleted': user_id
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users/<user_id>/roles', methods=['GET'])
    @requires_auth('get:users')
    def get_user_roles_endpoint(payload, user_id):
        try:
            mgmt_token = get_management_api_token()
            roles = get_user_roles(mgmt_token, user_id)

            return jsonify({
                'success': True,
                'roles': roles
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/users/<user_id>/roles', methods=['POST'])
    @requires_auth('post:users')
    def assign_user_roles(payload, user_id):
        try:
            body = request.get_json()

            if not body or 'roles' not in body:
                return jsonify({
                    'success': False,
                    'error': 400,
                    'message': 'Roles array is required'
                }), 400

            role_ids = body.get('roles')
            manager_permissions = payload.get('permissions', [])
            mgmt_token = get_management_api_token()

            user_roles = get_user_roles(mgmt_token, user_id)
            enforce_user_management_access(manager_permissions, user_roles)

            all_roles = get_all_roles(mgmt_token)
            for role_id in role_ids:
                role_name = None
                for role in all_roles:
                    if role.get('id') == role_id:
                        role_name = role.get('name')
                        break

                if role_name:
                    enforce_role_assignment_access(manager_permissions, role_name)

            assign_roles_to_user(mgmt_token, user_id, role_ids)

            return jsonify({
                'success': True,
                'message': 'Roles assigned successfully'
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    @app.route('/roles', methods=['GET'])
    @requires_auth('get:users')
    def get_roles(payload):
        try:
            mgmt_token = get_management_api_token()
            all_roles = get_all_roles(mgmt_token)

            manager_permissions = payload.get('permissions', [])
            assignable_roles = get_assignable_roles(manager_permissions, all_roles)

            return jsonify({
                'success': True,
                'roles': assignable_roles,
                'total': len(assignable_roles),
                'your_role_level': get_user_role_level(manager_permissions)
            }), 200
        except Auth0ManagementError as e:
            return jsonify({
                'success': False,
                'error': e.status_code,
                'message': e.message
            }), e.status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 500,
                'message': str(e)
            }), 500


    # ERROR HANDLERS

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            'success': False,
            'error': error.status_code,
            'message': error.error['description']
        }), error.status_code

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app

APP = create_app()


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
