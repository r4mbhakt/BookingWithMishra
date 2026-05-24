# Shivoham Mishra | BTech

import razorpay
import qrcode

from io import BytesIO

from django.core.files import File

from django.conf import settings

from django.core.mail import send_mail

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required

from .models import Movie
from .models import Booking



# =========================================================
# MOVIES PAGE
# =========================================================

def movies_page(request):

    movies = Movie.objects.all()

    return render(

        request,

        'movies.html',

        {
            'movies': movies
        }
    )




# =========================================================
# BOOK MOVIE
# =========================================================

@login_required(login_url='/login/')
def book_movie(request, movie_id):

    movie = get_object_or_404(

        Movie,

        id=movie_id
    )



    booked_seats = Booking.objects.filter(
        movie=movie
    )



    occupied = []



    for booking in booked_seats:

        seat_list = booking.seats.split(',')

        for seat in seat_list:

            occupied.append(seat)



    if request.method == 'POST':

        name = request.POST.get('name')

        email = request.POST.get('email')

        seats = request.POST.getlist('seats')



        seats_string = ",".join(seats)



        total = movie.price * len(seats)



        # SAVE SESSION

        request.session['movie_id'] = movie.id

        request.session['name'] = name

        request.session['email'] = email

        request.session['seats'] = seats_string

        request.session['total'] = total



        return redirect('/movies/payment/')



    return render(

        request,

        'book_movie.html',

        {
            'movie': movie,

            'occupied': occupied
        }
    )




# =========================================================
# PAYMENT PAGE
# =========================================================

def payment_page(request):

    total = request.session.get('total')



    # RAZORPAY CLIENT

    client = razorpay.Client(

        auth=(

            settings.RAZORPAY_KEY_ID,

            settings.RAZORPAY_KEY_SECRET
        )
    )



    # CREATE ORDER

    payment = client.order.create({

        "amount": int(total) * 100,

        "currency": "INR",

        "payment_capture": "1"
    })



    # AFTER PAYMENT SUCCESS

    if request.method == 'POST':



        movie_id = request.session.get('movie_id')



        movie = Movie.objects.get(
            id=movie_id
        )



        # CREATE BOOKING

        booking = Booking.objects.create(

            movie=movie,

            name=request.session.get('name'),

            email=request.session.get('email'),

            seats=request.session.get('seats'),

            total_price=request.session.get('total')
        )



        # =================================================
        # QR CODE DATA
        # =================================================

        qr_data = f'''

Booking With Mishra

Movie: {movie.title}

Name: {request.session.get("name")}

Seats: {request.session.get("seats")}

Total Paid: ₹{request.session.get("total")}
'''



        # =================================================
        # GENERATE QR
        # =================================================

        qr = qrcode.make(qr_data)



        buffer = BytesIO()



        qr.save(buffer)



        # =================================================
        # SAVE QR
        # =================================================

        file_name = f'booking_{booking.id}.png'



        booking.qr_code.save(

            file_name,

            File(buffer),

            save=True
        )



        # =================================================
        # SEND EMAIL
        # =================================================

        send_mail(

            'Booking Confirmed - Booking With Mishra',

            f'''
Hello {request.session.get("name")}

Your booking is confirmed.

Movie: {movie.title}

Seats: {request.session.get("seats")}

Total Paid: ₹{request.session.get("total")}

Thank you for using Booking With Mishra.
''',

            settings.EMAIL_HOST_USER,

            [request.session.get('email')],

            fail_silently=False
        )



        # SAVE BOOKING ID

        request.session['booking_id'] = booking.id



        return redirect('/movies/success/')



    return render(

        request,

        'payment.html',

        {
            'payment': payment,

            'razorpay_key': settings.RAZORPAY_KEY_ID,

            'total': total
        }
    )




# =========================================================
# SUCCESS PAGE
# =========================================================

def success_page(request):

    booking_id = request.session.get('booking_id')



    booking = Booking.objects.get(
        id=booking_id
    )



    return render(

        request,

        'success.html',

        {
            'booking': booking
        }
    )