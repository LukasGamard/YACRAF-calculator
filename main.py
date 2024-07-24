import tkinter as tk
import pickle
import sys
import os

sys.path.append("src")
from config import *
sys.path.append(os.path.join("src", "calculations"))
sys.path.append(os.path.join("src", "gui_blocks"))
sys.path.append(SCRIPTS_PATH)
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
