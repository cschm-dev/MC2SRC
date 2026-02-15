"""Treppen-Geometrie"""

from pyvmf import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def create_straight_stairs(solids, x, y, z, facing, half):
    """Erstellt eine gerade Treppe"""
    sg = SolidGenerator()
    h = BLOCK_SIZE / 2
    if half == "top":
        # Platform at the top
        platform_z = z + h
        solids.append(sg.cube(Vertex(x, y, platform_z), BLOCK_SIZE, BLOCK_SIZE, h))
        # Step below the platform
        if facing == "north":
            solids.append(sg.cube(Vertex(x, y, z), BLOCK_SIZE, h, h))
        elif facing == "south":
            solids.append(sg.cube(Vertex(x, y + h, z), BLOCK_SIZE, h, h))
        elif facing == "east":
            solids.append(sg.cube(Vertex(x + h, y, z), h, BLOCK_SIZE, h))
        elif facing == "west":
            solids.append(sg.cube(Vertex(x, y, z), h, BLOCK_SIZE, h))
    else:
        base_z = z
        # Lower part
        solids.append(sg.cube(Vertex(x, y, base_z), BLOCK_SIZE, BLOCK_SIZE, h))
        # Step above the platform
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
            facing = properties["facing"]
        if "half" in properties:
            half = properties["half"]
        if "shape" in properties:
            shape = properties["shape"]
    
    if shape == "straight":
        create_straight_stairs(solids, x, y, z, facing, half)
    elif shape == "inner_left":
        sg = SolidGenerator()
        h = BLOCK_SIZE / 2
        if half == "bottom":
            create_straight_stairs(solids, x, y, z, facing, half)
            if facing == "north":
                solids.append(sg.cube(Vertex(x, y + h, z + h), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x + h, y, z + h), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x, y, z + h), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z + h), h, h, h))
        else:
            # Build upside-down straight stair using the fixed function
            create_straight_stairs(solids, x, y, z, facing, half)
            # Corner cube below the platform (z)
            h = BLOCK_SIZE / 2
            if facing == "north":
                solids.append(sg.cube(Vertex(x, y + h, z), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x + h, y, z), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x, y, z), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z), h, h, h))
    elif shape == "inner_right":
        sg = SolidGenerator()
        h = BLOCK_SIZE / 2
        if half == "bottom":
            create_straight_stairs(solids, x, y, z, facing, half)
            if facing == "north":
                solids.append(sg.cube(Vertex(x + h, y + h, z + h), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x, y, z + h), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x + h, y, z + h), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z + h), h, h, h))
        else:
            # Build upside-down straight stair using the fixed function
            create_straight_stairs(solids, x, y, z, facing, half)
            # Corner cube below the platform (z)
            h = BLOCK_SIZE / 2
            if facing == "north":
                solids.append(sg.cube(Vertex(x + h, y + h, z), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x, y, z), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x + h, y, z), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z), h, h, h))
    elif shape == "inner_right":
        # Place a straight stair in the main direction
        create_straight_stairs(solids, x, y, z, facing, half)
        # Add a small cube in the connecting corner (bottom only)
        sg = SolidGenerator()
        h = BLOCK_SIZE / 2
        if half == "bottom":
            if facing == "north":
                solids.append(sg.cube(Vertex(x + h, y + h, z + h), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x, y, z + h), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x + h, y, z + h), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z + h), h, h, h))
        # For 'top' (upside-down), place the corner cube at the upper half
        else:
            if facing == "north":
                solids.append(sg.cube(Vertex(x + h, y + h, z), h, h, h))
            elif facing == "south":
                solids.append(sg.cube(Vertex(x, y, z), h, h, h))
            elif facing == "east":
                solids.append(sg.cube(Vertex(x + h, y, z), h, h, h))
            elif facing == "west":
                solids.append(sg.cube(Vertex(x, y + h, z), h, h, h))
            # Move the cube up by h
            for cube in solids[-1:]:
                cube.move(0, 0, h)
    else:
        # Fallback für komplexe Formen
        sg = SolidGenerator()
        solids.append(sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))