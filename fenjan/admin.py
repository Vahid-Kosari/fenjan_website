from django.contrib import admin

from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['registration_state', 'get_keywords_list', 'registration_date']

    def get_keywords_list(self, customer):
        keywords = customer.keywords.all()
        return ", ".join(keyword for keyword in keywords)
    
    get_keywords_list.short_description = 'keywords'
