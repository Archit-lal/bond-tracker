from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import os

from backend.database.models import Base, Bond, Transaction, Exchange

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/bond_dashboard")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Sample bonds
    bonds = [
        Bond(
            isin="INE001A07BH4",
            name="7.26% GOI 2029",
            issuer="Government of India",
            exchange=Exchange.NSE,
            face_value=100.0,
            coupon_rate=7.26,
            maturity_date=datetime(2029, 2, 15),
            yield_to_maturity=7.15,
            last_price=99.85,
            volume=1000000
        ),
        Bond(
            isin="INE002A07BH5",
            name="6.54% GOI 2032",
            issuer="Government of India",
            exchange=Exchange.BSE,
            face_value=100.0,
            coupon_rate=6.54,
            maturity_date=datetime(2032, 5, 15),
            yield_to_maturity=6.45,
            last_price=100.25,
            volume=800000
        ),
        Bond(
            isin="INE003A07BH6",
            name="7.10% GOI 2033",
            issuer="Government of India",
            exchange=Exchange.NSDL,
            face_value=100.0,
            coupon_rate=7.10,
            maturity_date=datetime(2033, 8, 15),
            yield_to_maturity=7.05,
            last_price=99.95,
            volume=1200000
        )
    ]
    
    # Add bonds to database
    for bond in bonds:
        db.add(bond)
    db.commit()
    
    # Generate sample transactions
    for bond in bonds:
        for _ in range(50):  # 50 transactions per bond
            transaction = Transaction(
                bond_id=bond.id,
                price=random.uniform(bond.last_price * 0.99, bond.last_price * 1.01),
                quantity=random.randint(1000, 10000),
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 1440))
            )
            db.add(transaction)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db() 