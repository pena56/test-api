from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetup(APITestCase):
  
  def setUp(self):
    self.register_url = reverse('register')
    self.login_url = reverse('login')

    self.user_data = {
      'email': 'email@test.com',
      'username': 'test',
      'password': 'email@test.com',
    }

    return super().setUp()

  def tearDown(self):
    return super().tearDown()