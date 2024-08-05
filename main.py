import tkinter as tk
import sys
import os

# Paths to all directories from which modules may be imported elsewhere in the program
sys.path.append("src")
from config import *
sys.path.append(BLOCKS_CALCULATION_PATH)
sys.path.append(BLOCKS_GUI_PATH)
sys.path.append(SCRIPTS_PATH)
from model import Model

def main():
    new_save = False
    
    # Force new save
    if len(sys.argv) == 2:
        if sys.argv[1] == "new":
            new_save = True
            
    root = tk.Tk()
    model = Model(root, new_save)
    root.mainloop()
    
if __name__ == "__main__":
    main()
