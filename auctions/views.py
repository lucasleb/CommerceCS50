from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import User, Listing, Comment, Bid
from django.forms import ModelForm
from django.db.models import Max, Subquery, OuterRef
from django.core.exceptions import ValidationError
import decimal
from django.contrib.auth.decorators import login_required




def get_highest_bidder(listing_id):
    highest_bid = Bid.objects.filter(listing=listing_id).order_by('-price').first()
    if highest_bid:
        return highest_bid.bidder.username
    return None


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_price', 'image', 'category']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']





def index(request):

    highest_bids = Bid.objects.filter(listing=OuterRef('pk')).order_by('-price')
    listings_with_highest_bids = Listing.objects.annotate(highest_bid=Subquery(highest_bids[:1].values('price')))

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
            return HttpResponseRedirect(reverse('auctions:index'))  
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('auctions:index'))  



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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")



@login_required
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
    listing = get_object_or_404(Listing, id=id)
    highest_bid = Bid.objects.filter(listing=id).aggregate(Max('price'))['price__max']
    users_watching = Listing.objects.get(pk=id).watchlist.all()
    highest_bidder = get_highest_bidder(id)    
    added_to_watchlist = request.user in users_watching
    comments = Comment.objects.filter(listing=id).all()

    if 'has_viewed_listing_{}'.format(id) not in request.session:
        request.session['has_viewed_listing_{}'.format(id)] = True
        listing.number_of_views += 1
        listing.save()

    bid_message = request.session.get('bid_message', '')
    request.session['bid_message'] = ''


    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(pk=id),
        "current_price": highest_bid,
        "added_to_watchlist": added_to_watchlist,
        "bid": BidForm(),
        "bid_message": bid_message,
        "highest_bidder": highest_bidder,
        "new_comment": CommentForm(),
        "comments": comments,
    })

@login_required   
def watchlist(request):
    if request.method == "POST": 
        listing_id = request.POST.get("listing_id")
        listing = Listing.objects.get(id=listing_id)
        user = request.user
        if request.POST.get("remove"):
            listing.watchlist.remove(user)
        else:
            listing.watchlist.add(user)  
        listing.save()
        return HttpResponseRedirect(reverse('auctions:listing', args=(listing_id, )))  

    else: 
        highest_bids = Bid.objects.filter(listing=OuterRef('pk')).order_by('-price')
        watchlist = Listing.objects.filter(watchlist=request.user).annotate(highest_bid=Subquery(highest_bids[:1].values('price')))
        return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
    })
    


@login_required   
def bid(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        form = BidForm(request.POST)

        if form.is_valid():

            newBid = form.save(commit=False)
            newBid.bidder = request.user
            newBid.listing = Listing.objects.get(id=listing_id)

            highest_bid = Bid.objects.filter(listing=listing_id).aggregate(Max('price'))['price__max']
            starting_price = Listing.objects.get(pk=listing_id).starting_price
            current_bid = decimal.Decimal(form['price'].value())

            if highest_bid:  
                if current_bid > highest_bid:
                    newBid.save()
                    request.session['bid_message'] = "Your bid was successfully registered!"
                    return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))
                else:
                    request.session['bid_message'] = "Error: Your bid must be higher than the current highest bid."
                    return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))
            else: 
                if current_bid > starting_price:
                    newBid.save()
                    request.session['bid_message'] = "Your bid was successfully registered!"
                    return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))
                else:
                    request.session['bid_message'] = "Error: Your bid must be higher than the starting price"
                    return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))
        else:
            pass
    else: 
        pass

@login_required   
def close_auction (request):
    if request.method == "POST": 
        listing_id = request.POST.get("listing_id")
        listing = Listing.objects.get(id=listing_id)
        listing.is_active = False

        highest_bid = Bid.objects.filter(listing=listing_id).order_by('-price').first()
        print (highest_bid)

        if highest_bid:
            winner = highest_bid.bidder
            print (winner)
            listing.winner = winner

        

        listing.save()
        return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))

@login_required  
def comment (request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        form = CommentForm(request.POST)
        if form.is_valid():
            newComment = form.save(commit=False)
            newComment.author = request.user
            newComment.listing = Listing.objects.get(id=listing_id)
            newComment.save()
            return HttpResponseRedirect(reverse('auctions:listing', args=({listing_id})))
        else: 
            pass
    else: 
        pass    
        

def index_categories(request):
    categories = dict.fromkeys((Listing.objects.values_list('category', flat=True)))
    print(categories)
    return render(request, "auctions/index_categories.html", {
        "categories": categories,
    })

def category_search(request, category):
    listings = Listing.objects.filter(category=category).order_by('created_at')
    return render(request, "auctions/category_search.html", {
        "category": category,
        "listings": listings,
    })