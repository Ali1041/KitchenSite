import factory
from faker import Factory
from application.models import MetaStatic, Blogs, Accessories, AccessoriesType, Worktop_category, WorkTop \
    , Category_Applianes, Appliances

faker = Factory.create()


# Meta instance for test
class MetaStaticFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaStatic

    home_name = faker.name()
    home_title = faker.word()
    home_description = faker.text()

    kitchen_title = faker.word()
    kitchen_name = faker.name()
    kitchen_description = faker.text()

    design_title = faker.word()
    design_name = faker.name()
    design_description = faker.text()

    install_title = faker.word()
    install_name = faker.name()
    install_description = faker.text()

    contact_title = faker.word()
    contact_name = faker.name()
    contact_description = faker.text()

    blog_title = faker.word()
    blog_name = faker.name()
    blog_description = faker.text()

    cancellation_title = faker.word()
    cancellation_name = faker.name()
    cancellation_description = faker.text()

    cookies_title = faker.word()
    cookies_name = faker.name()
    cookies_description = faker.text()

    disclaimer_title = faker.word()
    disclaimer_name = faker.name()
    disclaimer_description = faker.text()

    faq_title = faker.word()
    faq_name = faker.name()
    faq_description = faker.text()

    gdpr_title = faker.word()
    gdpr_name = faker.name()
    gdpr_description = faker.text()

    ip_title = faker.word()
    ip_name = faker.name()
    ip_description = faker.text()

    return_title = faker.word()
    return_name = faker.name()
    return_description = faker.text()

    shipping_title = faker.word()
    shipping_name = faker.name()
    shipping_description = faker.text()

    terms_title = faker.word()
    terms_name = faker.name()
    terms_description = faker.text()

    login_title = faker.word()
    login_name = faker.name()
    login_description = faker.text()

    signup_title = faker.word()
    signup_name = faker.name()
    signup_description = faker.text()

    install_form_title = faker.word()
    install_form_name = faker.name()
    install_form_description = faker.text()

    search_title = faker.word()
    search_name = faker.name()
    search_description = faker.text()

    wishlist_title = faker.word()
    wishlist_name = faker.name()
    wishlist_description = faker.text()


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
