from account.models import User, Profile, Otp
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import jwt
from blog.settings import SECRET_KEY
from datetime import datetime, timedelta
from django.contrib.auth import logout
from account.models import BlacklistedToken
from django.contrib.auth import get_user_model
from django.views import View
from random import randint
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils import timezone

# User = get_user_model()

@csrf_exempt
def register(request):
    if request.method == "POST":
        if request.user.is_authenticated:
          return JsonResponse({"error": "an authenticated user cant register again"}, status=403)
        data = json.loads(request.body)
        fullname = data.get("fullname")
        password = data.get("password")
        password2 = data.get("password2")
        email = data.get("email")
        phone = data.get("phone")
        if not fullname or not password or not password2:
            return JsonResponse({"error":"fullname and passwords are required"}, status=400)
        if password != password2:
            return JsonResponse({"error":"password are not same"}, status=400)
        if User.objects.filter(phone=phone).exists():
            return JsonResponse({"error":"not unique phone number"}, status=409)
    
        user = User.objects.create(phone=phone, email=email, fullname=fullname)
        user.set_password(password)
        user.save()
        pay_load = {
             "user_id":user.id,
             "exp":timezone.now() + timedelta(minutes=5),
             "iat":timezone.now()
        }
        token = jwt.encode(pay_load, SECRET_KEY, algorithm = "HS256")
        return JsonResponse({"status":"201","Token":token,"fullname":user.fullname, "email":user.email, "phone":user.phone}, status=201)

def users_list(request):
    if request.method =="GET":
        if not request.user.is_authenticated:
             return JsonResponse({"error":"not authenticated"}, status=401)
        elif not request.user.is_staff:
             return JsonResponse({"error":"you dont have permission"}, status=403)
        users = User.objects.all()
        data=[{"id":u.id,"phone":u.phone, "fullname":u.fullname, 'email':u.email}for u in users]
        return JsonResponse({"users":data}, status=200, safe=False)
@csrf_exempt
def user_detail(request, pk):
    if request.method == "GET":
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return JsonResponse({"status":"404"}, status=404)
        

            
        
        return JsonResponse({"phone":user.phone, "fullname":user.fullname, "email":user.email}, status=200)
    
    if request.method =='PUT':
        
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return JsonResponse({"error":"404"}, status=404)
        if  not request.user.is_authenticated:
             return JsonResponse({"error":"not authenticated"}, status=401)
        elif request.user != user and not request.user.is_staff:
             return JsonResponse({"error":"you dont have permission"}, status=403)
        data = json.loads(request.body)
        phone = data.get("phone")
        email = data.get("email")
        fullname=data.get("fullname")
        password = data.get("password")
        password2= data.get("password2")
        if phone:
                if User.objects.filter(phone=phone).exists():
                    return JsonResponse({"error": "not unique"})
                user.phone = phone
        if email:
                user.email = email
        if fullname:
                user.fullname=fullname
        if password:
            if password != password2:
               return JsonResponse({"error":"password are not same"}, status=400)
            else:
                user.set_password(password)
        user.save()       

        return JsonResponse({"status":"200", "phone":user.phone, "email":user.email, "fullname":user.fullname}, status=201)    


    if request.method == "DELETE":
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return JsonResponse({"status":"404"},status=404)    
        if not request.user.is_authenticated:
             return JsonResponse({"error":"not authenticated"}, status=401)
        elif request.user != user and not request.user.is_staff:
             return JsonResponse({"error":"you dont have permission"}, status=403)
        user.delete()
        return JsonResponse({"message":"deleted"}, status=200)

    
@method_decorator(csrf_exempt, name="dispatch")
class RegisterLoginOtp(View):
     def post(self,request):
          Otp.objects.filter(created_at__lt = timezone.now() - timedelta(days=1)).delete() 
          if request.user.is_authenticated:
               return JsonResponse({"error":"you are authenticated"}, status=403)
          data = json.loads(request.body)
          phone = data.get("phone")
          if not phone:
               return JsonResponse({"error":"phone number is required"}, status=400)
          today= timezone.now().date()
          
          failed_count =Otp.objects.filter(phone=phone, failed=True, created_at__date=today).count()
          if failed_count >= 5:
               return JsonResponse({"error":"daily limit reached"}, status=429)
          last_otp = Otp.objects.filter(phone=phone).order_by("-created_at").first()
          if last_otp:
               if timezone.now() - last_otp.created_at < timedelta(minutes=2):
                    return JsonResponse({"error":"wait 2 minutes before requesting a new code"}, status=429)
               
     
          token = get_random_string(length=100)
          code = randint(1000,9999)     
          otp_obj = Otp.objects.create(phone=phone, code=code, token=token)
          print("token:",otp_obj.token)
          print("code:", otp_obj.code)
          return JsonResponse({"message":"otp sent","token":otp_obj.token}, status=200)
     
@method_decorator(csrf_exempt, name="dispatch")
class CheckOtp(View):
     def post(self,request):
          data= json.loads(request.body)
          code = data.get("code")
          token = request.headers.get("token")

          if not token:
               return JsonResponse({"error":"token not provided"}, status=400)
          try:
               otp_obj= Otp.objects.get(token=token)
          except Otp.DoesNotExist:
               return JsonResponse({"error":"invalid token"}, status=400)
          
          if timezone.now() - otp_obj.created_at > timedelta(minutes=2):
               otp_obj.failed = True
               otp_obj.save()
               return JsonResponse({"error":"otp expired"}, status=400)
          if otp_obj.attempts >= 5:
               otp_obj.failed=True
               otp_obj.save()
               return JsonResponse({"error":"too many attemps please wait for 2 minutes to request for a new code"}, status=429)
          if str(code) != str(otp_obj.code):
               otp_obj.attempts += 1
               otp_obj.save()
               return JsonResponse({"error":"invalid code"}, status=400)
          
          user, is_created = User.objects.get_or_create(phone= otp_obj.phone)
          

          access_payload ={
             "user_id":user.id,
             "type": "access",
             "exp":timezone.now() + timedelta(minutes=5),
             "iat":timezone.now()
             }
          access_token = jwt.encode(access_payload, SECRET_KEY, algorithm = "HS256")

          if isinstance(access_token,bytes):
               access_token = access_token.decode("utf-8")

          refresh_payload = {
             "user_id":user.id,
             "type":"refresh",
             "exp":timezone.now() + timedelta(days=1),
             "iat":timezone.now()
             }
          refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm = "HS256")

          if isinstance(refresh_token,bytes):
               refresh_token = refresh_token.decode("utf-8")

          otp_obj.delete()     

          return JsonResponse({"access token":access_token, "refresh token":refresh_token},status=200)

          

               

                              


  
@csrf_exempt
def login_user(request):
     BlacklistedToken.objects.filter(created_at__lt= timezone.now() -timedelta(days=1)).delete()
     if request.method == "POST":
          if request.user.is_authenticated:
               return JsonResponse({"error":"you already loged in"}, status=400)
          data = json.loads(request.body)
          phone = data.get("phone")
          password = data.get("password")
          try:
               user = User.objects.get(phone=phone)
          except User.DoesNotExist:
               return JsonResponse({"status":"404"}, status=404) 
          if not user.check_password(password):
               return JsonResponse({"message":"incorrect password"}, status=400)    
          access_payload = {
             "user_id":user.id,
             "exp":timezone.now() + timedelta(minutes=5),
             "iat":timezone.now()
             }
          access_token = jwt.encode(access_payload, SECRET_KEY, algorithm = "HS256")

          if isinstance(access_token,bytes):
               access_token = access_token.decode("utf-8")

          refresh_payload = {
             "user_id":user.id,
             "exp":timezone.now() + timedelta(days=1),
             "iat":timezone.now()
             }
          refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm = "HS256")

          if isinstance(refresh_token,bytes):
               refresh_token = refresh_token.decode("utf-8")

          return JsonResponse({"access token":access_token, "refresh token":refresh_token},status=200)
          
     else:
          return JsonResponse({"status":"405"},status=405) 

@csrf_exempt
def refresh_access_token(request):
    if request.method == "POST":
         data = json.loads(request.body)
         refresh_token = data.get("refresh_token")

         if not refresh_token:
              return JsonResponse({"error":"refresh token is required"}, status=400)
         try:
              payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
              user_id = payload.get("user_id")
              user = User.objects.get(id=user_id)


              access_payload = {
                   "user_id":user.id,
                   "exp":datetime.now() + timedelta(minutes=5),
                   "iat":datetime.now()
              } 
              access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
              if isinstance(access_token, bytes):
                   access_token = access_token.decode('utf-8')

              return JsonResponse({"access_token":access_token})   
         except jwt.ExpiredSignatureError:
              return JsonResponse({"error":"refresh token expired please login again"}, status=401)
         except jwt.InvalidTokenError:
              return JsonResponse({"error":"invalid refresh token"}, status=401)
         except User.DoesNotExist:
              return JsonResponse({"error":"user not found"}, status=404)
    else:
         return JsonResponse({"error":"just POST method is allowed"})
    
@csrf_exempt
def logout_user(request):
     if request.method =="POST":
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
             token = auth_header.split(" ",1)[1]
             BlacklistedToken.objects.create(token=token)
             return JsonResponse({"message":"you logged out"},status=200)
        else:
             return JsonResponse({"error":"no token provided"}, status=401) 
               
                       
     else:
          return JsonResponse({"error":"request.method not allowed"}, status=405)

               
               

      