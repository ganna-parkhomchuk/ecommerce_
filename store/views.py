from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from liqpay import LiqPay

from .models import *
from .utils import cookieCart, cartData, guestOrder


# def product_detail(request, product_id):
#     product = get_object_or_404(Product, pk=product_id)
#     return render(request, 'store/product_detail.html', {'product': product})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Получаем информацию о корзине
    data = cartData(request)
    cartItems = data['cartItems']

    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/product_detail.html', context)


def store(request):
    """
        View for rendering the main store page.

        Parameters:
        - request: HTTP request object.

        Returns:
        - Rendered HTML page displaying the store.
        """
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    """
        View for rendering the shopping cart page.

        Parameters:
        - request: HTTP request object.

        Returns:
        - Rendered HTML page displaying the shopping cart.
        """
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    """
        View for rendering the checkout page.

        Parameters:
        - request: HTTP request object.

        Returns:
        - Rendered HTML page displaying the checkout.
        """
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    order_data = {
        "amount": str(order.get_cart_total),
        "currency": "UAH",
        "description": "Order description",
        "transaction_id": str(order.transaction_id),
        "version": "3",
        "action": "pay"
    }

    public_key = "sandbox_12345"
    private_key = "sandbox_54321"

    # Creating LiqPay object
    liqpay = LiqPay(public_key, private_key)

    # Receiving HTML-form Liqpay
    liqpay_form = liqpay.cnb_form(order_data)

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    """
        View for handling AJAX requests to update the quantity of items in the cart.

        Parameters:
        - request: HTTP request object.

        Returns:
        - JsonResponse: JSON response indicating the success of the item update.
        """
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    """
    View for handling AJAX requests to process an order.

    Parameters:
    - request: HTTP request object.

    Returns:
    - JsonResponse: JSON response indicating the success of the order processing.
    """
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete!', safe=False)
