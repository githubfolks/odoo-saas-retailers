import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_users():
    print("Seeding users for all tenants...")
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        if not tenants:
            print("No tenants found in database. Run seed_tenants logic first.")
            return

        for tenant in tenants:
            admin_email = f"admin@{tenant.tenant_id}.com"
            admin_password = "admin123"
            
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == admin_email).first()
            if not existing_user:
                print(f"Creating owner user for tenant {tenant.tenant_id}: {admin_email}")
                new_user = User(
                    email=admin_email,
                    hashed_password=pwd_context.hash(admin_password),
                    role=UserRole.OWNER,
                    tenant_id=tenant.tenant_id
                )
                db.add(new_user)
            else:
                # Update password if it's the default or doesn't match
                if not pwd_context.verify(admin_password, existing_user.hashed_password):
                    print(f"Updating password for existing user: {admin_email}")
                    existing_user.hashed_password = pwd_context.hash(admin_password)
                else:
                    print(f"User {admin_email} already exists with correct password")
        
        db.commit()
        print("✅ User seeding/sync completed!")

    except Exception as e:
        print(f"❌ Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
