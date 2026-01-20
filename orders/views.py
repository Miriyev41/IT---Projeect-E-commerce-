from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Order, Payment, OrderProduct
from carts.models import CartItem
from store.models import Product
import json
import datetime
from django.contrib.auth.decorators import login_required

# 1. Logic to save the initial order details from the checkout form
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = 0
    grand_total = total

    if request.method == 'POST':
        # Create the order record
        data = Order()
        data.user = current_user
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address_line_1 = request.POST.get('address_line_1')
        data.city = request.POST.get('city')
        data.country = request.POST.get('country')
        data.order_total = grand_total
        data.tax = tax
        data.save() 

        # Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save() 

        # --- ADDED THIS FOR LOCAL TESTING ---
        # This creates the OrderProduct records immediately so you see them in Admin
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = data.id # Link to the new order
            orderproduct.user_id = current_user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = False # False because payment isn't done yet
            orderproduct.save()
        # ------------------------------------

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
        }
        return render(request, 'orders/payments.html', context)
    
    return redirect('checkout')

# 2. Logic to handle the PayPal payment data (Backend update)
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    # Update the Order
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # Update Stock
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear the Cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order details back to JavaScript to redirect to success page
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)

# 3. Logic to display the final "Thank You" receipt page
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')
    
@login_required(login_url='login')
def order_detail(request, order_id):
    try:
        # Get the specific order and all products inside it
        order_detail = OrderProduct.objects.filter(order__order_number=order_id)
        order = Order.objects.get(order_number=order_id)
        
        subtotal = 0
        for i in order_detail:
            subtotal += i.product_price * i.quantity

        context = {
            'order_detail': order_detail,
            'order': order,
            'subtotal': subtotal,
        }
        return render(request, 'accounts/order_detail.html', context)
    except (Order.DoesNotExist):
        return redirect('dashboard')

