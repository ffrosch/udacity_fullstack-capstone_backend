import json
from flask import request
from jose import jwt
from os import environ
from urllib.request import urlopen


AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN', 'sturmpuls.eu.auth0.com')
ALGORITHMS = ['RS256']
API_AUDIENCE = environ.get('API_AUDIENCE', 'udacity-capstone-backend')


class AuthError(Exception):
    '''A standardized way to communicate auth failure modes'''

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    '''Get Auth header and return token part.

    Raise exception if Auth header not present or not valid.'''

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


def verify_decode_jwt(token):
    '''Validate and decode Auth0 jwt token using Auth0 /.well-known/jwks.json.

    Parameters:
        token: Auth0 token with key id kid

    Returns:
        payload: decoded jwt payload'''

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


def user_status(f):
    def decorator(*args, **kwargs):
        user = {'auth': False,
                'permissions': [],
                'id': None}
        try:
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            user['auth'] = True
            user['permissions'] = payload['permissions']
            user['id'] = payload['sub']
        except AuthError as e:
            print(e)
            pass
        return f(*args, user=user, **kwargs)
    return decorator