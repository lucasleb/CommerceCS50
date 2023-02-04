# Register your models here.
from django import forms

from django.contrib import admin
from .models import Listing, User, Comment, Bid



class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "seller", "category", "is_active",  "number_of_views",  "created_at",)

class BidAdmin(admin.ModelAdmin):
    def listing_title(self, obj):
        return obj.listing.title
    listing_title.short_description = 'Listing Title'
    listing_title.admin_order_field = 'listing__title' 

    list_display = ("id", "listing_title", "bidder", "price", "created_at")

class CommentAdmin(admin.ModelAdmin):
    def listing_title(self, obj):
        return obj.listing.title
    listing_title.short_description = 'Listing Title'
    listing_title.admin_order_field = 'listing__title' 
    list_display = ("id", "listing_title", "author", "created_at")
    raw_id_fields = ['listing']



class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "date_joined",)

# Register your models here.
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(User, UserAdmin)


