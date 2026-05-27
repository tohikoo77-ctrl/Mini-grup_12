# UUID primary key -> BigAutoField (integer)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0005_integer_primary_keys"),
        ("cart", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="cartitem", name="id"),
        migrations.AddField(
            model_name="cartitem",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="cart", name="id"),
        migrations.AddField(
            model_name="cart",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
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
