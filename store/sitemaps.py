
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Page

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
        
    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])

class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Page.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
        
    def location(self, obj):
        return reverse('page_detail', args=[obj.slug])

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['product_list', 'shop', 'contact', 'press', 'gallery']

    def location(self, item):
        return reverse(item)
