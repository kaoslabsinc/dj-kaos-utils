from simple.models import Category


def test_HasAutoFields(db):
    category = Category(name="Name")
    assert not category.slug
    category.save()
    assert category.slug
