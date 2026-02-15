Converts a minecraft map to vmf.

Tested in Minecraft 1.21.5.

Works pretty decent some blocks which have multiple sides e.g. bee hives are not fully automated #

Your MC map can contain full blocks, fences, trapdoors, iron bars, glas panes, stairs and slabs.
Everything else converts to a full block.

Here are the textures I used for the map:
[Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3665986205)

Recommended settings:
<pre>

{
    "world_path": "PATH_TO_WORLD_FOLDER",
    "output_path": "VMF_OUTPUT",
    "x1": "0",
    "z1": "0",
    "x2": "100",
    "z2": "100",
    "y_min": "-64",
    "y_max": "320",
    "materials_path": "PATH_TO_MC_MATERIALS relative to the materials folder e.g. just minecraft_magenta",
    "face_mapping": "standard",
    "force_ns": false,
    "force_ew": true,
    "group_mode": "no_group",
    "merge_blocks": true,
    "texture_scale_x": 0.375,
    "texture_scale_y": 0.375
}
  
</pre>
