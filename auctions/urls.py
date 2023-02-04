from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<str:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("close_auction", views.close_auction, name="close_auction"),
    path("comment", views.comment, name="comment"),
    path("index_categories", views.index_categories, name="index_categories"),
]
