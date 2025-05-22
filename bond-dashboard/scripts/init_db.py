#!/usr/bin/env python3
"""
Database initialization script.
Run this script to create the database tables and initialize sample data.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine, SessionLocal
from backend.database.models import Base, Bond, Transaction, SourceEnum, MarketTypeEnum

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created!")

def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")
    db = SessionLocal()
    
    try:
        # Check if there's already data
        if db.query(Bond).count() > 0:
            print("Database already contains data. Skipping sample data creation.")
            return
        
        # Create sample bonds
        print("Creating sample bonds...")
        bonds = [
            Bond(
                isin="INE001A01036",
                symbol="HDFCBANK",
                name="HDFC Bank Ltd. Bond",
                issuer="HDFC Bank Ltd.",
                issue_date=datetime.now() - timedelta(days=365),
                maturity_date=datetime.now() + timedelta(days=365 * 5),
                coupon_rate=7.5,
                face_value=1000.0,
                source=SourceEnum.NSE,
                description="5-year bond from HDFC Bank Ltd."
            ),
            Bond(
                isin="INE002B02046",
                symbol="TATASTEEL",
                name="Tata Steel Ltd. Bond",
                issuer="Tata Steel Ltd.",
                issue_date=datetime.now() - timedelta(days=180),
                maturity_date=datetime.now() + timedelta(days=365 * 3),
                coupon_rate=8.2,
                face_value=1000.0,
                source=SourceEnum.BSE,
                description="3-year bond from Tata Steel Ltd."
            ),
            Bond(
                isin="INE003C03056",
                symbol="RELIANCE",
                name="Reliance Industries Ltd. Bond",
                issuer="Reliance Industries Ltd.",
                issue_date=datetime.now() - timedelta(days=90),
                maturity_date=datetime.now() + timedelta(days=365 * 7),
                coupon_rate=6.9,
                face_value=1000.0,
                source=SourceEnum.NSDL,
                description="7-year bond from Reliance Industries Ltd."
            ),
        ]
        
        db.add_all(bonds)
        db.commit()
        
        # Create sample transactions
        print("Creating sample transactions...")
        
        # Get the bonds we just created
        bonds = db.query(Bond).all()
        
        # Generate 50 transactions for each bond over the last 30 days
        for bond in bonds:
            for _ in range(50):
                # Random date in the last 30 days
                days_ago = random.randint(0, 30)
                trade_date = datetime.now().date() - timedelta(days=days_ago)
                
                # Random time
                hour = random.randint(9, 15)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                trade_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                
                # Price variation around face value
                price_variation = random.uniform(-50, 50)
                price = bond.face_value + price_variation
                
                # Calculate yield based on price and coupon
                yield_value = (bond.coupon_rate / (price / bond.face_value)) * 100
                
                # Random volume
                volume = random.randint(10, 1000)
                
                # Calculate value
                value = price * volume
                
                # Create transaction
                transaction = Transaction(
                    bond_id=bond.id,
                    trade_date=trade_date,
                    trade_time=trade_time,
                    price=price,
                    yield_value=yield_value,
                    volume=volume,
                    value=value,
                    market_type=MarketTypeEnum.SECONDARY,
                    source=bond.source,
                    created_at=datetime.now() - timedelta(days=days_ago, 
                                                         hours=random.randint(0, 23),
                                                         minutes=random.randint(0, 59))
                )
                db.add(transaction)
        
        db.commit()
        print("Sample data created!")
    
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    create_sample_data()
    print("Database initialization completed!") 