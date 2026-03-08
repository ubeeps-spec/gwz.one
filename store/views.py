from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from .models import Product, Order, OrderItem, Coupon, PaymentMethod, OrderNote, UserProfile, HeroSlide, Page, Wishlist
from decimal import Decimal
from django.utils import timezone
from .forms import CouponApplyForm, RegisterForm
from django.contrib import messages
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # If no secret set, try to construct event without signature verification (INSECURE - Dev only)
            # Or just parse the payload directly
            import json
            event = json.loads(payload)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Find order with this payment intent in notes
        # This is a bit hacky, ideally we should store payment_intent_id in Order model
        # But for now we search in OrderNote
        try:
            # Note format: "Stripe PaymentIntent confirmed: {intent_id}"
            note = OrderNote.objects.filter(message__contains=payment_intent['id']).first()
            if note:
                order = note.order
                if order.status != 'paid':
                    order.status = 'paid'
                    order.save()
                    OrderNote.objects.create(order=order, message="Payment confirmed via Webhook.")
        except Exception as e:
            pass

    return HttpResponse(status=200)

from django.db.models import Q, Count
from django.conf import settings
import stripe

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful.")
            return redirect('product_list')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def coupon_apply(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            now = timezone.now()
            try:
                coupon = Coupon.objects.get(code__iexact=code, valid_from__lte=now, valid_to__gte=now, active=True)
                request.session['coupon_id'] = coupon.id
                messages.success(request, f"Coupon '{code}' applied successfully!")
            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
                messages.error(request, "Invalid or expired coupon code.")
    
    # Redirect back to where the user came from (e.g. checkout or cart)
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
        
    return redirect('cart_view')

def index(request):
    hero_slides = HeroSlide.objects.filter(is_active=True)
    
    # Get featured products (e.g., newest 4 or specific category)
    featured_products = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:4]

    # Fallback: if no featured products, show newest
    if not featured_products:
         featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:4]

    return render(request, 'index.html', {
        'hero_slides': hero_slides,
        'featured_products': featured_products,
    })

def product_list(request, is_shop=False):
    # If this is the homepage URL ('/') but not explicitly the shop page, redirect to new index view
    if request.path == '/' and not is_shop:
         return index(request)

    products = Product.objects.filter(is_active=True)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(categories__name=category_filter)
        
    # Sorting Logic
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
    
    # Grid Layout (Columns)
    grid_cols = request.GET.get('cols', '3')
    
    # Get categories with count
    # Old: Product.objects.filter(is_active=True).values('category').annotate(count=Count('id')).order_by('category')
    # New: Query Category model directly
    from .models import Category
    from django.core.paginator import Paginator
    categories = Category.objects.annotate(
        count=Count('products', filter=Q(products__is_active=True))
    ).filter(count__gt=0).order_by('name')
    
    hero_slides = HeroSlide.objects.filter(is_active=True)

    # Pagination Logic
    per_page = request.GET.get('per_page', '9') # Default to 9
    try:
        per_page = int(per_page)
        if per_page not in [9, 12, 18, 24]:
            per_page = 9
    except ValueError:
        per_page = 9
        
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Elided pagination
    custom_page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'store/product_list.html', {
        'products': page_obj, 
        'custom_page_range': custom_page_range,
        'search_query': query,
        'categories': categories,
        'current_category': category_filter,
        'is_shop_page': is_shop,
        'hero_slides': hero_slides,
        'per_page': per_page,
        'sort_by': sort_by,
        'grid_cols': grid_cols,
        'wishlist_product_ids': wishlist_product_ids
    })


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    
    context = {'page': page}
    
    if slug == 'about-us':
        book_images = []
        book_dir = os.path.join(settings.MEDIA_ROOT, 'book')
        if os.path.isdir(book_dir):
            for fname in sorted(os.listdir(book_dir)):
                lower = fname.lower()
                if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    book_images.append({
                        'url': settings.MEDIA_URL + 'book/' + fname,
                        'name': os.path.splitext(fname)[0]
                    })
        context['book_images'] = book_images
        
    return render(request, 'store/page_detail.html', context)

def tutorial(request):
    try:
        page = Page.objects.get(slug='tutorial', is_active=True)
    except Page.DoesNotExist:
        page = None
    return render(request, 'store/tutorial.html', {'page': page})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'store/product_detail.html', {'product': product, 'is_wishlisted': is_wishlisted})


@login_required
def toggle_wishlist(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                wishlist_item.delete()
                is_wishlisted = False
            else:
                is_wishlisted = True
                
            count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({'status': 'ok', 'is_wishlisted': is_wishlisted, 'count': count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, _("Removed from wishlist."))
    return redirect('profile')



@login_required
def wishlist_view(request):
    return redirect(reverse('profile') + '#wishlist')


def _get_cart(session):
    return session.setdefault('cart', {})


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    qty = int(request.POST.get('quantity', 1))
    
    # Check Stock
    if product.stock < qty:
        messages.error(request, _("Sorry, %(name)s is out of stock (remaining: %(stock)s)") % {'name': product.name, 'stock': product.stock})
        # Redirect back to product detail or list
        return redirect(request.META.get('HTTP_REFERER', 'product_list'))

    cart = _get_cart(request.session)
    
    # Determine image URL
    img_url = ''
    if product.image:
        img_url = product.image.url
    elif product.image_url:
        img_url = product.image_url
        
    item = cart.get(str(product.id), {'name': product.name, 'price': str(product.effective_price()), 'qty': 0, 'image': img_url})
    
    # Check if total quantity exceeds stock
    new_qty = item['qty'] + qty
    if product.stock < new_qty:
        messages.error(request, _("Sorry, %(name)s is out of stock (current cart: %(qty)s, remaining: %(stock)s)") % {'name': product.name, 'qty': item['qty'], 'stock': product.stock})
        return redirect('cart_view')
        
    item['qty'] = new_qty
    item['image'] = img_url  # Ensure image is set/updated
    cart[str(product.id)] = item
    request.session.modified = True
    messages.success(request, _("Added %(name)s to cart") % {'name': product.name})
    return redirect('cart_view')


def cart_remove(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('cart_view')


def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    total = Decimal('0')
    for pid, item in cart.items():
        price = Decimal(item['price'])
        qty = int(item['qty'])
        subtotal = price * qty
        items.append({'id': int(pid), 'name': item['name'], 'price': price, 'qty': qty, 'subtotal': subtotal, 'image': item.get('image', '')})
        total += subtotal
    
    # Coupon logic
    coupon_id = request.session.get('coupon_id')
    coupon = None
    discount = Decimal('0')
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            discount = coupon.calculate_discount(total)
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    
    if total < discount:
        discount = total
    
    grand_total = total - discount
    coupon_form = CouponApplyForm()

    return render(request, 'store/cart.html', {
        'items': items, 
        'total': total, 
        'coupon': coupon, 
        'discount': discount, 
        'grand_total': grand_total,
        'coupon_form': coupon_form
    })


@login_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        return redirect('product_list')
    
    # Get Coupon Object
    coupon_id = request.session.get('coupon_id')
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    if request.method == 'POST':
        name = request.POST.get('customer_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        notes = request.POST.get('notes', '').strip()
        payment_method_id = request.POST.get('payment_method')
        
        # First check stock
        for pid, item in cart.items():
            product = get_object_or_404(Product, id=int(pid))
            if product.stock < int(item['qty']):
                from django.contrib import messages
                messages.error(request, f"抱歉，{product.name} 庫存不足 (僅剩 {product.stock})，請調整數量。")
                return redirect('cart_view')

        # Validate Payment Method BEFORE creating order
        if payment_method_id:
            try:
                pm_check = PaymentMethod.objects.get(id=payment_method_id)
                if pm_check.code == 'credit_card' and not request.POST.get('stripe_payment_intent'):
                    messages.error(request, "信用卡付款未完成或失敗，請確認信用卡資訊並重試。")
                    return redirect('checkout')
            except PaymentMethod.DoesNotExist:
                pass

        # Create Order (initial)
        ip_address = _get_client_ip(request)
        order = Order.objects.create(
            customer_name=name, email=email, phone=phone, address=address, notes=notes, status='created',
            coupon=coupon, discount_amount=0, # Will update later
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address
        )
        
        # Handle Payment Method
        if payment_method_id:
            try:
                pm = PaymentMethod.objects.get(id=payment_method_id)
                order.payment_method = pm
                
                # If Payment Method requires proof, check for file upload
                if pm.requires_proof and 'payment_proof' in request.FILES:
                    order.payment_proof = request.FILES['payment_proof']
                    # Add a note that proof was uploaded
                    OrderNote.objects.create(order=order, message=f"Customer uploaded payment proof ({pm.name} Receipt).")
                # If Credit Card, capture masked info in order note (do not store card)
                if pm.code == 'credit_card':
                    intent_id = request.POST.get('stripe_payment_intent')
                    if intent_id:
                        OrderNote.objects.create(order=order, message=f"Stripe PaymentIntent confirmed: {intent_id}")
                    else:
                        # If no payment intent, and it's credit card, this is an invalid attempt (unless testing)
                        # But since we already created the order, we should probably mark it as 'created' or 'cancelled' 
                        # instead of 'paid'.
                        # Better yet, prevent order creation if payment failed?
                        # For now, let's just ensure status is NOT 'paid'
                        pass
                    
            except PaymentMethod.DoesNotExist:
                pass
        
        total = Decimal('0')
        for pid, item in cart.items():
            product = get_object_or_404(Product, id=int(pid))
            price = Decimal(item['price'])
            qty = int(item['qty'])
            
            # Deduct stock
            product.stock -= qty
            product.save()
            
            subtotal = price * qty
            OrderItem.objects.create(order=order, product=product, unit_price=price, quantity=qty, subtotal=subtotal)
            total += subtotal
        
        # Calculate Discount
        discount = Decimal('0')
        if coupon:
            discount = coupon.calculate_discount(total)

        # Apply discount to total
        if total < discount:
            discount = total
        
        order.discount_amount = discount
        order.total_amount = total - discount
        
        # Status logic
        if order.payment_method and order.payment_method.requires_proof:
            order.status = 'created' # Wait for verification
        elif order.payment_method and order.payment_method.code in ['cod', 'cash_on_delivery']:
            order.status = 'fulfilling' # Confirmed but not yet paid
        elif order.payment_method and order.payment_method.code == 'credit_card':
            if request.POST.get('stripe_payment_intent'):
                order.status = 'paid'
            else:
                order.status = 'created' # Payment failed or not completed
        else:
            order.status = 'paid' # Assume instant payment for others
            
        order.save()
        request.session['cart'] = {}
        request.session['coupon_id'] = None
        request.session.modified = True
        return redirect(reverse('order_success', kwargs={'order_id': order.id}))
    
    # GET Request: Calculate totals for display
    items = []
    total = Decimal('0')
    for pid, item in cart.items():
        price = Decimal(item['price'])
        qty = int(item['qty'])
        subtotal = price * qty
        items.append({'id': int(pid), 'name': item['name'], 'price': price, 'qty': qty, 'subtotal': subtotal})
        total += subtotal
    
    discount = Decimal('0')
    if coupon:
        discount = coupon.calculate_discount(total)
        
    if total < discount:
        discount = total
    grand_total = total - discount
    
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    # Stripe PaymentIntent (for credit card)
    stripe_public_key = None
    client_secret = None
    stripe_error = None
    stripe_min_amount_warning = None

    if getattr(settings, 'STRIPE_ENABLED', False) and grand_total > 0:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY
        
        # Check minimum amount for HKD (approx 4.00 HKD)
        if grand_total < Decimal('4.00'):
             stripe_min_amount_warning = _("Minimum amount for credit card payment is HK$4.00")
        else:
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(grand_total * 100),  # cents
                    currency='hkd',
                    automatic_payment_methods={'enabled': True},
                    description='PrintSmart Order (Preview)',
                )
                client_secret = intent.client_secret
            except Exception as e:
                stripe_error = str(e)
                print(f"Stripe Error: {e}") # Log to console/logs

    # Pre-fill user data if authenticated
    user_data = {}
    if request.user.is_authenticated:
        user_data['first_name'] = request.user.first_name
        user_data['last_name'] = request.user.last_name
        user_data['email'] = request.user.email
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_data['phone'] = profile.phone
            user_data['address'] = profile.address
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'store/checkout.html', {
        'items': items, 
        'total': total,
        'coupon': coupon,
        'discount': discount,
        'grand_total': grand_total,
        'payment_methods': payment_methods,
        'stripe_public_key': stripe_public_key,
        'stripe_client_secret': client_secret,
        'stripe_error': stripe_error,
        'stripe_min_amount_warning': stripe_min_amount_warning,
        'user_data': user_data
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})


def invoice_view(request, order_id):
    # Only allow admin or staff to view invoices, or potentially the user who owns it (if we had user accounts)
    # For now, let's restrict to staff member required
    if not request.user.is_staff:
        # Alternatively, if it's a public link, use a UUID or similar. 
        # But per requirements "Order Management System", this is likely for Admin use.
        from django.contrib.auth.decorators import login_required, user_passes_test
        return redirect('admin:login')
        
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/invoice.html', {'order': order})


from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    active_coupons = Coupon.objects.filter(active=True, valid_to__gte=timezone.now())
    
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=profile)
            password_form = PasswordChangeForm(request.user)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, '個人資料已更新')
                return redirect('profile')
        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = UserProfileForm(instance=profile)
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, '密碼已成功修改')
                return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
        password_form = PasswordChangeForm(request.user)
        
    context = {
        'orders': orders,
        'wishlist_items': wishlist_items,
        'active_coupons': active_coupons,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'store/profile.html', context)

@login_required
def user_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/user_order_detail.html', {'order': order})

def contact_view(request):
    return render(request, 'store/contact.html')

def press_gallery(request):
    # Fetch Video/Blog content
    try:
        video_page = Page.objects.get(slug='blog', is_active=True)
    except Page.DoesNotExist:
        video_page = None

    # Fetch Press Images
    images = []
    press_dir = os.path.join(settings.MEDIA_ROOT, 'press')
    if os.path.isdir(press_dir):
        for fname in sorted(os.listdir(press_dir)):
            lower = fname.lower()
            if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                images.append({
                    'url': settings.MEDIA_URL + 'press/' + fname,
                    'name': os.path.splitext(fname)[0]
                })

    return render(request, 'store/press.html', {'images': images, 'video_page': video_page})

def gallery_view(request):
    images = []
    gal_dir = os.path.join(settings.MEDIA_ROOT, 'gallery')
    if os.path.isdir(gal_dir):
        for fname in sorted(os.listdir(gal_dir)):
            lower = fname.lower()
            if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                images.append({
                    'url': settings.MEDIA_URL + 'gallery/' + fname,
                    'name': os.path.splitext(fname)[0]
                })
    return render(request, 'store/gallery.html', {'images': images})
