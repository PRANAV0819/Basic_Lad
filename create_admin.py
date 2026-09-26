# create_admin.py
#
# WHAT: Standalone utility script to manually create or update an Admin account in MySQL.
#
# WHY:  There is no public Admin Signup page.
#       Initial admin credentials must be created manually using our custom algorithm.
#
# FLOW:
#   create_admin.py
#         ↓
#   Enter username
#         ↓
#   Enter password
#         ↓
#   generate_salt() -> 64-character random hexadecimal salt
#         ↓
#   hash_password(password, salt) -> 64-character custom hash
#         ↓
#   Save username, salt, password_hash in MySQL (or update if already exists)
#         ↓
#   Display confirmation (without printing the raw hash)

import os
import sys
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from adminpanel.models import Admin
from adminpanel.logic.password import generate_salt, hash_password


def create_or_update_admin(username: str, raw_password: str):
    username = username.strip()
    raw_password = raw_password.strip()

    if not username or not raw_password:
        print("[ERROR] Username and password cannot be empty.")
        return

    # Step 1: Generate 64-character random hexadecimal salt
    salt = generate_salt()

    # Step 2: Generate 64-character hash using our custom teaching algorithm
    password_hash = hash_password(raw_password, salt)

    # Step 3: Save to MySQL (creates new, or updates if username already exists)
    admin_obj, created = Admin.objects.update_or_create(
        username=username,
        defaults={
            'salt': salt,
            'password_hash': password_hash,
        }
    )

    action_text = "created" if created else "updated"

    # Step 4: Simple, secure confirmation without revealing the hash
    print()
    print(f"Admin {action_text} successfully.")
    print(f"Username: {admin_obj.username}")
    print("Password: securely stored.")


if __name__ == '__main__':
    print("=== Placement Readiness Platform - Admin Creator ===")
    if len(sys.argv) == 3:
        u = sys.argv[1]
        p = sys.argv[2]
    else:
        u = input("Enter admin username (default 'admin'): ").strip() or "admin"
        p = input("Enter admin password (default 'admin123'): ").strip() or "admin123"

    create_or_update_admin(u, p)
