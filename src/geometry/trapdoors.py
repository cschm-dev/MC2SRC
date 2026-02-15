"""Falltüren-Geometrie"""

from pyvmf import SolidGenerator, Vertex
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
            facing = properties["facing"]
        if "half" in properties:
            half = properties["half"]
        if "open" in properties:
            is_open = properties["open"] == "true"
    
    trapdoor_thickness = BLOCK_SIZE / 6
    
    if not is_open:
        # Closed - horizontal
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
        # Open - vertical, attached to the correct (opposite) side
        if facing == "north":
            # attached to south (y + BLOCK_SIZE - thickness)
            solids.append(
                sg.cube(Vertex(x, y + BLOCK_SIZE - trapdoor_thickness, z),
                        BLOCK_SIZE, trapdoor_thickness, BLOCK_SIZE)
            )
        elif facing == "south":
            # attached to north (y)
            solids.append(
                sg.cube(Vertex(x, y, z),
                        BLOCK_SIZE, trapdoor_thickness, BLOCK_SIZE)
            )
        elif facing == "west":
            # attached to east (x + BLOCK_SIZE - thickness)
            solids.append(
                sg.cube(Vertex(x + BLOCK_SIZE - trapdoor_thickness, y, z),
                        trapdoor_thickness, BLOCK_SIZE, BLOCK_SIZE)
            )
        elif facing == "east":
            # attached to west (x)
            solids.append(
                sg.cube(Vertex(x, y, z),
                        trapdoor_thickness, BLOCK_SIZE, BLOCK_SIZE)
            )