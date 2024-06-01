# """
# Model Tests
from django.test import TestCase
from .models import Customer, RegistrationState


class CustomerModelTests(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            keywords=["django", "python"],
            registration_state=RegistrationState.TRIAL,
        )
        self.assertEqual(customer.username, "john.doe")
        self.assertEqual(customer.first_name, "John")
        self.assertEqual(customer.last_name, "Doe")
        self.assertEqual(customer.email, "john.doe@example.com")
        self.assertEqual(customer.keywords, ["django", "python"])
        self.assertEqual(customer.registration_state, RegistrationState.TRIAL)


# """

# """
# View Tests
from django.test import TestCase, Client
from django.urls import reverse
from .models import Customer


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_view_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "fenjan/register.html")

    def test_register_view_post_valid(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "keyword1": "django",
                "keyword2": "python",
                "keyword3": "",
                "keyword4": "",
                "keyword5": "",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertTrue(Customer.objects.filter(email="john.doe@example.com").exists())

    def test_register_view_post_invalid(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "",
                "email": "invalid-email",
            },
        )
        self.assertEqual(response.status_code, 200)  # Form re-rendered on failure
        self.assertFalse(Customer.objects.filter(email="invalid-email").exists())


# """

"""
# Email Sending Tests
from django.core import mail
from django.test import TestCase


class EmailSendingTests(TestCase):
    def test_send_email(self):
        mail.send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, "Subject here")
"""

"""
# Keyword Search and Mocking External Services
from unittest.mock import patch
from django.test import TestCase
from myapp.jobs import search_linkedin


class LinkedInSearchTests(TestCase):
    @patch("myapp.jobs.selenium.webdriver.Chrome")
    @patch("myapp.jobs.requests.get")
    def test_search_linkedin(self, mock_requests_get, mock_chrome):
        mock_chrome_instance = mock_chrome.return_value
        mock_chrome_instance.find_elements_by_xpath.return_value = []

        # Mock the requests response
        mock_requests_get.return_value.json.return_value = {
            "positions": [
                {
                    "title": "PhD in Django",
                    "company": "Example Corp",
                    "link": "https://example.com/job1",
                }
            ]
        }

        results = search_linkedin(["django", "python"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "PhD in Django")
"""
