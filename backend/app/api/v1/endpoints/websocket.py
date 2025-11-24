from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
from app.core.auth import get_current_user_ws
from app.models.user import User
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
# Key: user_id, Value: WebSocket connection
active_connections: Dict[str, WebSocket] = {}

# Store subscriptions for each user
# Key: user_id, Value: Set of subscribed events
user_subscriptions: Dict[str, Set[str]] = {}


class ConnectionManager:
    """Manages WebSocket connections"""

    @staticmethod
    async def connect(user_id: str, websocket: WebSocket):
        """Connect a new WebSocket"""
        await websocket.accept()
        active_connections[user_id] = websocket
        user_subscriptions[user_id] = set()
        logger.info(f"User {user_id} connected to WebSocket")

    @staticmethod
    async def disconnect(user_id: str):
        """Disconnect WebSocket"""
        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in user_subscriptions:
            del user_subscriptions[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")

    @staticmethod
    async def send_message(user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in active_connections:
            try:
                await active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                await ConnectionManager.disconnect(user_id)

    @staticmethod
    async def broadcast(message: dict, organization_id: str = None):
        """Broadcast message to all connected users or organization"""
        disconnected_users = []

        for user_id, websocket in active_connections.items():
            try:
                # If organization_id is provided, only send to users in that org
                # This requires storing org info in connection manager
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            await ConnectionManager.disconnect(user_id)

    @staticmethod
    def subscribe(user_id: str, event: str):
        """Subscribe user to an event"""
        if user_id in user_subscriptions:
            user_subscriptions[user_id].add(event)
            logger.info(f"User {user_id} subscribed to {event}")

    @staticmethod
    def unsubscribe(user_id: str, event: str):
        """Unsubscribe user from an event"""
        if user_id in user_subscriptions and event in user_subscriptions[user_id]:
            user_subscriptions[user_id].remove(event)
            logger.info(f"User {user_id} unsubscribed from {event}")

    @staticmethod
    async def send_to_subscribers(event: str, message: dict, organization_id: str = None):
        """Send message to all users subscribed to an event"""
        for user_id, subscriptions in user_subscriptions.items():
            if event in subscriptions:
                await ConnectionManager.send_message(user_id, message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for real-time communication

    Query Parameters:
    - token: JWT access token for authentication
    """
    try:
        # Authenticate user with token
        user = await get_current_user_ws(token)
        user_id = str(user.id)

        # Connect WebSocket
        await manager.connect(user_id, websocket)

        # Send welcome message
        await manager.send_message(
            user_id,
            {
                "type": "connected",
                "message": "Connected to FitFlow Pro WebSocket",
                "user_id": user_id,
            },
        )

        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                # Handle different message types
                message_type = data.get("type")

                if message_type == "ping":
                    # Respond to heartbeat
                    await manager.send_message(
                        user_id,
                        {"type": "pong", "timestamp": data.get("timestamp")},
                    )

                elif message_type == "subscribe":
                    # Subscribe to event
                    event = data.get("event")
                    if event:
                        manager.subscribe(user_id, event)
                        await manager.send_message(
                            user_id,
                            {
                                "type": "subscribed",
                                "event": event,
                                "message": f"Subscribed to {event}",
                            },
                        )

                elif message_type == "unsubscribe":
                    # Unsubscribe from event
                    event = data.get("event")
                    if event:
                        manager.unsubscribe(user_id, event)
                        await manager.send_message(
                            user_id,
                            {
                                "type": "unsubscribed",
                                "event": event,
                                "message": f"Unsubscribed from {event}",
                            },
                        )

                elif message_type == "message":
                    # Echo message back (for testing)
                    await manager.send_message(user_id, {"type": "echo", "data": data})

                else:
                    await manager.send_message(
                        user_id,
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        },
                    )

            except json.JSONDecodeError:
                await manager.send_message(
                    user_id,
                    {"type": "error", "message": "Invalid JSON format"},
                )
            except Exception as e:
                logger.error(f"Error processing message from user {user_id}: {e}")
                await manager.send_message(
                    user_id,
                    {"type": "error", "message": "Error processing message"},
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
        await manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.disconnect(user_id)
        except:
            pass


# Helper functions to send real-time updates


async def notify_check_in(user_id: str, check_in_data: dict):
    """Notify user about check-in event"""
    await manager.send_to_subscribers(
        "check_ins",
        {
            "type": "check_in",
            "event": "check_ins",
            "data": check_in_data,
        },
    )


async def notify_booking(user_id: str, booking_data: dict):
    """Notify user about booking event"""
    await manager.send_message(
        user_id,
        {
            "type": "booking",
            "event": "bookings",
            "data": booking_data,
        },
    )


async def notify_membership_update(user_id: str, membership_data: dict):
    """Notify user about membership update"""
    await manager.send_message(
        user_id,
        {
            "type": "membership_update",
            "event": "membership",
            "data": membership_data,
        },
    )


async def notify_payment(user_id: str, payment_data: dict):
    """Notify user about payment event"""
    await manager.send_message(
        user_id,
        {
            "type": "payment",
            "event": "payments",
            "data": payment_data,
        },
    )


async def send_notification(user_id: str, notification_data: dict):
    """Send notification to user"""
    await manager.send_message(
        user_id,
        {
            "type": "notification",
            "event": "notifications",
            "data": notification_data,
        },
    )
