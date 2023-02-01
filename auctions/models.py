from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1000)
    active = models.BooleanField(),
    image = models.URLField(max_length=500),
    category = models.CharField(max_length=64),
    creator = FOREIGN 
    winner = FOREIGN
    comments = FOREIGN,
    # CHECK IF MINIMUM WORKS
    startingBid = models.DecimalField(max_digits=9, decimal_places=2, min=0)
    bids = FOREIGN,
    highestBid = FOREIGN,
    # EXTRA
    dateCreated = models.DateField()
    numbersViews = models.IntegerField

class Bid(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    user = FOREIGN
    listing = FOREIGN
    minimumBid = FOREIGN

class Comment(models.Model):
    listing = FOREIGN
    user = FOREIGN
    content = models.CharField(max_length=1000)

