from django.db import models
from django.contrib.auth.models import User

class Incident(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]

    URGENCY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    CATEGORY_CHOICES = [
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network', 'Network'),
        ('Access', 'Access'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')

    # New fields
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='Medium')

    def __str__(self):
        return f"{self.title} ({self.status})"
