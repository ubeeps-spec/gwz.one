from django import template
from django.conf import settings
import os

register = template.Library()

@register.inclusion_tag('store/gallery_grid.html')
def render_gallery(category):
    """
    Scans MEDIA_ROOT/gallery for images matching {category}-*.jpg
    Excludes *-hero.jpg
    Sorts numerically by suffix.
    """
    gallery_dir = os.path.join(settings.MEDIA_ROOT, 'gallery')
    images = []
    
    if os.path.exists(gallery_dir):
        files = os.listdir(gallery_dir)
        prefix = f"{category}-"
        
        for f in files:
            lf = f.lower()
            if lf.startswith(prefix) and lf.endswith(('.jpg', '.jpeg')):
                # Skip hero images
                if 'hero' in lf:
                    continue
                
                # Check if suffix is a number (e.g. travel-01.jpg -> 01)
                base = os.path.splitext(lf)[0]
                tail = base[len(prefix):]
                
                if tail.isdigit():
                    images.append(f)
    
    # Sort numerically
    def get_sort_key(filename):
        try:
            base = os.path.splitext(filename)[0]
            # Assuming format category-number
            parts = base.split('-')
            if parts[-1].isdigit():
                return int(parts[-1])
            return 999
        except:
            return 999

    images.sort(key=get_sort_key)
            
    return {
        'images': images, 
        'category': category, 
        'MEDIA_URL': settings.MEDIA_URL
    }
