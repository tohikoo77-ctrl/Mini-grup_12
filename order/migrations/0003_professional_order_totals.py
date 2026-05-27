from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


MONEY_QUANT = Decimal("0.01")


def money(value):
    return Decimal(value or 0).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def clamp_promos_and_recalculate_orders(apps, schema_editor):
    PromoCode = apps.get_model("order", "PromoCode")
    Order = apps.get_model("order", "Order")

    PromoCode.objects.filter(discount_percent__gt=100).update(discount_percent=100)
    PromoCode.objects.filter(discount_percent__lt=1).update(discount_percent=1)

    now = timezone.now()

    for order in Order.objects.select_related("promocode").all():
        subtotal = money(
            order.items.aggregate(total=models.Sum("total_price"))["total"]
        )
        discount_amount = money(0)

        promo = order.promocode
        if promo and promo.active and promo.valid_from <= now <= promo.valid_to:
            discount_amount = money(subtotal * Decimal(promo.discount_percent) / Decimal("100"))
            discount_amount = min(discount_amount, subtotal)

        order.total_price = max(money(subtotal - discount_amount), money(0))
        order.save(update_fields=["total_price"])


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0002_promocode_alter_order_options_alter_order_status_and_more"),
    ]

    operations = [
        migrations.RunPython(clamp_promos_and_recalculate_orders, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="users.user",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="product.product",
            ),
        ),
        migrations.AlterField(
            model_name="promocode",
            name="discount_percent",
            field=models.PositiveIntegerField(
                validators=[MinValueValidator(1), MaxValueValidator(100)]
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["user", "status"], name="order_order_user_id_f784ac_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["created_at"], name="order_order_created_ffede0_idx"),
        ),
        migrations.AddIndex(
            model_name="promocode",
            index=models.Index(
                fields=["active", "valid_from", "valid_to"],
                name="order_promo_active_50efdb_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="promocode",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    discount_percent__gte=1,
                    discount_percent__lte=100,
                ),
                name="promo_discount_percent_1_100",
            ),
        ),
    ]
