import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for certain paths
        skip_paths = ['/admin/', '/graphql/', '/api/auth/']
        
        if any(request.path.startswith(path) for path in skip_paths):
            response = self.get_response(request)
            return response

        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = User.objects.get(id=payload['user_id'])
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
                request.user = None
        else:
            request.user = None

        response = self.get_response(request)
        return response