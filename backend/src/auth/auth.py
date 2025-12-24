import json
from flask import request
from functools import wraps
from jose import jwt
import os
from urllib.request import urlopen

AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 'dev-dzv8dgf6ff6qu41d.us.auth0.com')
ALGORITHMS = ['RS256']
API_AUDIENCE = os.environ.get('API_AUDIENCE', 'casting-agency')
SKIP_AUTH = os.environ.get('SKIP_AUTH', 'False').lower() == 'true'

'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'You are not authorized to perform this action.'
        }, 403)

    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Skip all auth if SKIP_AUTH is enabled
            if SKIP_AUTH:
                mock_payload = {
                    'permissions': [
                        'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
                        'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
                        'post:casting', 'delete:casting',
                        'get:users', 'post:users', 'patch:users', 'delete:users'
                    ]
                }
                return f(mock_payload, *args, **kwargs)

            # Public endpoints that don't require auth
            public_permissions = ['get:movies', 'get:actors']

            # For public endpoints, try to get token but don't fail if missing
            if permission in public_permissions:
                try:
                    token = get_token_auth_header()
                    payload = verify_decode_jwt(token)
                    # Token is valid, use it
                    return f(payload, *args, **kwargs)
                except AuthError:
                    # No token or invalid token, use public payload
                    public_payload = {'permissions': public_permissions}
                    return f(public_payload, *args, **kwargs)

            # Protected endpoints require valid token
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator