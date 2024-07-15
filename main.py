import tkinter as tk
import pickle
import sys

sys.path.append("src")
sys.path.append("src/calculations")
sys.path.append("src/gui_blocks")
from model import Model

def main():
    new_save = False
    
    if len(sys.argv) == 2:
        if sys.argv[1] == "new":
            new_save = True
            
    root = tk.Tk()
    model = Model(root, new_save)
    root.mainloop()
    
main()
