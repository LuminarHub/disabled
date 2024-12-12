from django.db import models
from django.contrib.auth.models import User,AbstractUser
import os
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
# Create your models here.

def user_directory_path(instance, filename):
    """
    This function renames the uploaded image file to the username of the user.
    """
    extension = filename.split('.')[-1]  
    new_filename = f"{instance.std_id}.{extension}"  
    return os.path.join('student image', new_filename) 


class CustomUserManager(BaseUserManager):
    def create_user(self, email,password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email ,**extra_fields)
        if password:
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValueError(f"Password validation error: {e.messages}")
            user.set_password(password)
        else:
            raise ValueError("Password is required")
        user.save(using=self._db)
        return user

    def create_superuser(self, email,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email,password, **extra_fields)


class CustUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_faculty=models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['email']

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return self.email

class Subject(models.Model):
    subject_name=models.CharField(max_length=100)

    def __str__(self):
        return self.subject_name

class Faculty(CustUser):
    name=models.CharField(max_length=100)
    options=( 
        ("Male","Male"),
        ("Female","Female"),
        ("Others","Others")
    )
    gender=models.CharField(max_length=100,choices=options,default="Male")
    age=models.IntegerField() 
    exp=models.IntegerField(default=1) 
    image=models.ImageField(upload_to="Faculty Image",null=True)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
    

    def __str__(self):
        return self.name

class Class_Name(models.Model):
    class_name=models.CharField(max_length=100)
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE)

    def __str__(self):
        return self.class_name

class Student(CustUser):
    std_id=models.CharField(unique=True,max_length=50)
    student_name=models.CharField(max_length=100,null=True,blank=True)
    img=models.FileField(upload_to=user_directory_path,null=True,blank=True)
    options=( 
        ("Male","Male"),
        ("Female","Female"),
        ("Others","Others")
    )
    gender=models.CharField(max_length=100,choices=options,default="Male")
    age=models.PositiveIntegerField(null=True)
    class_id=models.ForeignKey(Class_Name,on_delete=models.CASCADE)

    def __str__(self):
        return self.std_id 
    

class  Exam(models.Model):
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE)
    exam_name=models.CharField(max_length=100)

    def __str__(self):
        return self.exam_name
    
class ExamQuestions(models.Model):
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
    question=models.TextField()
    option_1=models.CharField(max_length=200)
    option_2=models.CharField(max_length=200)
    option_3=models.CharField(max_length=200)
    option_4=models.CharField(max_length=200)
    answer=models.CharField(max_length=200)

    def __str__(self):
        return self.question

class AssignExam(models.Model):
    faculty=models.ForeignKey(Faculty,on_delete=models.CASCADE)
    exam=models.ForeignKey(Exam,on_delete=models.CASCADE)
    class_id=models.ForeignKey(Class_Name,on_delete=models.CASCADE)
    time=models.TimeField()

    def __str__(self):
        return self.class_id.class_name


class ExamResult(models.Model):
    assignedexam=models.ForeignKey(AssignExam,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    question=models.ForeignKey(ExamQuestions,on_delete=models.CASCADE,related_name='exam_ques')
    ans=models.ForeignKey(ExamQuestions,on_delete=models.CASCADE,related_name='student_answer')
    is_correct=models.BooleanField(null=True,blank=True,default=False)

    def __str__(self):
        return self.assignedexam.exam.exam_name
   
    
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name     
    
class Categorys(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name     


    

class ScoreModel(models.Model):
    assignedexam=models.ForeignKey(AssignExam,on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,related_name='score_student')
    score = models.IntegerField(blank=True,null=True)
    cat = models.ForeignKey(Categorys,on_delete=models.CASCADE,null=True,blank=True)
    suggestion=models.TextField(null=True,blank=True) 
    video=models.FileField(upload_to='suggested video',null=True,blank=True)

    def __str__(self):
        return self.student.student_name

  
class Suggestion(models.Model):
     suggestion=models.TextField(null=True)  
     cat=models.ForeignKey(Categorys,on_delete=models.CASCADE,related_name='sugg')  
     video=models.FileField(upload_to='suggested video',null=True)
     thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
     
     def __str__(self):
        return self.cat.name
        




 


