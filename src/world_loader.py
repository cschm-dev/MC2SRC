"""Minecraft Welt laden und verarbeiten"""

from amulet import load_format
from amulet.api.level import World, Structure
from amulet.api.wrapper.world_format_wrapper import WorldFormatWrapper
from amulet.api.wrapper.structure_format_wrapper import StructureFormatWrapper


def load_level(path):
    """Lädt eine Minecraft Welt oder Struktur"""
    format_wrapper = load_format(path)
    if isinstance(format_wrapper, WorldFormatWrapper):
        return World(path, format_wrapper)
    elif isinstance(format_wrapper, StructureFormatWrapper):
        return Structure(path, format_wrapper)
    raise Exception(f"Unsupported format: {format_wrapper.__class__.__name__}")


def get_full_block_name(block):
    """Extrahiert den vollständigen Block-Namen mit Properties"""
    base_name = block.base_name.replace("minecraft:", "")
    
    # Spezielle Behandlung für Carpet-Blöcke
    if base_name == "carpet":
        try:
            properties = block.properties
            if 'color' in properties:
                return f"{properties['color']}_carpet"
        except:
            pass
        return "carpet"
    
    try:
        properties = block.properties
        if base_name in ['wool', 'concrete', 'concrete_powder', 'terracotta', 'glazed_terracotta', 'shulker_box']:
            if 'color' in properties:
                return f"{properties['color']}_{base_name}"
        
        wood_blocks = ['planks', 'log', 'wood', 'stairs', 'slab', 'fence', 'fence_gate', 'trapdoor', 'leaves']
        if base_name in wood_blocks:
            for prop_name in ['variant', 'wood_type', 'material']:
                if prop_name in properties:
                    return f"{properties[prop_name]}_{base_name}"
    except:
        pass
    return base_name