
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gwz.settings")
django.setup()

from store.models import Product, Category

def check_data():
    with open('shop_data.txt', 'w', encoding='utf-8') as f:
        f.write("=== Checking Categories ===\n")
        categories = Category.objects.all()
        for cat in categories:
            f.write(f"ID: {cat.id}, Name: {cat.name}, Slug: {cat.slug}\n")
        
        f.write("\n=== Checking Products ===\n")
        products = Product.objects.all()
        if not products:
            f.write("NO PRODUCTS FOUND!\n")
        
        for p in products:
            f.write(f"ID: {p.id}, Name: {p.name}, Slug: {p.slug}, Active: {p.is_active}, Price: {p.price}\n")
            f.write(f"  Image: {p.image}\n")
            f.write(f"  Image URL: {p.image_url}\n")
            f.write(f"  Categories: {', '.join([c.name for c in p.categories.all()])}\n")
            f.write("-" * 30 + "\n")

if __name__ == "__main__":
    check_data()
