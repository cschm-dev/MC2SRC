"""Treppen-Geometrie"""

from PyVMF import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def create_straight_stairs(solids, x, y, z, facing, half):
    """Erstellt eine gerade Treppe"""
    sg = SolidGenerator()
    h = BLOCK_SIZE / 2
    base_z = z + h if half == "top" else z
    
    # Unterer Teil
    solids.append(sg.cube(Vertex(x, y, base_z), BLOCK_SIZE, BLOCK_SIZE, h))
    
    # Obere Stufe
    if facing == "north":
        solids.append(sg.cube(Vertex(x, y, base_z + h), BLOCK_SIZE, h, h))
    elif facing == "south":
        solids.append(sg.cube(Vertex(x, y + h, base_z + h), BLOCK_SIZE, h, h))
    elif facing == "east":
        solids.append(sg.cube(Vertex(x + h, y, base_z + h), h, BLOCK_SIZE, h))
    elif facing == "west":
        solids.append(sg.cube(Vertex(x, y, base_z + h), h, BLOCK_SIZE, h))


def create_stairs(solids, x, y, z, properties):
    """Erstellt Treppen basierend auf Properties"""
    facing = "north"
    half = "bottom"
    shape = "straight"
    
    if properties:
        if "facing" in properties:
            facing = properties["facing"].py_str
        if "half" in properties:
            half = properties["half"].py_str
        if "shape" in properties:
            shape = properties["shape"].py_str
    
    if shape == "straight":
        create_straight_stairs(solids, x, y, z, facing, half)
    else:
        # Fallback für komplexe Formen
        sg = SolidGenerator()
        solids.append(sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))