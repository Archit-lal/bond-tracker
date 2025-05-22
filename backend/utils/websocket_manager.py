from fastapi import WebSocket
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Remaining connections: {len(self.active_connections)}")

    async def broadcast_transaction(self, transaction: Dict[str, Any]):
        """
        Broadcast a new transaction to all connected clients.
        """
        if not self.active_connections:
            return

        message = {
            "type": "new_transaction",
            "data": transaction
        }

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

    async def broadcast_bond_update(self, bond: Dict[str, Any]):
        """
        Broadcast a bond update to all connected clients.
        """
        if not self.active_connections:
            return

        message = {
            "type": "bond_update",
            "data": bond
        }

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

    async def send_initial_data(self, websocket: WebSocket, transactions: List[Dict[str, Any]]):
        """
        Send initial transaction data to a newly connected client.
        """
        try:
            message = {
                "type": "initial_data",
                "data": transactions
            }
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
            self.disconnect(websocket) 