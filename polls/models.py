from django.db import models


class Polls(models.Model):
    name = models.CharField(max_length=200)
    question = models.CharField(max_length=200)
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

