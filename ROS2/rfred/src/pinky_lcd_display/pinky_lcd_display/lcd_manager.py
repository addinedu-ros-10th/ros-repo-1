# pinky_lcd_display/lcd_manager.py
from PIL import Image, ImageDraw, ImageFont
import time
import os
import threading
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
        
        # 현재 스타일 저장소
        self.current_style = {
            'bg_color': bg_color,
            'title_color': (0, 255, 0),
            'body_color': (255, 255, 255),
            'timestamp_color': (100, 100, 255),
            'title_font_size': font_size_title,
            'body_font_size': font_size_body,
            'font_path': font_path
        }
        
        # 현재 레이아웃 저장소
        self.current_layout = {
            'alignment': 0,  # 0: LEFT, 1: CENTER, 2: RIGHT
            'layout_mode': 1,  # 0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID
            'margin_top': 10,
            'margin_bottom': 10,
            'margin_left': 10,
            'margin_right': 10,
            'line_spacing': 24,
            'grid_columns': 1,
            'grid_rows': 1
        }
    
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
        img = Image.new("RGB", (self.width, self.height), color=self.current_style['bg_color'])
        draw = ImageDraw.Draw(img)
        return img, draw
    
    def set_style(self, bg_color_r, bg_color_g, bg_color_b,
                  title_color_r, title_color_g, title_color_b,
                  body_color_r, body_color_g, body_color_b,
                  timestamp_color_r, timestamp_color_g, timestamp_color_b,
                  title_font_size, body_font_size, font_path):
        """
        스타일을 설정하고 폰트를 재로드합니다.
        
        Args:
            bg_color_r/g/b: 배경 색상 (RGB, 0-255)
            title_color_r/g/b: 타이틀 색상 (RGB, 0-255)
            body_color_r/g/b: 본문 색상 (RGB, 0-255)
            timestamp_color_r/g/b: 타임스탬프 색상 (RGB, 0-255)
            title_font_size: 타이틀 폰트 크기
            body_font_size: 본문 폰트 크기
            font_path: 폰트 파일 경로 (빈 문자열이면 기본값 사용)
        """
        # 스타일 저장
        self.current_style['bg_color'] = (bg_color_r, bg_color_g, bg_color_b)
        self.current_style['title_color'] = (title_color_r, title_color_g, title_color_b)
        self.current_style['body_color'] = (body_color_r, body_color_g, body_color_b)
        self.current_style['timestamp_color'] = (timestamp_color_r, timestamp_color_g, timestamp_color_b)
        self.current_style['title_font_size'] = title_font_size
        self.current_style['body_font_size'] = body_font_size
        
        # 폰트 경로 처리
        if font_path and font_path.strip():
            # 지정된 폰트 경로 사용
            new_font_path = font_path
        else:
            # 기본 폰트 경로 사용 (한글 폰트 자동 탐색)
            new_font_path = self.current_style['font_path']
            if new_font_path is None:
                korean_font_path = self._find_korean_font()
                if korean_font_path:
                    new_font_path = korean_font_path
                else:
                    new_font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        # 폰트 재로드
        try:
            self.font_title = ImageFont.truetype(new_font_path, title_font_size)
            self.font_body = ImageFont.truetype(new_font_path, body_font_size)
            self.current_style['font_path'] = new_font_path
            self.korean_font_path = new_font_path if 'MaruBuri' in new_font_path else None
        except Exception as e:
            print(f"Font loading error: {e}, keeping current font")
            # 폰트 로드 실패 시 현재 폰트 유지
    
    def set_layout(self, alignment, layout_mode, margin_top, margin_bottom,
                   margin_left, margin_right, line_spacing, grid_columns, grid_rows):
        """
        레이아웃을 설정합니다.
        
        Args:
            alignment: 텍스트 정렬 (0: LEFT, 1: CENTER, 2: RIGHT)
            layout_mode: 레이아웃 모드 (0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID)
            margin_top/bottom/left/right: 여백 (픽셀)
            line_spacing: 라인 간격 (픽셀)
            grid_columns/rows: 그리드 모드 시 열/행 수
        """
        self.current_layout['alignment'] = alignment
        self.current_layout['layout_mode'] = layout_mode
        self.current_layout['margin_top'] = margin_top
        self.current_layout['margin_bottom'] = margin_bottom
        self.current_layout['margin_left'] = margin_left
        self.current_layout['margin_right'] = margin_right
        self.current_layout['line_spacing'] = line_spacing
        self.current_layout['grid_columns'] = grid_columns
        self.current_layout['grid_rows'] = grid_rows

    def render_status_frame(self, title="Pinky Status", lines=None, footer_timestamp=True):
        if lines is None:
            lines = []

        img, draw = self._new_canvas()

        # 레이아웃 설정 가져오기
        margin_left = self.current_layout['margin_left']
        margin_top = self.current_layout['margin_top']
        margin_right = self.current_layout['margin_right']
        margin_bottom = self.current_layout['margin_bottom']
        line_spacing = self.current_layout['line_spacing']
        alignment = self.current_layout['alignment']
        layout_mode = self.current_layout['layout_mode']

        # 타이틀 위치 계산
        y = margin_top
        
        # 정렬에 따른 x 위치 계산
        if alignment == 0:  # LEFT
            x = margin_left
        elif alignment == 1:  # CENTER
            try:
                text_width = draw.textlength(title, font=self.font_title)
                x = (self.width - text_width) // 2
            except:
                x = margin_left
        else:  # RIGHT
            try:
                text_width = draw.textlength(title, font=self.font_title)
                x = self.width - margin_right - text_width
            except:
                x = margin_left
        
        # 타이틀 그리기
        draw.text((x, y), title, fill=self.current_style['title_color'], font=self.font_title)
        y += self.current_style['title_font_size'] + 10

        # 본문 라인 그리기
        if layout_mode == 0:  # SINGLE_LINE
            # 모든 라인을 한 줄로 합치기
            combined_line = ' '.join(lines)
            if alignment == 0:  # LEFT
                x = margin_left
            elif alignment == 1:  # CENTER
                try:
                    text_width = draw.textlength(combined_line, font=self.font_body)
                    x = (self.width - text_width) // 2
                except:
                    x = margin_left
            else:  # RIGHT
                try:
                    text_width = draw.textlength(combined_line, font=self.font_body)
                    x = self.width - margin_right - text_width
                except:
                    x = margin_left
            draw.text((x, y), combined_line, fill=self.current_style['body_color'], font=self.font_body)
        elif layout_mode == 2:  # GRID
            # 그리드 모드
            grid_cols = self.current_layout['grid_columns']
            grid_rows = self.current_layout['grid_rows']
            cell_width = (self.width - margin_left - margin_right) // grid_cols
            cell_height = (self.height - margin_top - margin_bottom - self.current_style['title_font_size'] - 10) // grid_rows
            
            for idx, line in enumerate(lines[:grid_cols * grid_rows]):
                row = idx // grid_cols
                col = idx % grid_cols
                cell_x = margin_left + col * cell_width
                cell_y = y + row * cell_height
                draw.text((cell_x, cell_y), line, fill=self.current_style['body_color'], font=self.font_body)
        else:  # MULTI_LINE
            # 다중 라인 모드
            for line in lines:
                if alignment == 0:  # LEFT
                    x = margin_left
                elif alignment == 1:  # CENTER
                    try:
                        text_width = draw.textlength(line, font=self.font_body)
                        x = (self.width - text_width) // 2
                    except:
                        x = margin_left
                else:  # RIGHT
                    try:
                        text_width = draw.textlength(line, font=self.font_body)
                        x = self.width - margin_right - text_width
                    except:
                        x = margin_left
                draw.text((x, y), line, fill=self.current_style['body_color'], font=self.font_body)
                y += line_spacing

        # 타임스탬프 그리기
        if footer_timestamp:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            draw.text(
                (margin_left, self.height - margin_bottom - self.current_style['body_font_size']),
                ts,
                fill=self.current_style['timestamp_color'],
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

    def show_status_with_animation(self, title="Pinky Status", lines=None, footer_timestamp=True, animation_type='fade_in'):
        """
        애니메이션 효과와 함께 상태를 표시합니다.
        
        Args:
            title: 타이틀 텍스트
            lines: 본문 라인들
            footer_timestamp: 타임스탬프 표시 여부
            animation_type: 애니메이션 타입 ('fade_in', 'slide')
        """
        if lines is None:
            lines = []
        
        # 최종 프레임 생성
        final_frame = self.render_status_frame(title, lines, footer_timestamp)
        
        if animation_type == 'fade_in':
            # FADE_IN 효과: 알파값을 점진적으로 증가
            num_frames = 10
            for i in range(num_frames + 1):
                alpha = i / num_frames
                # 배경 이미지 (검은색)
                bg_img = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
                # 블렌딩
                fade_img = Image.blend(bg_img, final_frame, alpha)
                lcd = self.ensure_lcd_ready()
                lcd.img_show(fade_img)
                time.sleep(0.03)  # 30ms 간격
        elif animation_type == 'slide':
            # SLIDE 효과: 왼쪽에서 오른쪽으로 슬라이드
            num_frames = 10
            for i in range(num_frames + 1):
                slide_distance = self.width
                current_x = int(slide_distance * (1 - i / num_frames))
                # 새 이미지 생성
                slide_img = Image.new("RGB", (self.width, self.height), color=self.current_style['bg_color'])
                # final_frame을 current_x 위치에 붙여넣기
                slide_img.paste(final_frame, (current_x, 0))
                lcd = self.ensure_lcd_ready()
                lcd.img_show(slide_img)
                time.sleep(0.04)  # 40ms 간격
        
        # 최종 프레임 표시
        lcd = self.ensure_lcd_ready()
        lcd.img_show(final_frame)
        self._last_frame = final_frame
        return final_frame
    
    def show_image(self, image_path=None, image_obj=None, x=0, y=0, width=0, height=0, clear_before=False):
        """
        이미지를 LCD에 표시합니다.
        
        Args:
            image_path: 이미지 파일 경로 (GIF, PNG, JPEG 등)
            image_obj: PIL Image 객체 (image_path가 None인 경우 사용)
            x, y: 이미지 위치 (픽셀)
            width, height: 이미지 크기 (0이면 원본 크기)
            clear_before: 표시 전 화면 지우기 여부
        """
        try:
            # 이미지 로드
            if image_path:
                img = Image.open(image_path)
            elif image_obj:
                img = image_obj.copy()
            else:
                raise ValueError("Either image_path or image_obj must be provided")
            
            # RGB로 변환
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 리사이즈
            if width > 0 and height > 0:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif width > 0:
                # 비율 유지하며 너비만 조정
                ratio = width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            elif height > 0:
                # 비율 유지하며 높이만 조정
                ratio = height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, height), Image.Resampling.LANCZOS)
            
            # LCD 해상도에 맞게 리사이즈 (필요시)
            if img.width > self.width or img.height > self.height:
                img.thumbnail((self.width, self.height), Image.Resampling.LANCZOS)
            
            # 배경 이미지 생성
            if clear_before:
                bg_img = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
            else:
                # 기존 프레임이 있으면 사용, 없으면 검은 배경
                if self._last_frame:
                    bg_img = self._last_frame.copy()
                else:
                    bg_img = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
            
            # 이미지 배치 (중앙 정렬)
            if x == 0 and y == 0:
                # 중앙 정렬
                x = (self.width - img.width) // 2
                y = (self.height - img.height) // 2
            
            # 배경에 이미지 붙여넣기
            bg_img.paste(img, (x, y))
            
            # LCD에 표시
            lcd = self.ensure_lcd_ready()
            lcd.img_show(bg_img)
            
            self._last_frame = bg_img
            return bg_img
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            raise
    
    def show_scroll_text(self, text, direction=0, scroll_speed_ms=50, repeat_count=1, callback=None):
        """
        스크롤 텍스트를 표시합니다.
        
        Args:
            text: 스크롤할 텍스트
            direction: 스크롤 방향 (0: LEFT, 1: RIGHT, 2: UP, 3: DOWN)
            scroll_speed_ms: 스크롤 속도 (밀리초)
            repeat_count: 반복 횟수 (0이면 무한)
            callback: 피드백 콜백 함수 (current_position, progress_percent)
        """
        img, draw = self._new_canvas()
        
        # 텍스트 너비 측정
        try:
            text_width = draw.textlength(text, font=self.font_body)
        except:
            text_width = len(text) * 10  # 대략적인 너비
        
        # 스크롤이 필요한지 확인
        if text_width <= self.width - self.current_layout['margin_left'] - self.current_layout['margin_right']:
            # 스크롤 불필요, 그냥 표시
            x = self.current_layout['margin_left']
            y = self.current_layout['margin_top'] + self.current_style['title_font_size'] + 10
            draw.text((x, y), text, fill=self.current_style['body_color'], font=self.font_body)
            lcd = self.ensure_lcd_ready()
            lcd.img_show(img)
            self._last_frame = img
            return
        
        # 스크롤 애니메이션
        total_distance = text_width + self.width
        current_position = 0
        cycle_count = 0
        
        lcd = self.ensure_lcd_ready()
        
        while True:
            # 무한 반복이 아니고 반복 횟수에 도달하면 종료
            if repeat_count > 0 and cycle_count >= repeat_count:
                break
            
            # 스크롤 위치 계산
            if direction == 0:  # LEFT
                x = self.width - current_position
            elif direction == 1:  # RIGHT
                x = -text_width + current_position
            else:  # UP/DOWN은 현재 구현하지 않음
                x = self.current_layout['margin_left']
            
            y = self.current_layout['margin_top'] + self.current_style['title_font_size'] + 10
            
            # 새 이미지 생성
            scroll_img, scroll_draw = self._new_canvas()
            scroll_draw.text((x, y), text, fill=self.current_style['body_color'], font=self.font_body)
            
            # LCD에 표시
            lcd.img_show(scroll_img)
            self._last_frame = scroll_img
            
            # 피드백 발행
            if callback:
                progress = int((current_position / total_distance) * 100) if total_distance > 0 else 0
                callback(current_position, progress)
            
            # 다음 위치로 이동
            current_position += 10  # 10픽셀씩 이동
            if current_position >= total_distance:
                current_position = 0
                cycle_count += 1
            
            time.sleep(scroll_speed_ms / 1000.0)
    
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
