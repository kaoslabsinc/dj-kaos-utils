from simple.models import Category


def test_HasAutoFields_save(db):
    category = Category(name="Cat")
    assert not category.slug
    category.save()
    assert category.slug


def test_HasAutoFields_clean(db):
    category = Category(name="Cat")
    assert not category.slug
    category.clean()
    assert category.slug
