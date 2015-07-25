from django import forms
from django.contrib import admin
from .models import UserProfile

# Now register the new UserAdmin...
admin.site.register(UserProfile)
