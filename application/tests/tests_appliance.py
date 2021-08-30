from django.test import TestCase, Client
from django.urls import reverse
from .testdata import *


class TestApplicationAppliance(TestCase):

    def setUp(self):
        self.client = Client()
        self.meta = MetaStaticFactory()
        self.worktop_category = WorktopCategoyFactory()
        self.appliance_category = AppliancesCategoryFactory()
        self.worktop = [WorktopFactory() for _ in range(0, 10)]
        self.appliance = [ApplianceFactory() for _ in range(0, 10)]
        self.appliance_url = reverse('application:appliances-list', kwargs={'slug': self.appliance_category.slug})
        self.appliance_detail_url = reverse('application:appliances-detail-view',
                                            kwargs={'name': 'appliance', 'slug': self.appliance_category.slug
                                                , 'pk': 1})

    def test_appliance_list_GET(self):
        response = self.client.get(self.appliance_url)
        self.assert_(response.status_code, 200)
        self.assertTemplateUsed(response, 'worktop.html')
        self.assertEquals(response.context['list'].count(), 10)
        # self.assertEqual(str(response.context['list'][0].accessories_type), str(self.category))

    def test_appliance_detail_GET(self):
        response = self.client.get(self.appliance_detail_url)
        self.assert_(response.status_code, 200)
        # print(self.appliance_detail_url,response.context)

        self.assertTemplateUsed(response, 'worktop_app_detail.html')
        # self.assertEquals(response.context['detail'], self.accessory[3])
