from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import date, timedelta

from .forms import ProductForm, ExpenseForm, OrderForm, OrderItemForm
from .models import Product, Order, OrderItem, Expense


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    delivered_today = Order.objects.filter(status="delivered", created_at__date=today)
    delivered_month = Order.objects.filter(status="delivered", created_at__date__gte=month_start)

    revenue_today = sum(order.total for order in delivered_today)
    revenue_month = sum(order.total for order in delivered_month)

    expenses_today = Expense.objects.filter(date=today).aggregate(total=Sum("amount"))["total"] or 0
    expenses_month = Expense.objects.filter(date__gte=month_start).aggregate(total=Sum("amount"))["total"] or 0

    profit_today = revenue_today - expenses_today
    profit_month = revenue_month - expenses_month

    low_stock_products = Product.objects.filter(
        is_active=True, stock_quantity__lte=models_f("low_stock_threshold")
    )

    context = {
        "delivered_today_count": delivered_today.count(),
        "revenue_today": revenue_today,
        "expenses_today": expenses_today,
        "profit_today": profit_today,
        "revenue_month": revenue_month,
        "profit_month": profit_month,
        "low_stock_products": low_stock_products,
    }
    return render(request, "dashboard.html", context)


def models_f(field):
    from django.db.models import F
    return F(field)


@login_required
def product_list(request):
    query = request.GET.get("q", "")
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(color__icontains=query) | Q(size__icontains=query)
        )

    return render(request, "products/product_list.html", {"products": products, "query": query})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Маҳсулот илова карда шуд.")
        return redirect("product_list")

    return render(
        request,
        "products/product_form.html",
        {"form": form, "title": "Илова кардани маҳсулот"},
    )

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Маҳсулот навсозӣ шуд.")
        return redirect("product_list")

    return render(
        request,
        "products/product_form.html",
        {"form": form, "title": "Тағйир додани маҳсулот"},
    )

@login_required
def order_list(request):
    status = request.GET.get("status", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    orders = Order.objects.all()

    if status:
        orders = orders.filter(status=status)
    if start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__date__lte=end_date)

    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_create(request):
    products = Product.objects.filter(is_active=True)

    if request.method == "POST":
        order = Order.objects.create(status="new")

        product_ids = request.POST.getlist("product")
        quantities = request.POST.getlist("quantity")

        for product_id, quantity in zip(product_ids, quantities):
            try:
                product = Product.objects.get(pk=product_id)
                quantity = int(quantity)
            except (Product.DoesNotExist, ValueError):
                continue

            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.selling_price,
                    unit_purchase_price=product.purchase_price,
                )

        messages.success(request, f"Заказ {order.order_number} создан.")
        return redirect("order_detail", pk=order.pk)

    return render(request, "orders/order_form.html", {"products": products})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            old_status = Order.objects.get(pk=order.pk).status
            new_status = form.cleaned_data["status"]
            form.save()

            if new_status == "delivered" and old_status != "delivered" and not order.stock_updated:
                for item in order.items.all():
                    product = item.product
                    product.stock_quantity = max(0, product.stock_quantity - item.quantity)
                    product.save()
                order.stock_updated = True
                order.save()

            if new_status == "returned" and old_status != "returned" and order.stock_updated:
                for item in order.items.all():
                    product = item.product
                    product.stock_quantity += item.quantity
                    product.save()
                order.stock_updated = False
                order.save()

            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)

    return render(request, "orders/order_detail.html", {"order": order, "form": form})


@login_required
def order_add_item(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderItemForm()

    return render(request, "orders/order_item_form.html", {"order": order, "form": form})


@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, "expenses/expense_list.html", {"expenses": expenses})


@login_required
def expense_create(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("expense_list")
    return render(request, "expenses/expense_form.html", {"form": form, "title": "Добавить расход"})


@login_required
def report(request):
    period = request.GET.get("period", "today")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    today = timezone.localdate()

    if period == "today":
        start, end = today, today
    elif period == "yesterday":
        start = end = today - timedelta(days=1)
    elif period == "month":
        start, end = today.replace(day=1), today
    elif period == "custom" and start_date and end_date:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    else:
        start, end = today, today

    orders = Order.objects.filter(status="delivered", created_at__date__range=(start, end))
    expenses = Expense.objects.filter(date__range=(start, end))

    revenue = sum(order.total for order in orders)
    cost = sum(order.total_purchase for order in orders)
    expenses_total = expenses.aggregate(total=Sum("amount"))["total"] or 0
    gross_profit = revenue - cost
    net_profit = gross_profit - expenses_total

    context = {
        "start": start,
        "end": end,
        "orders_count": orders.count(),
        "revenue": revenue,
        "cost": cost,
        "expenses_total": expenses_total,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "expenses": expenses,
    }
    return render(request, "reports/report.html", context)


from django.contrib import messages
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.is_active = False
        product.save()
        messages.success(request, "Товар деактивирован.")
        return redirect("product_list")

    return render(
        request,
        "confirm_delete.html",
        {
            "title": "Деактивировать товар",
            "object_name": str(product),
            "cancel_url": "product_list",
        },
    )


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    form = ExpenseForm(request.POST or None, instance=expense)

    if form.is_valid():
        form.save()
        messages.success(request, "Расход обновлен.")
        return redirect("expense_list")

    return render(
        request,
        "expenses/expense_form.html",
        {"form": form, "title": "Изменить расход"},
    )


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Расход удален.")
        return redirect("expense_list")

    return render(
        request,
        "confirm_delete.html",
        {
            "title": "Удалить расход",
            "object_name": str(expense),
            "cancel_url": "expense_list",
        },
    )


@login_required
def order_item_delete(request, pk):
    item = get_object_or_404(OrderItem, pk=pk)
    order_pk = item.order.pk

    if request.method == "POST":
        item.delete()
        messages.success(request, "Товар удален из заказа.")
        return redirect("order_detail", pk=order_pk)

    return render(
        request,
        "confirm_delete.html",
        {
            "title": "Удалить позицию заказа",
            "object_name": str(item),
            "cancel_url": f"/orders/{order_pk}/",
        },
    )