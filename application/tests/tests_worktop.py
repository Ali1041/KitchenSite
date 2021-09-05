from django.test import TestCase, Client
from django.urls import reverse
from .testdata import *


class TestApplicationWorktop(TestCase):

    def setUp(self):
        self.client = Client()
        self.meta = MetaStaticFactory()
        self.worktop_category = WorktopCategoyFactory()
        self.appliance_category = AppliancesCategoryFactory()
        self.worktop = [WorktopFactory() for _ in range(0, 10)]
        self.appliance = [ApplianceFactory() for _ in range(0, 10)]
        self.worktop_url = reverse('application:worktop-view', kwargs={'slug': self.worktop_category.slug})
        self.worktop_detail_url = reverse('application:worktop-detail-view', kwargs={'slug': self.worktop_category.slug,
                                                                                     'name': 'worktop', 'pk': 1})

    # worktop tests
    def test_worktop_list_GET(self):
        response = self.client.get(self.worktop_url)
        self.assert_(response.status_code, 200)
        self.assertTemplateUsed(response, 'worktop.html')
        self.assertEquals(response.context['list'].count(), 10)
        self.assertEqual(str(response.context['list'][0].category), str(self.worktop_category))

    def test_worktop_detail_GET(self):
        response = self.client.get(self.worktop_detail_url)
        self.assert_(response.status_code, 200)
        self.assertTemplateUsed(response, 'worktop_app_detail.html')

    # self.assertEquals(response.context['detail'], self.accessory[3])


