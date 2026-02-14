"""Main entry point for the Minecraft to VMF Converter"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Add PyVMF to path
pymf_path = "./pyvmf"
sys.path.append(pymf_path)

# Start GUI
from src.ui import MinecraftToSourceUI

if __name__ == "__main__":
    app = MinecraftToSourceUI()
    app.run()