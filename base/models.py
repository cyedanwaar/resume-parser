from django.db import models
from uuid import uuid4

# Create your models here.

class ParsedResume(models.Model):
    id = models.UUIDField(primary_key=True ,default=uuid4)
    name = models.CharField(max_length=100, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='uploads/')
    parsed_data = models.JSONField()
    
    def __str__(self):
        return self.name or "untitled_Resume"

    def get_file_url(self):
        return self.resume.url