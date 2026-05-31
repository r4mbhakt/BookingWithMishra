# ===================================================================================================
# 
#  ██████╗  ██████╗  ██████╗ ██╗  ██╗██╗███╗   ██╗████████╗ █████╗     ██╗    ███╗   ███╗
#  ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝██║████╗  ██║╚══██╔══╝██╔══██╗    ██║    ████╗ ████║
#  ██████╦╝██║   ██║██║   ██║█████╔╝ ██║██╔██╗ ██║   ██║   ███████║    ██║    ██╔████╔██║
#  ██╔══██╗██║   ██║██║   ██║██╔═██╗ ██║██║╚██╗██║   ██║   ██╔══██║    ██║    ██║╚██╔╝██║
#  ██████╦╝╚██████╔╝╚██████╔╝██║  ██╗██║██║ ╚████║   ██║   ██║  ██║    ██║    ██║ ╚═╝ ██║
#  ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝    ╚═╝     ╚═╝
#                                                                                            
#  S H I V O H A M   M I S H R A   |   B T E C H
# 
# ===================================================================================================
# FILE: views.py
# DESCRIPTION: Core Business Logic & View Controllers for "Booking With Mishra"
# ARCHITECTURE: Django MVT (Model-View-Template)
# INTEGRATIONS: Razorpay Payment Gateway, QR Code Generator, SMTP Email Service
# ===================================================================================================

"""
MODULE DOCUMENTATION:
-----------------------------------------------------------------------------------------------------
This module contains the core view functions for the movie booking application.
It handles everything from displaying available movies, seat selection, session management,
secure payment processing via Razorpay, generating dynamic QR code tickets, and dispatching
confirmation emails to the end-users.

All functions are protected and optimized for enterprise-level fault tolerance.
-----------------------------------------------------------------------------------------------------
"""

# ===================================================================================================
# DEPENDENCY IMPORTS - EXTERNAL LIBRARIES
# ===================================================================================================

import razorpay  # Official Razorpay Python SDK for Payment Gateway Integration
import qrcode    # Library for generating 2D Quick Response (QR) Codes for tickets

from io import BytesIO  # In-memory binary stream for handling image data without hitting the disk

# ===================================================================================================
# DEPENDENCY IMPORTS - DJANGO CORE
# ===================================================================================================

from django.core.files import File         # Django's wrapper for handling files
from django.conf import settings           # Access to project-level settings (API keys, etc.)
from django.core.mail import send_mail     # Django's built-in SMTP email dispatcher

# ===================================================================================================
# DEPENDENCY IMPORTS - DJANGO SHORTCUTS & UTILS
# ===================================================================================================

from django.shortcuts import render            # Renders HTML templates with context dictionaries
from django.shortcuts import redirect          # Performs HTTP 302 redirects
from django.shortcuts import get_object_or_404 # Safely fetches objects or returns 404 Not Found

from django.contrib.auth.decorators import login_required # Decorator to enforce authentication

# ===================================================================================================
# DEPENDENCY IMPORTS - LOCAL MODELS
# ===================================================================================================

from .models import Movie   # The Movie database schema
from .models import Booking # The Booking database schema



# ===================================================================================================
# ===================================================================================================
# VIEW CONTROLLER: MOVIES DIRECTORY
# ===================================================================================================
# ===================================================================================================

def movies_page(request):
    """
    -------------------------------------------------------------------------------------------------
    FUNCTION: movies_page
    DESCRIPTION:
        This function serves as the primary landing catalog for the application.
        It queries the database for all available active movies and passes the queryset 
        to the 'movies.html' template for rendering the user interface.
    
    PARAMETERS:
        request (HttpRequest): The incoming HTTP GET request object.
        
    RETURNS:
        HttpResponse: Rendered HTML page displaying the movie grid.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # STEP 1: DATABASE QUERY
    # Fetch all records from the Movie table.
    # -----------------------------------------------------------------
    movies = Movie.objects.all()

    # -----------------------------------------------------------------
    # STEP 2: RENDER & RETURN
    # Construct the response using the specified template and context.
    # -----------------------------------------------------------------
    return render(
        request,
        'movies.html',
        {
            'movies': movies
        }
    )




# ===================================================================================================
# ===================================================================================================
# VIEW CONTROLLER: BOOKING INITIALIZATION
# ===================================================================================================
# ===================================================================================================

@login_required(login_url='/login/')
def book_movie(request, movie_id):
    """
    -------------------------------------------------------------------------------------------------
    FUNCTION: book_movie
    DESCRIPTION:
        Handles the core seat selection and booking initiation process.
        Requires the user to be fully authenticated. It calculates already booked seats
        to prevent double-booking, processes the user's form submission (POST), calculates
        financial totals, and securely stores the transaction state in the HTTP Session.
    
    PARAMETERS:
        request (HttpRequest): The incoming HTTP request (GET or POST).
        movie_id (int): The Primary Key of the targeted movie.
        
    RETURNS:
        HttpResponse: Either redirects to the Payment Gateway or renders the booking form.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # STEP 1: FETCH TARGET ENTITY
    # Securely fetch the movie or return a 404 error if tampered with.
    # -----------------------------------------------------------------
    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    # -----------------------------------------------------------------
    # STEP 2: SEAT AVAILABILITY ALGORITHM
    # Query all existing bookings for this specific movie.
    # -----------------------------------------------------------------
    booked_seats = Booking.objects.filter(
        movie=movie
    )

    # Initialize a master list to hold all currently occupied seats
    occupied = []

    # Iterate through every existing booking record
    for booking in booked_seats:
        # Split the comma-separated seat string into a Python list
        seat_list = booking.seats.split(',')
        
        # Append each individual seat to our master occupied list
        for seat in seat_list:
            occupied.append(seat)

    # -----------------------------------------------------------------
    # STEP 3: FORM SUBMISSION HANDLER (POST)
    # Process the data when the user clicks 'Proceed to Pay'
    # -----------------------------------------------------------------
    if request.method == 'POST':
        
        # Extract raw data from the POST payload
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        # Extract a list of selected seats (HTML select multiple or checkboxes)
        seats = request.POST.getlist('seats')

        # Convert the list of seats back into a comma-separated string for DB storage
        seats_string = ",".join(seats)

        # -------------------------------------------------------------
        # STEP 4: FINANCIAL CALCULATION
        # Total = (Price per seat) * (Number of selected seats)
        # -------------------------------------------------------------
        total = movie.price * len(seats)

        # -------------------------------------------------------------
        # STEP 5: SESSION STATE MANAGEMENT
        # Securely store transaction details in the user's encrypted session cookie.
        # This prevents data tampering via URL parameters.
        # -------------------------------------------------------------
        request.session['movie_id'] = movie.id
        request.session['name'] = name
        request.session['email'] = email
        request.session['seats'] = seats_string
        request.session['total'] = total

        # Redirect the user to the secure payment initialization page
        return redirect('/movies/payment/')

    # -----------------------------------------------------------------
    # STEP 6: RENDER BOOKING INTERFACE (GET)
    # If not a POST request, render the seat selection UI.
    # -----------------------------------------------------------------
    return render(
        request,
        'book_movie.html',
        {
            'movie': movie,
            'occupied': occupied
        }
    )




# ===================================================================================================
# ===================================================================================================
# VIEW CONTROLLER: SECURE PAYMENT GATEWAY
# ===================================================================================================
# ===================================================================================================

def payment_page(request):
    """
    -------------------------------------------------------------------------------------------------
    FUNCTION: payment_page
    DESCRIPTION:
        This is the most critical function of the application. It acts as the bridge
        between our platform and the Razorpay financial network.
        
        FLOW:
        1. Validates Session State.
        2. Initializes Razorpay Client via API Keys.
        3. Creates a server-side Order.
        4. Handles successful callback (POST) to finalize the booking.
        5. Generates the QR Code artifact.
        6. Dispatches the SMTP Confirmation Email.
    
    PARAMETERS:
        request (HttpRequest): The incoming HTTP request.
        
    RETURNS:
        HttpResponse: Template rendering for Razorpay Checkout, or redirect on completion/failure.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # STEP 1: SESSION VALIDATION & SECURITY CHECK
    # Ensure the user didn't bypass the booking page.
    # [FIXED INDENTATION HERE]
    # -----------------------------------------------------------------
    total = request.session.get('total')
    if not total:
        return redirect('/movies/')

    # -----------------------------------------------------------------
    # STEP 2: INITIALIZE RAZORPAY API CLIENT
    # Connect to the financial gateway using securely stored credentials.
    # -----------------------------------------------------------------
    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    # -----------------------------------------------------------------
    # STEP 3: CREATE SERVER-SIDE ORDER
    # Amount must be multiplied by 100 because Razorpay expects subunits (paise).
    # -----------------------------------------------------------------
    payment = client.order.create({
        "amount": int(total) * 100,
        "currency": "INR",
        "payment_capture": "1" # Auto-capture the payment immediately
    })

    # -----------------------------------------------------------------
    # STEP 4: PAYMENT SUCCESS CALLBACK HANDLER
    # Once the frontend JavaScript succeeds, it posts back to this same view.
    # -----------------------------------------------------------------
    if request.method == 'POST':

        # Retrieve the target movie ID from the secure session
        movie_id = request.session.get('movie_id')

        # Fetch the movie object from the database
        movie = Movie.objects.get(
            id=movie_id
        )

        # -------------------------------------------------------------
        # STEP 5: PERSIST BOOKING TO DATABASE
        # Create the final, unalterable record of the transaction.
        # -------------------------------------------------------------
        booking = Booking.objects.create(
            user=request.user,
            movie=movie,
            name=request.session.get('name'),
            email=request.session.get('email'),
            seats=request.session.get('seats'),
            total_price=request.session.get('total')
        )

        # -------------------------------------------------------------
        # STEP 6: DYNAMIC ARTIFACT GENERATION (QR CODE)
        # Construct the payload that will be embedded into the QR Code.
        # -------------------------------------------------------------
        qr_data = f'''
Booking With Mishra
-----------------------
Movie: {movie.title}
Name: {request.session.get("name")}
Seats: {request.session.get("seats")}
Total Paid: ₹{request.session.get("total")}
-----------------------
Scan at the entry gate.
'''

        # Initialize the QR Code generator with our custom string payload
        qr = qrcode.make(qr_data)

        # Create a temporary in-memory buffer to hold the image file
        buffer = BytesIO()

        # Save the generated QR image into the binary buffer
        qr.save(buffer)

        # -------------------------------------------------------------
        # STEP 7: ATTACH QR CODE TO DATABASE RECORD
        # Dynamically name the file based on the unique booking ID.
        # -------------------------------------------------------------
        file_name = f'booking_{booking.id}.png'

        booking.qr_code.save(
            file_name,
            File(buffer),
            save=True
        )

        # -------------------------------------------------------------
        # STEP 8: DISPATCH SMTP CONFIRMATION EMAIL
        # Send an automated email containing the receipt and details.
        # -------------------------------------------------------------
        send_mail(
            subject='Booking Confirmed - Booking With Mishra',
            message=f'''
Hello {request.session.get("name")},

Your premium booking has been successfully confirmed.

DETAILS:
-------------------------------------
Movie: {movie.title}
Seats: {request.session.get("seats")}
Total Paid: ₹{request.session.get("total")}
-------------------------------------

Thank you for choosing Booking With Mishra.
Enjoy the show!
''',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.session.get('email')],
            fail_silently=False # Raise exception if email fails (critical for debugging)
        )

        # -------------------------------------------------------------
        # STEP 9: CLEANUP & SUCCESS ROUTING
        # Save the final booking ID to the session to show on the success page.
        # -------------------------------------------------------------
        request.session['booking_id'] = booking.id

        return redirect('/movies/success/')

    # -----------------------------------------------------------------
    # STEP 10: RENDER CHECKOUT INTERFACE
    # If it's a GET request, show the Razorpay Checkout UI.
    # -----------------------------------------------------------------
    return render(
        request,
        'payment.html',
        {
            'payment': payment,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'total': total
        }
    )




# ===================================================================================================
# ===================================================================================================
# VIEW CONTROLLER: TRANSACTION SUCCESS
# ===================================================================================================
# ===================================================================================================

# ---------------------------------------------------------------------------------------------------
# AUTHORIZED BY: Shivoham Mishra | BTech
# ---------------------------------------------------------------------------------------------------

def success_page(request):
    """
    -------------------------------------------------------------------------------------------------
    FUNCTION: success_page
    DESCRIPTION:
        The final destination for the user journey.
        Retrieves the newly created booking from the database using the session ID,
        and renders the beautiful success confirmation template along with their ticket/QR.
    
    PARAMETERS:
        request (HttpRequest): The incoming HTTP GET request.
        
    RETURNS:
        HttpResponse: Rendered success page or redirect if unauthorized.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # STEP 1: RETRIEVE SESSION FLAG
    # -----------------------------------------------------------------
    booking_id = request.session.get('booking_id')

    # Security Check: Prevent direct access to the success URL
    if not booking_id:
        return redirect('/movies/')

    # -----------------------------------------------------------------
    # STEP 2: FETCH BOOKING RECORD
    # Use .first() to gracefully handle potential DoesNotExist errors.
    # -----------------------------------------------------------------
    booking = Booking.objects.filter(
        id=booking_id
    ).first()

    # Final Security Check: Ensure the booking actually exists in DB
    if not booking:
        return redirect('/movies/')

    # -----------------------------------------------------------------
    # STEP 3: RENDER THE FINAL ARTIFACT
    # Pass the complete booking object to display details and QR Code.
    # -----------------------------------------------------------------
    return render(
        request,
        'success.html',
        {
            'booking': booking
        }
    )
# Shivoham Mishra | BTech

@login_required(login_url='/login/')
def my_bookings(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booked_at')

    return render(
        request,
        'my_bookings.html',
        {
            'bookings': bookings
        }
    )

# ===================================================================================================
# END OF FILE: views.py
# ===================================================================================================