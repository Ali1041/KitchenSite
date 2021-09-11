from django.db import models


# Create your models here.
class UploadFile(models.Model):
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    file = models.FileField(db_index=True,upload_to='files')

    def __str__(self):
        return self.name
