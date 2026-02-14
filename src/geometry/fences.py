"""Zaun-Geometrie"""

from PyVMF import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def get_fence_connections(block_x, block_y, block_z, blocks_dict):
    """
    Prüft Zaun-Verbindungen zu Nachbarblöcken
    
    Args:
        block_x, block_y, block_z: Position des Zauns
        blocks_dict: Dictionary aller Blöcke {(x,y,z): (x,y,z,type,faces,props)}
    
    Returns:
        Dict mit Verbindungen {'north': bool, 'south': bool, 'east': bool, 'west': bool}
    """
    connections = {'north': False, 'south': False, 'east': False, 'west': False}
    neighbors = [
        (block_x, block_y, block_z - 1, 'north'),
        (block_x, block_y, block_z + 1, 'south'),
        (block_x + 1, block_y, block_z, 'east'),
        (block_x - 1, block_y, block_z, 'west')
    ]
    
    for nx, ny, nz, direction in neighbors:
        if (nx, ny, nz) in blocks_dict:
            neighbor_type = blocks_dict[(nx, ny, nz)][3]
            # Verbinde mit anderen Zäunen oder soliden Blöcken
            if '_fence' in neighbor_type or (neighbor_type not in ["air", "cave_air", "void_air", "water", "lava"]):
                connections[direction] = True
    
    return connections

def create_fence(solids, x, y, z, connections):
    """
    Erstellt Zaun-Geometrie mit Verbindungen
    """
    sg = SolidGenerator()

    post_width = BLOCK_SIZE / 4
    post_height = BLOCK_SIZE * 1.5

    rail_width = BLOCK_SIZE / 8
    rail_offset_bottom = BLOCK_SIZE * 0.375
    rail_offset_top = BLOCK_SIZE * 0.9375

    # Leichte Überlappung der Rails in den Pfosten
    overlap = rail_width / 2

    # Zentraler Pfosten
    center_x = x + (BLOCK_SIZE - post_width) / 2
    center_y = y + (BLOCK_SIZE - post_width) / 2

    solids.append(
        sg.cube(
            Vertex(center_x, center_y, z),
            post_width,
            post_width,
            post_height
        )
    )

    # NORD
    if connections.get('north'):
        rail_start_y = y
        rail_end_y = center_y + overlap
        rail_length = rail_end_y - rail_start_y

        solids.append(
            sg.cube(
                Vertex(center_x + (post_width - rail_width) / 2, rail_start_y, z + rail_offset_bottom),
                rail_width,
                rail_length,
                rail_width
            )
        )
        solids.append(
            sg.cube(
                Vertex(center_x + (post_width - rail_width) / 2, rail_start_y, z + rail_offset_top),
                rail_width,
                rail_length,
                rail_width
            )
        )

    # SÜD
    if connections.get('south'):
        rail_start_y = center_y + post_width - overlap
        rail_end_y = y + BLOCK_SIZE
        rail_length = rail_end_y - rail_start_y

        solids.append(
            sg.cube(
                Vertex(center_x + (post_width - rail_width) / 2, rail_start_y, z + rail_offset_bottom),
                rail_width,
                rail_length,
                rail_width
            )
        )
        solids.append(
            sg.cube(
                Vertex(center_x + (post_width - rail_width) / 2, rail_start_y, z + rail_offset_top),
                rail_width,
                rail_length,
                rail_width
            )
        )

    # OST
    if connections.get('east'):
        rail_start_x = center_x + post_width - overlap
        rail_end_x = x + BLOCK_SIZE
        rail_length = rail_end_x - rail_start_x

        solids.append(
            sg.cube(
                Vertex(rail_start_x, center_y + (post_width - rail_width) / 2, z + rail_offset_bottom),
                rail_length,
                rail_width,
                rail_width
            )
        )
        solids.append(
            sg.cube(
                Vertex(rail_start_x, center_y + (post_width - rail_width) / 2, z + rail_offset_top),
                rail_length,
                rail_width,
                rail_width
            )
        )

    # WEST
    if connections.get('west'):
        rail_start_x = x
        rail_end_x = center_x + overlap
        rail_length = rail_end_x - rail_start_x

        solids.append(
            sg.cube(
                Vertex(rail_start_x, center_y + (post_width - rail_width) / 2, z + rail_offset_bottom),
                rail_length,
                rail_width,
                rail_width
            )
        )
        solids.append(
            sg.cube(
                Vertex(rail_start_x, center_y + (post_width - rail_width) / 2, z + rail_offset_top),
                rail_length,
                rail_width,
                rail_width
            )
        )
