from django.db import models

# Create your models here.
class App(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    icon_path = models.ImageField(upload_to='icons/')
    zip_path = models.FileField(upload_to='zip/', null=True, blank=True)
    unzip_path = models.CharField(max_length=255, null=True, blank=True)
    script = models.CharField(max_length=255, null=True, blank=True)
    
