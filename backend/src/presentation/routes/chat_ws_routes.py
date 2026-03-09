from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from application.auth.jwt_service import JWTService
from infrastructure.db.session import SessionLocal
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.realtime.chat_connection_manager import chat_connection_manager

router = APIRouter(prefix="/chat", tags=["Chat WebSocket"])


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        payload = JWTService.verify_token(token)
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        user_repo = UserRepositoryImpl(db)
        user = user_repo.get_by_id(user_id)

        if not user:
            await websocket.close(code=1008)
            return

        await chat_connection_manager.connect(user_id, websocket)

        await websocket.send_json(
            {
                "event": "connected",
                "user_id": user_id,
                "message": "WebSocket connection established",
            }
        )

        while True:
            data = await websocket.receive_json()

            # Keep it intentionally minimal.
            # Client may send ping to keep the connection alive.
            if data.get("type") == "ping":
                await websocket.send_json({"event": "pong"})
            else:
                await websocket.send_json(
                    {
                        "event": "ignored",
                        "message": "Use REST endpoints to create messages. WebSocket is for realtime updates only.",
                    }
                )

    except WebSocketDisconnect:
        chat_connection_manager.disconnect(user_id, websocket)
    except Exception:
        chat_connection_manager.disconnect(user_id, websocket)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
    finally:
        db.close()
