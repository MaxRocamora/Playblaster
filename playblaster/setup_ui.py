from PySide6 import QtCore, QtGui, QtWidgets


def build_main_window(parent=None):
    # QMainWindow
    main_window = QtWidgets.QMainWindow(parent)
    main_window.setObjectName("main_window")
    main_window.setWindowTitle("Animation Playblaster")
    main_window.setFixedSize(420, 400)
    font = QtGui.QFont("Segoe UI", 8)
    main_window.setFont(font)

    # Central widget
    central_widget = QtWidgets.QWidget(main_window)
    central_widget.setObjectName("centralwidget")
    main_window.setCentralWidget(central_widget)

    # --- Log Layout (bottom) ---
    log_layout_widget = QtWidgets.QWidget(central_widget)
    log_layout_widget.setGeometry(QtCore.QRect(10, 220, 401, 161))
    log_layout_widget.setFont(font)
    log_layout_widget.setObjectName("verticalLayoutWidget")
    log_layout = QtWidgets.QVBoxLayout(log_layout_widget)
    log_layout.setObjectName("log_layout")
    log_layout.setContentsMargins(0, 0, 0, 0)

    # --- Options GroupBox (top) ---
    group_box = QtWidgets.QGroupBox("Options", central_widget)
    group_box.setGeometry(QtCore.QRect(10, 10, 401, 201))
    group_box.setFont(font)
    group_box.setObjectName("groupBox_options")

    # FPS Label
    lbl_fps = QtWidgets.QLabel(group_box)
    lbl_fps.setGeometry(QtCore.QRect(10, 168, 121, 20))
    lbl_fps.setFont(font)
    lbl_fps.setObjectName("lbl_fps")
    lbl_fps.setText("FPS: 24")

    # Browse Button (QPushButton)
    btn_browse = QtWidgets.QPushButton(group_box)
    btn_browse.setGeometry(QtCore.QRect(311, 160, 81, 32))
    btn_browse.setFont(font)
    btn_browse.setObjectName("btn_browse")
    btn_browse.setText("Folder")

    # Publish Button (QPushButton)
    btn_publish = QtWidgets.QPushButton(group_box)
    btn_publish.setGeometry(QtCore.QRect(135, 160, 130, 31))
    btn_publish.setFont(QtGui.QFont("Segoe UI", 8, QtGui.QFont.Bold))
    btn_publish.setObjectName("btn_publish")
    btn_publish.setText(" PLAYBLAST")

    # Horizontal Line
    line = QtWidgets.QFrame(group_box)
    line.setGeometry(QtCore.QRect(10, 140, 381, 21))
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    line.setObjectName("line")

    # Options Layout (QGridLayout)
    grid_layout_widget = QtWidgets.QWidget(group_box)
    grid_layout_widget.setGeometry(QtCore.QRect(10, 20, 381, 121))
    grid_layout_widget.setObjectName("gridLayoutWidget")
    options_lyt = QtWidgets.QGridLayout(grid_layout_widget)
    options_lyt.setObjectName("options_lyt")
    options_lyt.setContentsMargins(0, 0, 0, 0)

    # Expose key widgets/layouts as explicit attributes used by main.py
    main_window.btn_browse = btn_browse
    main_window.btn_publish = btn_publish
    main_window.options_lyt = options_lyt
    main_window.log_layout = log_layout
    main_window.lbl_fps = lbl_fps

    return main_window
