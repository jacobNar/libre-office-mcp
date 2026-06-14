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
        self.set_page_size(42000, 29700)
        return self.document

    def set_page_size(self, width: int, height: int):
        doc = self.get_active_document()
        page_styles = doc.getStyleFamilies().getByName("PageStyles")
        for name in page_styles.getElementNames():
            style = page_styles.getByName(name)
            try:
                style.setPropertyValue("Width", width)
                style.setPropertyValue("Height", height)
                style.setPropertyValue("IsLandscape", True)
            except Exception:
                pass

    def get_active_document(self):
        if self.document is None:
            self.get_uno_context()
            self.document = self.desktop.getCurrentComponent()
        return self.document

    def draw_erd_entity(self, name: str, attributes: list[str], x: int, y: int, width: int = 4000, height: int = 3000):
        if x < 1000:
            x = x * 100
        if y < 1000:
            y = y * 100
        if width < 1000:
            width = width * 100
        if height < 1000:
            height = height * 100
        width = max(width, 3500)
        height = max(height, 2000)
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
        target = f"[{name.strip().lower()}]"
        for i in range(draw_page.getCount()):
            shape = draw_page.getByIndex(i)
            if hasattr(shape, "String"):
                lines = shape.String.split("\n")
                if lines and lines[0].strip().lower() == target:
                    return shape
        return None

    def connect_entities(self, from_entity_name: str, to_entity_name: str, cardinality: str):
        doc = self.get_active_document()
        draw_page = doc.getDrawPages().getByIndex(0)
        from_shape = self.find_shape_by_entity_name(from_entity_name)
        to_shape = self.find_shape_by_entity_name(to_entity_name)
        if from_shape is None or to_shape is None:
            missing = []
            if from_shape is None:
                missing.append(from_entity_name)
            if to_shape is None:
                missing.append(to_entity_name)
            return f"Error: Start or End shape not found for: {', '.join(missing)}. Please draw them first."
        connector = doc.createInstance("com.sun.star.drawing.ConnectorShape")
        draw_page.add(connector)
        connector.StartShape = from_shape
        connector.EndShape = to_shape
        card = cardinality.strip().lower()
        if "many-to-many" in card or "many to many" in card or "m:n" in card or "m-n" in card:
            connector.setPropertyValue("LineStartName", "Arrow")
            connector.setPropertyValue("LineEndName", "Arrow")
            connector.String = "M:N"
        elif "one-to-many" in card or "one to many" in card or "1:n" in card or "1:m" in card or "1-n" in card:
            connector.setPropertyValue("LineEndName", "Arrow")
            connector.String = "1:N"
        elif "many-to-one" in card or "many to one" in card or "n:1" in card or "m:1" in card or "n-1" in card:
            connector.setPropertyValue("LineStartName", "Arrow")
            connector.String = "N:1"
        elif "one-to-one" in card or "one to one" in card or "1:1" in card or "1-1" in card:
            connector.String = "1:1"
        else:
            connector.String = cardinality
        return connector

    def save_as_odg(self, output_filename: str):
        import uno
        import os
        base, _ = os.path.splitext(output_filename)
        output_filename = base + ".odg"
        doc = self.get_active_document()
        output_url = uno.systemPathToFileUrl(output_filename)
        doc.storeToURL(output_url, ())
