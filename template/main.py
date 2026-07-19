import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, 
                             QMenu, QAction, QLabel)
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QTransform


def get_resource_path(relative_path):
    """获取资源文件路径（兼容打包后exe运行）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class PetWindow(QWidget):
    """桌面宠物主窗口"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_state()
        self.init_animations()
        self.init_tray()

    def init_ui(self):
        """初始化窗口样式"""
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.pet_size = QSize(120, 140)
        self.resize(self.pet_size)

        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.resize(self.pet_size)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 50, 
                  screen.height() - self.height() - 100)

    def init_state(self):
        """初始化状态变量"""
        self.is_dragging = False
        self.drag_offset = QPoint()

        self.is_walking = True
        self.walk_direction = 1
        self.walk_speed = 2
        self.walk_timer = QTimer()
        self.walk_timer.timeout.connect(self.update_walk)

        self.breath_timer = QTimer()
        self.breath_timer.timeout.connect(self.update_breath)
        self.breath_scale = 1.0
        self.breath_dir = 1

        self.is_jumping = False
        self.jump_height = 0
        self.jump_velocity = 0
        self.jump_timer = QTimer()
        self.jump_timer.timeout.connect(self.update_jump)

        self.load_images()

    def load_images(self):
        """加载宠物图片"""
        assets_dir = get_resource_path('assets')
        
        self.image_stand = QPixmap(os.path.join(assets_dir, 'pet_stand.png'))
        self.image_sit = QPixmap(os.path.join(assets_dir, 'pet_sit.png'))
        self.image_lie = QPixmap(os.path.join(assets_dir, 'pet_lie.png'))

        if self.image_stand.isNull():
            self.image_stand = QPixmap(os.path.join(assets_dir, 'pet_stand.jpg'))
        if self.image_sit.isNull():
            self.image_sit = QPixmap(os.path.join(assets_dir, 'pet_sit.jpg'))
        if self.image_lie.isNull():
            self.image_lie = QPixmap(os.path.join(assets_dir, 'pet_lie.jpg'))

        # 备用：如果只有一张图，全部用站立图代替
        if self.image_sit.isNull():
            self.image_sit = self.image_stand
        if self.image_lie.isNull():
            self.image_lie = self.image_stand

        self.current_image = self.image_stand
        self.update_pet_display()

    def init_animations(self):
        """启动动画"""
        self.walk_timer.start(50)
        self.breath_timer.start(80)

    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        
        tray_pixmap = self.image_stand.scaled(
            32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.tray_icon.setIcon(QIcon(tray_pixmap))
        self.tray_icon.setToolTip('桌面宠物')

        tray_menu = QMenu()

        self.action_toggle = QAction('显示宠物', self)
        self.action_toggle.triggered.connect(self.toggle_visible)
        tray_menu.addAction(self.action_toggle)

        tray_menu.addSeparator()

        self.action_walk = QAction('停止行走', self)
        self.action_walk.triggered.connect(self.toggle_walk)
        tray_menu.addAction(self.action_walk)

        action_jump = QAction('让它跳一下', self)
        action_jump.triggered.connect(self.start_jump)
        tray_menu.addAction(action_jump)

        tray_menu.addSeparator()

        menu_appearance = tray_menu.addMenu('切换形象')
        action_stand = QAction('站立', self)
        action_stand.triggered.connect(lambda: self.change_appearance('stand'))
        menu_appearance.addAction(action_stand)

        action_sit = QAction('坐姿', self)
        action_sit.triggered.connect(lambda: self.change_appearance('sit'))
        menu_appearance.addAction(action_sit)

        action_lie = QAction('趴着', self)
        action_lie.triggered.connect(lambda: self.change_appearance('lie'))
        menu_appearance.addAction(action_lie)

        tray_menu.addSeparator()

        action_quit = QAction('退出', self)
        action_quit.triggered.connect(self.quit_app)
        tray_menu.addAction(action_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visible()

    def toggle_visible(self):
        if self.isVisible():
            self.hide()
            self.action_toggle.setText('显示宠物')
        else:
            self.show()
            self.action_toggle.setText('隐藏宠物')

    def toggle_walk(self):
        self.is_walking = not self.is_walking
        self.action_walk.setText('停止行走' if self.is_walking else '开始行走')

    def change_appearance(self, mode):
        if mode == 'stand':
            self.current_image = self.image_stand
        elif mode == 'sit':
            self.current_image = self.image_sit
        elif mode == 'lie':
            self.current_image = self.image_lie
        self.update_pet_display()

    def update_pet_display(self):
        if self.current_image.isNull():
            return
        scaled = self.current_image.scaled(
            self.pet_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.pet_label.setPixmap(scaled)
        self.pet_label.move(0, 0)

    def update_walk(self):
        if not self.is_walking or self.is_jumping or self.is_dragging:
            return

        if random.random() < 0.01:
            self.walk_direction *= -1

        new_x = self.x() + self.walk_speed * self.walk_direction

        screen = QApplication.primaryScreen().geometry()
        if new_x <= 0:
            new_x = 0
            self.walk_direction = 1
        elif new_x + self.width() >= screen.width():
            new_x = screen.width() - self.width()
            self.walk_direction = -1

        self.move(new_x, self.y())

        if self.walk_direction < 0:
            transform = QTransform()
            transform.scale(-1, 1)
            scaled = self.current_image.scaled(
                self.pet_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ).transformed(transform)
            self.pet_label.setPixmap(scaled)
        else:
            self.update_pet_display()
        self.pet_label.move(0, 0)

    def update_breath(self):
        if self.is_walking or self.is_jumping or self.is_dragging:
            return
        
        self.breath_scale += 0.003 * self.breath_dir
        if self.breath_scale > 1.03:
            self.breath_dir = -1
        elif self.breath_scale < 0.97:
            self.breath_dir = 1

        scaled_size = QSize(
            self.pet_size.width(),
            int(self.pet_size.height() * self.breath_scale)
        )
        scaled = self.current_image.scaled(
            scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.pet_label.setPixmap(scaled)
        self.pet_label.move(0, (self.height() - scaled.height()) // 2)

    def start_jump(self):
        if self.is_jumping:
            return
        self.is_jumping = True
        self.jump_velocity = -12
        self.jump_height = 0
        self._base_y = self.y()
        self.jump_timer.start(20)

    def update_jump(self):
        gravity = 0.8
        self.jump_velocity += gravity
        self.jump_height += self.jump_velocity

        if self.jump_height >= 0:
            self.jump_height = 0
            self.is_jumping = False
            self.jump_timer.stop()
            self.move(self.x(), self._base_y)
            return

        self.move(self.x(), self._base_y + int(self.jump_height))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.transparent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_jump()
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        toggle_action = QAction('隐藏' if self.isVisible() else '显示', self)
        toggle_action.triggered.connect(self.toggle_visible)
        menu.addAction(toggle_action)

        walk_action = QAction('停止行走' if self.is_walking else '开始行走', self)
        walk_action.triggered.connect(self.toggle_walk)
        menu.addAction(walk_action)

        jump_action = QAction('跳一下', self)
        jump_action.triggered.connect(self.start_jump)
        menu.addAction(jump_action)

        menu.addSeparator()

        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        menu.exec_(event.globalPos())

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet = PetWindow()
    pet.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
