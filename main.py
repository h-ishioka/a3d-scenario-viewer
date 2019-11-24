import sys
from PIL.ImageQt import ImageQt
from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QScrollArea, QGridLayout

from a3d_class import *


class Window(QScrollArea):
    def __init__(self, filenames):
        super(Window, self).__init__()
        self.row = 0
        widget = QWidget()
        self.layout = QGridLayout(widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.populate(filenames)
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.show()

    def append_row(self, name, value):
        label1 = QLabel(name)
        self.layout.addWidget(label1, self.row, 0)
        if type(value) == str:
            label2 = QLabel(value)
            self.layout.addWidget(label2, self.row, 1)
        elif type(value) == Image.Image:
            label2 = QLabel("")
            image_qt = ImageQt(value)
            pixmap = QPixmap.fromImage(image_qt)
            pixmap.detach()
            # https://stackoverflow.com/questions/35204123/python-pyqt-pixmap-update-crashes
            label2.setPixmap(pixmap)
            self.layout.addWidget(label2, self.row, 1)
        else:
            raise ValueError()
        self.row += 1

    def populate(self, filenames):
        pages = []
        for filename in filenames:
            print('loading: %s' % filename)
            page = ScenarioPage.open(filename)
            pages.append(page)

        print('processing...')
        scenario = Scenario.frompages(*pages)

        author = str(scenario.body.author)
        title = str(scenario.header.title)
        filename = f"{author}_{title}.dat"
        with open(filename, mode="wb") as f:
            f.write(scenario.body)

        self.append_row("作者名", str(scenario.body.author))
        self.append_row("シナリオ名", str(scenario.header.title))
        self.append_row("シナリオ説明文", str(scenario.header.description))

        # height map
        height_map_im = scenario.body.height_map.to_image()
        self.append_row("Height map", height_map_im)

        # building?
        building_map_im = scenario.body.building_map.to_image()
        self.append_row("Building map?", building_map_im)

        # layers?
        for i in range(len(scenario.body.layers)):
            name = "Layer " + str(i).zfill(2)
            layer_im = scenario.body.layers[i].to_image()
            self.append_row(name, layer_im)

        # area name
        for i in range(len(scenario.body.areas)):
            name = "地名 " + str(i).zfill(2)
            area = scenario.body.areas[i]
            self.append_row(name, str(area.name))

        # scene
        for i in range(40):
            for j in range(50):
                mes_struct = scenario.body.messages[i][j]
                data = mes_struct.data
                if len(data) > 0 and data[0] != ord('%'):
                    mes = str(mes_struct)
                    self.append_row("シーン %02d, %02d" % (i+1, j), mes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window(sys.argv[1:])
    sys.exit(app.exec_())
