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

init_new_draw_document.__doc__ = "Initialize a new LibreOffice Draw document."
draw_erd_entity.__doc__ = "Draw an ERD entity table shape with its name, attributes, coordinates, and dimensions."
connect_entities.__doc__ = "Connect two entities using a connector shape with a specified cardinality."
save_as_odg.__doc__ = "Save the drawing canvas as a native LibreOffice Draw (.odg) document."

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
