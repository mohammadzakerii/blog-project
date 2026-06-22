from django.utils.deprecation import MiddlewareMixin
import jwt
from blog.settings import SECRET_KEY
from datetime import datetime, timedelta,timezone
from account.models import BlacklistedToken, User
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from datetime import datetime



class JwtauthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/admin/"):
             return
        auth_header = request.headers.get("Authorization")

        
        if not (auth_header and auth_header.startswith("Bearer ")):
            return

        token = auth_header.split(" ", 1)[1]

        if BlacklistedToken.objects.filter(token=token).exists():
            return JsonResponse({"error": "token blacklisted"}, status=401)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                request.user = AnonymousUser()
                return

            request.user = User.objects.get(id=user_id)

        # except Exception as e:
        #     print("ERROR:", e)
        #     request.user = AnonymousUser
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            request.user = AnonymousUser()
            return
