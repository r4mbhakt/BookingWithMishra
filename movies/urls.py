# Shivoham Mishra | BTech

from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.movies_page,
        name='movies'
    ),

    path(
        'book/<int:movie_id>/',
        views.book_movie,
        name='book_movie'
    ),

    path(
        'payment/',
        views.payment_page,
        name='payment'
    ),

    path(
        'success/',
        views.success_page,
        name='success'
    ),
    path(
        'my-bookings/',
        views.my_bookings,
        name='my_bookings'
    ),
]