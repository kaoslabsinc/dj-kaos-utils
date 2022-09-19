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


def test_LowerCaseCharField(db):
    product = Product(name="Product", price=21.30, code_id="ABxDc")
    assert product.code_id == "ABxDc"
    product.save()
    product.refresh_from_db()
    assert product.code_id == "abxdc"


def test_LowerCaseCharField__lookup(db):
    Product(name="Product", price=21.30, code_id="ABxDc1").save()
    assert Product.objects.filter(code_id="abXdc1").exists()
    assert Product.objects.filter(code_id="aBxdC1").exists()
    assert Product.objects.filter(code_id="ABxDc1").exists()
    assert Product.objects.filter(code_id="abxdc1").exists()
    assert Product.objects.filter(code_id="ABXDC1").exists()
