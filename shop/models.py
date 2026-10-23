from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField("Номи маҳсулот", max_length=200)
    photo = models.ImageField(
    "Аксҳо",
    upload_to="products/",
    blank=True,
    null=True,
)
    size = models.CharField("Андоза", max_length=50)
    color = models.CharField("Ранг", max_length=50)
    purchase_price = models.DecimalField("Нархи харид", max_digits=10, decimal_places=2)
    selling_price = models.DecimalField("Нархи фурӯш", max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField("Миқдори боқимонда", default=0)
    low_stock_threshold = models.PositiveIntegerField("Ҳадди ақали боқимонда", default=3)
    is_active = models.BooleanField("Фаъол", default=True)

    class Meta:
        verbose_name = "Маҳсулот"
        verbose_name_plural = "Маҳсулотҳо"

    def __str__(self):
        return f"{self.name} — {self.size} — {self.color}"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Нав"),
        ("sent", "Фиристода шуд"),
        ("delivered", "Расонда шуд"),
        ("canceled", "Бекор карда шуд"),
        ("returned", "Баргардонидан"),
    ]

    order_number = models.CharField("Рақами фармоиш", max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField("Санаи эҷод", default=timezone.now)
    status = models.CharField("Ҳолат", max_length=20, choices=STATUS_CHOICES, default="new")
    comment = models.TextField("Шарҳ", blank=True)
    stock_updated = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Фармоиш"
        verbose_name_plural = "Фармоишҳо"
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_id = Order.objects.count() + 1
            self.order_number = f"ORD-{last_id:05d}"
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    @property
    def total_purchase(self):
        return sum(item.total_purchase for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("Миқдор", default=1)
    unit_price = models.DecimalField("Нархи фурӯш", max_digits=10, decimal_places=2)
    unit_purchase_price = models.DecimalField("Нархи харид", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Маҳсулоти фармоиш"
        verbose_name_plural = "Маҳсулоти фармоишҳо"

    def __str__(self):
        return f"{self.product} x {self.quantity}"

    @property
    def total(self):
        return self.unit_price * self.quantity

    @property
    def total_purchase(self):
        return self.unit_purchase_price * self.quantity


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("advertising", "Реклама"),
        ("delivery", "Расонидан"),
        ("packaging", "Пакеткунӣ"),
        ("purchase", "Хариди маҳсулот"),
        ("other", "Дигар"),
    ]

    date = models.DateField("Сана", default=timezone.now)
    category = models.CharField("Гурӯҳ", max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField("Маблағ", max_digits=10, decimal_places=2)
    comment = models.TextField("Шарҳ", blank=True)

    class Meta:
        verbose_name = "Хароҷот"
        verbose_name_plural = "Хароҷотҳо"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_category_display()} — {self.amount} TJS"