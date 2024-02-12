import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("左右垂直布局示例")


        # 创建一个中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建一个水平布局
        main_layout = QHBoxLayout()

        # 创建左边的垂直布局
        left_layout = QVBoxLayout()

        # 创建左边的标签
        left_label1 = QLabel("左边标签 1")
        left_label2 = QLabel("左边标签 2")
        left_label3 = QLabel("左边标签 3")

        # 将左边的标签添加到左边的垂直布局中
        left_layout.addWidget(left_label1)
        left_layout.addWidget(left_label2)
        left_layout.addWidget(left_label3)

        # 创建右边的垂直布局
        right_layout = QVBoxLayout()

        # 创建右边的标签
        right_label1 = QLabel("右边标签 1")
        right_label2 = QLabel("右边标签 2")
        right_label3 = QLabel("右边标签 3")

        # 将右边的标签添加到右边的垂直布局中
        right_layout.addWidget(right_label1)
        right_layout.addWidget(right_label2)
        right_layout.addWidget(right_label3)

        # 将左右两个垂直布局添加到水平布局中
        main_layout.addLayout(left_layout)
        # main_layout.addLayout(right_layout)

        # 设置布局的边距，如果需要的话
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 设置布局的间距，如果需要的话
        main_layout.setSpacing(10)

        # 将布局设置到中央小部件
        central_widget.setLayout(main_layout)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
