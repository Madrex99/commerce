from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max

from .models import User, Listings, Category, Bids, Auction, Comment


def index(request):
    data = Listings.objects.all()
    return render(request, "auctions/index.html", {
        "data": data,
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


def newlisting(request):
    options = Category.objects.all()
    if request.method == "POST":
        title = request.POST["title"]
        text = request.POST["text"]
        price = request.POST["price"]
        image = request.POST["image"]
        user = request.user

        category = request.POST.get("category")
        
        if category:
            category_id = Category.objects.get(categoryname=category)
        else:
            return render(request, "auctions/newlisting.html", {
                "options": options,
                "error_message": "Must Proviide Category"
            })


        data = Listings(
            title = title,
            text = text,
            price = float(price),
            image = image,
            user = user,
            category = category_id
        )
        data.save()

        return(HttpResponseRedirect(reverse("index")))
    

    return render(request, "auctions/newlisting.html", {
        "options": options
    })


def listing(request, product_id):
    listing = get_object_or_404(Listings, pk=product_id)
    user = request.user

    watchlisted = listing.watchlist.filter(id=user.id).exists()

    close = False

    if user == listing.user:
        close = True
    else:
        close = False
    
    try:
        comments = Comment.objects.filter(listing = listing)
    except:
        messages.error(login_required, "There is no auction won!")
        return HttpResponseRedirect(reverse("listing", args=(product_id,)))
        

    if listing:

        return render(request, "auctions/listing.html", {
            "data": listing,
            "watchlisted": watchlisted,
            "close": close,
            "comments": comments
        })



@login_required
def watchlist(request, product_id):

    if request.method == "POST":
        listing = Listings.objects.get(pk=product_id)
        user = request.user

        action = request.POST.get('action')

        if action == "add":
            listing.watchlist.add(user)
        elif action == "remove":
            listing.watchlist.remove(user)
        
        
        return HttpResponseRedirect(reverse("listing", args=(product_id,)))
    
@login_required
def watchlist_page(request):

    user = request.user
    try:
        listings = Listings.objects.filter(watchlist=user)
    except:
        messages.error(login_required, "There is no bid on that listing")
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/watchlist.html", {
        "data": listings
    })
    

@login_required
def bid_function(request, product_id):

    if request.method == "POST":
        bid = request.POST.get('new_bid')
        listing = get_object_or_404(Listings, pk=product_id)
        user = request.user
        bid_model = Bids.objects.filter(user=user, id=product_id)
    
        if listing:
            price = listing.price
            if float(bid) > float(price):

                if not bid_model:
                    data = Bids(
                        id = product_id,
                        bid = bid,
                        user = user,
                        listingbid = listing
                    )
                    data.save()
                    listing.price = bid
                    listing.save()
                    messages.success(request, "The bid is successfully placed")
                    return HttpResponseRedirect(reverse("listing", args=(product_id,)))
                

                else:

                    bid_model.delete()
                    data = Bids(
                        id = product_id,
                        bid = bid,
                        user = user,
                        listingbid = listing
                    )
                    data.save()
                    listing.price = bid
                    listing.save()
                    messages.success(request, "The bid is successfully placed")
                    return HttpResponseRedirect(reverse("listing", args=(product_id,)))
            else:
                messages.error(login_required, "The bid must be greater than the current price!")
                return HttpResponseRedirect(reverse("listing", args=(product_id,))) 

        else:
            return HttpResponse("no such listing")
    

@login_required
def end_bid(request, product_id):
    if request.method == 'POST':
        try:
            listing = Listings.objects.get(pk=product_id)
        except:
            return HttpResponseRedirect(reverse("index"))
        user = request.user
        try:
            bids = Bids.objects.filter(listingbid=listing)
        except:
            messages.error(login_required, "There is no bid on that listing")
            return HttpResponseRedirect(reverse("listing", args=(product_id,)))
        
        highest_bid = bids.order_by('-bid').first()
        try:
            highest_bidder = highest_bid.user
        except:
            return HttpResponseRedirect(reverse("index"))

        data = Auction(
            id = product_id,
            title = listing.title,
            text = listing.text,
            price = highest_bid.bid, 
            image = listing.image,
            user = highest_bidder,
            category = listing.category
        )

        data.save()
        listing.delete()

        win_auction = Auction.objects.filter(user=user)
        return render(request, "auctions/auctionlist.html", {
            "data": win_auction
        })
    else:
       
        try:
            auction_won = Auction.objects.filter(id=product_id)
        except:
            return HttpResponseRedirect(reverse("index"))
        if auction_won.exists():
            data1 = auction_won.first()
        print(auction_won)
        return render(request, "auctions/auctions.html", {
            "data": data1
        })
    
@login_required
def auction_page(request):
    user = request.user
    try:
        listings = Auction.objects.filter(user=user)
    except:
        messages.error(login_required, "There is no auction won!")
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/auctionlist.html", {
        "data": listings
    })

@login_required
def comment(request, product_id):
    if request.method == "POST":
        user = request.user
        comment = request.POST.get('comment') 
        try:
            listing = Listings.objects.get(pk=product_id)
        except:
            return HttpResponseRedirect(reverse("index"))
        
        new_comment = Comment(
            listing = listing,
            user = user,
            comment = comment
        )
        new_comment.save()

        return HttpResponseRedirect(reverse("listing", args=(product_id,)))
    
    
@login_required
def categories(request):
    user = request.user

    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_re(request, category):

    try:
        category = Category.objects.get(categoryname=category)
        
    except:
        return HttpResponseRedirect(reverse("index"))
    
    listings = Listings.objects.filter(category=category)

    return render(request, "auctions/index.html", {
        "data": listings
    })