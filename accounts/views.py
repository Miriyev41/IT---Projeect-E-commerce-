from django.shortcuts import render, redirect, get_object_or_404
from .models import Account, UserProfile
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from .forms import UserForm, UserProfileForm
from carts.models import Cart, CartItem
from carts.views import _cart_id 

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            if Account.objects.filter(email=email).exists():
                messages.error(request, 'Email address already exists')
                return redirect('register')
            else:
                username = email.split("@")[0]
                user = Account.objects.create_user(
                    first_name=first_name, 
                    last_name=last_name, 
                    email=email, 
                    username=username, 
                    password=password
                )
                user.phone_number = phone_number
                user.is_active = True 
                user.save()
                profile = UserProfile()
                profile.user_id = user.id
                profile.save()

                messages.success(request, 'Registration successful!')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

    return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                guest_cart_items = CartItem.objects.filter(cart=cart)
                
                if guest_cart_items.exists():
                    for item in guest_cart_items:
                        item.user = user
                        item.cart = None 
                        item.save()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


from orders.models import Order 

@login_required(login_url='login')
def dashboard(request):

    orders = Order.objects.order_by('-created_at').filter(user=request.user, is_ordered=True)
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'orders': orders,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)