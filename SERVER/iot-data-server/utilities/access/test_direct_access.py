import httpx
import asyncio

async def test_direct_access():
    """FastAPI 직접 접근 테스트"""
    
    # 포트 8000으로 직접 접근
    urls_to_test = [
        "http://localhost:8000/health",
        "http://localhost:8000/docs",
        "http://localhost:8000/api/v1/users",
        "http://localhost:8080/health",
        "http://localhost:8080/docs"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in urls_to_test:
            try:
                print(f"테스트 중: {url}")
                response = await client.get(url)
                print(f"✅ 성공: {response.status_code}")
                if url.endswith("/health"):
                    print(f"   응답: {response.text}")
                elif url.endswith("/docs"):
                    print(f"   Swagger UI 접근 가능")
                elif url.endswith("/users"):
                    print(f"   API 응답: {response.status_code}")
                print()
            except Exception as e:
                print(f"❌ 실패: {e}")
                print()

if __name__ == "__main__":
    asyncio.run(test_direct_access())

