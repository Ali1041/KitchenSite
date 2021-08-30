from django.test import TestCase, Client
from django.urls import reverse
from application.models import Brochure
from .testdata import *
from django.conf import settings


# Create your tests here.
class TestApplicationHome(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('application:index')
        self.meta = MetaStaticFactory()
        self.blog = [BlogFactory(), BlogFactory(), BlogFactory(), BlogFactory(), BlogFactory()]
        self.captcha = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'

    def test_home_GET(self):
        response = self.client.get(self.home_url)
        self.assert_(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(response.context['blog'][1], self.blog[1])
        self.assertEqual(response.context['blog'][2], self.blog[2])

    def test_home_POST(self):
        response = self.client.post(self.home_url, {
            'g-recaptcha-response': self.captcha,
            'first': 'new',
            'last': 'new last',
            'email': 'new@gmail.com',
            'phone': 321,
            'detail': 'disdains'
        })
        brochure = Brochure.objects.first()
        self.assert_(response.status_code, 302)
        self.assertEqual(brochure.first_name, 'new')
