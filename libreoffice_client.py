import os
import sys

try:
    if os.name == "nt":
        lo_path = r"C:\Program Files\LibreOffice\program"
        if os.path.exists(lo_path):
            if lo_path not in sys.path:
                sys.path.append(lo_path)
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(lo_path)
except Exception:
    pass

import uno
from com.sun.star.awt import Point, Size
from com.sun.star.beans import PropertyValue
from config import AppConfig

class LibreOfficeDrawClient:
    def __init__(self):
        self.host = AppConfig.LIBREOFFICE_HOST
        self.port = AppConfig.LIBREOFFICE_PORT
        self.context = None
        self.desktop = None
        self.document = None

    def get_uno_context(self):
        if self.context is None:
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_context
            )
            url = f"uno:socket,host={self.host},port={self.port};urp;StarOffice.ComponentContext"
            self.context = resolver.resolve(url)
            self.desktop = self.context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.context
            )
        return self.context

    def init_new_draw_document(self):
        self.get_uno_context()
        self.document = self.desktop.loadComponentFromURL(
            "private:factory/sdraw", "_blank", 0, ()
        )
        return self.document

    def get_active_document(self):
        if self.document is None:
            self.get_uno_context()
            self.document = self.desktop.getCurrentComponent()
        return self.document

    def draw_erd_entity(self, name: str, attributes: list[str], x: int, y: int, width: int = 4000, height: int = 3000):
        doc = self.get_active_document()
        draw_page = doc.getDrawPages().getByIndex(0)
        shape = doc.createInstance("com.sun.star.drawing.RectangleShape")
        shape.setPosition(Point(x, y))
        shape.setSize(Size(width, height))
        draw_page.add(shape)
        lines = [f"[{name}]", "------------------"]
        for attr in attributes:
            lines.append(f"• {attr}")
        shape.String = "\n".join(lines)
        return shape

    def find_shape_by_entity_name(self, name: str):
        doc = self.get_active_document()
        draw_page = doc.getDrawPages().getByIndex(0)
        target = f"[{name}]"
        for i in range(draw_page.getCount()):
            shape = draw_page.getByIndex(i)
            if hasattr(shape, "String"):
                lines = shape.String.split("\n")
                if lines and lines[0] == target:
                    return shape
        return None

    def connect_entities(self, from_entity_name: str, to_entity_name: str, cardinality: str):
        doc = self.get_active_document()
        draw_page = doc.getDrawPages().getByIndex(0)
        from_shape = self.find_shape_by_entity_name(from_entity_name)
        to_shape = self.find_shape_by_entity_name(to_entity_name)
        if from_shape is None or to_shape is None:
            raise ValueError("Start or End shape not found")
        connector = doc.createInstance("com.sun.star.drawing.ConnectorShape")
        draw_page.add(connector)
        connector.StartShape = from_shape
        connector.EndShape = to_shape
        if cardinality == "one-to-many":
            connector.setPropertyValue("EdgeLineEndName", "Arrow")
        return connector

    def save_and_export_vsdx(self, output_filename: str):
        doc = self.get_active_document()
        output_url = uno.systemPathToFileUrl(output_filename)
        prop = PropertyValue()
        prop.Name = "FilterName"
        prop.Value = "Visio Document"
        doc.storeToURL(output_url, (prop,))
