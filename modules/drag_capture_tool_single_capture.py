print("🐍 실행 중인 drag_capture_tool 파일 확인용 - THIS IS THE RIGHT FILE")
import sys
import os
import time
from PyQt5 import QtWidgets, QtGui, QtCore

save_dir = os.path.join(os.path.expanduser("~"), "Documents", "사주세요_스크린샷")
os.makedirs(save_dir, exist_ok=True)

popup_window = None  # 전역 팝업창

class CaptureOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("🖼️ [Overlay] CaptureOverlay 객체 생성됨")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)

        screen = QtWidgets.QApplication.primaryScreen()
        geo = screen.virtualGeometry()
        self.setGeometry(geo)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.drawing = False
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()
        self.activateWindow()
        self.raise_()
        print("[DEBUG] Overlay 창에 포커스 설정됨")

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))

        if self.drawing:
            pen = QtGui.QPen(QtGui.QColor(255, 255, 0), 2)
            painter.setPen(pen)
            rect = QtCore.QRect(self.begin, self.end).normalized()
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.globalPos()
        self.end = event.globalPos()
        self.drawing = True
        self.update()
        print("🖱️ [Overlay] 마우스 누름")

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.globalPos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.globalPos()
        self.drawing = False
        self.update()
        print("🖼️ [Overlay] 마우스 놓음 → 캡처 시도")
        self.hide()
        QtCore.QTimer.singleShot(100, self.capture_screen)
        QtCore.QTimer.singleShot(100, show_popup_again)

    def keyPressEvent(self, event):
        print("[DEBUG] keyPressEvent 진입됨")
        if event.key() == QtCore.Qt.Key_Escape:
            print("❌ [Overlay] ESC 눌림 → 캡처 취소")
            self.hide()
            show_popup_again()

    def capture_screen(self):
        rect = QtCore.QRect(self.begin, self.end).normalized()
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
            timestamp = int(time.time())
            filepath = os.path.join(save_dir, f"screenshot_crop_{timestamp}.png")
            screenshot.save(filepath)
            print("✅ [Overlay] 캡처 저장 완료:", filepath)

class SKeyPopup(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        print("💬 [Popup] SKeyPopup 생성됨")
        self.setWindowTitle("캡처")
        self.setFixedSize(440, 160)
        self.setStyleSheet("font-size: 11pt; background-color: white;")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("🟡 S 키를 누르면 캡처가 시작됩니다.\n⚠️ ESC 키를 누르면 종료됩니다.\n📦 캡처가 편하도록 창을 이동시킬 수 있습니다.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()

    def center_on_screen(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def keyPressEvent(self, event):
        print("[DEBUG] keyPressEvent 진입됨")
        if event.key() == QtCore.Qt.Key_S:
            print("🟡 [Popup] S 키 입력됨 → Overlay 실행")
            self.hide()
            QtCore.QTimer.singleShot(100, self.launch_overlay)
        elif event.key() == QtCore.Qt.Key_Escape:
            print("❌ ESC 입력 → 앱 종료")
            QtWidgets.QApplication.quit()

    def launch_overlay(self):
        try:
            self.overlay = CaptureOverlay(parent=self)
            self.overlay.show()
        except Exception as e:
            print("❗ Overlay 예외 발생:", e)

def show_popup_again():
    global popup_window
    print("🔁 다시 팝업 표시")
    popup_window.show()
    popup_window.raise_()
    popup_window.activateWindow()

def main():
    global popup_window
    print("✅ PyQt 캡처 테스트 실행 시작됨")
    app = QtWidgets.QApplication(sys.argv)
    popup_window = SKeyPopup()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()