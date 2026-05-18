from sqlalchemy import create_engine, text
from app.core.config import settings


def migrate():
    base_urls = [
        settings.postgres_url,
        settings.postgres_url.replace('@postgres:', '@localhost:')
    ]
    drivers = ['postgresql+psycopg2://', 'postgresql+psycopg://', 'postgresql://']
    engine = None

    for base_url in base_urls:
        for driver in drivers:
            try:
                url = base_url.replace('postgresql://', driver, 1)
                engine = create_engine(url, connect_args={'connect_timeout': 2})
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print(f"Connected via {driver}")
                break
            except Exception:
                continue
        if engine:
            break

    if not engine:
        print("Failed to connect to database")
        return

    with engine.connect() as conn:
        try:
            conn.execute(text(
                "ALTER TABLE tenants ADD COLUMN razorpay_webhook_secret VARCHAR"
            ))
            conn.commit()
            print("Added razorpay_webhook_secret to tenants table")
        except Exception as e:
            print(f"Column may already exist: {e}")


if __name__ == "__main__":
    migrate()
