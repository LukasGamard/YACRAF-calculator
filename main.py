import tkinter as tk
import sys
import os

from config.settings import Settings
from config.program_paths import SAVES_PATH


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_name>")
        
        print(f"Existing saves: {[name for name in os.listdir(SAVES_PATH) if os.path.isdir(os.path.join(SAVES_PATH, name))]}")
        return
        
    save_name = sys.argv[1]
    
    settings = Settings(save_name)
    settings.save()
    
    from model import Model
    
    root = tk.Tk()
    model = Model(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()

