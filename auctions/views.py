from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Comment, Bid
from django.forms import ModelForm
from django.db.models import Max, Subquery, OuterRef


def index(request):

    highest_bids = Bid.objects.filter(listing=OuterRef('pk')).order_by('-price')
    listings_with_highest_bids = Listing.objects.annotate(
        highest_bid=Subquery(highest_bids[:1].values('price')))

    return render(request, "auctions/index.html", {
        "listings": listings_with_highest_bids
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'image']

def create_listing(request):
    # For a post request, add a new flight
    if request.method == "POST": 
        # add the dictionary during initialization
        form = ListingForm(request.POST)
        if form.is_valid():
            Listing = form.save(commit=False)
            Listing.seller = request.user
            Listing.save()
            return HttpResponseRedirect(reverse('auctions:index'))  
        else:
            print("form not valid")    
            return HttpResponseRedirect(reverse('auctions:create_listing'))  


    else: 
        return render(request, "auctions/create_listing.html", {
        "form": ListingForm(),
    })

def listing(request, id):
    highest_bid = Bid.objects.filter(listing=id).aggregate(Max('price'))
    users_watching = Listing.objects.get(pk=id).watchlist.all()
    print(users_watching)
    print(request.user)
    if users_watching == None:
        watchlist = False    
    else:
        if request.user in users_watching:
            watchlist = True
        else:           
            watchlist = False    
    print(watchlist) 
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(pk=id),
        "current_price": highest_bid,
        "watchlist": watchlist
    })
           
def watchlist(request):
    if request.method == "POST": 
        listing_id = request.POST.get("listing_id")
        listing = Listing.objects.get(id=listing_id)
        user = request.user
        print(request.POST.get("remove"))
        print(request.POST.get("remove"))
        if request.POST.get("remove"):
            listing.watchlist.remove(user)
            print(listing)
            print("user removed")

        else:
            listing.watchlist.add(user)  
            print("user added")
  
        listing.save()
        return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))  

    else: 
        pass
    



