from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import Product, ProductImage, Order, OrderItem, SiteSettings, Page, Coupon, OrderNote, Category, Customer, PaymentMethod, SalesDashboard, HeroSlide, UserProfile
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from django.template.response import TemplateResponse
from django.utils import timezone
import json
from datetime import timedelta, datetime
import uuid
from django import forms
from django.forms import CheckboxSelectMultiple
from django.db import models
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from openpyxl import Workbook
from django.urls import path
from django.shortcuts import redirect
from django.core.files import File
import zipfile
import tempfile
import os
import re

class RecaptchaAdminLoginForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

admin.site.login_form = RecaptchaAdminLoginForm

from django.utils.translation import gettext_lazy as _

@admin.action(description=_('複製所選商品'))
def duplicate_product(modeladmin, request, queryset):
    for product in queryset:
        # Capture categories before resetting pk
        categories = list(product.categories.all())
        
        product.pk = None  # Reset primary key to create a new instance
        product.slug = f"{product.slug}-copy" # Update slug to be unique
        product.sku = f"{product.sku}-copy" # Update sku to be unique
        if Product.objects.filter(slug=product.slug).exists():
             import uuid
             product.slug = f"{product.slug}-{uuid.uuid4().hex[:4]}"
        if Product.objects.filter(sku=product.sku).exists():
             import uuid
             product.sku = f"{product.sku}-{uuid.uuid4().hex[:4]}"
             
        product.save()
        
        # Restore categories for the new instance
        product.categories.set(categories)
duplicate_product.short_description = _("複製所選商品")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# @admin.register(Page)
# class PageAdmin(TranslationAdmin):
#     list_display = ('title', 'slug', 'is_active', 'updated_at')
#     prepopulated_fields = {'slug': ('title',)}
#     fieldsets = (
#         (_('Basic Information'), {
#             'fields': ('title', 'slug', 'content', 'is_active')
#         }),
#         (_('About Us Page Settings'), {
#             'fields': ('feature_title', 'feature_subtitle', 'feature_image', 'founder_image', 'founder_name', 'founder_intro_title', 'founder_intro_text'),
#             'description': _('These settings only apply to the About Us page.')
#         }),
#     )

@admin.register(HeroSlide)
class HeroSlideAdmin(TranslationAdmin):
    list_display = ('title', 'image', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order',)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('基本設定'), {
            'fields': ('site_name', 'logo')
        }),
        (_('聯絡頁面設定'), {
            'fields': ('contact_phone', 'contact_email', 'contact_address', 'contact_opening_hours')
        }),
        (_('社群媒體'), {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'whatsapp_url')
        }),
        (_('郵件設定 (SMTP)'), {
            'fields': ('smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_use_tls', 'smtp_from_email'),
            'description': _('設定 SMTP 伺服器以發送系統郵件（如重設密碼）。')
        }),
    )

    def has_add_permission(self, request):
        # Disable add button if an instance already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.action(description=_('下載匯入範本'))
def download_template(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Product Template"
    
    # Headers
    headers = ['id', 'name', 'sku', 'price', 'discount_price', 'stock', 'categories', 'description', 'specs', 'image_url', 'image_urls', 'is_active']
    ws.append(headers)
    
    # Sample Row
    ws.append(['', 'Sample Product', 'SKU-SAMPLE-01', 100, 80, 50, 'HP,Canon', '<p>Description...</p>', '<p>Specs...</p>', '', 'https://example.com/img1.jpg,https://example.com/img2.jpg', True])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=product_import_template.xlsx'
    wb.save(response)
    return response

class CleanManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            # Handle spaces after commas
            value = ",".join([v.strip() for v in value.split(self.separator) if v.strip()])
        return super().clean(value, row, *args, **kwargs)

class ProductResource(resources.ModelResource):
    name = fields.Field(attribute='name', column_name=_('商品名稱'))
    slug = fields.Field(attribute='slug', column_name=_('網址代稱'))
    sku = fields.Field(attribute='sku', column_name=_('商品編號 (SKU)'))
    price = fields.Field(attribute='price', column_name=_('價格'))
    discount_price = fields.Field(attribute='discount_price', column_name=_('特價'))
    stock = fields.Field(attribute='stock', column_name=_('庫存'))
    categories = fields.Field(
        column_name=_('分類'),
        attribute='categories',
        widget=CleanManyToManyWidget(Category, field='name', separator=',')
    )
    description = fields.Field(attribute='description', column_name=_('描述'))
    specs = fields.Field(attribute='specs', column_name=_('規格'))
    image_url = fields.Field(attribute='image_url', column_name=_('圖片網址'))
    image_urls = fields.Field(column_name=_('所有圖片網址'), attribute='image_urls')
    is_active = fields.Field(attribute='is_active', column_name=_('是否上架'))

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'sku', 'price', 'discount_price', 'stock', 'categories', 'description', 'specs', 'image_url', 'image_urls', 'is_active')
        export_order = ('id', 'name', 'sku', 'categories', 'price', 'discount_price', 'stock', 'is_active', 'image_url', 'image_urls', 'description', 'specs', 'slug')
        import_id_fields = ('id',)
        # We disable skip_unchanged to ensure our custom image processing logic
        # in after_save_instance ALWAYS runs, even if the main fields haven't changed.
        skip_unchanged = False
        report_skipped = True
    
    def dehydrate_image_urls(self, obj):
        urls = []
        if obj.image_url:
            urls.append(obj.image_url)
        for pi in obj.images.all():
            if pi.image_url:
                urls.append(pi.image_url)
            elif pi.image:
                try:
                    urls.append(pi.image.url)
                except Exception:
                    pass
        return ",".join(urls)
    
    def before_import_row(self, row, **kwargs):
        print(f"DEBUG: before_import_row called. keys: {list(row.keys())}", flush=True)
        
        # Support English/Alternate Headers mapping to Chinese (Canonical)
        # Map common English/Chinese headers to the Chinese column_name defined in fields
        header_map = {
            # Canonical: '商品名稱'
            'name': '商品名稱', 'product name': '商品名稱', '名稱': '商品名稱', '品名': '商品名稱',
            # Canonical: '商品編號 (SKU)'
            'sku': '商品編號 (SKU)', '貨號': '商品編號 (SKU)',
            # Canonical: '價格'
            'price': '價格', '售價': '價格',
            # Canonical: '特價'
            'discount_price': '特價', '優惠價': '特價', 'discount': '特價',
            # Canonical: '庫存'
            'stock': '庫存', '數量': '庫存', 'quantity': '庫存',
            # Canonical: '分類'
            'categories': '分類', 'category': '分類', '類別': '分類',
            # Canonical: '描述'
            'description': '描述', '商品描述': '描述',
            # Canonical: '規格'
            'specs': '規格', 'specifications': '規格', '商品規格': '規格',
            # Canonical: '是否上架'
            'is_active': '是否上架', 'active': '是否上架', '上架': '是否上架',
            # Canonical: '圖片網址'
            'image_url': '圖片網址', 'image': '圖片網址',
            # Canonical: '所有圖片網址'
            'image_urls': '所有圖片網址', 'images': '所有圖片網址',
            # Canonical: '網址代稱'
            'slug': '網址代稱',
        }
        
        # Normalize input keys to Canonical Chinese Keys
        for key in list(row.keys()):
            key_lower = key.strip().lower()
            if key_lower in header_map:
                canonical = header_map[key_lower]
                if canonical not in row:
                    row[canonical] = row[key]

        super().before_import_row(row, **kwargs)
        
        # Ensure non-nullable text fields are empty strings if missing or None
        # Use Canonical Chinese Keys
        if row.get('描述') is None:
            row['描述'] = ''
        if row.get('規格') is None:
            row['規格'] = ''
        if row.get('圖片網址') is None:
            row['圖片網址'] = ''
            
        # Handle "No SKU" case by auto-generating one
        sku_val = row.get('商品編號 (SKU)')
        if not sku_val or str(sku_val).strip() == '':
            import uuid
            # Try to use a sanitized name slug first, else random
            name_val = row.get('商品名稱')
            if name_val:
                from django.utils.text import slugify
                # slugify might return empty for pure Chinese, so we need a fallback
                # But here we just want a prefix.
                base = str(name_val)[:10]
                # If slugify works (e.g. alphanumeric), use it, otherwise use raw hex or something
                # Actually, slugify removes non-ascii by default in Django unless allow_unicode=True
                # Let's just use a random prefix if slugify fails or just "PROD"
                # Simpler:
                base = "PROD"
                # Add random suffix to ensure uniqueness
                row['商品編號 (SKU)'] = f"{base}-{uuid.uuid4().hex[:8].upper()}"
            else:
                row['商品編號 (SKU)'] = f"SKU-{uuid.uuid4().hex[:8].upper()}"

        # Validate Name and Price (Critical fields)
        name_val = row.get('商品名稱')
        if not name_val or str(name_val).strip() == '':
            raise ValueError(_("資料錯誤：商品名稱為必填，請檢查 Excel 內容。"))

        price_val = row.get('價格')
        if price_val is None or str(price_val).strip() == '':
             raise ValueError(_("資料錯誤：價格為必填，請檢查 Excel 內容。"))

    def before_save_instance(self, instance, row, **kwargs):
        # Check if SKU already exists in another product to prevent IntegrityError crash
        if instance.sku:
            qs = Product.objects.filter(sku=instance.sku)
            if instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                # This will be caught by import-export and shown as a row error
                raise Exception(_("錯誤：SKU '%(sku)s' 已存在於其他商品中，請確保 SKU 唯一。") % {'sku': instance.sku})
        
        super().before_save_instance(instance, row, **kwargs)

    def import_instance(self, instance, row, **kwargs):
        super().import_instance(instance, row, **kwargs)
        
        # Robustly find image URLs from various possible column names
        raw_list = []
        # Check standard fields first
        if row.get('image_urls'):
            raw_list.append(str(row.get('image_urls')))
        
        # Also scan for other likely column names (case-insensitive)
        for key in row.keys():
            k_lower = key.strip().lower()
            # Added Chinese column names support and 'image_urls' (to handle potential trailing spaces in header)
            if k_lower in ['image_urls', 'image_url', 'image url', 'images', 'photo', 'photos', 'pic', 'pics', '圖片', '圖片連結', '照片', '連結']:
                # Avoid adding if it's already caught by the standard 'image_urls' check above
                if key != 'image_urls' and row[key]:
                    raw_list.append(str(row[key]))

        # Join everything found and split by comma to get individual URLs
        full_raw = ",".join(raw_list)
        # Handle full-width comma (common in Chinese input) and other separators
        full_raw = full_raw.replace('，', ',').replace('、', ',')
        
        # Clean URLs: remove whitespace, backticks, and single quotes
        # We also handle non-breaking spaces (\xa0) and ideographic spaces (\u3000) by standard strip()
        all_urls = [u.strip().replace('`', '').replace("'", "") for u in full_raw.split(',') if u and u.strip()]
        
        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for u in all_urls:
            if u not in seen:
                unique_urls.append(u)
                seen.add(u)
        
        instance._import_image_urls = unique_urls
        # Set this attribute so it appears in the import preview
        instance.image_urls = ",".join(unique_urls)
        print(f"DEBUG: Extracted URLs: {unique_urls}")

        # Safety: If obj.image_url (singular) contains commas, it might fail validation.
        # So we clean it up to be just the first URL or empty.
        if instance.image_url and ',' in instance.image_url:
            instance.image_url = instance.image_url.split(',')[0].strip()

        # Double check to ensure fields are not None (in case they were not in row)
        if getattr(instance, 'description', None) is None:
            instance.description = ''
        if getattr(instance, 'specs', None) is None:
            instance.specs = ''
        if getattr(instance, 'image_url', None) is None:
            instance.image_url = ''

    def after_save_instance(self, instance, row, **kwargs):
        super().after_save_instance(instance, row, **kwargs)
        # Note: We do NOT skip dry_run here because we want the preview to show the changes.
        # The transaction rollback mechanism in django-import-export will handle the cleanup.
        
        urls = getattr(instance, '_import_image_urls', [])
        print(f"DEBUG: after_save_instance for {instance.sku}. urls: {urls}")
        
        if urls:
            instance.images.all().delete()
            for idx, u in enumerate(urls):
                ProductImage.objects.create(product=instance, image_url=u, sort_order=idx)
            
            # Repopulate image_urls attribute for the preview display
            instance.image_urls = ",".join(urls)
            
            # Auto-set the main image_url if it's empty but we have imported URLs
            # This ensures the main product has a default image without needing extra queries
            if not instance.image_url and urls:
                print(f"DEBUG: Setting main image_url to {urls[0]}")
                instance.image_url = urls[0]
                instance.save(update_fields=['image_url'])

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    change_list_template = 'admin/store/product/custom_product_list.html'
    change_form_template = 'admin/store/product/change_form.html'
    list_per_page = 20

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context)
    resource_class = ProductResource
    list_display = ('product_thumbnail', 'name', 'sku', 'stock_status', 'price', 'discount_price', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured', 'categories')
    list_editable = ('is_active', 'is_featured')
    search_fields = ('name', 'sku', 'categories__name')
    prepopulated_fields = {'slug': ('name',)}
    actions = [duplicate_product, download_template]
    list_display_links = ('name', 'product_thumbnail')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    
    fieldsets = (
        (_('商品資料'), {
            'fields': ('name', 'slug', 'sku', 'description', 'specs', 'is_active', 'is_featured')
        }),
        (_('價格與庫存'), {
            'fields': ('price', 'discount_price', 'stock')
        }),
        (_('分類與標籤'), {
            'fields': ('categories',)
        }),
        (_('主圖設定 (Main Image)'), {
            'fields': ('image', 'image_url'),
            'description': _('上傳圖片或輸入圖片網址（二擇一）。若兩者皆提供，將優先顯示上傳的圖片。')
        }),
    )
    
    class ProductImageInline(admin.TabularInline):
        model = ProductImage
        extra = 1
        verbose_name = "更多圖片 (Additional Images)"
        verbose_name_plural = "更多圖片 (Additional Images)"
        fields = ('image', 'image_url', 'caption', 'sort_order', 'preview')
        readonly_fields = ('preview',)
        
        def preview(self, obj):
            from django.utils.html import format_html
            if obj.image:
                return format_html('<img src="{}" style="max-height:120px;"/>', obj.image.url)
            elif obj.image_url:
                return format_html('<img src="{}" style="max-height:120px;"/>', obj.image_url)
            return "-"
        preview.short_description = _('預覽')
    
    inlines = [ProductImageInline]
    
    def shipping_address_display(self, obj):
        return obj.address
    shipping_address_display.short_description = _("運送地址")

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('upload-images/', self.admin_site.admin_view(self.upload_images_view), name='store_product_upload_images'),
        ]
        return custom + urls
    
    def upload_images_view(self, request):
        context = {**self.admin_site.each_context(request), 'opts': self.model._meta, 'title': _('批次上傳商品圖片 (ZIP)')}
        if request.method == 'POST' and request.FILES.get('zip_file'):
            zf = request.FILES['zip_file']
            tmpdir = tempfile.mkdtemp()
            tmpzip = os.path.join(tmpdir, 'upload.zip')
            with open(tmpzip, 'wb') as f:
                for chunk in zf.chunks():
                    f.write(chunk)
            with zipfile.ZipFile(tmpzip) as z:
                z.extractall(tmpdir)
            created = 0
            updated_products = set()
            for root, _, files in os.walk(tmpdir):
                for fname in files:
                    ext = os.path.splitext(fname)[1].lower()
                    if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        continue
                    full = os.path.join(root, fname)
                    base = os.path.splitext(fname)[0]
                    candidate = re.split(r'[_\-\s]', base)[0]
                    dir_candidate = os.path.basename(root)
                    sku = candidate or dir_candidate
                    try:
                        product = Product.objects.get(sku__iexact=sku)
                    except Product.DoesNotExist:
                        continue
                    sort_order = product.images.count()
                    with open(full, 'rb') as f:
                        django_file = File(f)
                        pi = ProductImage(product=product, sort_order=sort_order)
                        pi.image.save(fname, django_file, save=True)
                        created += 1
                        updated_products.add(product.pk)
                    if not product.image:
                        try:
                            product.image = pi.image
                            product.save()
                        except Exception:
                            pass
            context['result'] = {'created': created, 'updated_products': len(updated_products)}
            from django.contrib import messages
            messages.success(request, _('已建立 %(created)d 張圖片，更新了 %(updated)d 個商品') % {'created': created, 'updated': len(updated_products)})
            return redirect('admin:store_product_changelist')
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'admin/store/product/upload_images.html', context)

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = _('分類')

    def product_thumbnail(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        elif obj.image_url:
             return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image_url)
        # Fallback to the first related image if main image is not set
        elif obj.images.exists():
            first_img = obj.images.first()
            if first_img.image_url:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', first_img.image_url)
            elif first_img.image:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', first_img.image.url)
        return "-"
    product_thumbnail.short_description = _('圖片')

    def stock_status(self, obj):
        from django.utils.html import format_html
        if obj.stock > 0:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', obj.stock)
        return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.stock)
    stock_status.short_description = _('庫存')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    verbose_name = _("訂單項目")
    verbose_name_plural = _("訂單項目")


class OrderNoteInline(admin.StackedInline):
    model = OrderNote
    extra = 1
    verbose_name = _("訂單備註")
    verbose_name_plural = _("訂單備註")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_display', 'valid_from', 'valid_to', 'active')
    list_filter = ('active', 'discount_type', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'active')
        }),
        (_('折扣設定'), {
            'fields': ('discount_type', 'discount')
        }),
        (_('有效期限'), {
            'fields': ('valid_from', 'valid_to')
        }),
    )

    def discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount}%"
        return f"HK${obj.discount}"
    discount_display.short_description = _("折扣")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'requires_proof', 'is_active')
    list_filter = ('is_active', 'requires_proof')
    search_fields = ('name', 'code')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'instructions', 'requires_proof', 'is_active')
        }),
    )


class OrderResource(resources.ModelResource):
    items_summary = fields.Field(column_name=_('訂單項目'))
    payment_method_display = fields.Field(column_name=_('付款方式'))
    status_display = fields.Field(column_name=_('訂單狀態'))
    created_at_display = fields.Field(column_name=_('訂單日期'))

    class Meta:
        model = Order
        fields = ('order_number', 'created_at_display', 'status_display', 'total_amount', 'customer_name', 'email', 'phone', 'address', 'payment_method_display', 'items_summary')
        export_order = ('order_number', 'created_at_display', 'status_display', 'total_amount', 'items_summary', 'customer_name', 'email', 'phone', 'address', 'payment_method_display')
        import_id_fields = ('order_number',)

    def dehydrate_items_summary(self, order):
        return "; ".join([f"{item.product.name} x{item.quantity}" for item in order.items.all()])

    def dehydrate_payment_method_display(self, order):
        return order.payment_method.name if order.payment_method else ''

    def dehydrate_status_display(self, order):
        return order.get_status_display()

    def dehydrate_created_at_display(self, order):
        return timezone.localtime(order.created_at).strftime('%Y-%m-%d %H:%M')

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    list_per_page = 20
    resource_class = OrderResource
    change_form_template = 'admin/store/order/change_form.html'
    list_display = ('order_number', 'customer_name', 'status', 'total_amount', 'created_at', 'invoice_link')
    list_filter = ('status', 'payment_method')
    search_fields = ('order_number', 'customer_name', 'email', 'phone')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'invoice_view_link', 'total_amount', 'discount_amount', 'payment_proof_preview', 'ip_address', 'shipping_address_display', 'created_at')

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('user_link',)
        return self.readonly_fields

    def user_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if obj.user:
            # Check if user is staff (backend user) or customer
            if obj.user.is_staff:
                try:
                    url = reverse('admin:auth_user_change', args=[obj.user.id])
                    return format_html('<a href="{}">{} (Staff)</a>', url, obj.user.username)
                except:
                    return obj.user.username
            else:
                # Use Customer admin for customers
                try:
                    url = reverse('admin:store_customer_change', args=[obj.user.id])
                    return format_html('<a href="{}">{}</a>', url, obj.user.username)
                except:
                    return obj.user.username
        return "-"
    user_link.short_description = _("User Account")

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.fieldsets
        
        new_fieldsets = []
        for name, opts in self.fieldsets:
            new_opts = opts.copy()
            fields = list(new_opts['fields'])
            if 'user' in fields:
                fields[fields.index('user')] = 'user_link'
            new_opts['fields'] = tuple(fields)
            new_fieldsets.append((name, new_opts))
        return tuple(new_fieldsets)

    fieldsets = (
        (_('一般資訊'), {
            'classes': ('box-general',),
            'fields': ('created_at', 'status', 'user', 'ip_address')
        }),
        (_('帳單資訊'), {
            'classes': ('box-billing',),
            'fields': ('customer_name', 'address', 'email', 'phone', 'payment_method', 'payment_proof', 'payment_proof_preview')
        }),
        (_('運送資訊'), {
            'classes': ('box-shipping',),
            'fields': ('shipping_address_display',)
        }),
    )
    
    def shipping_address_display(self, obj):
        return obj.address
    shipping_address_display.short_description = _("運送地址")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/add-note/', self.admin_site.admin_view(self.add_note_view), name='store_order_add_note'),
            path('<int:note_id>/delete-note/', self.admin_site.admin_view(self.delete_note_view), name='store_order_delete_note'),
            path('get-user-details/<int:user_id>/', self.admin_site.admin_view(self.get_user_details_view), name='store_order_get_user_details'),
            path('get-product-details/<int:product_id>/', self.admin_site.admin_view(self.get_product_details_view), name='store_order_get_product_details'),
        ]
        return custom_urls + urls

    def get_product_details_view(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            # Ensure Decimals are converted to strings or floats for JSON serialization
            data = {
                'price': str(product.price),
                'discount_price': str(product.discount_price) if product.discount_price else None,
                'effective_price': str(product.effective_price()),
            }
            return JsonResponse(data)
        except Product.DoesNotExist:
             return JsonResponse({'error': 'Product not found'}, status=404)

    def get_user_details_view(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            # Try to get profile data if exists
            if hasattr(user, 'profile'):
                data['phone'] = user.profile.phone
                data['address'] = user.profile.address
            else:
                 data['phone'] = ''
                 data['address'] = ''
            return JsonResponse(data)
        except User.DoesNotExist:
             return JsonResponse({'error': 'User not found'}, status=404)

    def add_note_view(self, request, order_id):
        if request.method == 'POST':
            order = Order.objects.get(pk=order_id)
            message = request.POST.get('note_content')
            is_customer_note = request.POST.get('is_customer_note') == 'on'
            if message:
                OrderNote.objects.create(
                    order=order,
                    user=request.user,
                    message=message,
                    is_customer_note=is_customer_note
                )
                
                if is_customer_note and order.email:
                    subject = f"{_('訂單備註通知')} - {order.order_number}"
                    email_message = f"""
{_('親愛的')} {order.customer_name},

{_('您的訂單')} {order.order_number} {_('有新的備註：')}

{message}

{_('謝謝！')}
"""
                    try:
                        send_mail(
                            subject,
                            email_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [order.email],
                            fail_silently=True
                        )
                        from django.contrib import messages
                        messages.success(request, _('已新增備註並發送郵件給客戶'))
                    except Exception as e:
                        from django.contrib import messages
                        messages.warning(request, _('已新增備註但發送郵件失敗：%(error)s') % {'error': e})
                else:
                    from django.contrib import messages
                    messages.success(request, _('已新增備註'))
            return redirect('admin:store_order_change', order_id)
        return redirect('admin:store_order_change', order_id)

    def delete_note_view(self, request, note_id):
        note = OrderNote.objects.get(pk=note_id)
        order_id = note.order.id
        note.delete()
        from django.contrib import messages
        messages.success(request, _('備註已刪除'))
        return redirect('admin:store_order_change', order_id)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            order = Order.objects.get(pk=object_id)
            extra_context['order_notes'] = order.order_notes.all().order_by('-created_at')
            
            # Customer Statistics
            from django.db.models import Sum, Avg
            
            base_qs = None
            if order.user:
                base_qs = Order.objects.filter(user=order.user)
            elif order.email:
                base_qs = Order.objects.filter(email=order.email)
            
            if base_qs is not None:
                # Valid statuses for financial calculations
                valid_statuses = ['paid', 'fulfilling', 'partially_shipped', 'shipped', 'completed']
                
                total_orders = base_qs.count()
                spend_qs = base_qs.filter(status__in=valid_statuses)
                total_spend = spend_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                aov = spend_qs.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
                
                extra_context['customer_stats'] = {
                    'total_orders': total_orders,
                    'total_spend': total_spend,
                    'aov': aov,
                }
                
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def payment_proof_preview(self, obj):
        from django.utils.html import format_html
        if obj.payment_proof:
             return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height: 200px; max-width: 300px;" /></a>', obj.payment_proof.url, obj.payment_proof.url)
        return _("未上傳")
    payment_proof_preview.short_description = _("付款證明預覽")

    def invoice_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('invoice_view', args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">{}</a>', url, _("查看發票"))
    invoice_link.short_description = _('發票')

    def invoice_view_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        url = reverse('invoice_view', args=[obj.id])
        return format_html('<a href="{}" target="_blank" style="font-size:16px; font-weight:bold;">{}</a>', url, _("開啟發票"))
    invoice_view_link.short_description = _('列印發票')


class OrderInline(admin.TabularInline):
    model = Order
    fk_name = 'user'
    extra = 0
    readonly_fields = ('order_number', 'created_at', 'status', 'total_amount', 'get_payment_method_name')
    fields = ('order_number', 'created_at', 'status', 'total_amount', 'get_payment_method_name')
    can_delete = False
    show_change_link = True
    ordering = ('-created_at',)
    verbose_name = _("訂單紀錄")
    verbose_name_plural = _("訂單紀錄")
    
    def has_add_permission(self, request, obj):
        return False

    def get_payment_method_name(self, obj):
        return obj.payment_method.name if obj.payment_method else "-"
    get_payment_method_name.short_description = _('付款方式')

class CustomerChangeForm(UserChangeForm):
    phone = forms.CharField(label=_('電話'), required=False, max_length=30)
    address = forms.CharField(label=_('地址'), required=False, max_length=255)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['phone'].initial = profile.phone
                self.fields['address'].initial = profile.address
            except UserProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.save()
        return user

class CustomerResource(resources.ModelResource):
    username = fields.Field(attribute='username', column_name=_('使用者名稱'))
    email = fields.Field(attribute='email', column_name=_('電子郵件'))
    first_name = fields.Field(attribute='first_name', column_name=_('名字'))
    last_name = fields.Field(attribute='last_name', column_name=_('姓氏'))
    is_active = fields.Field(attribute='is_active', column_name=_('啟用狀態'))
    date_joined = fields.Field(attribute='date_joined', column_name=_('加入日期'))
    last_login = fields.Field(attribute='last_login', column_name=_('最後登入'))
    phone = fields.Field(column_name=_('電話'))
    address = fields.Field(column_name=_('地址'))
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'phone', 'address')
        export_order = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'is_active', 'date_joined', 'last_login')
        import_id_fields = ('username',)
        skip_unchanged = True
        report_skipped = False

    def dehydrate_phone(self, user):
        return user.profile.phone if hasattr(user, 'profile') else ''

    def dehydrate_address(self, user):
        return user.profile.address if hasattr(user, 'profile') else ''

    def after_save_instance(self, instance, row, **kwargs):
        if not kwargs.get('dry_run'):
            # Ensure UserProfile exists
            profile, created = UserProfile.objects.get_or_create(user=instance)
            # Update profile fields from row data
            # Use Chinese keys matching column_name
            profile.phone = row.get('電話', '')
            profile.address = row.get('地址', '')
            profile.save()
            
    def before_import_row(self, row, **kwargs):
        # Canonical Chinese Mapping
        header_map = {
            'username': '使用者名稱',
            'email': '電子郵件',
            'first_name': '名字', 'first name': '名字',
            'last_name': '姓氏', 'last name': '姓氏',
            'phone': '電話',
            'address': '地址',
            'is_active': '啟用狀態', 'active': '啟用狀態',
            'date_joined': '加入日期',
            'last_login': '最後登入',
        }
        
        for key in list(row.keys()):
            key_lower = key.strip().lower()
            if key_lower in header_map:
                canonical = header_map[key_lower]
                if canonical not in row:
                    row[canonical] = row[key]

        # Handle password if needed, or set default
        if 'password' not in row:
             # If no password provided, we might want to set an unusable one or default
             pass

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin, UserAdmin):
    list_per_page = 20
    resource_class = CustomerResource
    form = CustomerChangeForm
    list_display = ('username', 'email', 'order_count', 'total_spend', 'average_order_value', 'last_login', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'date_joined')
    inlines = [OrderInline]
    
    fieldsets = (
        (_('基本資料'), {'fields': ('username', 'password_info', 'last_name', 'first_name', 'email', 'phone', 'address', 'is_active')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    
    readonly_fields = ('password_info', 'last_login', 'date_joined')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show non-staff users (customers)
        return qs.filter(is_staff=False, is_superuser=False)

    def password_info(self, obj):
        from django.utils.html import format_html
        return format_html(
            '******** <a href="../password/" class="button" style="margin-left: 10px;">{}</a>',
            _("重設密碼")
        )
    password_info.short_description = _('密碼')

    def order_count(self, obj):
        return Order.objects.filter(user=obj).count()
    order_count.short_description = _('訂單數量')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Manually save UserProfile fields because ModelAdmin calls form.save(commit=False)
        try:
            profile, created = UserProfile.objects.get_or_create(user=obj)
            profile.phone = form.cleaned_data.get('phone', '')
            profile.address = form.cleaned_data.get('address', '')
            profile.save()
        except Exception as e:
            print(f"Error saving profile: {e}")

    def total_spend(self, obj):
        from django.db.models import Sum
        # Updated statuses to match Order.STATUS_CHOICES keys
        valid_statuses = ['paid', 'fulfilling', 'partially_shipped', 'shipped', 'completed']
        total = Order.objects.filter(user=obj, status__in=valid_statuses).aggregate(Sum('total_amount'))['total_amount__sum']
        return f"HK${total:.2f}" if total else "HK$0.00"
    total_spend.short_description = _('總消費金額')

    def average_order_value(self, obj):
        from django.db.models import Avg
        valid_statuses = ['paid', 'fulfilling', 'partially_shipped', 'shipped', 'completed']
        avg = Order.objects.filter(user=obj, status__in=valid_statuses).aggregate(Avg('total_amount'))['total_amount__avg']
        return f"HK${avg:.2f}" if avg else "HK$0.00"
    average_order_value.short_description = _('平均客單價 (AOV)')

@admin.register(SalesDashboard)
class SalesDashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/store/salesdashboard/change_list.html'
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Date Range Filtering
        period = request.GET.get('period', '30days')
        today = timezone.now().date()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == '7days':
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'last_month':
            last_month_end = today.replace(day=1) - timedelta(days=1)
            start_date = last_month_end.replace(day=1)
            end_date = last_month_end
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == 'custom':
            s_date = request.GET.get('start_date')
            e_date = request.GET.get('end_date')
            try:
                if s_date:
                    start_date = datetime.strptime(s_date, '%Y-%m-%d').date()
                else:
                    start_date = today - timedelta(days=30)
                
                if e_date:
                    end_date = datetime.strptime(e_date, '%Y-%m-%d').date()
                else:
                    end_date = today
            except ValueError:
                start_date = today - timedelta(days=30)
                end_date = today
        else: # Default 30 days
            start_date = today - timedelta(days=30)
            end_date = today

        # Convert to datetime for filtering
        start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
        end_dt = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
        
        # Base Query: Paid or Completed Orders
        valid_statuses = ['paid', 'fulfilling', 'partially_shipped', 'shipped', 'completed']
        orders = Order.objects.filter(status__in=valid_statuses, created_at__range=(start_dt, end_dt))

        # Product Filter
        product_id = request.GET.get('product_id')
        products = Product.objects.all().values('id', 'name')
        selected_product_name = "所有商品"

        if product_id:
            try:
                selected_product = Product.objects.get(id=product_id)
                selected_product_name = selected_product.name
                
                # Filter OrderItems for this product within the date range and valid orders
                order_items = OrderItem.objects.filter(
                    order__in=orders,
                    product_id=product_id
                )
                
                # 1. Total Sales (Revenue from this product)
                total_sales = order_items.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
                
                # 2. Total Orders (containing this product)
                total_orders = order_items.values('order').distinct().count()
                
                # 3. Average Order Value (Average spend on this product per order)
                avg_order_value = total_sales / total_orders if total_orders else 0
                
                # 4. Sales Trend (Daily for this product)
                sales_by_date = order_items.annotate(date=TruncDate('order__created_at'))\
                    .values('date')\
                    .annotate(daily_sales=Sum('subtotal'), daily_orders=Count('order', distinct=True))\
                    .order_by('date')
            except Product.DoesNotExist:
                product_id = None

        if not product_id:
            # 1. Total Sales
            total_sales = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            # 2. Total Orders
            total_orders = orders.count()
            
            # 3. Average Order Value
            avg_order_value = orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
            
            # 4. Sales Trend (Daily)
            sales_by_date = orders.annotate(date=TruncDate('created_at'))\
                .values('date')\
                .annotate(daily_sales=Sum('total_amount'), daily_orders=Count('id'))\
                .order_by('date')
            
        # Prepare Chart Data
        chart_labels = []
        chart_data = []
        daily_report = [] # For Table
        
        sales_dict = {item['date']: item for item in sales_by_date}
        
        current_date = start_date
        while current_date <= end_date:
            item = sales_dict.get(current_date, {'daily_sales': 0, 'daily_orders': 0})
            chart_labels.append(current_date.strftime('%Y-%m-%d'))
            chart_data.append(float(item['daily_sales'] or 0))
            
            daily_report.append({
                'date': current_date,
                'sales': item['daily_sales'] or 0,
                'orders': item['daily_orders'] or 0,
                'avg': (item['daily_sales'] or 0) / (item['daily_orders'] or 1) if item['daily_orders'] else 0
            })
            current_date += timedelta(days=1)
            
        # Reverse daily report for table display (newest first)
        daily_report.reverse()
            
        # 5. Top Selling Products
        top_products = OrderItem.objects.filter(order__in=orders)\
            .values('product__name', 'product__sku')\
            .annotate(total_qty=Sum('quantity'), total_revenue=Sum('subtotal'))\
            .order_by('-total_qty')[:10]

        # 6. Top Selling Categories
        top_categories = OrderItem.objects.filter(order__in=orders)\
            .values('product__categories__name')\
            .annotate(total_qty=Sum('quantity'), total_revenue=Sum('subtotal'))\
            .exclude(product__categories__name=None)\
            .order_by('-total_qty')[:10]

        # Export CSV
        if request.GET.get('export') == 'true':
            import csv
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.csv"'
            response.write('\ufeff') # BOM for Excel
            writer = csv.writer(response)
            
            # Summary
            writer.writerow([_('銷售報表'), f'{start_date} {_("至")} {end_date}'])
            writer.writerow([_('商品'), selected_product_name])
            writer.writerow([_('總銷售額'), f'HK${total_sales:.2f}'])
            writer.writerow([_('總訂單數'), total_orders])
            writer.writerow([_('平均客單價'), f'HK${avg_order_value:.2f}'])
            writer.writerow([])
            
            # Daily Report
            writer.writerow([_('日期'), _('銷售額'), _('訂單數'), _('平均客單價')])
            for item in daily_report:
                writer.writerow([
                    item['date'], 
                    f"{item['sales']:.2f}", 
                    item['orders'], 
                    f"{item['avg']:.2f}"
                ])
            
            return response

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': _('銷售報表'),
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'products': products,
            'selected_product_id': int(product_id) if product_id else '',
            'selected_product_name': selected_product_name,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'top_products': top_products,
            'top_categories': top_categories,
            'daily_report': daily_report,
        }
        
        return TemplateResponse(request, self.change_list_template, context)

# Unregister default User admin and register custom one to show only staff
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class StaffUserAdmin(UserAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('last_login', 'date_joined')
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show staff users (Backend Users)
        return qs.filter(is_staff=True)
    
    def save_model(self, request, obj, form, change):
        # Automatically set is_staff=True for users created in this admin
        if not change:
            obj.is_staff = True
        super().save_model(request, obj, form, change)

