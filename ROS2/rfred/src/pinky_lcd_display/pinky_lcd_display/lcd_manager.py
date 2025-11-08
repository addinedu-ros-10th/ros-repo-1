# pinky_lcd_display/lcd_manager.py
from PIL import Image, ImageDraw, ImageFont
import time
import os
from pathlib import Path

try:
    from pinky_lcd import LCD
except ImportError:
    LCD = None


class LCDDisplayManager:
    def __init__(
        self,
        width=320,
        height=240,
        bg_color=(0, 0, 0),
        font_path=None,  # None이면 자동으로 한글 폰트 탐색
        font_size_title=20,
        font_size_body=18,
    ):
        self.width = width
        self.height = height
        self.bg_color = bg_color

        self.lcd = None  # lazy init
        
        # 한글 폰트 경로 찾기 (font_path가 None인 경우)
        if font_path is None:
            korean_font_path = self._find_korean_font()
            if korean_font_path:
                font_path = korean_font_path
                print(f"Korean font found: {font_path}")
            else:
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                print("Korean font not found, using default font")
        
        # 폰트 로드
        try:
            self.font_title = ImageFont.truetype(font_path, font_size_title)
            self.font_body = ImageFont.truetype(font_path, font_size_body)
            self.korean_font_path = font_path if 'MaruBuri' in font_path else None
        except Exception as e:
            print(f"Font loading error: {e}, using default font")
            try:
                self.font_title = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                    font_size_title
                )
                self.font_body = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                    font_size_body
                )
            except:
                self.font_title = ImageFont.load_default()
                self.font_body = ImageFont.load_default()
            self.korean_font_path = None

        self._last_frame = None
    
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
        
        # 4. 패키지 설치 경로 (ament_index 사용)
        try:
            from ament_index_python.packages import get_package_share_directory
            package_share_dir = get_package_share_directory('pinky_lcd_display')
            installed_font_path = Path(package_share_dir) / 'fonts' / 'maruburi' / 'TTF' / font_filename
            possible_paths.append(str(installed_font_path))
        except Exception:
            pass
        
        # 경로 확인
        for font_path in possible_paths:
            if os.path.exists(font_path) and os.path.isfile(font_path):
                return str(Path(font_path).resolve())
        
        return None

    def ensure_lcd_ready(self):
        if self.lcd is None:
            if LCD is None:
                raise RuntimeError("LCD hardware driver not available")
            self.lcd = LCD()
        return self.lcd

    def _new_canvas(self):
        img = Image.new("RGB", (self.width, self.height), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        return img, draw

    def render_status_frame(self, title="Pinky Status", lines=None, footer_timestamp=True):
        if lines is None:
            lines = []

        img, draw = self._new_canvas()

        x = 10
        y = 10
        draw.text((x, y), title, fill=(0, 255, 0), font=self.font_title)
        y += 30

        for line in lines:
            draw.text((x, y), line, fill=(255, 255, 255), font=self.font_body)
            y += 24

        if footer_timestamp:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            draw.text(
                (10, self.height - 24),
                ts,
                fill=(100, 100, 255),
                font=self.font_body,
            )

        return img

    def show_status(self, title="Pinky Status", lines=None, footer_timestamp=True):
        img = self.render_status_frame(
            title=title,
            lines=lines,
            footer_timestamp=footer_timestamp,
        )
        lcd = self.ensure_lcd_ready()
        lcd.img_show(img)
        self._last_frame = img
        return img

    def close(self):
        if self.lcd is not None:
            try:
                self.lcd.clear()
            except Exception:
                pass
            try:
                self.lcd.close()
            except Exception:
                pass
            finally:
                self.lcd = None
