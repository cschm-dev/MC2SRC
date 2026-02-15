"""VMF file creation and material application"""

import logging
from pyvmf import PyVMF, World as VMFWorld, Group, VMF
from .constants import BLOCK_SIZE
from .textures import get_texture
from .block_detector import get_exposed_blocks
from .geometry import (
    create_normal_block, create_merged_block, create_stairs, create_slab, 
    create_fence, get_fence_connections,
    create_iron_bars, get_bars_connections,
    create_trapdoor, create_carpet
)

from .block_merger import greedy_mesh_3d
from .slab_merger import greedy_mesh_slabs
from .stair_merger import greedy_mesh_stairs

log = logging.getLogger(__name__)


def _ensure_group(vmf, attr_name):
    """Ensure a Group object exists on the VMF and return it (stored as attribute)."""
    try:
        grp = getattr(vmf, attr_name, None)
        if grp is None:
            grp = Group()
            try:
                vmf.world.group.append(grp)
            except Exception:
                pass
            setattr(vmf, attr_name, grp)
        return grp
    except Exception:
        return None


def apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest=False, texture_scale_x=1.0, texture_scale_y=1.0):
    """Applies materials to a solid
    
    Args:
        solid: PyVMF Solid object
        block_type: Minecraft block type
        exposed_faces: List of visible faces
        mat_path: Material path
        face_mapping: Face mapping mode
        is_lowest: Is this the lowest block at this position?
        texture_scale_x: Texture scale factor for X axis
        texture_scale_y: Texture scale factor for Y axis
    """
    if solid is None:
        raise ValueError(f"Cannot apply materials to None solid for block_type {block_type}")
    
    base_tex = get_texture(block_type)
    
    # Face-Mapping Konfiguration
    if face_mapping == "swap_ns":
        face_map = {"south": 0, "north": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_ew":
        face_map = {"north": 0, "south": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_both":
        face_map = {"south": 0, "north": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    else:
        face_map = {"north": 0, "south": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}

    for i, side in enumerate(solid.side):
        face_name = next((name for name, idx in face_map.items() if idx == i), None)
        if face_name:
            # Never assign nodraw to trapdoors or their neighbors
            if block_type.endswith("_trapdoor") or block_type.endswith("_stairs") or block_type.endswith("_slab"):
                # Always assign the correct texture
                if block_type == "grass_block":
                    if i == 4:
                        side.material = f"{mat_path}/grass_block_top"
                    elif i == 5:
                        side.material = f"{mat_path}/dirt"
                    else:
                        side.material = f"{mat_path}/grass_block_side"
                elif block_type.endswith(("_log", "_stem", "_wood")):
                    side.material = f"{mat_path}/{base_tex}_top" if i in [4, 5] else f"{mat_path}/{base_tex}"
                else:
                    side.material = f"{mat_path}/{base_tex}"
            else:
                # Wenn unterster Block: Bottom-Face immer auf nodraw setzen
                if is_lowest and face_name == "bottom":
                    side.material = "tools/toolsnodraw"
                elif face_name in exposed_faces:
                    if block_type == "grass_block":
                        if i == 4:
                            side.material = f"{mat_path}/grass_block_top"
                        elif i == 5:
                            side.material = f"{mat_path}/dirt"
                        else:
                            side.material = f"{mat_path}/grass_block_side"
                    elif block_type.endswith(("_log", "_stem", "_wood")):
                        side.material = f"{mat_path}/{base_tex}_top" if i in [4, 5] else f"{mat_path}/{base_tex}"
                    else:
                        side.material = f"{mat_path}/{base_tex}"
                else:
                    side.material = "tools/toolsnodraw"
            # UV-Mapping
            if i in [4, 5]:  # Top/Bottom
                side.uaxis, side.vaxis = f"[1 0 0 0] {texture_scale_x}", f"[0 -1 0 0] {texture_scale_y}"
            elif i in [0, 1]:  # North/South
                side.uaxis, side.vaxis = f"[1 0 0 0] {texture_scale_x}", f"[0 0 -1 0] {texture_scale_y}"
            else:  # East/West
                side.uaxis, side.vaxis = f"[0 1 0 0] {texture_scale_x}", f"[0 0 -1 0] {texture_scale_y}"
            side.lightmapscale = 16
            side.smoothing_groups = 0


def create_block(vmf, x, y, z, block_type, exposed_faces, mat_path="minecraft", 
                properties=None, face_mapping="standard", blocks_dict=None, 
                block_coords=None, is_lowest=False, group_mode="group_blocks",
                texture_scale_x=1.0, texture_scale_y=1.0):
    """
    Creates a block in the VMF
    
    Args:
        vmf: VMF object
        x, y, z: Position in Hammer Units
        block_type: Minecraft block type
        exposed_faces: List of visible faces
        mat_path: Material path
        properties: Block properties
        face_mapping: Face mapping mode
        blocks_dict: Dictionary of all blocks for connections
        block_coords: Original Minecraft coordinates (x, y, z)
        is_lowest: Is this the lowest block at this position?
        group_mode: Grouping mode
        texture_scale_x: Texture scale factor for X axis
        texture_scale_y: Texture scale factor for Y axis
    """
    log.debug(f"Creating block: {block_type} at ({x}, {y}, {z}) with properties: {properties}")
    
    is_slab = "_slab" in block_type
    is_stairs = "_stairs" in block_type
    is_fence = "_fence" in block_type
    is_bars = "bars" in block_type or "glass_pane" in block_type
    is_trapdoor = "_trapdoor" in block_type

        # IRON BARS / GLASS PANES
    if is_bars:
        log.info(f"Creating bars/pane: {block_type} at {block_coords}")
        solids = []
        connections = {'north': False, 'south': False, 'east': False, 'west': False}
        if blocks_dict and block_coords:
            connections = get_bars_connections(block_coords[0], block_coords[1], block_coords[2], blocks_dict)
            log.info(f"  Connections: {connections}")
        create_iron_bars(solids, x, y, z, connections)
        for solid in solids:
            apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
            # Group non-full blocks if requested
            if group_mode == "group_nonfull_blocks":
                grp = _ensure_group(vmf, "_nonfull_group")
                try:
                    if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                        solid.editor.groupid = grp.id
                except Exception:
                    pass
                try:
                    vmf.add_to_visgroup("non_full_blocks", solid)
                except Exception:
                    pass
            vmf.add_solids([solid])
        return

    # TRAPDOORS
    if is_trapdoor:
        log.info(f"Creating trapdoor: {block_type} at {block_coords}, props: {properties}")
        solids = []
        create_trapdoor(solids, x, y, z, properties)
        for solid in solids:
            apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
            if group_mode == "group_nonfull_blocks":
                grp = _ensure_group(vmf, "_nonfull_group")
                try:
                    if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                        solid.editor.groupid = grp.id
                except Exception:
                    pass
                try:
                    vmf.add_to_visgroup("non_full_blocks", solid)
                except Exception:
                    pass
            vmf.add_solids([solid])
        return

    # ZÄUNE
    if is_fence:
        solids = []
        connections = {'north': False, 'south': False, 'east': False, 'west': False}
        if blocks_dict and block_coords:
            connections = get_fence_connections(block_coords[0], block_coords[1], block_coords[2], blocks_dict)
        create_fence(solids, x, y, z, connections)
        for solid in solids:
            apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
            if group_mode == "group_nonfull_blocks":
                grp = _ensure_group(vmf, "_nonfull_group")
                try:
                    if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                        solid.editor.groupid = grp.id
                except Exception:
                    pass
                try:
                    vmf.add_to_visgroup("non_full_blocks", solid)
                except Exception:
                    pass
            vmf.add_solids([solid])
        return

    # SLABS
    if is_slab:
        solid = create_slab(x, y, z, properties)
        apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
        if group_mode == "group_nonfull_blocks":
            grp = _ensure_group(vmf, "_nonfull_group")
            try:
                if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                    solid.editor.groupid = grp.id
            except Exception:
                pass
            try:
                vmf.add_to_visgroup("non_full_blocks", solid)
            except Exception:
                pass
        vmf.add_solids([solid])
        return

    # TREPPEN
    if is_stairs:
        solids = []
        create_stairs(solids, x, y, z, properties)
        for solid in solids:
            apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
            if group_mode == "group_nonfull_blocks":
                grp = _ensure_group(vmf, "_nonfull_group")
                try:
                    if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                        solid.editor.groupid = grp.id
                except Exception:
                    pass
                try:
                    vmf.add_to_visgroup("non_full_blocks", solid)
                except Exception:
                    pass
            vmf.add_solids([solid])
        return

    # CARPET
    if "_carpet" in block_type:
        log.info(f"Creating carpet: {block_type} at ({x}, {y}, {z})")
        try:
            solid = create_carpet(x, y, z, properties)
            if solid is None:
                log.warning(f"Skipping carpet block at ({x}, {y}, {z}) - solid creation failed")
                return
            apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest, texture_scale_x, texture_scale_y)
            if group_mode == "group_nonfull_blocks":
                grp = _ensure_group(vmf, "_nonfull_group")
                try:
                    if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                        solid.editor.groupid = grp.id
                except Exception:
                    pass
                try:
                    vmf.add_to_visgroup("non_full_blocks", solid)
                except Exception:
                    pass
            vmf.add_solids([solid])
        except Exception as e:
            log.error(f"Error creating carpet block at ({x}, {y}, {z}): {e}")
        return

    # NORMALE BLÖCKE
    solid = create_normal_block(x, y, z)
    
    # Face-Mapping für normale Blöcke
    if face_mapping == "swap_ns":
        face_map = {"south": 0, "north": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_ew":
        face_map = {"north": 0, "south": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_both":
        face_map = {"south": 0, "north": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    else:
        face_map = {"north": 0, "south": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}

    base_tex = get_texture(block_type)
    
    for i, side in enumerate(solid.side):
        face_name = next((name for name, idx in face_map.items() if idx == i), None)
        
        # Wenn unterster Block: Bottom-Face immer auf nodraw setzen
        if is_lowest and face_name == "bottom":
            side.material = "tools/toolsnodraw"
        elif face_name and face_name in exposed_faces:
            # Spezielle Texturen für bestimmte Blöcke
            if block_type == "grass_block":
                if i == 4:
                    side.material = f"{mat_path}/grass_block_top"
                elif i == 5:
                    side.material = f"{mat_path}/dirt"
                else:
                    side.material = f"{mat_path}/grass_block_side"
            elif block_type.endswith(("_log", "_stem", "_wood")):
                side.material = f"{mat_path}/{base_tex}_top" if i in [4, 5] else f"{mat_path}/{base_tex}"
            else:
                side.material = f"{mat_path}/{base_tex}"
        else:
            side.material = "tools/toolsnodraw"
        
        # UV-Mapping
        if i in [4, 5]:  # Top/Bottom
            side.uaxis, side.vaxis = f"[1 0 0 0] {texture_scale_x}", f"[0 -1 0 0] {texture_scale_y}"
        elif i in [0, 1]:  # North/South
            side.uaxis, side.vaxis = f"[1 0 0 0] {texture_scale_x}", f"[0 0 -1 0] {texture_scale_y}"
        else:  # East/West
            side.uaxis, side.vaxis = f"[0 1 0 0] {texture_scale_x}", f"[0 0 -1 0] {texture_scale_y}"
        
        side.lightmapscale = 16
        side.smoothing_groups = 0
    
    # Normale Vollblöcke sind 1x1 — ggf. in eine Hammer-Group packen
    try:
        if group_mode == "group_blocks":
            grp = _ensure_group(vmf, "_1x1_group")
            try:
                if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                    solid.editor.groupid = grp.id
            except Exception:
                pass
            try:
                vmf.add_to_visgroup("1x1_blocks", solid)
            except Exception:
                pass
        else:
            # If grouping non-full, we still may want to set visgroup for full blocks
            try:
                vmf.add_to_visgroup("1x1_blocks", solid)
            except Exception:
                pass
    except Exception:
        pass

    vmf.add_solids([solid])

def create_merged_vmf_block(vmf, hx, hy, hz, size_x, size_z, size_y,
                            block_type, exposed_faces, mat_path, face_mapping,
                            is_all_lowest, group_mode):
    """
    Erstellt einen zusammengeführten Block (Greedy Mesh) im VMF.

    Args:
        vmf: VMF-Objekt
        hx, hy, hz: Position in Hammer Units
        size_x: Anzahl Blöcke in MC X-Richtung (→ Hammer X)
        size_z: Anzahl Blöcke in MC Z-Richtung (→ Hammer Y)
        size_y: Anzahl Blöcke in MC Y-Richtung (→ Hammer Z, Höhe)
        block_type: Minecraft Block-Typ
        exposed_faces: Liste sichtbarer Faces
        mat_path: Materialpfad
        face_mapping: Face-Mapping-Modus
        is_all_lowest: Alle Bottom-Blöcke sind die untersten an ihrer Position
        group_mode: Gruppierungsmodus
    """
    # Dimensionen in Hammer Units
    w = size_x * BLOCK_SIZE   # Hammer X
    h = size_z * BLOCK_SIZE   # Hammer Y (von MC Z)
    l = size_y * BLOCK_SIZE   # Hammer Z (von MC Y = Höhe)

    solid = create_merged_block(hx, hy, hz, w, h, l)

    # Face-Mapping Konfiguration (identisch zu Einzelblöcken)
    if face_mapping == "swap_ns":
        face_map = {"south": 0, "north": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_ew":
        face_map = {"north": 0, "south": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    elif face_mapping == "swap_both":
        face_map = {"south": 0, "north": 1, "west": 2, "east": 3, "top": 4, "bottom": 5}
    else:
        face_map = {"north": 0, "south": 1, "east": 2, "west": 3, "top": 4, "bottom": 5}

    base_tex = get_texture(block_type)

    for i, side in enumerate(solid.side):
        face_name = next((name for name, idx in face_map.items() if idx == i), None)

        # Bottom-Face auf nodraw setzen wenn alle Unterseiten-Blöcke die untersten sind
        if is_all_lowest and face_name == "bottom":
            side.material = "tools/toolsnodraw"
        elif face_name and face_name in exposed_faces:
            # Spezielle Texturen für bestimmte Blöcke
            if block_type == "grass_block":
                if i == 4:
                    side.material = f"{mat_path}/grass_block_top"
                elif i == 5:
                    side.material = f"{mat_path}/dirt"
                else:
                    side.material = f"{mat_path}/grass_block_side"
            elif block_type.endswith(("_log", "_stem", "_wood")):
                side.material = f"{mat_path}/{base_tex}_top" if i in [4, 5] else f"{mat_path}/{base_tex}"
            else:
                side.material = f"{mat_path}/{base_tex}"
        else:
            side.material = "tools/toolsnodraw"

        # UV-Mapping (World-Space Projektion — tiled automatisch für jede Größe)
        if i in [4, 5]:   # Top/Bottom
            side.uaxis, side.vaxis = "[1 0 0 0] 0.25", "[0 -1 0 0] 0.25"
        elif i in [0, 1]:  # North/South
            side.uaxis, side.vaxis = "[1 0 0 0] 0.25", "[0 0 -1 0] 0.25"
        else:              # East/West
            side.uaxis, side.vaxis = "[0 1 0 0] 0.25", "[0 0 -1 0] 0.25"

        side.lightmapscale = 16
        side.smoothing_groups = 0

    # Grouping
    try:
        grp = _ensure_group(vmf, "_merged_group")
        try:
            if hasattr(solid, "editor") and solid.editor is not None and grp is not None:
                solid.editor.groupid = grp.id
        except Exception:
            pass
        try:
            vmf.add_to_visgroup("merged_blocks", solid)
        except Exception:
            pass
    except Exception:
        pass

    # Markiere als Detail-Brush
    if hasattr(solid, "editor") and solid.editor is not None:
        solid.editor.visgroupid = 9999  # Dummy-ID für "detail"

    vmf.add_solids([solid])


def convert_to_vmf(world_path, x1, z1, x2, z2, output_vmf, y_min=-64, y_max=320, 
                   mat_path="minecraft", dimension='minecraft:overworld', 
                   face_mapping="standard", force_ns=False, force_ew=False,
                   group_mode="group_blocks", merge_blocks=True):
    """
    Converts a Minecraft area to VMF
    
    Args:
        world_path: Path to Minecraft world
        x1, z1, x2, z2: Coordinates of the area
        output_vmf: Output VMF file
        y_min, y_max: Height range
        mat_path: Material path
        dimension: Minecraft dimension
        face_mapping: Face mapping mode
        force_ns: Force North/South faces visible
        force_ew: Force East/West faces visible
        group_mode: Grouping mode
        merge_blocks: Enable greedy meshing (merge blocks)
    """
    log.info(f"Start conversion from {world_path}")
    blocks = get_exposed_blocks(world_path, x1, z1, x2, z2, y_min, y_max, dimension, force_ns, force_ew)
    log.info(f"Found: {len(blocks)} visible blocks")
    
    # Dictionary for connection checks
    blocks_dict = {(x, y, z): (x, y, z, bt, ef, props) for x, y, z, bt, ef, props in blocks}
    
    # Find the lowest block for each (x, z) position
    lowest_blocks = {}
    for x, y, z, block_type, exposed_faces, properties in blocks:
        key = (x, z)
        if key not in lowest_blocks or y < lowest_blocks[key]:
            lowest_blocks[key] = y
    
    vmf = VMF()
    vmf.world = VMFWorld()
    
    if not blocks:
        vmf.export(output_vmf)
        log.info(f"VMF saved: {output_vmf}")
        return

    coords = [(x, y, z) for x, y, z, _, _, _ in blocks]
    min_x = min(x for x, _, _ in coords)
    min_y = min(y for _, y, _ in coords)
    min_z = min(z for _, _, z in coords)

    if merge_blocks:
        # GREEDY MESHING: Merge blocks & slabs
        log.info("Greedy meshing enabled — merging same blocks & slabs...")

        # Block-Infos für den Merger aufbereiten
        blocks_info = {}
        for x, y, z, block_type, exposed_faces, properties in blocks:
            blocks_info[(x, y, z)] = {
                'block_type': block_type,
                'exposed_faces': exposed_faces,
                'properties': properties
            }

        # 1. Normale Blöcke
        merged_regions, non_mergeable = greedy_mesh_3d(blocks_info)

        # 2. Slabs
        merged_slabs, non_mergeable_slabs = greedy_mesh_slabs(blocks_info)

        # 3. Stairs
        merged_stairs, non_mergeable_stairs = greedy_mesh_stairs(blocks_info)

        # Merged blocks created
        for region in merged_regions:
            hx = (region['mc_x'] - min_x) * BLOCK_SIZE
            hy = (region['mc_z'] - min_z) * BLOCK_SIZE
            hz = (region['mc_y'] - min_y) * BLOCK_SIZE

            # Prüfe ob ALLE Bottom-Layer-Blöcke die untersten an ihrer Position sind
            is_all_lowest = True
            for bx, by, bz in region['constituent_blocks']:
                if by == region['mc_y']:  # Bottom-Layer der Region
                    if lowest_blocks.get((bx, bz)) != by:
                        is_all_lowest = False
                        break

            create_merged_vmf_block(
                vmf, hx, hy, hz,
                region['size_x'], region['size_z'], region['size_y'],
                region['block_type'], region['exposed_faces'],
                mat_path, face_mapping, is_all_lowest, group_mode
            )

        # Non-mergeable blocks created individually (stairs, slabs, etc.)
        for x, y, z, block_type, exposed_faces, properties in (non_mergeable + non_mergeable_slabs + non_mergeable_stairs):
            hx = (x - min_x) * BLOCK_SIZE
            hy = (z - min_z) * BLOCK_SIZE
            hz = (y - min_y) * BLOCK_SIZE
            is_lowest = (lowest_blocks.get((x, z)) == y)

            # Stairs/Slabs als Detail-Brush markieren
            solid = None
            if "_slab" in block_type:
                solid = create_slab(hx, hy, hz, properties)
            elif "_stairs" in block_type:
                solids = []
                create_stairs(solids, hx, hy, hz, properties)
                for s in solids:
                    apply_materials_to_solid(s, block_type, exposed_faces, mat_path, face_mapping, is_lowest)
                    if hasattr(s, "editor") and s.editor is not None:
                        s.editor.visgroupid = 9999
                    vmf.add_solids([s])
                continue
            if solid is not None:
                apply_materials_to_solid(solid, block_type, exposed_faces, mat_path, face_mapping, is_lowest)
                if hasattr(solid, "editor") and solid.editor is not None:
                    solid.editor.visgroupid = 9999
                vmf.add_solids([solid])
                continue
            # Normale Spezialblöcke
            create_block(vmf, hx, hy, hz, block_type, exposed_faces, mat_path,
                        properties, face_mapping, blocks_dict, (x, y, z), is_lowest, group_mode, texture_scale_x, texture_scale_y)

        log.info(
            f"Erstellt: {len(merged_regions)} zusammengeführte Blöcke, {len(merged_slabs)} zusammengeführte Slabs, {len(merged_stairs)} zusammengeführte Stairs + "
            f"{len(non_mergeable) + len(non_mergeable_slabs) + len(non_mergeable_stairs)} einzelne Spezialblöcke"
        )
    else:
        # ORIGINAL: Each block individually (1x1x1)
        for x, y, z, block_type, exposed_faces, properties in blocks:
            hx = (x - min_x) * BLOCK_SIZE
            hy = (z - min_z) * BLOCK_SIZE
            hz = (y - min_y) * BLOCK_SIZE
            is_lowest = (lowest_blocks.get((x, z)) == y)

            create_block(vmf, hx, hy, hz, block_type, exposed_faces, mat_path,
                        properties, face_mapping, blocks_dict, (x, y, z), is_lowest, group_mode, texture_scale_x, texture_scale_y)
    
    vmf.export(output_vmf)
    log.info(f"VMF saved: {output_vmf}")


def convert_to_vmf(world_path, x1, z1, x2, z2, output_vmf, y_min=-64, y_max=320, 
                   mat_path="minecraft", dimension='minecraft:overworld', 
                   face_mapping="standard", force_ns=False, force_ew=False,
                   group_mode="group_blocks", merge_blocks=True, texture_scale_x=1.0, texture_scale_y=1.0):
    """
    Converts a Minecraft area to VMF
    
    Args:
        world_path: Path to Minecraft world
        x1, z1, x2, z2: Coordinates of the area
        output_vmf: Output VMF file
        y_min, y_max: Height range
        mat_path: Material path
        dimension: Minecraft dimension
        face_mapping: Face mapping mode
        force_ns: Force North/South faces visible
        force_ew: Force East/West faces visible
        group_mode: Grouping mode
        merge_blocks: Enable greedy meshing (merge blocks)
        texture_scale_x: Texture scale factor for X axis
        texture_scale_y: Texture scale factor for Y axis
    """
    log.info(f"Start conversion from {world_path}")
    blocks = get_exposed_blocks(world_path, x1, z1, x2, z2, y_min, y_max, dimension, force_ns, force_ew)
    log.info(f"Found: {len(blocks)} visible blocks")
    
    # Dictionary for connection checks
    blocks_dict = {(x, y, z): (x, y, z, bt, ef, props) for x, y, z, bt, ef, props in blocks}
    
    # Find the lowest block for each (x, z) position
    lowest_blocks = {}
    for x, y, z, block_type, exposed_faces, properties in blocks:
        key = (x, z)
        if key not in lowest_blocks or y < lowest_blocks[key]:
            lowest_blocks[key] = y
    
    vmf = VMF()
    vmf.world = VMFWorld()
    
    if not blocks:
        vmf.export(output_vmf)
        log.info(f"VMF saved: {output_vmf}")
        return

    coords = [(x, y, z) for x, y, z, _, _, _ in blocks]
    min_x = min(x for x, _, _ in coords)
    min_y = min(y for _, y, _ in coords)
    min_z = min(z for _, _, z in coords)

    if merge_blocks:
        # GREEDY MESHING: Merge blocks & slabs
        log.info("Greedy meshing enabled — merging same blocks & slabs...")

        # Block-Infos für den Merger aufbereiten
        blocks_info = {}
        for x, y, z, block_type, exposed_faces, properties in blocks:
            blocks_info[(x, y, z)] = {
                'block_type': block_type,
                'exposed_faces': exposed_faces,
                'properties': properties
            }

        # 1. Normale Blöcke
        merged_regions, non_mergeable = greedy_mesh_3d(blocks_info)

        # 2. Slabs
        merged_slabs, non_mergeable_slabs = greedy_mesh_slabs(blocks_info)

        # 3. Stairs
        merged_stairs, non_mergeable_stairs = greedy_mesh_stairs(blocks_info)

        # Zusammengeführte Blöcke erstellen
        for region in merged_regions:
            hx = (region['mc_x'] - min_x) * BLOCK_SIZE
            hy = (region['mc_z'] - min_z) * BLOCK_SIZE
            hz = (region['mc_y'] - min_y) * BLOCK_SIZE

            # Prüfe ob ALLE Bottom-Layer-Blöcke die untersten an ihrer Position sind
            is_all_lowest = True
            for bx, by, bz in region['constituent_blocks']:
                if by == region['mc_y']:  # Bottom-Layer der Region
                    if lowest_blocks.get((bx, bz)) != by:
                        is_all_lowest = False
                        break

            from .geometry import create_merged_block
            solid = create_merged_block(hx, hy, hz, region['size_x'] * BLOCK_SIZE, region['size_z'] * BLOCK_SIZE, region['size_y'] * BLOCK_SIZE)
            apply_materials_to_solid(solid, region['block_type'], region['exposed_faces'], mat_path, face_mapping, is_all_lowest, texture_scale_x, texture_scale_y)
            vmf.add_solids([solid])

        # Nicht-zusammenführbare Blöcke einzeln erstellen (Treppen, Slabs, etc.)
        for x, y, z, block_type, exposed_faces, properties in (non_mergeable + non_mergeable_slabs + non_mergeable_stairs):
            hx = (x - min_x) * BLOCK_SIZE
            hy = (z - min_z) * BLOCK_SIZE
            hz = (y - min_y) * BLOCK_SIZE
            is_lowest = (lowest_blocks.get((x, z)) == y)

            create_block(vmf, hx, hy, hz, block_type, exposed_faces, mat_path,
                        properties, face_mapping, blocks_dict, (x, y, z), is_lowest, group_mode, texture_scale_x, texture_scale_y)

        log.info(
            f"Created: {len(merged_regions)} merged blocks + "
            f"{len(non_mergeable) + len(non_mergeable_slabs) + len(non_mergeable_stairs)} individual special blocks"
        )
    else:
        # ORIGINAL: Each block individually (1x1x1)
        for x, y, z, block_type, exposed_faces, properties in blocks:
            hx = (x - min_x) * BLOCK_SIZE
            hy = (z - min_z) * BLOCK_SIZE
            hz = (y - min_y) * BLOCK_SIZE
            is_lowest = (lowest_blocks.get((x, z)) == y)

            create_block(vmf, hx, hy, hz, block_type, exposed_faces, mat_path,
                        properties, face_mapping, blocks_dict, (x, y, z), is_lowest, group_mode, texture_scale_x, texture_scale_y)
    
    vmf.export(output_vmf)
    log.info(f"VMF saved: {output_vmf}")