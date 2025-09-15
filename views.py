from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.urls import reverse
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import json

from .models import CustomerProfile, ShopOwnerProfile, Food, Order, OrderItem


# ✅ Custom LoginView for role-based redirection
class RoleBasedLoginView(LoginView):
    template_name = 'canteen/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'customerprofile'):
            return reverse('customer_dashboard')
        elif hasattr(user, 'shopownerprofile'):
            return reverse('shop_owner_dashboard')
        return reverse('home')


def home(request):
    return render(request, 'canteen/home.html')


def customer_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        roll_no = request.POST.get('roll_no', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'canteen/customer_signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        CustomerProfile.objects.create(user=user, name=name, roll_no=roll_no)
        
        messages.success(request, 'Account created successfully')
        return redirect('login')
    
    return render(request, 'canteen/customer_signup.html')


def shop_owner_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        shop_name = request.POST['shop_name']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'canteen/shop_owner_signup.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        ShopOwnerProfile.objects.create(user=user, name=name, shop_name=shop_name)
        
        messages.success(request, 'Account created successfully')
        return redirect('login')
    
    return render(request, 'canteen/shop_owner_signup.html')


@login_required
def dashboard(request):
    try:
        customer_profile = CustomerProfile.objects.get(user=request.user)
        return redirect('customer_dashboard')
    except CustomerProfile.DoesNotExist:
        pass

    try:
        shop_owner_profile = ShopOwnerProfile.objects.get(user=request.user)
        return redirect('shop_owner_dashboard')
    except ShopOwnerProfile.DoesNotExist:
        pass

    return redirect('home')


@login_required
def customer_dashboard(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    foods = Food.objects.filter(available=True, stock__gt=0)
    
    context = {
        'customer_profile': customer_profile,
        'foods': foods,
    }
    return render(request, 'canteen/customer_dashboard.html', context)


@login_required
def place_order(request):
    if request.method == 'POST':
        customer_profile = get_object_or_404(CustomerProfile, user=request.user)
        data = json.loads(request.body)
        
        cart_items = data.get('cart_items', [])
        scheduled_time = data.get('scheduled_time')
        
        if not cart_items:
            return JsonResponse({'success': False, 'message': 'Cart is empty'})
        
        scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        shop_orders = {}
        for item in cart_items:
            food = get_object_or_404(Food, id=item['food_id'])
            if food.shop_owner.id not in shop_orders:
                shop_orders[food.shop_owner.id] = {
                    'shop_owner': food.shop_owner,
                    'items': [],
                    'total': 0
                }
            shop_orders[food.shop_owner.id]['items'].append({
                'food': food,
                'quantity': item['quantity']
            })
            shop_orders[food.shop_owner.id]['total'] += food.price * item['quantity']
        
        for shop_id, order_data in shop_orders.items():
            order = Order.objects.create(
                customer=customer_profile,
                shop_owner=order_data['shop_owner'],
                scheduled_time=scheduled_datetime,
                total_amount=order_data['total']
            )
            
            for item_data in order_data['items']:
                OrderItem.objects.create(
                    order=order,
                    food=item_data['food'],
                    quantity=item_data['quantity']
                )
                food = item_data['food']
                food.stock -= item_data['quantity']
                food.save()
        
        return JsonResponse({'success': True, 'message': 'Order placed successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def customer_orders(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    orders = Order.objects.filter(customer=customer_profile).order_by('-order_time')
    
    return render(request, 'canteen/customer_orders.html', {'orders': orders})


@login_required
def shop_owner_dashboard(request):
    shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
    today = timezone.now().date()
    today_orders = Order.objects.filter(
        shop_owner=shop_owner_profile,
        order_time__date=today
    )
    
    total_orders = today_orders.count()
    total_income = today_orders.filter(status='accepted').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    pending_orders = today_orders.filter(status='pending').count()
    
    context = {
        'shop_owner_profile': shop_owner_profile,
        'total_orders': total_orders,
        'total_income': total_income,
        'pending_orders': pending_orders,
    }
    return render(request, 'canteen/shop_owner_dashboard.html', context)


@login_required
def manage_orders(request):
    shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
    orders = Order.objects.filter(shop_owner=shop_owner_profile).order_by('-order_time')
    return render(request, 'canteen/manage_orders.html', {'orders': orders})


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
        order = get_object_or_404(Order, id=order_id, shop_owner=shop_owner_profile)

        new_status = request.POST.get('status')
        print("New status:", new_status)  # ✅ Debug print

        allowed_statuses = ['pending', 'accepted', 'ready', 'collected', 'rejected', 'cancelled']

        if new_status in allowed_statuses:
            if order.status in ['collected', 'cancelled']:
                messages.error(request, 'You cannot update a collected or cancelled order.')
            else:
                order.status = new_status
                order.save()
                messages.success(request, f'Order status updated to {new_status}')
        else:
            messages.error(request, f'Invalid status: {new_status}')
    
    return redirect('manage_orders')



@login_required
def manage_food_items(request):
    shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
    foods = Food.objects.filter(shop_owner=shop_owner_profile)
    return render(request, 'canteen/manage_food_items.html', {'foods': foods})


@login_required
def add_food_item(request):
    if request.method == 'POST':
        shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
        
        name = request.POST['name']
        price = request.POST['price']
        stock = request.POST['stock']
        image = request.FILES.get('image')
        
        Food.objects.create(
            name=name,
            price=price,
            stock=stock,
            image=image,
            shop_owner=shop_owner_profile
        )
        messages.success(request, 'Food item added successfully')
        return redirect('manage_food_items')
    
    return render(request, 'canteen/add_food_item.html')


@login_required
def edit_food_item(request, food_id):
    shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
    food = get_object_or_404(Food, id=food_id, shop_owner=shop_owner_profile)
    
    if request.method == 'POST':
        food.name = request.POST['name']
        food.price = request.POST['price']
        food.stock = request.POST['stock']
        food.available = 'available' in request.POST
        
        if 'image' in request.FILES:
            food.image = request.FILES['image']
        
        food.save()
        messages.success(request, 'Food item updated successfully')
        return redirect('manage_food_items')
    
    return render(request, 'canteen/edit_food_item.html', {'food': food})


@login_required
def generate_receipt(request, order_id):
    try:
        customer_profile = CustomerProfile.objects.get(user=request.user)
        order = get_object_or_404(Order, id=order_id, customer=customer_profile)
    except CustomerProfile.DoesNotExist:
        shop_owner_profile = get_object_or_404(ShopOwnerProfile, user=request.user)
        order = get_object_or_404(Order, id=order_id, shop_owner=shop_owner_profile)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{order.id}.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Receipt - Order #{order.id}")
    
    p.setFont("Helvetica", 12)
    y = height - 100
    p.drawString(50, y, f"Customer: {order.customer.name}")
    y -= 20
    p.drawString(50, y, f"Shop: {order.shop_owner.shop_name}")
    y -= 20
    p.drawString(50, y, f"Order Time: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Scheduled Time: {order.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
    y -= 20
    p.drawString(50, y, f"Status: {order.get_status_display()}")
    y -= 40
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Items:")
    y -= 20
    
    p.setFont("Helvetica", 10)
    for item in order.items.all():
        p.drawString(70, y, f"{item.food.name} x {item.quantity} = ${item.get_total_price()}")
        y -= 15
    
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Amount: ${order.total_amount}")
    
    p.showPage()
    p.save()
    
    return response
