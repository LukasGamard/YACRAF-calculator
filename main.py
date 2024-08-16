import tkinter as tk
import sys
import os

sys.path.append("config")
from program_paths import IMPORT_PATHS

# Set up the paths for modules that are imported elsewhere in the program
for path in IMPORT_PATHS:
    sys.path.append(path)
    
from settings import Settings

def main():
    new_save = False
    testing = False
    
    if len(sys.argv) == 2:
        # Force new save
        if sys.argv[1] == "new":
            new_save = True
            
        # Test the program by using specific test views and adding additional test scripts
        elif sys.argv[1] == "test":
            testing = True
            
    settings = Settings(testing=testing)
    settings.save()
    
    from model import Model
    
    root = tk.Tk()
    model = Model(root, new_save)
    root.mainloop()
    
if __name__ == "__main__":
    main()

