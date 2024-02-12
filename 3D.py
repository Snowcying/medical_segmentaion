import vtk
import nibabel as nib
import numpy as np

# 读取.nii.gz文件
img_path = './P00225518_gt.nii.gz'
img = nib.load(img_path)
data = img.get_fdata()
data=np.round((data - 0) * ((255 - 0) / (6 - 0)) + 0).astype(np.uint8)

# 将数据转换为VTK可接受的格式
data = np.rot90(data, k=3, axes=(0, 1))  # 调整数组方向以匹配VTK的坐标系统
data = data.astype('float32')  # 确保数据类型正确

# 创建一个VTK图像数据对象
vtk_image_data = vtk.vtkImageData()
vtk_image_data.SetDimensions(data.shape)
vtk_image_data.SetSpacing(img.header.get_zooms())  # 设置体素大小
vtk_image_data.SetOrigin([0, 0, 0])  # 设置数据原点
vtk_image_data.AllocateScalars(vtk.VTK_FLOAT, 1)  # 分配存储空间

# 将numpy数组复制到VTK图像数据中
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        for k in range(data.shape[2]):
            vtk_image_data.SetScalarComponentFromFloat(i, j, k, 0, data[i, j, k])

# 创建一个体积映射器
volume_mapper = vtk.vtkSmartVolumeMapper()
volume_mapper.SetInputData(vtk_image_data)

# 创建一个体积属性，用于设置渲染的透明度、颜色等
volume_property = vtk.vtkVolumeProperty()
volume_property.SetInterpolationTypeToLinear()
volume_property.ShadeOn()

# 创建一个颜色传输函数
color_transfer_function = vtk.vtkColorTransferFunction()
color_transfer_function.AddRGBPoint(0, 0.0, 0.0, 0.0)
color_transfer_function.AddRGBPoint(500, 1.0, 0.5, 0.3)
color_transfer_function.AddRGBPoint(1000, 1.0, 1.0, 0.9)

# 创建一个不透明度传输函数
opacity_transfer_function = vtk.vtkPiecewiseFunction()
opacity_transfer_function.AddPoint(0, 0.0)
opacity_transfer_function.AddPoint(500, 0.3)
opacity_transfer_function.AddPoint(1000, 1.0)

# 将颜色和不透明度传输函数应用到体积属性中
volume_property.SetColor(color_transfer_function)
volume_property.SetScalarOpacity(opacity_transfer_function)

# 创建一个体积
volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# 创建渲染器并添加体积
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.SetBackground(0, 0, 0)  # 设置背景颜色为黑色

# 创建窗口和交互器
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# 启动交互器
render_window.Render()
render_window_interactor.Start()
