from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.http import JsonResponse
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, phone, password, fullname):
        
        if not phone:
            return JsonResponse({"error":"phone number is required"})
        
        user = self.model(phone = phone, fullname=fullname)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, phone, password, fullname):
        user = self.create_user(
            phone=phone,
            password = password,
            fullname=fullname
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    fullname=models.CharField(max_length=50)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone= models.CharField(max_length=11, unique=True, default='0')
    is_active = models.BooleanField(default=True)
    is_admin= models.BooleanField(default=False)    


    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["fullname"]

    

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name="profile")
    identity_code = models.CharField(max_length=10, unique=True)
    image = models.ImageField(null=True, blank=True)


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500 , unique=True)
    created_at=models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.token  


class Otp(models.Model):
    phone = models.CharField(max_length=11)
    token= models.CharField(max_length=200, unique=True)
    code = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    failed = models.BooleanField(default=True)  

    def __str__(self):
        return self.phone      