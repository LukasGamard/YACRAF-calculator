import tkinter as tk
import sys
import os

from src.yacraf_calculator.config.settings import Settings

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_name>")
        
        saves_path = "saves"
        print(f"Existing saves: {[name for name in os.listdir(saves_path) if os.path.isdir(os.path.join(saves_path, name))]}")
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

