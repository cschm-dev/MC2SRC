"""Greedy Meshing für Stairs (Treppen)

Führt benachbarte Stairs mit identischen Eigenschaften (facing, half, shape) zu Quadern zusammen.
"""

def is_mergeable_stairs(block_type, properties):
    if not block_type.endswith("_stairs"):
        return False
    if not properties:
        return False
    required = ["facing", "half", "shape"]
    return all(key in properties for key in required)


def greedy_mesh_stairs(blocks_info):
    """
    Führt benachbarte Stairs mit identischen Eigenschaften zusammen.
    Args:
        blocks_info: dict mapping (x, y, z) -> { 'block_type', 'exposed_faces', 'properties' }
    Returns:
        merged_stairs: list of dicts (wie merged_regions)
        non_mergeable: list of Einzel-Stairs (x, y, z, ...)
    """
    # Gruppiere nach (block_type, facing, half, shape)
    groups = {}
    for (x, y, z), info in blocks_info.items():
        if is_mergeable_stairs(info['block_type'], info['properties']):
            facing = info['properties']['facing'].py_str
            half = info['properties']['half'].py_str
            shape = info['properties']['shape'].py_str
            key = (info['block_type'], facing, half, shape)
            if key not in groups:
                groups[key] = {}
            groups[key][(x, y, z)] = info

    merged_stairs = []
    used = set()
    for (block_type, facing, half, shape), positions_info in groups.items():
        remaining = set(positions_info.keys())
        for pos in sorted(remaining):
            if pos in used:
                continue
            x, y, z = pos
            # --- Schritt 1: Erweitere in X-Richtung ---
            x_end = x
            while (x_end + 1, y, z) in remaining and (x_end + 1, y, z) not in used:
                x_end += 1
            # --- Schritt 2: Erweitere in Z-Richtung ---
            z_end = z
            while True:
                can_extend = True
                for xi in range(x, x_end + 1):
                    if (xi, y, z_end + 1) not in remaining or (xi, y, z_end + 1) in used:
                        can_extend = False
                        break
                if not can_extend:
                    break
                z_end += 1
            # --- Schritt 3: Keine Erweiterung in Y (Treppen sind nicht stapelbar) ---
            y_end = y

            # Markiere alle als benutzt
            for xi in range(x, x_end + 1):
                for yi in range(y, y_end + 1):
                    for zi in range(z, z_end + 1):
                        used.add((xi, yi, zi))
            # Sichtbare Faces
            constituent_blocks = [(xi, yi, zi) for xi in range(x, x_end + 1) for yi in range(y, y_end + 1) for zi in range(z, z_end + 1)]
            exposed = set()
            for bx, by, bz in constituent_blocks:
                info = positions_info.get((bx, by, bz))
                if info:
                    exposed.update(info['exposed_faces'])
            merged_stairs.append({
                'block_type': block_type,
                'facing': facing,
                'half': half,
                'shape': shape,
                'mc_x': x, 'mc_y': y, 'mc_z': z,
                'size_x': x_end - x + 1,
                'size_y': y_end - y + 1,
                'size_z': z_end - z + 1,
                'exposed_faces': list(exposed),
                'constituent_blocks': constituent_blocks,
                'properties': positions_info[pos]['properties']
            })

    # Nicht-mergebare Stairs
    non_mergeable = [
        (x, y, z, info['block_type'], info['exposed_faces'], info['properties'])
        for (x, y, z), info in blocks_info.items()
        if is_mergeable_stairs(info['block_type'], info['properties']) and (x, y, z) not in used
    ]
    return merged_stairs, non_mergeable