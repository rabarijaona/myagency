import unittest
import json
import sys
import os
from unittest.mock import patch
from functools import wraps

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

def mock_requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = {
                'permissions': [
                    'get:movies', 'get:actors',
                    'post:movies', 'post:actors',
                    'patch:movies', 'patch:actors',
                    'delete:movies', 'delete:actors',
                    'post:casting', 'delete:casting'
                ]
            }
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

with patch('src.auth.auth.requires_auth', side_effect=mock_requires_auth):
    from src.app import create_app
from src.database.models import db_drop_and_create_all


class CastingAgencyTestCase(unittest.TestCase):

    def setUp(self):
        self.database_name = "casting_agency_test.db"
        self.database_path = "sqlite:///{}".format(self.database_name)

        os.environ['DATABASE_URL'] = self.database_path

        self.app = create_app()
        self.client = self.app.test_client

        with self.app.app_context():
            db_drop_and_create_all()

    def tearDown(self):
        pass

    def get_headers(self, role='producer'):
        token_map = {
            'assistant': self.assistant_token,
            'director': self.director_token,
            'producer': self.producer_token
        }
        token = token_map.get(role, self.producer_token)
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def test_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_movies'])
        self.assertTrue(len(data['movies']))

    def test_get_movie_by_id(self):
        res = self.client().get('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['id'], 1)

    def test_404_get_movie_by_invalid_id(self):
        res = self.client().get('/movies/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_movie(self):
        new_movie = {
            'title': 'Interstellar',
            'release_date': '2014-11-07'
        }
        res = self.client().post('/movies', json=new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'Interstellar')

    def test_400_create_movie_missing_title(self):
        new_movie = {
            'release_date': '2014-11-07'
        }
        res = self.client().post('/movies', json=new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_400_create_movie_missing_release_date(self):
        new_movie = {
            'title': 'Interstellar'
        }
        res = self.client().post('/movies', json=new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_400_create_movie_invalid_date_format(self):
        new_movie = {
            'title': 'Interstellar',
            'release_date': 'invalid-date'
        }
        res = self.client().post('/movies', json=new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_update_movie(self):
        update_data = {
            'title': 'The Shawshank Redemption - Updated'
        }
        res = self.client().patch('/movies/1', json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'The Shawshank Redemption - Updated')

    def test_404_update_movie_invalid_id(self):
        update_data = {
            'title': 'Updated Title'
        }
        res = self.client().patch('/movies/1000', json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_movie(self):
        res = self.client().delete('/movies/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_404_delete_movie_invalid_id(self):
        res = self.client().delete('/movies/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_actors'])
        self.assertTrue(len(data['actors']))

    def test_get_actor_by_id(self):
        res = self.client().get('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['id'], 1)
        self.assertTrue('age' in data['actor'])
        self.assertTrue('birth_date' in data['actor'])

    def test_404_get_actor_by_invalid_id(self):
        res = self.client().get('/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_actor(self):
        new_actor = {
            'name': 'Meryl Streep',
            'birth_date': '1949-06-22',
            'gender': 'Female'
        }
        res = self.client().post('/actors', json=new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], 'Meryl Streep')
        self.assertTrue('age' in data['actor'])

    def test_400_create_actor_missing_name(self):
        new_actor = {
            'birth_date': '1949-06-22',
            'gender': 'Female'
        }
        res = self.client().post('/actors', json=new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_400_create_actor_missing_birth_date(self):
        new_actor = {
            'name': 'Meryl Streep',
            'gender': 'Female'
        }
        res = self.client().post('/actors', json=new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_400_create_actor_missing_gender(self):
        new_actor = {
            'name': 'Meryl Streep',
            'birth_date': '1949-06-22'
        }
        res = self.client().post('/actors', json=new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_update_actor(self):
        update_data = {
            'name': 'Morgan Freeman - Updated'
        }
        res = self.client().patch('/actors/1', json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], 'Morgan Freeman - Updated')

    def test_404_update_actor_invalid_id(self):
        update_data = {
            'name': 'Updated Name'
        }
        res = self.client().patch('/actors/1000', json=update_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_actor(self):
        res = self.client().delete('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_404_delete_actor_invalid_id(self):
        res = self.client().delete('/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_actor_age_calculation(self):
        res = self.client().get('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        actor = data['actor']

        self.assertTrue('age' in actor)
        self.assertIsInstance(actor['age'], int)
        self.assertGreater(actor['age'], 0)

    def test_get_movie_with_actors(self):
        res = self.client().get('/movies/3?include_actors=true')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue('actors' in data['movie'])
        self.assertIsInstance(data['movie']['actors'], list)
        self.assertEqual(len(data['movie']['actors']), 2)

    def test_get_movie_without_actors(self):
        res = self.client().get('/movies/3')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse('actors' in data['movie'])

    def test_get_actor_with_movies(self):
        res = self.client().get('/actors/1?include_movies=true')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue('movies' in data['actor'])
        self.assertIsInstance(data['actor']['movies'], list)
        self.assertEqual(len(data['actor']['movies']), 2)

    def test_get_actor_without_movies(self):
        res = self.client().get('/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse('movies' in data['actor'])

    def test_get_movie_actors(self):
        res = self.client().get('/movies/3/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], 3)
        self.assertEqual(data['movie_title'], 'The Dark Knight')
        self.assertTrue(data['actors'])
        self.assertEqual(data['total_actors'], 2)
        self.assertEqual(len(data['actors']), 2)

    def test_404_get_movie_actors_invalid_id(self):
        res = self.client().get('/movies/1000/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_movie_actors_no_actors(self):
        new_movie = {
            'title': 'New Movie',
            'release_date': '2024-01-01'
        }
        create_res = self.client().post('/movies', json=new_movie)
        created_movie = json.loads(create_res.data)
        movie_id = created_movie['created']

        res = self.client().get(f'/movies/{movie_id}/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_actors'], 0)
        self.assertEqual(len(data['actors']), 0)

    def test_get_actor_movies(self):
        res = self.client().get('/actors/1/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['actor_name'], 'Morgan Freeman')
        self.assertTrue(data['movies'])
        self.assertEqual(data['total_movies'], 2)
        self.assertEqual(len(data['movies']), 2)

    def test_404_get_actor_movies_invalid_id(self):
        res = self.client().get('/actors/1000/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_actor_movies_no_movies(self):
        new_actor = {
            'name': 'New Actor',
            'birth_date': '1990-01-01',
            'gender': 'Male'
        }
        create_res = self.client().post('/actors', json=new_actor)
        created_actor = json.loads(create_res.data)
        actor_id = created_actor['created']

        res = self.client().get(f'/actors/{actor_id}/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_movies'], 0)
        self.assertEqual(len(data['movies']), 0)

    def test_assign_actor_to_movie(self):
        res = self.client().post('/movies/2/actors/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertIn('Tom Hanks', data['message'])
        self.assertIn('The Godfather', data['message'])
        self.assertTrue(data['movie'])
        self.assertTrue('actors' in data['movie'])

        verify_res = self.client().get('/movies/2/actors')
        verify_data = json.loads(verify_res.data)
        actor_ids = [actor['id'] for actor in verify_data['actors']]
        self.assertIn(5, actor_ids)

    def test_400_assign_duplicate_actor_to_movie(self):
        res = self.client().post('/movies/3/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertIn('already assigned', data['message'])

    def test_404_assign_actor_invalid_movie_id(self):
        res = self.client().post('/movies/1000/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_404_assign_actor_invalid_actor_id(self):
        res = self.client().post('/movies/1/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_404_assign_actor_both_invalid_ids(self):
        res = self.client().post('/movies/1000/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_remove_actor_from_movie(self):
        self.client().post('/movies/2/actors/5')

        res = self.client().delete('/movies/2/actors/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIn('Tom Hanks', data['message'])
        self.assertIn('removed', data['message'])
        self.assertTrue(data['movie'])

        verify_res = self.client().get('/movies/2/actors')
        verify_data = json.loads(verify_res.data)
        actor_ids = [actor['id'] for actor in verify_data['actors']]
        self.assertNotIn(5, actor_ids)

    def test_400_remove_actor_not_in_movie(self):
        res = self.client().delete('/movies/2/actors/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertIn('not assigned', data['message'])

    def test_404_remove_actor_invalid_movie_id(self):
        res = self.client().delete('/movies/1000/actors/1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_404_remove_actor_invalid_actor_id(self):
        res = self.client().delete('/movies/1/actors/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_relationship_bidirectional(self):
        self.client().post('/movies/3/actors/4')

        movie_res = self.client().get('/movies/3/actors')
        movie_data = json.loads(movie_res.data)
        actor_ids = [actor['id'] for actor in movie_data['actors']]
        self.assertIn(4, actor_ids)

        actor_res = self.client().get('/actors/4/movies')
        actor_data = json.loads(actor_res.data)
        movie_ids = [movie['id'] for movie in actor_data['movies']]
        self.assertIn(3, movie_ids)

    def test_relationship_multiple_assignments(self):
        self.client().post('/movies/4/actors/1')
        self.client().post('/movies/4/actors/5')

        res = self.client().get('/movies/4/actors')
        data = json.loads(res.data)

        self.assertEqual(data['total_actors'], 3)

    def test_relationship_actor_in_multiple_movies(self):
        self.client().post('/movies/1/actors/3')
        self.client().post('/movies/4/actors/3')

        res = self.client().get('/actors/3/movies')
        data = json.loads(res.data)

        self.assertEqual(data['total_movies'], 3)

    def test_delete_movie_removes_relationships(self):
        res = self.client().get('/movies/3/actors')
        data = json.loads(res.data)
        self.assertGreater(data['total_actors'], 0)

        self.client().delete('/movies/3')

        res = self.client().get('/movies/3/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_actor_removes_relationships(self):
        res = self.client().get('/actors/1/movies')
        data = json.loads(res.data)
        self.assertGreater(data['total_movies'], 0)

        self.client().delete('/actors/1')

        res = self.client().get('/actors/1/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)


def create_rbac_mock_auth(user_permissions):
    def mock_requires_auth(permission=''):
        def requires_auth_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if permission and permission not in user_permissions:
                    from src.auth.auth import AuthError
                    raise AuthError({
                        'code': 'unauthorized',
                        'description': 'You are not authorized to perform this action.'
                    }, 403)
                payload = {'permissions': user_permissions}
                return f(payload, *args, **kwargs)
            return wrapper
        return requires_auth_decorator
    return mock_requires_auth


class RBACTestCase(unittest.TestCase):

    def setUp(self):
        self.database_name = "casting_agency_rbac_test.db"
        self.database_path = "sqlite:///{}".format(self.database_name)
        os.environ['DATABASE_URL'] = self.database_path

    def tearDown(self):
        pass

    def get_app_with_permissions(self, permissions):
        with patch('src.auth.auth.requires_auth', side_effect=create_rbac_mock_auth(permissions)):
            import importlib
            import src.app
            importlib.reload(src.app)
            app = src.app.create_app()

            with app.app_context():
                db_drop_and_create_all()

            return app

    def test_public_can_get_movies(self):
        app = self.get_app_with_permissions(['get:movies', 'get:actors'])
        client = app.test_client()
        res = client.get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    def test_public_can_get_actors(self):
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(['get:movies', 'get:actors'])):
            res = self.client().get('/actors')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertTrue(data['actors'])

    def test_public_cannot_create_movie(self):
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(['get:movies', 'get:actors'])):
            new_movie = {'title': 'Test Movie', 'release_date': '2024-01-01'}
            res = self.client().post('/movies', json=new_movie)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_public_cannot_delete_movie(self):
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(['get:movies', 'get:actors'])):
            res = self.client().delete('/movies/1')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_assistant_can_get_movies(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            res = self.client().get('/movies')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_assistant_can_get_actors(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            res = self.client().get('/actors')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_assistant_cannot_create_movie(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            new_movie = {'title': 'Test Movie', 'release_date': '2024-01-01'}
            res = self.client().post('/movies', json=new_movie)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_assistant_cannot_create_actor(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            new_actor = {'name': 'Test Actor', 'birth_date': '1990-01-01', 'gender': 'Male'}
            res = self.client().post('/actors', json=new_actor)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_assistant_cannot_update_movie(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            update_data = {'title': 'Updated Title'}
            res = self.client().patch('/movies/1', json=update_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_assistant_cannot_delete_actor(self):
        assistant_permissions = ['get:movies', 'get:actors']
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(assistant_permissions)):
            res = self.client().delete('/actors/1')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_director_can_get_movies(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            res = self.client().get('/movies')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_director_can_update_movie(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            update_data = {'title': 'Updated by Director'}
            res = self.client().patch('/movies/1', json=update_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['movie']['title'], 'Updated by Director')

    def test_director_cannot_create_movie(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            new_movie = {'title': 'New Movie', 'release_date': '2024-01-01'}
            res = self.client().post('/movies', json=new_movie)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_director_cannot_delete_movie(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            res = self.client().delete('/movies/1')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 403)
            self.assertEqual(data['success'], False)

    def test_director_can_create_actor(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            new_actor = {'name': 'Director Created Actor', 'birth_date': '1990-01-01', 'gender': 'Male'}
            res = self.client().post('/actors', json=new_actor)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['actor']['name'], 'Director Created Actor')

    def test_director_can_update_actor(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            update_data = {'name': 'Updated by Director'}
            res = self.client().patch('/actors/1', json=update_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['actor']['name'], 'Updated by Director')

    def test_director_can_delete_actor(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            res = self.client().delete('/actors/5')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['deleted'], 5)

    def test_director_can_assign_actor_to_movie(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            res = self.client().post('/movies/2/actors/5')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['success'], True)

    def test_director_can_remove_actor_from_movie(self):
        director_permissions = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_permissions)):
            self.client().post('/movies/2/actors/4')
            res = self.client().delete('/movies/2/actors/4')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_producer_can_create_movie(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            new_movie = {'title': 'Producer Movie', 'release_date': '2024-01-01'}
            res = self.client().post('/movies', json=new_movie)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['movie']['title'], 'Producer Movie')

    def test_producer_can_update_movie(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            update_data = {'title': 'Updated by Producer'}
            res = self.client().patch('/movies/1', json=update_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['movie']['title'], 'Updated by Producer')

    def test_producer_can_delete_movie(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            res = self.client().delete('/movies/4')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['deleted'], 4)

    def test_producer_can_create_actor(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            new_actor = {'name': 'Producer Actor', 'birth_date': '1990-01-01', 'gender': 'Female'}
            res = self.client().post('/actors', json=new_actor)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['actor']['name'], 'Producer Actor')

    def test_producer_can_update_actor(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            update_data = {'name': 'Updated by Producer'}
            res = self.client().patch('/actors/2', json=update_data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['actor']['name'], 'Updated by Producer')

    def test_producer_can_delete_actor(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            res = self.client().delete('/actors/3')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
            self.assertEqual(data['deleted'], 3)

    def test_producer_can_assign_actor_to_movie(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            res = self.client().post('/movies/1/actors/5')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 201)
            self.assertEqual(data['success'], True)

    def test_producer_can_remove_actor_from_movie(self):
        producer_permissions = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]
        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_permissions)):
            self.client().post('/movies/1/actors/4')
            res = self.client().delete('/movies/1/actors/4')
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)

    def test_permission_matrix_movies(self):
        readonly_perms = ['get:movies', 'get:actors']

        director_perms = [
            'get:movies', 'patch:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]

        producer_perms = [
            'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
            'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
            'post:casting', 'delete:casting',
            'get:users', 'post:users', 'patch:users', 'delete:users'
        ]

        for perms in [readonly_perms, director_perms, producer_perms]:
            with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(perms)):
                res = self.client().get('/movies')
                self.assertEqual(res.status_code, 200)

        new_movie = {'title': 'Test', 'release_date': '2024-01-01'}

        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(readonly_perms)):
            res = self.client().post('/movies', json=new_movie)
            self.assertEqual(res.status_code, 403)

        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(director_perms)):
            res = self.client().post('/movies', json=new_movie)
            self.assertEqual(res.status_code, 403)

        with patch('src.auth.auth.requires_auth', side_effect=self.create_mock_auth(producer_perms)):
            res = self.client().post('/movies', json=new_movie)
            self.assertEqual(res.status_code, 201)


if __name__ == "__main__":
    unittest.main()
