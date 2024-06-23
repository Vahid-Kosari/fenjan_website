from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "get_keywords_list",
        "registration_date",
        "expiration_date",
        "registration_state",
    ]

    def get_keywords_list(self, customer):
        keywords = customer.keywords
        return ", ".join(keyword for keyword in keywords)

    get_keywords_list.short_description = "keywords"
