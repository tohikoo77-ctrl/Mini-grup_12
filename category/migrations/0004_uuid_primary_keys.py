# BigAutoField -> UUID primary key

import uuid

import django.db.models.deletion
from django.db import migrations, models


def clear_related_data(apps, schema_editor):
    models_to_clear = [
        ("cart", "CartItem"),
        ("cart", "Cart"),
        ("order", "OrderItem"),
        ("order", "Order"),
        ("product", "Favourite"),
        ("product", "ProductImage"),
        ("product", "Product"),
        ("news", "News"),
        ("category", "PropertyOption"),
        ("category", "CategoryProperty"),
        ("category", "Category"),
    ]
    for app_label, model_name in models_to_clear:
        apps.get_model(app_label, model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0003_integer_primary_keys"),
    ]

    operations = [
        migrations.RunPython(clear_related_data, migrations.RunPython.noop),
        migrations.RemoveField(model_name="propertyoption", name="id"),
        migrations.AddField(
            model_name="propertyoption",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.RemoveField(model_name="categoryproperty", name="id"),
        migrations.AddField(
            model_name="categoryproperty",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.RemoveField(model_name="category", name="id"),
        migrations.AddField(
            model_name="category",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="category.category",
            ),
        ),
        migrations.AlterField(
            model_name="categoryproperty",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="properties",
                to="category.category",
            ),
        ),
        migrations.AlterField(
            model_name="propertyoption",
            name="property",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options",
                to="category.categoryproperty",
            ),
        ),
    ]
