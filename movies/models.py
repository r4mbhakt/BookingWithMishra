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
# FILE: models.py
# DESCRIPTION: Core Database Object Relational Mapping (ORM) Schemas
# ARCHITECTURE: Django Relational Database Models
# ===================================================================================================

"""
MODULE DOCUMENTATION:
-----------------------------------------------------------------------------------------------------
This module defines the core database architecture for the movie booking platform.
It establishes the data structures for 'Movies' (the catalog) and 'Bookings' (the transactions).
The models handle all relationships (Foreign Keys), field validations, and media upload paths.
-----------------------------------------------------------------------------------------------------
"""

# ===================================================================================================
# DEPENDENCY IMPORTS - DJANGO CORE
# ===================================================================================================

from django.db import models
from django.contrib.auth.models import User



# ===================================================================================================
# ===================================================================================================
# DATABASE SCHEMA: MOVIE ENTITY
# ===================================================================================================
# ===================================================================================================

class Movie(models.Model):
    """
    -------------------------------------------------------------------------------------------------
    MODEL: Movie
    DESCRIPTION:
        Represents a singular cinematic event available for booking. 
        Stores essential metadata including the poster image, synopsis, runtime, and pricing.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # CORE IDENTIFICATION FIELDS
    # -----------------------------------------------------------------
    title = models.CharField(
        max_length=200,
        help_text="The official title of the movie."
    )

    # -----------------------------------------------------------------
    # MEDIA & CONTENT FIELDS
    # -----------------------------------------------------------------
    image = models.ImageField(
        upload_to='movies',
        help_text="The official poster or promotional banner for the movie."
    )

    description = models.TextField(
        help_text="A detailed synopsis or plot summary of the movie."
    )

    duration = models.CharField(
        max_length=100,
        help_text="Total runtime of the movie (e.g., '2h 15m')."
    )

    # -----------------------------------------------------------------
    # FINANCIAL & METADATA FIELDS
    # -----------------------------------------------------------------
    price = models.IntegerField(
        help_text="The base price for a single ticket."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of when this movie was added to the database."
    )

    # -----------------------------------------------------------------
    # OBJECT REPRESENTATION
    # -----------------------------------------------------------------
    def __str__(self):
        """
        Returns the string representation of the Movie object (used in Django Admin).
        """
        return self.title




# ===================================================================================================
# ===================================================================================================
# DATABASE SCHEMA: BOOKING TRANSACTION ENTITY
# ===================================================================================================
# ===================================================================================================

class Booking(models.Model):
    """
    -------------------------------------------------------------------------------------------------
    MODEL: Booking
    DESCRIPTION:
        Represents a finalized ticket transaction. 
        Links to both the target 'Movie' and the purchasing 'User'. Contains seat allocation, 
        financial totals, and the dynamically generated QR Code ticket artifact.
    -------------------------------------------------------------------------------------------------
    """

    # -----------------------------------------------------------------
    # RELATIONAL FIELDS (FOREIGN KEYS)
    # -----------------------------------------------------------------
    
    # Relationship to the Movie being booked.
    # If the movie is deleted, all associated bookings are also deleted (CASCADE).
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )
    
    # [FIXED INDENTATION] 
    # Relationship to the authenticated User making the booking.
    # Allowed to be null/blank for potential guest checkouts or administrative overrides.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # -----------------------------------------------------------------
    # CUSTOMER INFORMATION FIELDS
    # -----------------------------------------------------------------
    name = models.CharField(
        max_length=200,
        help_text="Full name of the person under whom the booking is made."
    )

    email = models.EmailField(
        help_text="Contact email for sending the booking confirmation and QR ticket."
    )

    # -----------------------------------------------------------------
    # TRANSACTION & SEAT ALLOCATION FIELDS
    # -----------------------------------------------------------------
    seats = models.CharField(
        max_length=500,
        help_text="Comma-separated string of allocated seat numbers (e.g., 'A1,A2,A3')."
    )

    total_price = models.IntegerField(
        help_text="The final calculated amount paid for this transaction."
    )

    # -----------------------------------------------------------------
    # ARTIFACTS & METADATA
    # -----------------------------------------------------------------
    qr_code = models.ImageField(
        upload_to='qr_codes',
        blank=True,
        null=True,
        help_text="Dynamically generated QR code containing the booking payload."
    )

    booked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of when the transaction was successfully finalized."
    )

    # -----------------------------------------------------------------
    # OBJECT REPRESENTATION
    # -----------------------------------------------------------------
    def __str__(self):
        """
        Returns the string representation of the Booking object, 
        identifying the customer in the Django Admin portal.
        """
        return self.name

# ===================================================================================================
# END OF FILE: models.py
# ===================================================================================================