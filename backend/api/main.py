from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
from starlette.websockets import WebSocketDisconnect

from database.models import Bond, Transaction
from database.session import get_db
from utils.websocket_manager import WebSocketManager
from data_acquisition.nse_scraper import NSEScraper
from data_acquisition.bse_scraper import BSEScraper
from utils.celery_app import fetch_bond_data

app = FastAPI(title="Bond Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager instance
ws_manager = WebSocketManager()

@app.get("/")
async def root():
    return {"message": "Bond Dashboard API"}

@app.get("/bonds/")
async def get_bonds(db: Session = Depends(get_db)):
    try:
        # fetch_bond_data.delay()  # Removed to avoid triggering background fetch on every request
        bonds = db.query(Bond).all()
        return [
            {
                "isin": bond.isin,
                "name": bond.name,
                "issuer": bond.issuer,
                "exchange": bond.exchange.value,
                "face_value": bond.face_value,
                "coupon_rate": bond.coupon_rate,
                "maturity_date": bond.maturity_date.isoformat() if bond.maturity_date else None,
                "yield_to_maturity": bond.yield_to_maturity,
                "last_price": bond.last_price,
                "volume": bond.volume
            }
            for bond in bonds
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bonds/{isin}/")
async def get_bond(isin: str, db: Session = Depends(get_db)):
    try:
        bond = db.query(Bond).filter(Bond.isin == isin).first()
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        return {
            "isin": bond.isin,
            "name": bond.name,
            "issuer": bond.issuer,
            "exchange": bond.exchange.value,
            "face_value": bond.face_value,
            "coupon_rate": bond.coupon_rate,
            "maturity_date": bond.maturity_date.isoformat() if bond.maturity_date else None,
            "yield_to_maturity": bond.yield_to_maturity,
            "last_price": bond.last_price,
            "volume": bond.volume
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/")
async def get_transactions(db: Session = Depends(get_db)):
    try:
        transactions = db.query(Transaction).all()
        return [
            {
                "id": t.id,
                "bond_id": t.bond_id,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "price": t.price,
                "quantity": t.quantity
            }
            for t in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/{isin}/")
async def get_bond_transactions(isin: str, db: Session = Depends(get_db)):
    try:
        bond = db.query(Bond).filter(Bond.isin == isin).first()
        if not bond:
            raise HTTPException(status_code=404, detail="Bond not found")
        
        transactions = db.query(Transaction).filter(Transaction.bond_id == bond.id).all()
        return [
            {
                "id": t.id,
                "bond_id": t.bond_id,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "price": t.price,
                "quantity": t.quantity
            }
            for t in transactions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial data
        db = next(get_db())
        transactions = db.query(Transaction).order_by(Transaction.timestamp.desc()).limit(100).all()
        await ws_manager.send_initial_data(websocket, [
            {
                "id": t.id,
                "bond_id": t.bond_id,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "price": t.price,
                "quantity": t.quantity
            }
            for t in transactions
        ])
        
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# New endpoint to fetch bond data from NSE
@app.get("/nse/bond/{isin}")
async def get_nse_bond_data(isin: str):
    scraper = NSEScraper()
    transactions = scraper.fetch_bond_data(isin)
    return transactions

# New endpoint to fetch bond data from BSE
@app.get("/bse/bond/{from_date}/{to_date}")
async def get_bse_bond_data(from_date: str, to_date: str):
    scraper = BSEScraper()
    transactions = scraper.fetch_bond_data(from_date, to_date)
    return transactions

# New endpoint to trigger bond data fetch
@app.post("/fetch-bonds/")
async def trigger_bond_fetch():
    try:
        from utils.celery_app import fetch_bond_data
        fetch_bond_data.delay()
        return {"message": "Bond data fetch triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 