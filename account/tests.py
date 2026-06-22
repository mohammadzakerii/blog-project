from django.test import TestCase
from django.urls import reverse
import json
from account.models import User, Otp
from datetime import *
from django.utils import timezone
import jwt
from blog.settings import SECRET_KEY

# Create your tests here.

class UserTest(TestCase):
    def setUp(self):
        self.user_instance = User.objects.create_superuser(phone="09121234567", password="123456789", fullname="mohammadzakeri")
        self.user_instance2 = User.objects.create_user(phone="09122344527", password="123456789", fullname="alinazari")
        self.access_payload = {
             "user_id":self.user_instance.id,
             "exp":timezone.now() + timedelta(minutes=5),
             "iat":timezone.now()
             }
        self.access_token = jwt.encode(self.access_payload, SECRET_KEY, algorithm = "HS256")
        self.refresh_payload = {
             "user_id":self.user_instance.id,
             "exp":timezone.now() + timedelta(days=1),
             "iat":timezone.now()
             }
        self.refresh_token = jwt.encode(self.refresh_payload, SECRET_KEY, algorithm = "HS256")
        
    def test_register(self):
        data={
            "fullname":"alinazari",
            "phone":"09121234568",
            "password":"123456789",
            "password2":"123456789"
        }
        response = self.client.post(reverse("register"), data=json.dumps(data), content_type = "application/json")
        self.assertEqual(response.status_code, 201)

    def test_list_users(self):
        self.client.force_login(self.user_instance)
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 200)

    def test_retreive_user(self):
        response = self.client.get(reverse("user_detail", kwargs={'pk':self.user_instance.id}))
        self.assertEqual(response.status_code, 200)  

    def test_update_user(self):
        data={
            "fullname":"mohammad_z",
            "phone":"09123456789",
        }     
        self.client.force_login(self.user_instance)
        response = self.client.put(reverse("user_detail", kwargs={"pk":self.user_instance.id}), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_delete_user(self):
        self.client.force_login(self.user_instance)
        response = self.client.delete(reverse("user_detail", kwargs={"pk":self.user_instance.id}))
        self.assertEqual(response.status_code, 200) 

    def test_login(self):
        data={
            "phone":"09121234567",
            "password":"123456789"
        }
        response = self.client.post(reverse("login_user"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)


    def test_refresh_token(self):
        data = {
            "refresh_token":self.refresh_token
        }
        response = self.client.post(reverse("refresh_access_token"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.post(reverse("logout_user"), headers={"Authorization":f"Bearer {self.access_token}"})
        self.assertEqual(response.status_code, 200)


class OtpRegisterLogin(TestCase):
    def setUp(self):
        self.user_instance = User.objects.create_user(phone="09121234567", password="123456789", fullname="mohammadzakeri")

    def test_RegisterOrLogin_authenticatedUser(self):
        data={
            "phone":"09121234567"
        }
        self.client.force_login(self.user_instance)
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_RegisterOrLogin(self):
        data={
            "phone":"09121234567"
        }
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200) 

    def test_RegisterLoginOtpNoPhone(self):
        data={}
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_daily_limit_reacched(self):
        for i in range(5):
            Otp.objects.create(
                phone="09123456789",
                code=1234,
                token=f"test_token{i}",
                failed=True
            )
            
        response = self.client.post(reverse("register_login_otp"), data=json.dumps({"phone":"09123456789"}), content_type="application/json")
        self.assertEqual(response.status_code, 429)
    def test_less_2minutes_otp(self):
        otp = Otp.objects.create(phone="09123456789", code=1234, token="test-token")
        last_otp = Otp.objects.filter(phone=otp.phone).order_by("-created_at").first()
        last_otp.created_at = timezone.now() - timedelta(minutes=1)
        last_otp.save()
        response = self.client.post(reverse("register_login_otp"), data=json.dumps({"phone":"09123456789"}), content_type="application/json")
        self.assertEqual(response.status_code, 429)

    def test_more_than_2minutes_otp(self):
        otp = Otp.objects.create(phone="09123456789", code=1234, token="test-token")
        last_otp = Otp.objects.filter(phone=otp.phone).order_by("-created_at").first()
        last_otp.created_at = timezone.now() - timedelta(minutes=3)
        last_otp.save()
        response = self.client.post(reverse("register_login_otp"), data=json.dumps({"phone":"09123456789"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)    


class CheckOtpTest(TestCase):

    def test_otp(self):
        response = self.client.post(
            reverse("register_login_otp"),
            data=json.dumps({"phone":"09397795348"}), content_type="application/json")
        otp = Otp.objects.last()
        response= self.client.post(
            reverse("check_otp"), data = json.dumps({"code": otp.code}),
            content_type="application/json", headers={"token":otp.token})
        self.assertEqual(response.status_code, 200)
                         
    def test_otp_no_token(self):
        data={"phone":"09397795348"}
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        otp = Otp.objects.last()
        data2= {"code":otp.code}
        response = self.client.post(reverse("check_otp"), data=json.dumps(data2), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_otp_invalid_token(self):
        data={"phone":"09397795348"}
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        otp = Otp.objects.first()
        data2= {"code":otp.code}
        response = self.client.post(
            reverse("check_otp"),
            data=json.dumps(data2), content_type="application/json", 
            headers={"token":"token that doesnt exists"})
        self.assertEqual(response.status_code, 400)    

    def test_otp_wrong_code(self):
        data={"phone":"09397795348"}
        response = self.client.post(reverse("register_login_otp"), data=json.dumps(data), content_type="application/json")
        otp = Otp.objects.get(phone="09397795348")
        data2= {"code":"123"}
        response = self.client.post(
            reverse("check_otp"),
            data=json.dumps(data2), content_type="application/json", 
            headers={"token":otp.token})
        self.assertEqual(response.status_code, 400)

    def test_otp_expired(self):
        otp=Otp.objects.create(phone="09397795348", code=1234, token="test-token")
        otp.created_at = timezone.now() - timedelta(minutes=3)
        otp.save()
        response= self.client.post(
        reverse("check_otp"), data=json.dumps({"code":otp.code}),
        content_type= "application/json", headers={"token":otp.token})
        self.assertEqual(response.status_code, 400)

    def test_otp_5attemps(self):    
        otp=Otp.objects.create(phone="09397795348", code=1234, token="test-token")
        otp.attempts = 5
        otp.save()
        response= self.client.post(
        reverse("check_otp"), data=json.dumps({"code":otp.code}),
        content_type= "application/json", headers={"token":otp.token})
        self.assertEqual(response.status_code, 429)

    def test_otp_success(self):
        otp = Otp.objects.create(phone="09102345678", code=1234, token="test-token")
        response = self.client.post(
        reverse("check_otp"), data= json.dumps({"code":1234}), content_type="application/json", headers={"token":"test-token"})
        self.assertEqual(response.status_code, 200)    







