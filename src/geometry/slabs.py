"""Platten-Geometrie"""

from PyVMF import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def create_slab(x, y, z, properties):
    """Erstellt eine Platte (Slab)"""
    sg = SolidGenerator()
    slab_type = "bottom"
    
    if properties and "type" in properties:
        slab_type = properties["type"].py_str
    
    if slab_type == "double":
        solid = sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    elif slab_type == "top":
        solid = sg.cube(Vertex(x, y, z + BLOCK_SIZE / 2), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE / 2)
    else:
        # Default: bottom slab
        solid = sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE / 2)
    
    if solid is None:
        raise ValueError(f"Failed to create slab solid at ({x}, {y}, {z}) with type {slab_type}")
    return solid
def create_carpet(x, y, z, properties):
    """Erstellt einen Teppich (Carpet) - 4 Units hoch"""
    sg = SolidGenerator()
    # Carpet ist 1 Pixel hoch in Minecraft, also 4 Units in Hammer
    # Verwende eine Mindesthöhe von 4 Units
    carpet_height = 4  # Feste 4 Units Höhe
    solid = sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, carpet_height)
    if solid is None:
        # Fallback: Erstelle einen minimalen Block und skaliere später
        solid = sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, 1)
        if solid is None:
            raise ValueError(f"Failed to create carpet solid at ({x}, {y}, {z})")
    return solid