# UUID primary key -> BigAutoField (integer)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0003_integer_primary_keys"),
        ("product", "0004_product_product_pro_categor_2b9d78_idx_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="favourite", name="id"),
        migrations.AddField(
            model_name="favourite",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="productimage", name="id"),
        migrations.AddField(
            model_name="productimage",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="product", name="id"),
        migrations.AddField(
            model_name="product",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="category.category",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="product.product",
            ),
        ),
        migrations.AlterField(
            model_name="favourite",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favourited_by",
                to="product.product",
            ),
        ),
    ]
