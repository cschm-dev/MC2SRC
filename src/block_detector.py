"""Block detection and face visibility detection"""

import logging
from amulet.api.errors import ChunkDoesNotExist
from .world_loader import load_level, get_full_block_name

log = logging.getLogger(__name__)


def is_air_or_transparent(block_name):
    """Check if a block is transparent or air"""
    return block_name in ["air", "cave_air", "void_air", "water", "lava"]

def is_fence_or_bars(block_name):
    return ("_fence" in block_name or "bars" in block_name or "glass_pane" in block_name)

def is_slab(block_name):
    return block_name.endswith("_slab")

def is_stairs(block_name):
    return block_name.endswith("_stairs")

def is_carpet(block_name):
    return block_name.endswith("_carpet")


def get_exposed_blocks(world_path, x1, z1, x2, z2, y_min=-64, y_max=320, 
                       dimension='minecraft:overworld', force_ns=False, force_ew=False):
    """
    Find all visible blocks in a region
    
    Args:
        world_path: Path to Minecraft world
        x1, z1, x2, z2: Region coordinates
        y_min, y_max: Height range
        dimension: Minecraft dimension
        force_ns: Force north/south faces visible
        force_ew: Force east/west faces visible
    
    Returns:
        List of (x, y, z, block_type, exposed_faces, properties)
    """
    world = load_level(world_path)
    exposed_blocks = []
    cx1, cz1, cx2, cz2 = x1 // 16, z1 // 16, x2 // 16, z2 // 16
    chunk_cache = {}

    for cx in range(min(cx1, cx2), max(cx1, cx2) + 1):
        for cz in range(min(cz1, cz2), max(cz1, cz2) + 1):
            try:
                chunk = world.get_chunk(cx, cz, dimension)
                chunk_cache[(cx, cz)] = chunk
                
                start_x = max(0, x1 - cx * 16) if cx == cx1 else 0
                end_x = min(16, x2 - cx * 16 + 1) if cx == cx2 else 16
                start_z = max(0, z1 - cz * 16) if cz == cz1 else 0
                end_z = min(16, z2 - cz * 16 + 1) if cz == cz2 else 16

                for x in range(start_x, end_x):
                    for z in range(start_z, end_z):
                        for y in range(y_max, y_min - 1, -1):
                            try:
                                block = chunk.get_block(x, y, z)
                                block_name = get_full_block_name(block)
                                
                                if is_air_or_transparent(block_name):
                                    continue
                                
                                world_x, world_z = cx * 16 + x, cz * 16 + z
                                exposed_faces = []
                                neighbors = [
                                    (0, 1, 0, "top"), (0, -1, 0, "bottom"),
                                    (1, 0, 0, "east"), (-1, 0, 0, "west"),
                                    (0, 0, 1, "south"), (0, 0, -1, "north")
                                ]
                                
                                for dx, dy, dz, face_name in neighbors:
                                    nx, ny, nz = x + dx, y + dy, z + dz
                                    neighbor_cx = cx + (nx // 16) if nx < 0 or nx >= 16 else cx
                                    neighbor_cz = cz + (nz // 16) if nz < 0 or nz >= 16 else cz
                                    neighbor_x, neighbor_z = nx % 16, nz % 16
                                    try:
                                        if (neighbor_cx, neighbor_cz) not in chunk_cache:
                                            chunk_cache[(neighbor_cx, neighbor_cz)] = world.get_chunk(
                                                neighbor_cx, neighbor_cz, dimension
                                            )
                                        neighbor_block = chunk_cache[(neighbor_cx, neighbor_cz)].get_block(
                                            neighbor_x, ny, neighbor_z
                                        )
                                        neighbor_name = get_full_block_name(neighbor_block)
                                        # Visible if air/transparent, fence/bars, slab or stairs
                                        is_visible = (
                                            is_air_or_transparent(neighbor_name)
                                            or is_fence_or_bars(neighbor_name)
                                            or is_slab(neighbor_name)
                                            or is_stairs(neighbor_name)
                                        )
                                        # Faces on fences/bars/slabs/stairs always visible
                                        if force_ns and face_name in ["north", "south"]:
                                            is_visible = True
                                        if force_ew and face_name in ["east", "west"]:
                                            is_visible = True
                                        if is_visible:
                                            exposed_faces.append(face_name)
                                    except:
                                        # Chunk/block missing: face visible
                                        exposed_faces.append(face_name)

                                # Special case: fence/bars — all faces visible
                                if is_fence_or_bars(block_name):
                                    exposed_faces = ["top", "bottom", "north", "south", "east", "west"]
                                # Special case: slab/stairs/carpet — faces to neighbor blocks always visible
                                elif is_slab(block_name) or is_stairs(block_name) or is_carpet(block_name):
                                    for dx, dy, dz, face_name in neighbors:
                                        nx, ny, nz = x + dx, y + dy, z + dz
                                        neighbor_cx = cx + (nx // 16) if nx < 0 or nx >= 16 else cx
                                        neighbor_cz = cz + (nz // 16) if nz < 0 or nz >= 16 else cz
                                        neighbor_x, neighbor_z = nx % 16, nz % 16
                                        try:
                                            if (neighbor_cx, neighbor_cz) not in chunk_cache:
                                                chunk_cache[(neighbor_cx, neighbor_cz)] = world.get_chunk(
                                                    neighbor_cx, neighbor_cz, dimension
                                                )
                                            neighbor_block = chunk_cache[(neighbor_cx, neighbor_cz)].get_block(
                                                neighbor_x, ny, neighbor_z
                                            )
                                            neighbor_name = get_full_block_name(neighbor_block)
                                            # If neighbor is a block (not fence/bars/slab/stairs/carpet/air), face visible
                                            if not (
                                                is_air_or_transparent(neighbor_name)
                                                or is_fence_or_bars(neighbor_name)
                                                or is_slab(neighbor_name)
                                                or is_stairs(neighbor_name)
                                                or is_carpet(neighbor_name)
                                            ):
                                                if face_name not in exposed_faces:
                                                    exposed_faces.append(face_name)
                                        except:
                                            if face_name not in exposed_faces:
                                                exposed_faces.append(face_name)
                                if exposed_faces:
                                    block_props = None
                                    try:
                                        block_props = dict(block.properties)
                                    except:
                                        pass
                                    exposed_blocks.append((
                                        world_x, y, world_z, block_name, exposed_faces, block_props
                                    ))
                            except:
                                continue
            except ChunkDoesNotExist:
                continue
    world.close()
    return exposed_blocks