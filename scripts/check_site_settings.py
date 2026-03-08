import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gwz.settings")
django.setup()

from store.models import SiteSettings

def check_settings():
    with open('site_settings_check.txt', 'w', encoding='utf-8') as f:
        try:
            settings = SiteSettings.objects.first()
            if settings:
                f.write(f"Site Name: {settings.site_name}\n")
                f.write(f"Founder Name: {settings.founder_name}\n")
                f.write(f"Founder Image: {settings.founder_image}\n")
                if settings.founder_image:
                    f.write(f"Founder Image URL: {settings.founder_image.url}\n")
                else:
                    f.write("Founder Image is NOT set.\n")
            else:
                f.write("No SiteSettings found.\n")
        except Exception as e:
            f.write(f"Error checking settings: {e}\n")

if __name__ == "__main__":
    check_settings()
