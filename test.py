import sys

# import PyQt5.QtCore
import numpy as np
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
import nibabel as nib


class MyObject(QObject):
    valueChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._value = 100

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.valueChanged.emit(new_value)

def piecewise_linear_transform(image, breakpoints=[100.200], slopes=[0.5,1.0,0.5]):
    transformed_image = np.zeros_like(image)
    for i in range(len(breakpoints)):
        lower_bound = breakpoints[i - 1] if i > 0 else 0
        upper_bound = breakpoints[i]
        mask = (image >= lower_bound) & (image < upper_bound)
        transformed_image[mask] = slopes[i] * (image[mask] - lower_bound)
    mask = image >= breakpoints[-1]
    transformed_image[mask] = slopes[-1] * (image[mask] - breakpoints[-1])
    return transformed_image

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.nii_label = None
        self.nii_pred = None
        self.nii_img = None
        self.monitorIndex = MyObject()
        self.monitorIndex.valueChanged.connect(self.handle_change_img)
        self.index = QLabel(str(self.monitorIndex.value))
        self.setWindowTitle(u'medical slicer')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建工具栏
        toolbar = QToolBar("toolbar")
        self.addToolBar(toolbar)
        # 创建“工具”下拉菜单
        tools_menu = QMenu("file", self)
        open_action = QAction("open nii.gz file", self)
        load_model= QAction("load model",self)
        export_action = QAction("export output", self)
        tools_menu.addAction(open_action)
        tools_menu.addAction(load_model)
        tools_menu.addAction(export_action)
        # 创建“三维重建”下拉菜单
        reconstruction_menu = QMenu("3D-reconstruction", self)
        reconstruct_action = QAction("reconstruction", self)
        reconstruction_menu.addAction(reconstruct_action)
        # 创建工具栏按钮，并将下拉菜单设置为该动作的弹出菜单
        tools_action = QAction("file", self)
        tools_action.setMenu(tools_menu)
        reconstruction_action = QAction("3D-reconstruction", self)
        reconstruction_action.setMenu(reconstruction_menu)
        # 将动作添加到工具栏
        toolbar.addAction(tools_action)
        toolbar.addAction(reconstruction_action)
        # 连接动作的信号槽（这里只是简单地打印信息）
        open_action.triggered.connect(self.open_img_file)
        export_action.triggered.connect(lambda: print("导出文件"))
        load_model.triggered.connect(self.open_model_file)
        reconstruct_action.triggered.connect(lambda: print("重建被点击"))

        main_layout = QHBoxLayout()

        # 创建左侧窗口
        left_layout = QVBoxLayout()
        self.img_box = QLabel()
        self.img_box.setFixedSize(480, 480)
        img_text = QLabel("img")
        left_layout.addWidget(img_text)
        left_layout.addWidget(self.img_box)

        # 创建中间窗口
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        self.label_box = QLabel()
        center_layout.addWidget(QLabel("gt"))
        center_layout.addWidget(self.label_box)
        # center_layout.addWidget(QLabel("中间窗口"))
        self.buttonGt = QPushButton(u'open label file')
        self.buttonGt.clicked.connect(self.open_label_file)
        center_layout.addWidget(self.buttonGt)
        center_widget.setLayout(center_layout)

        # 创建右侧窗口
        right_layout = QVBoxLayout()
        self.pred_box = QLabel()
        self.pred_box.setFixedSize(480, 480)
        right_layout.addWidget(QLabel("prediction"))
        right_layout.addWidget(self.pred_box)

        tool_layout = QVBoxLayout()
        self.buttonP = QPushButton('segment')
        self.buttonP.clicked.connect(self.open_pred_file)
        tool_layout.addWidget(self.buttonP)
        tool_layout.setAlignment(self.buttonP, Qt.AlignTop)

        # 将窗口添加到分割器中
        main_layout.addLayout(tool_layout)
        main_layout.addLayout(left_layout)
        # main_layout.addWidget(center_widget)
        main_layout.addLayout(right_layout)

        central_widget.setLayout(main_layout)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.before_index()
        else:
            self.next_index()

    def handle_change_img(self):
        img = self.nii_img[:, :, self.monitorIndex.value].copy()
        # label=self.nii_label[:,:,self.monitorIndex.value].copy()
        pred = self.nii_pred[:, :, self.monitorIndex.value].copy()
        self.index.setText(str(self.monitorIndex.value))

        q_image = QImage(img, img.shape[0], img.shape[1], QImage.Format_Indexed8)
        image_pixmap = QPixmap.fromImage(q_image)

        # q_label = QImage(label, img.shape[0], img.shape[1], QImage.Format_Indexed8)
        # label_pixmap = QPixmap.fromImage(q_label)

        q_pred = QImage(pred, img.shape[0], img.shape[1], QImage.Format_Indexed8)
        pred_pixmap = QPixmap.fromImage(q_pred)
        self.img_box.setPixmap(image_pixmap)
        # self.label_box.setPixmap(label_pixmap)
        self.pred_box.setPixmap(pred_pixmap)

    def next_index(self):
        # todo 边界检测
        self.monitorIndex.value = self.monitorIndex.value + 1

    def before_index(self):
        # todo 边界检测
        if self.monitorIndex.value > 0:
            self.monitorIndex.value = self.monitorIndex.value - 1

    def open_model_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "open model file", "", "model files (*.pth)")


    def open_img_file(self):
        # 打开文件对话框
        file_name, _ = QFileDialog.getOpenFileName(self, "open img.nii.gz file", "", "NIfTI files (*.nii *.nii.gz)")
        img = nib.load(file_name)
        if file_name:
            # 读取.nii.gz文件
            data = img.get_fdata()
            data = data.astype(np.uint8)
            data = np.rot90(data, -1)
            self.nii_img = data

            # transformed_images = np.zeros_like(data)
            # for i in range(300):
            #     transformed_images[:, :, i] = piecewise_linear_transform(
            #         data[:, :, i]
            #     )
            # # 确保变换后的像素值在0-255的范围内
            # data = np.clip(transformed_images, 0, 255).astype(np.uint8)

            print(data.shape)

            index = self.monitorIndex.value
            image = data[:, :, index].copy()

            # image=np.rot90(image,-1).copy()
            q_image = QImage(image, image.shape[0], image.shape[1], QImage.Format_Indexed8)

            # 在图像显示区域显示图像
            pixmap = QPixmap.fromImage(q_image)
            self.img_box.setPixmap(pixmap)
            self.img_box.setScaledContents(True)

    def open_label_file(self):
        # 打开文件对话框
        file_name, _ = QFileDialog.getOpenFileName(self, "open gt.nii.gz file", "", "NIfTI files (*.nii *.nii.gz)")
        img = nib.load(file_name)
        if file_name:
            # 读取.nii.gz文件
            data = img.get_fdata()
            data = np.round((data - 0) * ((255 - 0) / (6 - 0)) + 0).astype(np.uint8)
            self.nii_label = data

            index = self.monitorIndex.value
            image = data[:, :, index].copy()
            q_image = QImage(image, image.shape[0], image.shape[1], QImage.Format_Indexed8)

            # 在图像显示区域显示图像
            pixmap = QPixmap.fromImage(q_image)
            self.label_box.setPixmap(pixmap)

    def open_pred_file(self):
        # 打开文件对话框
        file_name, _ = QFileDialog.getOpenFileName(self, "open pred.nii.gz file", "", "NIfTI files (*.nii *.nii.gz)")
        img = nib.load(file_name)
        if file_name:
            # 读取.nii.gz文件
            data = img.get_fdata()
            data = np.round((data - 0) * ((255 - 0) / (6 - 0)) + 0).astype(np.uint8)
            data = np.rot90(data, -1)
            self.nii_pred = data

            index = self.monitorIndex.value
            image = data[:, :, index].copy()
            # image = np.rot90(image, -1).copy()
            q_image = QImage(image, image.shape[0], image.shape[1], QImage.Format_Indexed8)

            # 在图像显示区域显示图像
            pixmap = QPixmap.fromImage(q_image)
            self.pred_box.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.setGeometry(0, 0, 800, 600)
    # window.resize(1600,800)
    window.show()
    sys.exit(app.exec_())
