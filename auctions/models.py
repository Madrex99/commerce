from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryname = models.CharField(max_length=24, unique=True)

    def __str__(self):
        return f"{self.categoryname}"


class Listings(models.Model):
    title = models.CharField(max_length=20)
    text = models.CharField(max_length=600, null=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    image = models.URLField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_list")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="caty")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="user_watchlist")

    def __str__(self):
        return f"{self.title} ({self.user})"
    

class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    text = models.CharField(max_length=300, null=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    image = models.URLField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_win")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="cat_win")
   
    def __str__(self):
        return f"{self.user} won the auction on {self.title}"

class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    bid = models.DecimalField(max_digits=12, null=True, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="bid_user")
    listingbid = models.ForeignKey(Listings,on_delete=models.CASCADE, null=True, related_name="listingname")

    def __str__(self):
        return f"{self.user} placed a bid on {self.listingbid} for {self.bid}"

class Comment(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, null=True, related_name="listingcom")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="commentuser")
    comment = models.CharField(max_length=300, null=True)
    timestamp = models.DateTimeField(default=timezone.now, null=True)
    
    def __str__(self):
        return f"{self.user} add a comment on the item id : {self.id} "
