# UUID primary key -> BigAutoField (integer)

import django.db.models.deletion
from django.db import migrations, models


def clear_related_data(apps, schema_editor):
    """UUID dan integer PK ga o'tishdan oldin bog'liq ma'lumotlarni tozalash."""
    # O'chirish tartibi muhim: PROTECT FK lar oldin tozalanadi
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
        ("category", "0002_category_is_deleted_and_more"),
        ("product", "0004_product_product_pro_categor_2b9d78_idx_and_more"),
        ("order", "0003_professional_order_totals"),
        ("cart", "0001_initial"),
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(clear_related_data, migrations.RunPython.noop),
        migrations.RemoveField(model_name="propertyoption", name="id"),
        migrations.AddField(
            model_name="propertyoption",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="categoryproperty", name="id"),
        migrations.AddField(
            model_name="categoryproperty",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="category", name="id"),
        migrations.AddField(
            model_name="category",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
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
