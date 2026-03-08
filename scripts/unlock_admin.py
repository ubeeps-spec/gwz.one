import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gwz.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def unlock_admin():
    username = 'admin'
    password = 'admin123'
    email = 'admin@example.com'
    
    try:
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            print(f"Successfully reset password for user '{username}' to '{password}'")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Successfully created superuser '{username}' with password '{password}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    unlock_admin()
