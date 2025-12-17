#!/usr/bin/env python3
"""
ROS2 API Server 스탠드얼론 실행 스크립트

호스트의 ROS2 환경을 사용하여 직접 실행합니다.
Docker 없이 Python으로 직접 실행하여 ROS2 서비스에 접근할 수 있습니다.

사용 방법:
    python3 run_standalone.py

또는:
    chmod +x run_standalone.py
    ./run_standalone.py
"""
import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ROS2 환경 설정 (호스트에 ROS2가 설치된 경우)
# ROS2 버전 자동 감지 (환경 변수 또는 자동 감지)
ros_distro = os.getenv("ROS_DISTRO")
if not ros_distro:
    # 자동 감지: jazzy 우선, 없으면 humble
    if os.path.exists("/opt/ros/jazzy"):
        ros_distro = "jazzy"
    elif os.path.exists("/opt/ros/humble"):
        ros_distro = "humble"
    else:
        ros_distro = "humble"  # 기본값

ros_install_path = f"/opt/ros/{ros_distro}/setup.bash"

# ROS2 워크스페이스 환경 설정
ros_workspace = project_root.parent  # SERVER/ros2-server
ros_workspace_install = ros_workspace / "install" / "setup.bash"

# ROS2 도메인 ID 설정 (환경 변수 또는 기본값 13)
# 사용 가능한 도메인 ID 목록 (환경 변수 또는 기본값 "11,12,13")
ros2_domain_id_allowed_str = os.getenv("ROS2_DOMAIN_ID_ALLOWED", "11,12,13")
ros2_domain_id = int(os.getenv("ROS2_DOMAIN_ID", "13"))

# 도메인 ID 검증
if ros2_domain_id < 0 or ros2_domain_id > 232:
    logger.error(f"ROS2_DOMAIN_ID는 0~232 사이의 값이어야 합니다: {ros2_domain_id}")
    sys.exit(1)

# 허용된 목록 확인 (설정된 경우)
if ros2_domain_id_allowed_str:
    allowed_list = [int(x.strip()) for x in ros2_domain_id_allowed_str.split(',') if x.strip()]
    if allowed_list and ros2_domain_id not in allowed_list:
        logger.error(
            f"ROS2_DOMAIN_ID {ros2_domain_id}는 허용된 값이 아닙니다. "
            f"허용된 값: {allowed_list}"
        )
        logger.info("다른 값을 사용하려면 ROS2_DOMAIN_ID_ALLOWED 환경 변수를 설정하세요.")
        sys.exit(1)

# 환경 변수 설정
os.environ["ROS_DOMAIN_ID"] = str(ros2_domain_id)
os.environ.setdefault("RMW_IMPLEMENTATION", "rmw_fastrtps_cpp")
os.environ.setdefault("SERVER_PORT", "8004")  # 외부 포트 8004

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_ros2_environment():
    """ROS2 환경 확인"""
    try:
        import rclpy
        logger.info("✅ ROS2 모듈 (rclpy) 사용 가능")
        return True
    except ImportError:
        logger.error("❌ ROS2 모듈 (rclpy)을 찾을 수 없습니다")
        logger.info("ROS2 환경 설정 방법:")
        logger.info(f"  1. source /opt/ros/{ros_distro}/setup.bash")
        logger.info(f"  2. source {ros_workspace_install}")
        logger.info("  3. 또는 이 스크립트를 ROS2 환경이 설정된 터미널에서 실행")
        return False

def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("ROS2 API Server 스탠드얼론 실행")
    logger.info("=" * 60)
    
    # ROS2 환경 확인
    if not check_ros2_environment():
        logger.error("ROS2 환경이 설정되지 않았습니다. 종료합니다.")
        sys.exit(1)
    
    # 환경 변수 로드
    env_file = project_root / ".env.local"
    if env_file.exists():
        logger.info(f"환경 변수 파일 로드: {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        logger.warning(f"환경 변수 파일을 찾을 수 없습니다: {env_file}")
        logger.info("기본값을 사용합니다.")
    
    # 서버 포트 확인
    server_port = int(os.getenv("SERVER_PORT", "8004"))
    logger.info(f"서버 포트: {server_port}")
    
    # uvicorn으로 서버 실행
    try:
        import uvicorn
        from src.main import app
        
        logger.info("FastAPI 서버 시작 중...")
        logger.info(f"서버 URL: http://0.0.0.0:{server_port}")
        logger.info(f"API 문서: http://localhost:{server_port}/docs")
        logger.info("=" * 60)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=server_port,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\n서버 종료 중...")
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

