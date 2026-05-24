# Shivoham Mishra | BTech

from django.contrib import admin

from .models import Movie
from .models import Booking


admin.site.register(Movie)

admin.site.register(Booking)