"""
WebSocket 실시간 채팅 테스트 클라이언트 (Python)

사용 방법:
    python test_websocket.py

또는 인터랙티브 모드:
    python test_websocket.py --interactive
"""

import asyncio
import websockets
import json
import argparse
import sys


class WebSocketChatClient:
    def __init__(self, uri: str = "ws://localhost:8001/ws/voice"):
        self.uri = uri
        self.websocket = None
        self.current_response = ""
    
    async def connect(self):
        """WebSocket 연결"""
        try:
            print(f"🔌 서버에 연결 중... ({self.uri})")
            self.websocket = await websockets.connect(self.uri)
            print("✅ 연결 성공!\n")
            return True
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False
    
    async def send_message(self, message: str):
        """메시지 전송"""
        if not self.websocket:
            print("❌ 서버에 연결되어 있지 않습니다.")
            return
        
        data = {
            "type": "text",
            "message": message
        }
        
        try:
            await self.websocket.send(json.dumps(data))
            print(f"👤 사용자: {message}")
        except Exception as e:
            print(f"❌ 메시지 전송 실패: {e}")
    
    async def receive_messages(self):
        """메시지 수신 및 처리"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "text_chunk":
                        # 스트리밍 응답 청크
                        content = data.get("content", "")
                        self.current_response += content
                        # 실시간으로 출력 (같은 줄에 덮어쓰기)
                        print(f"\r🤖 AI: {self.current_response}...", end="", flush=True)
                    
                    elif data.get("type") == "text_complete":
                        # 완료된 응답
                        full_response = data.get("full_response", "")
                        print(f"\r🤖 AI: {full_response}\n")
                        self.current_response = ""
                    
                    else:
                        print(f"\n📨 수신: {data}\n")
                
                except json.JSONDecodeError:
                    print(f"\n📨 수신 (텍스트): {message}\n")
                except Exception as e:
                    print(f"\n❌ 메시지 처리 오류: {e}\n")
        
        except websockets.exceptions.ConnectionClosed:
            print("\n❌ 서버와의 연결이 끊어졌습니다.")
        except Exception as e:
            print(f"\n❌ 오류: {e}")
    
    async def close(self):
        """연결 종료"""
        if self.websocket:
            await self.websocket.close()
            print("\n👋 연결 종료")


async def interactive_mode(client: WebSocketChatClient):
    """인터랙티브 채팅 모드"""
    print("=" * 60)
    print("🤖 WebSocket 실시간 채팅 테스트")
    print("=" * 60)
    print("명령어:")
    print("  - 'quit' 또는 'exit': 종료")
    print("  - 'clear': 화면 지우기")
    print("=" * 60)
    print()
    
    # 연결
    if not await client.connect():
        return
    
    # 메시지 수신 태스크 시작
    receive_task = asyncio.create_task(client.receive_messages())
    
    try:
        while True:
            # 사용자 입력 대기
            try:
                message = input("💬 메시지 입력: ").strip()
                
                if not message:
                    continue
                
                if message.lower() in ['quit', 'exit', 'q']:
                    break
                
                if message.lower() == 'clear':
                    import os
                    os.system('clear' if os.name != 'nt' else 'cls')
                    continue
                
                # 메시지 전송
                await client.send_message(message)
                
                # 잠시 대기 (응답 수신을 위해)
                await asyncio.sleep(0.1)
            
            except KeyboardInterrupt:
                print("\n\n⚠️  종료 요청 (Ctrl+C)")
                break
            except EOFError:
                print("\n\n⚠️  입력 종료")
                break
    
    finally:
        receive_task.cancel()
        await client.close()


async def send_single_message(client: WebSocketChatClient, message: str):
    """단일 메시지 전송 및 응답 수신"""
    if not await client.connect():
        return
    
    # 메시지 전송
    await client.send_message(message)
    
    # 응답 수신
    try:
        async for ws_message in client.websocket:
            try:
                data = json.loads(ws_message)
                
                if data.get("type") == "text_chunk":
                    content = data.get("content", "")
                    client.current_response += content
                    print(f"\r🤖 AI: {client.current_response}...", end="", flush=True)
                
                elif data.get("type") == "text_complete":
                    full_response = data.get("full_response", "")
                    print(f"\r🤖 AI: {full_response}\n")
                    break
                
            except json.JSONDecodeError:
                print(f"\n📨 수신: {ws_message}\n")
    
    except Exception as e:
        print(f"\n❌ 오류: {e}")
    
    finally:
        await client.close()


async def main():
    parser = argparse.ArgumentParser(description="WebSocket 실시간 채팅 테스트 클라이언트")
    parser.add_argument(
        "--uri",
        default="ws://localhost:8001/ws/voice",
        help="WebSocket 서버 URI (기본값: ws://localhost:8001/ws/voice)"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="인터랙티브 모드 실행"
    )
    parser.add_argument(
        "--message",
        "-m",
        type=str,
        help="전송할 메시지 (단일 메시지 모드)"
    )
    
    args = parser.parse_args()
    
    client = WebSocketChatClient(uri=args.uri)
    
    try:
        if args.message:
            # 단일 메시지 모드
            await send_single_message(client, args.message)
        else:
            # 인터랙티브 모드 (기본)
            await interactive_mode(client)
    
    except KeyboardInterrupt:
        print("\n\n👋 프로그램 종료")
        await client.close()
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        await client.close()


if __name__ == "__main__":
    # Python 3.7+ 호환성
    if sys.version_info >= (3, 7):
        asyncio.run(main())
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()

