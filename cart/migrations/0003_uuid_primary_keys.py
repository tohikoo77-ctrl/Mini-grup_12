import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0006_uuid_primary_keys"),
        ("cart", "0002_integer_primary_keys"),
    ]

    operations = [
        migrations.RemoveField(model_name="cartitem", name="id"),
        migrations.AddField(
            model_name="cartitem",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.RemoveField(model_name="cart", name="id"),
        migrations.AddField(
            model_name="cart",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="cart",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="cart.cart",
            ),
        ),
        migrations.AlterField(
            model_name="cartitem",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cart_items",
                to="product.product",
            ),
        ),
    ]
