import tkinter as tk
import sys
import os

# Paths to all directories from which modules may be imported elsewhere in the program
sys.path.append("src")
from config import BLOCKS_CALCULATION_PATH, BLOCKS_GUI_PATH, SCRIPTS_PATH
sys.path.append(BLOCKS_CALCULATION_PATH)
sys.path.append(BLOCKS_GUI_PATH)
sys.path.append(SCRIPTS_PATH)

def main():
    new_save = False
    
    # Force new save
    if len(sys.argv) == 2:
        if sys.argv[1] == "new":
            new_save = True
            
    root = tk.Tk()
    
    with open("settings.py", "w") as file_settings:
        ratio_of_screen = 0.85
        canvas_width = int(root.winfo_screenwidth() * ratio_of_screen)
        canvas_height = int(root.winfo_screenheight() * ratio_of_screen)
        
        file_settings.write(f"CANVAS_WIDTH = {canvas_width}\nCANVAS_HEIGHT = {canvas_height}")
        
    from model import Model
    
    model = Model(root, new_save)
    root.mainloop()
    
if __name__ == "__main__":
    main()

