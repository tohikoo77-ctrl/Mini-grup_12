import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0004_uuid_primary_keys"),
        ("product", "0005_integer_primary_keys"),
    ]

    operations = [
        migrations.RemoveField(model_name="favourite", name="id"),
        migrations.AddField(
            model_name="favourite",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.RemoveField(model_name="productimage", name="id"),
        migrations.AddField(
            model_name="productimage",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.RemoveField(model_name="product", name="id"),
        migrations.AddField(
            model_name="product",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
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
