import os

from program_paths import CONFIG_PATH

SETTINGS_FILE = os.path.join(CONFIG_PATH, "settings.txt")

class Settings:
    def __init__(self, *, testing=None):
        self.__canvas_width = 800
        self.__canvas_height = 600
        self.__testing = False
        self.__num_samples = 10000
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file_settings:
                for line in file_settings:
                    variable, value = [config.strip() for config in line.split("=")]
                    
                    if variable == "CANVAS_WIDTH":
                        self.__canvas_width = int(value)
                        
                    elif variable == "CANVAS_HEIGHT":
                        self.__canvas_height = int(value)
                        
                    elif variable == "TESTING":
                        self.__testing = value == "True"
                        
                    elif variable == "NUM_SAMPLES":
                        self.__num_samples = int(value) # Number of samples when comparing two triangle distributions
                        
        if testing != None:
            self.__testing = testing
            
    def get_canvas_width(self):
        return self.__canvas_width
        
    def get_canvas_height(self):
        return self.__canvas_height
        
    def set_canvas_size(self, width, height):
        self.__canvas_width = width
        self.__canvas_height = height
        
    def is_testing(self):
        return self.__testing
        
    def get_num_samples(self):
        return self.__num_samples
        
    def set_num_samples(self, num_samples):
        self.__num_samples = num_samples
        
    def save(self):
        with open(SETTINGS_FILE, "w") as file_settings:
            for variable, value in [("CANVAS_WIDTH", self.__canvas_width), \
                                    ("CANVAS_HEIGHT", self.__canvas_height), \
                                    ("TESTING", self.__testing), \
                                    ("NUM_SAMPLES", self.__num_samples)]:
                file_settings.write(f"{variable} = {value}\n")
