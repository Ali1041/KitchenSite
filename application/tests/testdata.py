import factory
from faker import Factory
from application.models import MetaStatic, Blogs, Accessories, AccessoriesType, Worktop_category, WorkTop \
    , Category_Applianes, Appliances

faker = Factory.create()


# Meta instance for test
class MetaStaticFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaStatic

    name = 'home'
    title = faker.word()
    description = faker.text()
    unique_id = name


# Blog model instances for test
class BlogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Blogs

    title = factory.LazyAttribute(lambda _: faker.word())
    text = faker.text()
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class AccessoryCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccessoriesType

    name = faker.word()
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class AccessoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Accessories

    accessories_type = factory.SubFactory(AccessoryCategoryFactory)
    description = faker.text()
    price = faker.random_number()
    sku = faker.random_number()
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class WorktopCategoyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Worktop_category

    worktop_type = faker.word()
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class WorktopFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WorkTop

    category = factory.SubFactory(WorktopCategoyFactory)
    name = faker.word()
    color = faker.word()
    description = faker.text()
    price = faker.random_number()
    size = faker.random_number()
    added = False
    available = True
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class AppliancesCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category_Applianes

    name = faker.word()
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()


class ApplianceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appliances

    category = factory.SubFactory(AppliancesCategoryFactory)
    name = faker.word()
    appliances_type = faker.word()
    brand_name = faker.word()
    description = faker.text()
    price = faker.random_number()
    appliance_category = faker.random_number()
    added = False
    available = True
    meta_name = faker.name()
    meta_title = faker.text()
    meta_description = faker.text()
