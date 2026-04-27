# splash_launcher_final.py
import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGraphicsOpacityEffect
from PyQt5.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRectF, QPointF

try:
    from home import TicketingHome
except Exception:
    TicketingHome = None

class FuturisticSplash(QWidget):
    def __init__(self, duration_ms=3200, parent=None):
        super().__init__(parent)
        self.duration_ms = duration_ms
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(900, 500)
        self._t = 0.0
        self._particles = []
        self._tick = 0

        # animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(30)

        # fadeout timer
        self.finish_timer = QTimer(self)
        self.finish_timer.setSingleShot(True)
        self.finish_timer.timeout.connect(self.start_fadeout)
        self.finish_timer.start(self.duration_ms)

        # fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        self._fading = False

        # subtitle
        self.subtitle = QLabel("Intelligent · Trackable · Fast", self)
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(QFont("Segoe UI", 12))
        self.subtitle.setStyleSheet("color: rgba(255,255,255,180);")
        self.subtitle.setGeometry(0, self.height()//2 + 40, self.width(), 24)

        # center window
        scr = QApplication.primaryScreen().availableGeometry()
        self.move(scr.center().x() - self.width()//2, int(scr.center().y() - self.height()//2 - 40))

        # particles
        self._make_particles(28)

        # -------- Typewriter text animation --------
        self.words = ["ITIL", "Ticketing", "System"]
        self.displayed_text = ""
        self.current_word_index = 0
        self.word_timer = QTimer(self)
        self.word_timer.timeout.connect(self.show_next_word)
        self.word_timer.start(700)  # adjust speed per word

    # ---------- Particles ----------
    def _make_particles(self, n):
        import random
        self._particles = []
        for _ in range(n):
            x = -self.width() * 0.2 * random.random()
            y = random.uniform(0, self.height())
            length = random.uniform(self.width()*0.2, self.width()*0.9)
            speed = random.uniform(2.0, 6.0)
            w = random.uniform(1.5, 3.5)
            hue = random.uniform(180, 260)
            self._particles.append([x, y, length, speed, w, hue, random.random()*0.6+0.4])

    def on_tick(self):
        self._tick += 1
        self._t += 0.03
        for p in self._particles:
            p[0] += p[3]
            p[1] += p[3]*0.12
            if p[0] - p[2] > self.width() + 100:
                import random
                p[0] = -p[2] - 40 - self.width()*0.2*random.random()
                p[1] = random.uniform(0, self.height())
                p[2] = random.uniform(self.width()*0.2, self.width()*0.9)
                p[3] = random.uniform(2.0, 6.0)
        self.update()

    # ---------- Typewriter ----------
    def show_next_word(self):
        if self.current_word_index < len(self.words):
            if self.displayed_text:
                self.displayed_text += " "
            self.displayed_text += self.words[self.current_word_index]
            self.current_word_index += 1
            self.update()
        else:
            self.word_timer.stop()

    # ---------- Fadeout ----------
    def start_fadeout(self):
        if self._fading:
            return
        self._fading = True
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(700)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.open_home)
        self.fade_anim.start()

    def open_home(self):
        self.close()

        from main_app import MainApp
        self.main_window = MainApp()
        self.main_window.show()
    def show_login(self):
        from login_page import MainWindow

        self.login_window = MainWindow(self)
        self.main_window.close()
        self.login_window.show()

    # ---------- Painting ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        rect = self.rect()
        painter.fillRect(rect, QColor(10, 12, 20))

        grad = QLinearGradient(0,0,self.width(),self.height())
        grad.setColorAt(0, QColor(6,20,40,140))
        grad.setColorAt(0.5, QColor(10,18,40,40))
        grad.setColorAt(1, QColor(18,8,30,200))
        painter.fillRect(rect, QBrush(grad))

        # grid lines
        pen = QPen(QColor(255,255,255,18))
        pen.setWidth(1)
        painter.setPen(pen)
        step = 40
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

        # vignette
        vign = QLinearGradient(0,0,0,self.height())
        vign.setColorAt(0, QColor(0,0,0,0))
        vign.setColorAt(1, QColor(0,0,0,100))
        painter.fillRect(rect, QBrush(vign))

        # particles
        for p in self._particles:
            x,y,length,speed,w,hue,alpha = p
            hue_shift = (hue + (self._tick*0.6)) % 360
            color = QColor.fromHsl(int(hue_shift),180,150,int(160*alpha))
            pen = QPen(color)
            pen.setWidthF(w)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            start = QPointF(x,y)
            end = QPointF(x+length,y+length*0.18)
            painter.drawLine(start,end)

            glow_color = QColor(color)
            glow_color.setAlpha(int(40*alpha))
            pen2 = QPen(glow_color)
            pen2.setWidthF(w*6)
            painter.setPen(pen2)
            painter.drawLine(start,end)

        # -------- Animated Text --------
        if self.displayed_text:
            font = QFont("Orbitron", 28, QFont.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            tw = metrics.horizontalAdvance(self.displayed_text)
            th = metrics.height()
            cx = (self.width() - tw) / 2
            cy = (self.height() + th) / 2 - 50

            # soft glow
            painter.setPen(Qt.NoPen)
            for radius, alpha in [(6,40), (4,60), (2,100)]:
                glow_color = QColor(80,200,255,alpha)
                painter.setPen(glow_color)
                painter.drawText(int(cx - radius), int(cy + th*0.8 - radius), self.displayed_text)

            # gradient fill
            g = QLinearGradient(cx, cy, cx + tw, cy + th)
            g.setColorAt(0, QColor(120,200,255))
            g.setColorAt(0.5, QColor(180,120,255))
            g.setColorAt(1, QColor(120,255,200))
            painter.setPen(QPen(QBrush(g), 1))
            painter.drawText(int(cx), int(cy + th*0.8), self.displayed_text)

    def closeEvent(self, event):
        self.timer.stop()
        self.finish_timer.stop()
        self.word_timer.stop()
        super().closeEvent(event)

def launch_app():
    app = QApplication(sys.argv)
    splash = FuturisticSplash(duration_ms=3200)
    splash.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_app()
