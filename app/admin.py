from django.contrib import admin
from .models import Subscription, Publication


class SubscriptionAdmin(admin.ModelAdmin):
    pass


class PublicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Publication, PublicationAdmin)
