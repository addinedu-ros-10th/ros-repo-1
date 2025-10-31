# pinky_lcd_display/lcd_manager.py
from PIL import Image, ImageDraw, ImageFont
import time

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
        font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        font_size_title=20,
        font_size_body=18,
    ):
        self.width = width
        self.height = height
        self.bg_color = bg_color

        self.lcd = None  # lazy init
        self.font_title = ImageFont.truetype(font_path, font_size_title)
        self.font_body = ImageFont.truetype(font_path, font_size_body)

        self._last_frame = None

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
