"""Iron Bars / Glass Pane Geometrie"""

from PyVMF import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def get_bars_connections(block_x, block_y, block_z, blocks_dict):
    """
    Prüft Iron Bars / Glass Pane Verbindungen
    
    Args:
        block_x, block_y, block_z: Position der Bars
        blocks_dict: Dictionary aller Blöcke
    
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
            # Verbinde mit anderen Bars/Panes oder soliden Blöcken
            if ('bars' in neighbor_type or 'pane' in neighbor_type or 
                neighbor_type not in ["air", "cave_air", "void_air", "water", "lava"]):
                connections[direction] = True
    
    return connections


def create_iron_bars(solids, x, y, z, connections):
    """
    Erstellt Iron Bars / Glass Pane Geometrie
    
    Args:
        solids: Liste zum Hinzufügen der Solid-Objekte
        x, y, z: Position in Hammer Units
        connections: Dict mit Verbindungsrichtungen
    """
    sg = SolidGenerator()
    
    bar_width = BLOCK_SIZE / 8
    bar_height = BLOCK_SIZE
    
    center_x = x + (BLOCK_SIZE - bar_width) / 2
    center_y = y + (BLOCK_SIZE - bar_width) / 2
    
    # Prüfe ob es Verbindungen gibt
    has_connections = any(connections.values())
    
    if has_connections:
        # Mit Verbindungen: Zentraler Pfosten + Verbindungen
        solids.append(
            sg.cube(Vertex(center_x, center_y, z), bar_width, bar_width, bar_height)
        )
        
        # Nord-Verbindung
        if connections.get('north'):
            solids.append(
                sg.cube(Vertex(center_x, y, z), 
                       bar_width, center_y - y, bar_height)
            )
        
        # Süd-Verbindung
        if connections.get('south'):
            solids.append(
                sg.cube(Vertex(center_x, center_y + bar_width, z), 
                       bar_width, (y + BLOCK_SIZE) - (center_y + bar_width), bar_height)
            )
        
        # Ost-Verbindung
        if connections.get('east'):
            solids.append(
                sg.cube(Vertex(center_x + bar_width, center_y, z), 
                       (x + BLOCK_SIZE) - (center_x + bar_width), bar_width, bar_height)
            )
        
        # West-Verbindung
        if connections.get('west'):
            solids.append(
                sg.cube(Vertex(x, center_y, z), 
                       center_x - x, bar_width, bar_height)
            )
    else:
        # Keine Verbindungen: Nur ein einzelner vertikaler Stab in der Mitte
        solids.append(
            sg.cube(Vertex(center_x, center_y, z), bar_width, bar_width, bar_height)
        )