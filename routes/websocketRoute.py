from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

router = APIRouter()


# ---------------------------------------------------------
# [Connection Manager] 웹소켓 연결 관리 클래스
# ---------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        # { "1234": [ws1, ws2], "5678": [ws3] } 형태의 딕셔너리
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, serial: str):
        await websocket.accept()
        if serial not in self.active_connections:
            self.active_connections[serial] = []
        self.active_connections[serial].append(websocket)
        print(
            f"🔗 [WS 연결] 시리얼: {serial} (현재 {len(self.active_connections[serial])}명 접속)"
        )

    def disconnect(self, websocket: WebSocket, serial: str):
        if serial in self.active_connections:
            self.active_connections[serial].remove(websocket)
            if not self.active_connections[serial]:
                del self.active_connections[serial]
            print(f"❌ [WS 해제] 시리얼: {serial}")

    async def send_personal_message(self, message: dict, serial: str):
        # 해당 시리얼 번호 방에 있는 사람들에게만 메시지 전송
        if serial in self.active_connections:
            for connection in self.active_connections[serial]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"전송 실패: {e}")


# 전역 매니저 인스턴스 생성
manager = ConnectionManager()


# ---------------------------------------------------------
# [WebSocket Endpoint] 클라이언트가 접속하는 곳
# ---------------------------------------------------------
@router.websocket("/ws/{serial}")
async def websocket_endpoint(websocket: WebSocket, serial: str):
    await manager.connect(websocket, serial)
    try:
        while True:
            # 연결 유지를 위해 대기 (클라이언트 메시지 수신용)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, serial)


# ---------------------------------------------------------
# [Helper Function] 컨트롤러에서 호출할 함수
# ---------------------------------------------------------
async def broadcast_mqtt_response(serial: str, data: dict):
    """
    MQTT 컨트롤러가 이 함수를 호출하여 웹으로 데이터를 보냅니다.
    """
    await manager.send_personal_message(data, serial)
