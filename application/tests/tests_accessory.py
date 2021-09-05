from django.test import TestCase, Client
from django.urls import reverse
from .testdata import *


# Create your tests here.
class TestApplicationAccessory(TestCase):

    def setUp(self):
        self.client = Client()
        self.meta = MetaStaticFactory()
        self.category = AccessoryCategoryFactory()
        self.worktop_category = WorktopCategoyFactory()
        self.appliance_category = AppliancesCategoryFactory()
        self.accessory = [AccessoryFactory() for _ in range(0, 50)]
        self.worktop = [WorktopFactory() for _ in range(0, 10)]
        self.appliance = [ApplianceFactory() for _ in range(0, 10)]
        self.accessory_url = reverse('application:accessories-list', kwargs={'slug': self.category.slug})
        self.accessory_detail_url = reverse('application:accessories-detail',
                                            kwargs={'slug': self.category.slug, 'pk': 4})

    # accessories test
    def test_accessory_list_GET(self):
        response = self.client.get(self.accessory_url)
        self.assert_(response.status_code, 200)
        self.assertTemplateUsed(response, 'accessories_list.html')
        self.assertEquals(response.context['list'].count(), 10)
        self.assertEqual(str(response.context['list'][0].accessories_type), str(self.category))

    # def test_accessory_detail_GET(self):
    #     response = self.client.get(self.accessory_detail_url)
    #     self.assert_(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'accessories_detail.html')
    #     self.assertEquals(response.context['detail'], self.accessory[3])



