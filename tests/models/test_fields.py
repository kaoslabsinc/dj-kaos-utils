from simple.models import Product


def test_TwoPlacesDecimalField():
    pass


def test_MoneyField():
    product = Product(name="Product", price=21.30)
    assert product.price


def test_CaseInsensitiveFieldMixin():
    pass


def test_ToLowerCaseFieldMixin():
    pass


def test_LowerCaseCharField():
    pass
