from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),

    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    path("orders/", views.order_list, name="order_list"),
    path("orders/add/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/add-item/", views.order_add_item, name="order_add_item"),
    path("orders/item/<int:pk>/delete/", views.order_item_delete, name="order_item_delete"),

    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/edit/", views.expense_update, name="expense_update"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),

    path("reports/", views.report, name="report"),
]