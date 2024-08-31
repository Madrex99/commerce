from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.newlisting, name="newlisting"),
    path("listing/<int:product_id>", views.listing, name="listing"),
    path("watchlist/<int:product_id>", views.watchlist, name="watchlist"),
    path("watchlist", views.watchlist_page, name="watchpage"),
    path("bid/<int:product_id>", views.bid_function, name="bid"),
    path("close/<int:product_id>", views.end_bid, name="close"),
    path("auctions", views.auction_page, name="auction"),
    path("comment/<int:product_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category_re, name="category")
]
