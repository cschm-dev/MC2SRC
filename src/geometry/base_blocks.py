"""Basis-Block Geometrie"""

from pyvmf import SolidGenerator, Vertex
from ..constants import BLOCK_SIZE


def create_normal_block(x, y, z):
    """Erstellt einen normalen würfelförmigen Block"""
    sg = SolidGenerator()
    return sg.cube(Vertex(x, y, z), BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)


def create_merged_block(x, y, z, w, h, l):
    """
    Erstellt einen Quader mit beliebigen Dimensionen (in Hammer Units).
    Wird für zusammengeführte Blöcke (Greedy Meshing) verwendet.

    Args:
        x, y, z: Position in Hammer Units
        w: Breite in Hammer Units (Hammer X-Richtung)
        h: Höhe in Hammer Units (Hammer Y-Richtung)
        l: Länge in Hammer Units (Hammer Z-Richtung)

    Returns:
        Solid-Objekt
    """
    sg = SolidGenerator()
    return sg.cube(Vertex(x, y, z), w, h, l)