# 한글 폰트 패치 가이드

## 개요

이 문서는 Pinky 로봇의 `pinky_lcd_display` 패키지에 한글 폰트 지원을 추가하는 방법을 설명합니다.

## 중요 사항

**한글 폰트 지원은 `pinky_lcd_display` 패키지에 패치되어야 합니다.**

- `pinky_lcd_display_controller`는 단순히 토픽에 메시지를 발행하는 역할만 합니다.
- 실제 폰트 렌더링은 `pinky_lcd_display` 패키지의 `LCDDisplayManager` 클래스에서 이루어집니다.
- 따라서 한글 폰트를 사용하려면 **로봇에 설치된 `pinky_lcd_display` 패키지**를 수정해야 합니다.

## 패키지 위치

### 로봇 (Pinky) 측
```
/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/
```

### 개발 환경
```
~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/
```

## 패치 방법

### 1단계: 한글 폰트 파일 복사

#### 방법 1: 개발 환경에서 로봇으로 복사 (권장)

**개발 환경에서 실행:**
```bash
# 한글 폰트 파일을 로봇으로 복사
scp -r /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/src/pinky_lcd_display_controller/fonts \
  pinky@<pinky-ip>:/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/
```

#### 방법 2: 로봇에서 직접 다운로드

**로봇에서 실행:**
```bash
# 로봇에 SSH 접속
ssh pinky@<pinky-ip>

# 패키지 디렉토리로 이동
cd ~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display

# fonts 디렉토리 생성
mkdir -p fonts/maruburi/TTF

# 한글 폰트 파일 다운로드 (또는 USB/네트워크로 복사)
# 예: wget, curl, scp 등을 사용하여 폰트 파일 복사
```

### 2단계: pinky_lcd_display 패키지 수정

#### 2.1 lcd_manager.py 파일 수정

**파일 경로**: `pinky_lcd_display/pinky_lcd_display/lcd_manager.py`

**기존 코드 (예상):**
```python
from PIL import Image, ImageDraw, ImageFont

class LCDDisplayManager:
    def __init__(self):
        # 기본 폰트 로드
        try:
            self.font = ImageFont.truetype(
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 
                20
            )
        except:
            self.font = ImageFont.load_default()
```

**수정된 코드:**
```python
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

class LCDDisplayManager:
    def __init__(self):
        # 한글 폰트 경로 찾기
        korean_font_path = self._find_korean_font()
        
        # 폰트 로드
        try:
            if korean_font_path and os.path.exists(korean_font_path):
                self.font = ImageFont.truetype(korean_font_path, 20)
                self.title_font = ImageFont.truetype(korean_font_path, 24)
                self.body_font = ImageFont.truetype(korean_font_path, 18)
            else:
                # 기본 폰트 사용
                self.font = ImageFont.truetype(
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 
                    20
                )
                self.title_font = self.font
                self.body_font = self.font
        except Exception as e:
            print(f"Font loading error: {e}")
            self.font = ImageFont.load_default()
            self.title_font = self.font
            self.body_font = self.font
    
    def _find_korean_font(self):
        """
        한글 폰트 파일 경로를 찾습니다.
        
        우선순위:
        1. 패키지 소스 디렉토리의 fonts/maruburi/TTF/MaruBuri-Regular.ttf
        2. 절대 경로 /home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf
        3. 상대 경로 ./fonts/maruburi/TTF/MaruBuri-Regular.ttf
        
        Returns:
            str: 폰트 파일 경로, 찾지 못하면 None
        """
        font_filename = 'MaruBuri-Regular.ttf'
        possible_paths = []
        
        # 1. 현재 파일 기준 상대 경로
        current_file = Path(__file__)
        package_dir = current_file.parent.parent
        local_font_path = package_dir / 'fonts' / 'maruburi' / 'TTF' / font_filename
        possible_paths.append(str(local_font_path))
        
        # 2. 절대 경로 (로봇 환경)
        robot_font_path = Path('/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF') / font_filename
        possible_paths.append(str(robot_font_path))
        
        # 3. 상대 경로 (개발 환경)
        relative_font_path = Path('fonts/maruburi/TTF') / font_filename
        possible_paths.append(str(relative_font_path))
        
        # 경로 확인
        for font_path in possible_paths:
            if os.path.exists(font_path) and os.path.isfile(font_path):
                return str(Path(font_path).resolve())
        
        return None
```

#### 2.2 setup.py 수정 (폰트 파일 설치)

**파일 경로**: `pinky_lcd_display/setup.py`

**기존 코드에 추가:**
```python
from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pinky_lcd_display'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 한글 폰트 파일 설치
        (os.path.join('share', package_name, 'fonts', 'maruburi', 'TTF'),
            glob('fonts/maruburi/TTF/*.ttf')),
    ],
    # ... 나머지 설정
)
```

### 3단계: 패키지 빌드 및 설치

**로봇에서 실행:**
```bash
# 패키지 디렉토리로 이동
cd ~/ros-repo-1/ROS2/rfred

# 패키지 빌드
colcon build --packages-select pinky_lcd_display

# 환경 설정
source install/setup.bash
```

### 4단계: 테스트

**로봇에서 실행:**
```bash
# LCD 노드 실행
ros2 run pinky_lcd_display lcd_node

# 다른 터미널에서 한글 텍스트 테스트
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '안녕 핑키\n한글 테스트\n테스트 성공!'}"
```

## 패치 확인 방법

### 1. 폰트 파일 확인
```bash
# 로봇에서 실행
ls -la ~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/
```

예상 출력:
```
MaruBuri-Regular.ttf
MaruBuri-Bold.ttf
MaruBuri-SemiBold.ttf
MaruBuri-Light.ttf
MaruBuri-ExtraLight.ttf
```

### 2. 코드 수정 확인
```bash
# 로봇에서 실행
grep -n "_find_korean_font" ~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/pinky_lcd_display/lcd_manager.py
```

### 3. 빌드 확인
```bash
# 로봇에서 실행
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display 2>&1 | grep -i error
```

### 4. 런타임 확인
```bash
# 로봇에서 실행
ros2 run pinky_lcd_display lcd_node

# 로그에서 다음 메시지 확인:
# "Korean font found: /path/to/MaruBuri-Regular.ttf"
# 또는
# "Using Korean font: MaruBuri-Regular.ttf"
```

## 문제 해결

### 문제 1: 폰트 파일을 찾을 수 없음

**증상**: 한글이 깨져서 표시되거나 기본 폰트로 표시됨

**해결 방법**:
1. 폰트 파일 경로 확인:
   ```bash
   find ~/ros-repo-1 -name "MaruBuri-Regular.ttf"
   ```

2. 폰트 파일 권한 확인:
   ```bash
   chmod 644 ~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/*.ttf
   ```

3. 코드에서 폰트 경로 로그 출력 추가:
   ```python
   korean_font_path = self._find_korean_font()
   print(f"Korean font path: {korean_font_path}")
   ```

### 문제 2: PIL/Pillow에서 폰트 로드 실패

**증상**: 폰트 파일은 있지만 로드 실패

**해결 방법**:
1. PIL/Pillow 버전 확인:
   ```bash
   pip3 show Pillow
   ```

2. 폰트 파일 무결성 확인:
   ```bash
   file ~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf
   ```

3. Python에서 직접 테스트:
   ```python
   from PIL import ImageFont
   font = ImageFont.truetype('/path/to/MaruBuri-Regular.ttf', 20)
   print("Font loaded successfully")
   ```

### 문제 3: 빌드 후 폰트 파일이 설치되지 않음

**증상**: 소스에는 폰트가 있지만 빌드 후 install 디렉토리에 없음

**해결 방법**:
1. setup.py의 data_files 설정 확인
2. 빌드 전에 폰트 파일 존재 확인:
   ```bash
   ls -la src/pinky_lcd_display/fonts/maruburi/TTF/*.ttf
   ```
3. 빌드 후 설치 경로 확인:
   ```bash
   find install -name "MaruBuri-Regular.ttf"
   ```

## 자동화 스크립트

로봇에 자동으로 패치를 적용하는 스크립트 예시:

```bash
#!/bin/bash
# apply_korean_font_patch.sh

PINKY_IP="<pinky-ip-address>"
PINKY_USER="pinky"
REMOTE_PATH="/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display"

# 1. 폰트 파일 복사
echo "Copying font files..."
scp -r fonts ${PINKY_USER}@${PINKY_IP}:${REMOTE_PATH}/

# 2. 패치 파일 복사 (수정된 lcd_manager.py)
echo "Copying patched files..."
scp pinky_lcd_display/lcd_manager.py ${PINKY_USER}@${PINKY_IP}:${REMOTE_PATH}/pinky_lcd_display/

# 3. setup.py 업데이트 (필요시)
echo "Updating setup.py..."
scp setup.py ${PINKY_USER}@${PINKY_IP}:${REMOTE_PATH}/

# 4. 원격에서 빌드 실행
echo "Building package on robot..."
ssh ${PINKY_USER}@${PINKY_IP} << 'EOF'
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display
source install/setup.bash
EOF

echo "Patch applied successfully!"
```

## 참고 사항

1. **폰트 라이선스**: MaruBuri 폰트는 SIL Open Font License 1.1을 따릅니다. 상업적 사용 시 라이선스를 확인하세요.

2. **성능**: 한글 폰트 파일은 크기가 큽니다 (약 7-8MB). 메모리 사용량을 고려하세요.

3. **폴백 처리**: 한글 폰트를 찾지 못하면 기본 폰트로 자동 전환됩니다.

4. **다른 폰트 사용**: MaruBuri 대신 다른 한글 폰트를 사용하려면 `_find_korean_font()` 메서드의 `font_filename`을 변경하세요.

## 추가 개선 사항

### 폰트 크기 동적 조절
```python
def set_font_size(self, size):
    """폰트 크기를 동적으로 변경"""
    if self.korean_font_path:
        self.font = ImageFont.truetype(self.korean_font_path, size)
```

### 폰트 스타일 선택
```python
def set_font_style(self, style='regular'):
    """폰트 스타일 변경 (regular, bold, light 등)"""
    style_map = {
        'regular': 'MaruBuri-Regular.ttf',
        'bold': 'MaruBuri-Bold.ttf',
        'light': 'MaruBuri-Light.ttf',
        'semibold': 'MaruBuri-SemiBold.ttf',
    }
    font_file = style_map.get(style, 'MaruBuri-Regular.ttf')
    # ... 폰트 로드
```

## 요약

1. ✅ 한글 폰트 파일을 `pinky_lcd_display/fonts/maruburi/TTF/` 경로에 복사
2. ✅ `lcd_manager.py`에 `_find_korean_font()` 메서드 추가
3. ✅ `__init__` 메서드에서 한글 폰트 로드하도록 수정
4. ✅ `setup.py`에 폰트 파일 설치 경로 추가
5. ✅ 패키지 빌드 및 테스트

이 가이드를 따라하면 Pinky 로봇의 LCD에서 한글을 정상적으로 표시할 수 있습니다.

