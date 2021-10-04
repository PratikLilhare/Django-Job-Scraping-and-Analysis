from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Plot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    figure = models.ImageField(upload_to='figures/')

    def delete(self, using=None, keep_parents=False):
        self.figure.storage.delete(self.figure.name)
        super().delete()