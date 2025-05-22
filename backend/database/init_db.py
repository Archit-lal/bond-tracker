from sqlalchemy.orm import Session
from database.models import Base, Bond, Exchange
from datetime import datetime, timedelta
from database.session import engine, SessionLocal

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

def add_sample_data(db: Session):
    # Add sample bonds
    sample_bonds = [
        Bond(
            isin="INE001A07BM4",
            name="7.26% GOI 2029",
            issuer="Government of India",
            exchange=Exchange.NSE,
            face_value=100.0,
            coupon_rate=7.26,
            maturity_date=datetime.now() + timedelta(days=365*5),
            yield_to_maturity=7.5,
            last_price=98.5,
            volume=1000000
        ),
        Bond(
            isin="INE002A07BM4",
            name="7.10% GOI 2029",
            issuer="Government of India",
            exchange=Exchange.BSE,
            face_value=100.0,
            coupon_rate=7.10,
            maturity_date=datetime.now() + timedelta(days=365*7),
            yield_to_maturity=7.3,
            last_price=99.2,
            volume=800000
        )
    ]
    
    # Check if bonds exist before adding
    for bond in sample_bonds:
        existing_bond = db.query(Bond).filter(Bond.isin == bond.isin).first()
        if not existing_bond:
            db.add(bond)
    
    try:
        db.commit()
    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.rollback()

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    add_sample_data(db)
    db.close() 