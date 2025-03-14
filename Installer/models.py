from django.db import models
from django.contrib.auth.models import User

class App(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Added price field
    icon_path = models.ImageField(upload_to='icons/')
    zip_path = models.FileField(upload_to='zip/', null=True, blank=True)
    unzip_path = models.CharField(max_length=255, null=True, blank=True)
    script = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class UserPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=64, unique=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])

    def __str__(self):
        return f"{self.user.username} - {self.app.name} ({self.status})"