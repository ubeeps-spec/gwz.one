from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Customer(User):
    class Meta:
        proxy = True
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_("User"))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Phone"))
    address = models.CharField(max_length=255, blank=True, verbose_name=_("Address"))
    
    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Category Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Product Name"))
    slug = models.SlugField(max_length=220, unique=True, verbose_name=_("Slug"))
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("特價"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    categories = models.ManyToManyField(Category, blank=True, related_name="products", verbose_name=_("Categories"))
    description = RichTextField(blank=True, verbose_name=_("Description"))
    specs = RichTextField(blank=True, verbose_name=_("Specifications"))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("Product Image"))
    image_url = models.URLField(blank=True, verbose_name=_("Image URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_featured = models.BooleanField(default=False, verbose_name=_("精選商品"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def effective_price(self):
        return self.discount_price if self.discount_price is not None else self.price

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name=_("Product"))
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("Image"))
    image_url = models.URLField(blank=True, verbose_name=_("Image URL"))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_("Caption"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    
    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return f"{self.product.name} Image #{self.id}"

class Page(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    content = RichTextField(verbose_name=_("Content"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    # About Us Specific Fields
    feature_title = models.CharField(max_length=200, blank=True, verbose_name=_("Feature Title"))
    feature_subtitle = models.CharField(max_length=500, blank=True, verbose_name=_("Feature Subtitle"))
    feature_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Feature Image"))
    
    founder_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Founder Image"))
    founder_name = models.CharField(max_length=100, blank=True, verbose_name=_("Founder Name"))
    founder_intro_title = models.CharField(max_length=200, blank=True, verbose_name=_("Founder Intro Title"))
    founder_intro_text = models.TextField(blank=True, verbose_name=_("Founder Intro Text"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __str__(self):
        return self.title

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    instructions = RichTextField(blank=True, verbose_name=_("Instructions"))
    requires_proof = models.BooleanField(default=False, verbose_name=_("Requires Proof"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Coupon Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    discount_type = models.CharField(max_length=20, choices=[('percent', _('Percentage')), ('fixed', _('Fixed Amount'))], default='percent', verbose_name=_("Discount Type"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Discount Value"))
    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_to = models.DateTimeField(verbose_name=_("Valid To"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return self.code

    def calculate_discount(self, total):
        if self.discount_type == 'percent':
             return total * (self.discount / 100)
        return self.discount

class Order(models.Model):
    STATUS_CHOICES = [
        ('created', _('Created')),
        ('paid', _('Paid')),
        ('fulfilling', _('Fulfilling')),
        ('partially_shipped', _('Partially Shipped')),
        ('shipped', _('Shipped')),
        ('completed', _('Completed')),
        ('canceled', _('Canceled')),
        ('returned', _('Returned')),
        ('refunded', _('Refunded')),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False, verbose_name=_("Order Number"), null=True)
    user = models.ForeignKey(User, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("User Account"))
    customer_name = models.CharField(max_length=100, verbose_name=_("Customer Name"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Phone"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Coupon"))
    payment_method = models.ForeignKey(PaymentMethod, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("Payment Method"))
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True, verbose_name=_("Payment Proof"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Discount Amount"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name=_("Status"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("Total Amount"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f'{self.order_number} - {self.customer_name}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            dt = self.created_at or timezone.now()
            self.order_number = f"ORD-{dt.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_("Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Unit Price"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Subtotal"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.discount_price if self.product.discount_price else self.product.price
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

class OrderNote(models.Model):
    order = models.ForeignKey(Order, related_name='order_notes', on_delete=models.CASCADE, verbose_name=_("Order"))
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("User"))
    message = models.TextField(verbose_name=_("Message"))
    is_customer_note = models.BooleanField(default=False, verbose_name=_("Sent to Customer"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Order Note")
        verbose_name_plural = _("Order Notes")
    
    def __str__(self):
        return f"Note for {self.order}"

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="My E-Shop", verbose_name=_("Site Name"))
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Logo"))
    hero_banner = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Hero Banner"))
    hero_title = models.CharField(max_length=200, blank=True, verbose_name=_("Hero Title"))
    hero_subtitle = models.CharField(max_length=200, blank=True, verbose_name=_("Hero Subtitle"))
    hero_button_text = models.CharField(max_length=50, blank=True, verbose_name=_("Hero Button Text"))
    hero_link = models.URLField(blank=True, verbose_name=_("Hero Link"))
    
    # YouTube Playlist
    youtube_playlist_url = models.URLField(blank=True, default="https://www.youtube.com/embed/videoseries?list=PLEjO4hD4At7yhmox4RhnjRWaUujB24TZ2", verbose_name=_("YouTube Playlist URL"), help_text=_("Embed URL for the playlist"))

    # Feature Section (Middle of Homepage)
    feature_title = models.CharField(max_length=200, blank=True, default="我們有什麽", verbose_name=_("Feature Title"))
    feature_subtitle = models.CharField(max_length=500, blank=True, default="加入我們對食物的精雕細琢之旅，感受我們的美食文化與獨特風格", verbose_name=_("Feature Subtitle"))
    feature_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Feature Image"))
    
    # Founder Section (Intro)
    founder_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name=_("Founder Image"))
    founder_name = models.CharField(max_length=100, blank=True, default="王子", verbose_name=_("Founder Name"))
    founder_intro_title = models.CharField(max_length=200, blank=True, default="平凡中見不凡", verbose_name=_("Founder Intro Title"))
    founder_intro_text = models.TextField(blank=True, default="加入王子的美食之旅，享受生活中的美好事物！", verbose_name=_("Founder Intro Text"))

    contact_phone = models.CharField(max_length=50, blank=True, verbose_name=_("Contact Phone"))
    contact_email = models.EmailField(blank=True, verbose_name=_("Contact Email"))
    contact_address = models.CharField(max_length=255, blank=True, verbose_name=_("Contact Address"))
    contact_opening_hours = models.CharField(max_length=255, blank=True, default="週一至週日: 10:00AM - 10:00PM", verbose_name=_("Opening Hours"))
    
    footer_about = models.TextField(blank=True, verbose_name=_("Footer About"))
    footer_copyright = models.CharField(max_length=200, blank=True, default="Copyright © 2026 GWZ", verbose_name=_("Footer Copyright"))
    
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    youtube_url = models.URLField(blank=True, verbose_name=_("YouTube URL"))
    whatsapp_url = models.URLField(blank=True, verbose_name=_("WhatsApp URL"))
    
    # Tracking Pixels
    facebook_pixel_id = models.CharField(max_length=50, blank=True, help_text="Example: 123456789", verbose_name=_("Facebook Pixel ID"))
    google_analytics_id = models.CharField(max_length=50, blank=True, help_text="Example: G-XXXXXXXXXX", verbose_name=_("Google Analytics ID"))
    
    # SMTP Email Settings
    smtp_host = models.CharField(max_length=200, blank=True, verbose_name=_("SMTP Host"))
    smtp_port = models.IntegerField(default=587, verbose_name=_("SMTP Port"))
    smtp_user = models.CharField(max_length=200, blank=True, verbose_name=_("SMTP User"))
    smtp_password = models.CharField(max_length=200, blank=True, verbose_name=_("SMTP Password"))
    smtp_use_tls = models.BooleanField(default=True, verbose_name=_("Use TLS"))
    smtp_from_email = models.EmailField(blank=True, verbose_name=_("From Email"))

    # Main Menu Text Customization
    menu_home_text = models.CharField(max_length=50, default="首頁", verbose_name=_("Menu Home Text"))
    menu_about_text = models.CharField(max_length=50, default="關於GWZ", verbose_name=_("Menu About Text"))
    menu_videos_text = models.CharField(max_length=50, default="王子煮場", verbose_name=_("Menu Videos Text"))
    menu_lifestyle_text = models.CharField(max_length=50, default="味覺足跡", verbose_name=_("Menu Lifestyle Text"))
    menu_store_text = models.CharField(max_length=50, default="GWZ商店", verbose_name=_("Menu Store Text"))
    menu_contact_text = models.CharField(max_length=50, default="聯絡我們", verbose_name=_("Menu Contact Text"))

    # Colors
    top_bar_bg_color = models.CharField(max_length=20, default="#5D2E86", verbose_name=_("Top Bar Bg Color"), help_text=_("Hex color code (e.g. #5D2E86)"))
    navbar_bg_color = models.CharField(max_length=20, default="#5D2E86", verbose_name=_("Navbar Bg Color"), help_text=_("Hex color code (e.g. #5D2E86)"))
    navbar_text_color = models.CharField(max_length=20, default="#ffffff", verbose_name=_("Navbar Text Color"), help_text=_("Hex color code (e.g. #ffffff)"))
    navbar_items = models.TextField(default="HP, CANON, BROTHER, EPSON, SAMSUNG, XEROX, PANTUM, LEXMARK, KODAK, 其他商品", verbose_name=_("Navbar Items"), help_text=_("Comma separated list"))
    product_label_bg_color = models.CharField(max_length=20, default="#5D2E86", verbose_name=_("Product Label Bg Color"))
    product_label_text_color = models.CharField(max_length=20, default="#ffffff", verbose_name=_("Product Label Text Color"))

    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")

    def __str__(self):
        return self.site_name
        
    def get_navbar_items_list(self):
        if self.navbar_items:
            return [item.strip() for item in self.navbar_items.split(',')]
        return []

class HeroSlide(models.Model):
    image = models.ImageField(upload_to='hero_slides/', verbose_name=_("Image"), help_text=_("Recommended size: 1920x450 pixels (WxH)"))
    title = models.CharField(max_length=200, blank=True, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=200, blank=True, verbose_name=_("Subtitle"))
    button_text = models.CharField(max_length=50, blank=True, verbose_name=_("Button Text"))
    link = models.URLField(blank=True, verbose_name=_("Link"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("Hero Slide")
        verbose_name_plural = _("Hero Slides")
        ordering = ['sort_order']

    def __str__(self):
        return self.title or f"Slide #{self.id}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name=_("User"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name=_("Product"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added At"))

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlist")
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class SalesDashboard(models.Model):
    class Meta:
        managed = False
        verbose_name = _('銷售報表')
        verbose_name_plural = _('銷售報表')
