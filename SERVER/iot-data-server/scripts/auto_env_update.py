#!/usr/bin/env python3
"""
IoT Care Backend System 환경변수 자동 업데이트 스크립트
macOS, Linux, Windows 환경을 자동으로 감지하여 IP 주소를 업데이트합니다.
"""

import os
import sys
import socket
import subprocess
import platform
import re
from pathlib import Path
from typing import Optional, Tuple
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvironmentUpdater:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.env_file = self.project_root / ".env.local"
        self.backup_dir = self.project_root / "env_backups"
        
        # 백업 디렉토리 생성
        self.backup_dir.mkdir(exist_ok=True)
    
    def get_current_ip(self) -> Optional[str]:
        """현재 시스템의 IP 주소를 가져옵니다."""
        system = platform.system().lower()
        
        try:
            if system == "darwin":  # macOS
                return self._get_macos_ip()
            elif system == "linux":
                return self._get_linux_ip()
            elif system == "windows":
                return self._get_windows_ip()
            else:
                logger.warning(f"지원하지 않는 운영체제: {system}")
                return self._get_fallback_ip()
        except Exception as e:
            logger.error(f"IP 주소 조회 실패: {e}")
            return self._get_fallback_ip()
    
    def _get_macos_ip(self) -> Optional[str]:
        """macOS에서 IP 주소를 가져옵니다."""
        try:
            # ifconfig 사용
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # IP 주소 추출 (127.0.0.1 제외)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
            
            # ipconfig getifaddr en0 시도
            result = subprocess.run(
                ["ipconfig", "getifaddr", "en0"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            logger.warning("ifconfig/ipconfig 명령어 실패")
            return None
    
    def _get_linux_ip(self) -> Optional[str]:
        """Linux에서 IP 주소를 가져옵니다."""
        try:
            # ip addr 사용
            result = subprocess.run(
                ["ip", "addr", "show"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
            
            # hostname -I 시도
            result = subprocess.run(
                ["hostname", "-I"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            ips = result.stdout.strip().split()
            if ips:
                return ips[0]
                
        except subprocess.CalledProcessError:
            logger.warning("ip/hostname 명령어 실패")
            return None
        
        return None
    
    def _get_windows_ip(self) -> Optional[str]:
        """Windows에서 IP 주소를 가져옵니다."""
        try:
            # PowerShell 사용
            cmd = [
                "powershell", "-Command",
                "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            ip = result.stdout.strip()
            if ip and re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                return ip
                
        except subprocess.CalledProcessError:
            logger.warning("PowerShell 명령어 실패")
        
        try:
            # ipconfig 사용
            result = subprocess.run(
                ["ipconfig"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4' in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
                        
        except subprocess.CalledProcessError:
            logger.warning("ipconfig 명령어 실패")
        
        return None
    
    def _get_fallback_ip(self) -> Optional[str]:
        """소켓을 사용한 fallback IP 조회"""
        try:
            # 외부 연결을 시도하여 로컬 IP 확인
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return None
    
    def read_env_file(self) -> dict:
        """환경변수 파일을 읽어서 딕셔너리로 반환합니다."""
        env_vars = {}
        
        if not self.env_file.exists():
            logger.error(f"환경변수 파일을 찾을 수 없습니다: {self.env_file}")
            return env_vars
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        except Exception as e:
            logger.error(f"환경변수 파일 읽기 실패: {e}")
        
        return env_vars
    
    def write_env_file(self, env_vars: dict):
        """환경변수 딕셔너리를 파일에 씁니다."""
        try:
            # 백업 생성
            backup_file = self.backup_dir / f".env.local.backup.{int(os.time.time())}"
            if self.env_file.exists():
                import shutil
                shutil.copy2(self.env_file, backup_file)
                logger.info(f"백업 파일 생성: {backup_file}")
            
            # 새 파일 작성
            with open(self.env_file, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"환경변수 파일 업데이트 완료: {self.env_file}")
            
        except Exception as e:
            logger.error(f"환경변수 파일 쓰기 실패: {e}")
            raise
    
    def update_ip_addresses(self, current_ip: str) -> bool:
        """IP 주소 관련 환경변수를 업데이트합니다."""
        env_vars = self.read_env_file()
        
        if not env_vars:
            return False
        
        updated = False
        ip_fields = ['DB_HOST', 'CADDY_DOMAIN']
        
        for field in ip_fields:
            if field in env_vars:
                old_value = env_vars[field]
                env_vars[field] = current_ip
                if old_value != current_ip:
                    logger.info(f"{field}: {old_value} → {current_ip}")
                    updated = True
                else:
                    logger.info(f"{field}: 이미 최신 ({current_ip})")
            else:
                logger.warning(f"{field} 환경변수가 없습니다")
        
        if updated:
            self.write_env_file(env_vars)
            return True
        
        return False
    
    def check_docker_status(self) -> bool:
        """Docker 상태를 확인합니다."""
        try:
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def restart_docker_compose(self):
        """Docker Compose를 재시작합니다."""
        if not self.check_docker_status():
            logger.error("Docker가 실행되지 않았습니다")
            return False
        
        try:
            logger.info("Docker Compose 중지 중...")
            subprocess.run(
                ["docker-compose", "down", "--volumes", "--remove-orphans"],
                cwd=self.project_root,
                check=True
            )
            
            logger.info("Docker 시스템 정리 중...")
            subprocess.run(["docker", "system", "prune", "-f"], check=True)
            
            logger.info("Docker Compose 시작 중...")
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.project_root,
                check=True
            )
            
            logger.info("Docker Compose 재시작 완료")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker Compose 재시작 실패: {e}")
            return False
    
    def run(self, auto_restart: bool = False) -> bool:
        """메인 실행 함수"""
        logger.info("🔍 환경변수 자동 업데이트 시작...")
        
        # 현재 IP 주소 조회
        current_ip = self.get_current_ip()
        if not current_ip:
            logger.error("IP 주소를 조회할 수 없습니다")
            return False
        
        logger.info(f"✅ 현재 IP 주소: {current_ip}")
        
        # 환경변수 파일 확인
        if not self.env_file.exists():
            logger.error(f"환경변수 파일을 찾을 수 없습니다: {self.env_file}")
            return False
        
        # IP 주소 업데이트
        updated = self.update_ip_addresses(current_ip)
        
        if updated:
            logger.info("🔄 IP 주소가 업데이트되었습니다")
            
            if auto_restart:
                logger.info("🚀 Docker Compose 자동 재시작 시작...")
                return self.restart_docker_compose()
        else:
            logger.info("✅ IP 주소가 이미 최신 상태입니다")
        
        return True

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="IoT Care Backend System 환경변수 자동 업데이트"
    )
    parser.add_argument(
        "--restart", 
        action="store_true",
        help="환경변수 업데이트 후 Docker Compose 자동 재시작"
    )
    parser.add_argument(
        "--project-root",
        help="프로젝트 루트 디렉토리 (기본값: 현재 디렉토리)"
    )
    
    args = parser.parse_args()
    
    # 프로젝트 루트 디렉토리 찾기
    if args.project_root:
        project_root = args.project_root
    else:
        # .env.local 파일이 있는 디렉토리를 찾음
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            if (current_dir / ".env.local").exists():
                project_root = str(current_dir)
                break
            current_dir = current_dir.parent
        else:
            project_root = str(Path.cwd())
    
    # 환경변수 업데이트 실행
    updater = EnvironmentUpdater(project_root)
    success = updater.run(auto_restart=args.restart)
    
    if success:
        logger.info("✅ 환경변수 자동 업데이트 완료!")
        sys.exit(0)
    else:
        logger.error("❌ 환경변수 자동 업데이트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()

