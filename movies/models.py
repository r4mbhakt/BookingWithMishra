# Shivoham Mishra | BTech

from django.db import models



class Movie(models.Model):

    title = models.CharField(
        max_length=200
    )

    image = models.ImageField(
        upload_to='movies'
    )

    description = models.TextField()

    duration = models.CharField(
        max_length=100
    )

    price = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.title




class Booking(models.Model):

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    seats = models.CharField(
        max_length=500
    )

    total_price = models.IntegerField()

    qr_code = models.ImageField(
        upload_to='qr_codes',
        blank=True,
        null=True
    )

    booked_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.name