from django.urls import reverse

from simple.models import Category


def test_EditReadonlyAdminMixin(admin_client):
    opts = Category._meta
    admin_url_add = reverse(f'admin:{opts.app_label}_{opts.model_name}_add')

    name = "name"
    slug = "name-slug"
    response = admin_client.post(
        admin_url_add,
        {
            "name": name,
            "slug": slug,
        },
    )
    assert response.status_code == 302

    obj = Category.objects.get(name=name)
    assert obj.slug == slug

    admin_url_change = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[obj.id])
    response = admin_client.post(
        admin_url_change,
        {
            "name": name,
            "slug": "new-slug",
        },
    )
    assert response.status_code == 302
    obj = Category.objects.get(name=name)
    assert obj.slug == slug  # check that the above request hasn't changed the slug, confirming the slug is readonly now
