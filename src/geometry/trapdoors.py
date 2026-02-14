"""Falltüren-Geometrie"""

from PyVMF import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def create_trapdoor(solids, x, y, z, properties):
    """
    Erstellt Trapdoor-Geometrie
    
    Args:
        solids: Liste zum Hinzufügen der Solid-Objekte
        x, y, z: Position in Hammer Units
        properties: Block-Properties (facing, half, open)
    """
    sg = SolidGenerator()
    
    facing = "north"
    half = "bottom"
    is_open = False
    
    if properties:
        if "facing" in properties:
            facing = properties["facing"].py_str
        if "half" in properties:
            half = properties["half"].py_str
        if "open" in properties:
            is_open = properties["open"].py_str == "true"
    
    trapdoor_thickness = BLOCK_SIZE / 6
    
    if not is_open:
        # Geschlossen - horizontal
        if half == "top":
            solids.append(
                sg.cube(Vertex(x, y, z + BLOCK_SIZE - trapdoor_thickness), 
                        BLOCK_SIZE, BLOCK_SIZE, trapdoor_thickness)
            )
        else:
            solids.append(
                sg.cube(Vertex(x, y, z), 
                        BLOCK_SIZE, BLOCK_SIZE, trapdoor_thickness)
            )
    else:
        # Geöffnet - vertikal
        if facing == "north":
            solids.append(
                sg.cube(Vertex(x, y, z), 
                        BLOCK_SIZE, trapdoor_thickness, BLOCK_SIZE)
            )
        elif facing == "south":
            solids.append(
                sg.cube(Vertex(x, y + BLOCK_SIZE - trapdoor_thickness, z), 
                        BLOCK_SIZE, trapdoor_thickness, BLOCK_SIZE)
            )
        elif facing == "east":
            solids.append(
                sg.cube(Vertex(x + BLOCK_SIZE - trapdoor_thickness, y, z), 
                        trapdoor_thickness, BLOCK_SIZE, BLOCK_SIZE)
            )
        elif facing == "west":
            solids.append(
                sg.cube(Vertex(x, y, z), 
                        trapdoor_thickness, BLOCK_SIZE, BLOCK_SIZE)
            )