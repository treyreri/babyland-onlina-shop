from django import forms
from .models import Product, Expense, Order, OrderItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "photo", "name", "size", "color", "purchase_price",
            "selling_price", "stock_quantity", "low_stock_threshold", "is_active",
        ]
        labels = {
            "photo": "Аксҳои маҳсулот",
            "name": "Номи маҳсулот",
            "size": "Андоза",
            "color": "Ранг",
            "purchase_price": "Нархи харид",
            "selling_price": "Нархи фурӯш",
            "stock_quantity": "Миқдори боқимонда",
            "low_stock_threshold": "Ҳадди ақали боқимонда",
            "is_active": "Фаъол",
        }
        widgets = {
            "photo": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "capture": "environment",
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "category", "amount", "comment"]
        labels = {
            "date": "Сана",
            "category": "Гурӯҳ",
            "amount": "Маблағ",
            "comment": "Шарҳ",
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "comment"]
        labels = {
            "status": "Ҳолат",
            "comment": "Шарҳ",
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price", "unit_purchase_price"]
        labels = {
            "product": "Маҳсулот",
            "quantity": "Миқдор",
            "unit_price": "Нархи фурӯш",
            "unit_purchase_price": "Нархи харид",
        }