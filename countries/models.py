from django.db import models


# Create your models here.

class Countries(models.Model):
    index = models.PositiveBigIntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=200, verbose_name="Country Name")
    languages = models.CharField(max_length=200, verbose_name="Country Languages")
    population = models.CharField(max_length=200, verbose_name="Country Population")
    sha1 = models.CharField(max_length=200, verbose_name="Country Encrypt Name")

    class Meta:
        db_table = 'countries'
