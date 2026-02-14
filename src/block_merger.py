"""Greedy Meshing - Verbindet benachbarte gleiche Blöcke zu größeren Rechtecken

Reduziert die Anzahl der Brushes drastisch und vermeidet dadurch Source Engine
Fehler wie Portal-Fehler, T-Junction-Fehler und verbessert die Kompilierzeit.

Algorithmus:
  1. Nur volle Blöcke werden zusammengeführt (keine Treppen, Slabs, Zäune, etc.)
  2. Blöcke werden nach Typ gruppiert (gleiche Textur = zusammenführbar)
  3. 3D Greedy Meshing: Erweitere in X, dann Z, dann Y zu maximalen Quadern
  4. Berechne sichtbare Faces für die zusammengeführte Region
"""

import logging

log = logging.getLogger(__name__)


def is_mergeable_block(block_type):
    """
    Prüft ob ein Block zusammengeführt werden kann.
    Nur volle 1x1x1 Blöcke können zusammengeführt werden.
    Spezialblöcke (Treppen, Slabs, Zäune, etc.) werden einzeln gelassen.
    """
    non_mergeable = [
        "_slab", "_stairs", "_fence", "_trapdoor",
        "bars", "glass_pane", "_carpet",
        "_door", "_button", "_plate",
    ]
    return not any(tag in block_type for tag in non_mergeable)


def greedy_mesh_3d(blocks_info):
    """
    3D Greedy Meshing - Verbindet benachbarte Blöcke gleichen Typs zu Quadern.

    Algorithmus:
      - Sortiere alle Positionen
      - Für jede noch nicht verbrauchte Position:
        1. Erweitere maximal in X-Richtung
        2. Erweitere maximal in Z-Richtung (volle X-Breite muss vorhanden sein)
        3. Erweitere maximal in Y-Richtung (volle X×Z-Fläche muss vorhanden sein)
      - Markiere alle verwendeten Positionen als verbraucht

    Args:
        blocks_info: dict mapping (x, y, z) -> {
            'block_type': str,
            'exposed_faces': list[str],
            'properties': dict or None
        }

    Returns:
        merged_regions: list of dicts mit Regionsinformationen
        non_mergeable_blocks: list of (x, y, z, block_type, exposed_faces, properties)
    """
    mergeable = {}
    non_mergeable_blocks = []

    for (x, y, z), info in blocks_info.items():
        if is_mergeable_block(info['block_type']):
            mergeable[(x, y, z)] = info
        else:
            non_mergeable_blocks.append((
                x, y, z,
                info['block_type'],
                info['exposed_faces'],
                info['properties']
            ))

    # Gruppiere nach Block-Typ (nur gleiche Typen können zusammengeführt werden)
    type_groups = {}
    for (x, y, z), info in mergeable.items():
        bt = info['block_type']
        if bt not in type_groups:
            type_groups[bt] = {}
        type_groups[bt][(x, y, z)] = info

    merged_regions = []
    total_before = len(mergeable)
    total_after = 0

    for block_type, positions_info in type_groups.items():
        remaining = set(positions_info.keys())

        # Sortiert durchgehen für deterministische Ergebnisse
        for pos in sorted(remaining):
            if pos not in remaining:
                continue

            x, y, z = pos

            # --- Schritt 1: Erweitere in X-Richtung ---
            x_end = x
            while (x_end + 1, y, z) in remaining:
                x_end += 1

            # --- Schritt 2: Erweitere in Z-Richtung ---
            # Alle X-Positionen müssen vorhanden sein
            z_end = z
            while True:
                can_extend = True
                for xi in range(x, x_end + 1):
                    if (xi, y, z_end + 1) not in remaining:
                        can_extend = False
                        break
                if not can_extend:
                    break
                z_end += 1

            # --- Schritt 3: Erweitere in Y-Richtung (Höhe) ---
            # Volle X×Z-Fläche muss auf der nächsten Y-Ebene vorhanden sein
            y_end = y
            while True:
                can_extend = True
                for xi in range(x, x_end + 1):
                    for zi in range(z, z_end + 1):
                        if (xi, y_end + 1, zi) not in remaining:
                            can_extend = False
                            break
                    if not can_extend:
                        break
                if not can_extend:
                    break
                y_end += 1

            # Alle Positionen als verbraucht markieren
            constituent_blocks = []
            for xi in range(x, x_end + 1):
                for yi in range(y, y_end + 1):
                    for zi in range(z, z_end + 1):
                        remaining.discard((xi, yi, zi))
                        constituent_blocks.append((xi, yi, zi))

            # Sichtbare Faces für die Region berechnen
            exposed = _compute_merged_exposed_faces(
                x, y, z, x_end, y_end, z_end,
                constituent_blocks, positions_info
            )

            size_x = x_end - x + 1
            size_y = y_end - y + 1
            size_z = z_end - z + 1

            merged_regions.append({
                'block_type': block_type,
                'mc_x': x, 'mc_y': y, 'mc_z': z,
                'size_x': size_x,   # Blöcke in MC X-Richtung
                'size_y': size_y,   # Blöcke in MC Y-Richtung (Höhe)
                'size_z': size_z,   # Blöcke in MC Z-Richtung
                'exposed_faces': exposed,
                'constituent_blocks': constituent_blocks,
            })
            total_after += 1

    if total_before > 0:
        reduction = (1 - total_after / total_before) * 100
        log.info(
            f"Greedy Mesh: {total_before} Vollblöcke -> {total_after} Regionen "
            f"({reduction:.1f}% Reduktion)"
        )
    else:
        log.info("Greedy Mesh: Keine zusammenführbaren Vollblöcke gefunden")

    log.info(f"Nicht-zusammenführbare Blöcke: {len(non_mergeable_blocks)}")

    return merged_regions, non_mergeable_blocks


def _compute_merged_exposed_faces(x1, y1, z1, x2, y2, z2, blocks, blocks_info):
    """
    Berechnet die sichtbaren Faces einer zusammengeführten Region.

    Eine Face der Region ist sichtbar, wenn MINDESTENS ein Block an der
    jeweiligen Grenzfläche diese Face als sichtbar markiert hat.

    In Source Engine wird eine sichtbare Face mit Textur versehen.
    Unsichtbare Faces bekommen toolsnodraw (werden nicht gerendert).

    Args:
        x1, y1, z1: Startkoordinaten der Region (MC-Koordinaten)
        x2, y2, z2: Endkoordinaten der Region (MC-Koordinaten)
        blocks: Liste aller Blockpositionen in der Region
        blocks_info: Dict mit Block-Infos (exposed_faces etc.)

    Returns:
        list[str]: Liste sichtbarer Face-Richtungen
    """
    exposed = set()

    for bx, by, bz in blocks:
        info = blocks_info.get((bx, by, bz))
        if not info:
            continue
        block_exposed = info['exposed_faces']

        # Top: nur Blöcke an der Oberkante (y == y2)
        if by == y2 and "top" in block_exposed:
            exposed.add("top")

        # Bottom: nur Blöcke an der Unterkante (y == y1)
        if by == y1 and "bottom" in block_exposed:
            exposed.add("bottom")

        # North (-Z): nur Blöcke an der Nordseite (z == z1)
        if bz == z1 and "north" in block_exposed:
            exposed.add("north")

        # South (+Z): nur Blöcke an der Südseite (z == z2)
        if bz == z2 and "south" in block_exposed:
            exposed.add("south")

        # East (+X): nur Blöcke an der Ostseite (x == x2)
        if bx == x2 and "east" in block_exposed:
            exposed.add("east")

        # West (-X): nur Blöcke an der Westseite (x == x1)
        if bx == x1 and "west" in block_exposed:
            exposed.add("west")

    return list(exposed)
