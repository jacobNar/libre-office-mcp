from fastmcp import FastMCP
from libreoffice_client import LibreOfficeDrawClient

mcp = FastMCP("libreoffice_draw_erd")
client = LibreOfficeDrawClient()

def get_uno_context():
    return client.get_uno_context()

@mcp.tool()
def init_new_draw_document():
    client.init_new_draw_document()
    return "New Draw document initialized."

@mcp.tool()
def draw_erd_entity(name: str, attributes: list[str], x: int, y: int, width: int = 4000, height: int = 3000):
    client.draw_erd_entity(name, attributes, x, y, width, height)
    return f"ERD entity '{name}' drawn."

@mcp.tool()
def connect_entities(from_entity_name: str, to_entity_name: str, cardinality: str):
    res = client.connect_entities(from_entity_name, to_entity_name, cardinality)
    if isinstance(res, str) and res.startswith("Error"):
        return res
    return f"Connected '{from_entity_name}' to '{to_entity_name}' with cardinality '{cardinality}'."

@mcp.tool()
def save_as_odg(output_filename: str):
    client.save_as_odg(output_filename)
    return f"Saved to '{output_filename}'."

@mcp.tool()
def set_page_size(width_mm: int, height_mm: int):
    client.set_page_size(width_mm * 100, height_mm * 100)
    return f"Page size set to {width_mm}mm x {height_mm}mm."

init_new_draw_document.__doc__ = "Initialize a new LibreOffice Draw document."
draw_erd_entity.__doc__ = "Draw an ERD entity table shape. Coordinates (x, y) and dimensions (width, height) are in 1/100ths of a mm (e.g. x=5000, y=8000, width=4000, height=3000). Values < 1000 will be auto-scaled by 100."
connect_entities.__doc__ = "Connect two entities using a connector shape. Possible cardinality values include: '1:1' (one-to-one), '1:N' or '1:M' (one-to-many), 'N:1' or 'M:1' (many-to-one), and 'M:N' (many-to-many), which determine arrowheads and line labels."
save_as_odg.__doc__ = "Save the drawing canvas as a native LibreOffice Draw (.odg) document."
set_page_size.__doc__ = "Set the drawing page dimensions in millimeters (e.g., width_mm=420, height_mm=297 for A3 landscape)."

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
