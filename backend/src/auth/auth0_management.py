import os
import requests
from flask import request, abort


# Auth0 Management API Configuration
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 'dev-dzv8dgf6ff6qu41d.us.auth0.com')
AUTH0_MGMT_CLIENT_ID = os.environ.get('AUTH0_MGMT_CLIENT_ID', 'OZnaJGx6Gy4jCrgR7iaBMnzEr9kNyjRO')
AUTH0_MGMT_CLIENT_SECRET = os.environ.get('AUTH0_MGMT_CLIENT_SECRET', 'fvuraaCQHShSaZDvh_bWWqNCz59ZuUTGxG2td04vBm2fKlKDOmLVKAKzuRgPzE-w')
AUTH0_MGMT_AUDIENCE = f'https://{AUTH0_DOMAIN}/api/v2/'


class Auth0ManagementError(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def get_management_api_token():
    url = f'https://{AUTH0_DOMAIN}/oauth/token'

    payload = {
        'client_id': AUTH0_MGMT_CLIENT_ID,
        'client_secret': AUTH0_MGMT_CLIENT_SECRET,
        'audience': AUTH0_MGMT_AUDIENCE,
        'grant_type': 'client_credentials'
    }

    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to get management API token: {str(e)}', 500)


def get_auth0_users(token, page=0, per_page=50, search_query=None):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users'

    headers = {'authorization': f'Bearer {token}'}
    params = {
        'page': page,
        'per_page': per_page,
        'include_totals': 'true'
    }

    if search_query:
        params['q'] = search_query

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to fetch users: {str(e)}', 500)


def get_auth0_user(token, user_id):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users/{user_id}'

    headers = {'authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            raise Auth0ManagementError('User not found', 404)
        raise Auth0ManagementError(f'Failed to fetch user: {str(e)}', 500)


def create_auth0_user(token, email, password, name=None, connection='Username-Password-Authentication'):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users'

    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    payload = {
        'email': email,
        'password': password,
        'connection': connection,
        'email_verified': False
    }

    if name:
        payload['name'] = name

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to create user: {str(e)}', 400)


def update_auth0_user(token, user_id, updates):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users/{user_id}'

    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    try:
        response = requests.patch(url, json=updates, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            raise Auth0ManagementError('User not found', 404)
        raise Auth0ManagementError(f'Failed to update user: {str(e)}', 400)


def delete_auth0_user(token, user_id):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users/{user_id}'

    headers = {'authorization': f'Bearer {token}'}

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            raise Auth0ManagementError('User not found', 404)
        raise Auth0ManagementError(f'Failed to delete user: {str(e)}', 500)


def assign_roles_to_user(token, user_id, role_ids):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users/{user_id}/roles'

    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    payload = {'roles': role_ids}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to assign roles: {str(e)}', 400)


def get_user_roles(token, user_id):
    url = f'https://{AUTH0_DOMAIN}/api/v2/users/{user_id}/roles'

    headers = {'authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to fetch user roles: {str(e)}', 500)


def get_all_roles(token):
    url = f'https://{AUTH0_DOMAIN}/api/v2/roles'

    headers = {'authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Auth0ManagementError(f'Failed to fetch roles: {str(e)}', 500)
