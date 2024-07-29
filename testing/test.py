import unittest
import tkinter as tk
import sys
import os
import time

sys.path.append(os.path.join(".."))
sys.path.append(os.path.join("..", "src"))
from config import *
sys.path.append(os.path.join("..", "src", "calculations"))
sys.path.append(os.path.join("..", "src", "gui_blocks"))
sys.path.append(os.path.join("..", SCRIPTS_PATH))
from model import Model

MOUSE_OFFSET = (int(LENGTH_UNIT / 2), int(LENGTH_UNIT / 2))

def process_changes(root):
    root.update_idletasks()
    root.update()
    
def perform_action(action, view, grid_x, grid_y):
    view.get_canvas().event_generate(action, x=grid_x*LENGTH_UNIT+MOUSE_OFFSET[0], y=grid_y*LENGTH_UNIT+MOUSE_OFFSET[1])
    process_changes(view.get_model().get_root())
    
def drag_to(block, view, grid_x, grid_y):
    perform_action(MOUSE_LEFT_PRESS, view, block.get_x(), block.get_y())
    perform_action(MOUSE_LEFT_DRAG, view, grid_x, grid_y)
    perform_action(MOUSE_LEFT_RELEASE, view, grid_x, grid_y)
    
class TestCreatingBlocks(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.model = Model(self.root, True)
        process_changes(self.root)
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        self.root.destroy()
        
    def test_configuration_class(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        self.assertEqual((configuration_class_gui.get_x(), configuration_class_gui.get_y()), GUI_BLOCK_START_COORDINATES[0])
        self.assertEqual(len(configuration_class_gui.get_configuration_class().get_configuration_attributes()), 0)
        
    def test_configuration_attribute(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        num_attributes = 5
        
        for i in range(num_attributes):
            configuration_class_gui.create_attribute()
            
        self.assertEqual(len(configuration_class_gui.get_configuration_class().get_configuration_attributes()), num_attributes)
        
        for i in range(num_attributes):
            configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[i]
            self.assertEqual((configuration_attribute_gui.get_x(), configuration_attribute_gui.get_y()), (configuration_class_gui.get_x(), configuration_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
    def test_configuration_input(self):
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        self.assertEqual((configuration_input_gui.get_x(), configuration_input_gui.get_y()), GUI_BLOCK_START_COORDINATES[0])
        
    def test_setup_class(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        
        self.assertEqual((setup_class_gui.get_x(), setup_class_gui.get_y()), GUI_BLOCK_START_COORDINATES[0])
        
    def test_setup_attribute(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        
        for i in range(3):
            configuration_class_gui.create_attribute()
            
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        
        for i in range(2):
            configuration_class_gui.create_attribute()
            
        self.assertEqual(len(setup_class_gui.get_setup_class().get_setup_attributes()), 5)
        
        for i in range(5):
            setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[i]
            self.assertEqual((setup_attribute_gui.get_x(), setup_attribute_gui.get_y()), (setup_class_gui.get_x(), setup_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
class TestDraggingBlocks(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.model = Model(self.root, True)
        process_changes(self.root)
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        self.root.destroy()
        
    def test_configuration_class(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        drag_to(configuration_class_gui, self.configuration_view, 20, 20)
        
        self.assertEqual((configuration_class_gui.get_x(), configuration_class_gui.get_y()), (20, 20))
        
    def test_configuration_attribute(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        
        for i in range(3):
            configuration_class_gui.create_attribute()
            
        drag_to(configuration_class_gui, self.configuration_view, 15, 15)
        
        for i in range(2):
            configuration_class_gui.create_attribute()
            
        drag_to(configuration_class_gui, self.configuration_view, 20, 20)
        
        for i in range(5):
            configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[i]
            self.assertEqual((configuration_attribute_gui.get_x(), configuration_attribute_gui.get_y()), (configuration_class_gui.get_x(), configuration_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
    def test_configuration_input(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        configuration_class_gui.create_attribute()
        drag_to(configuration_class_gui, self.configuration_view, 12, 12)
        
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        
        drag_to(configuration_input_gui, self.configuration_view, 12-INPUT_WIDTH, 12+CLASS_HEIGHT)
        drag_to(configuration_class_gui, self.configuration_view, 20, 20)
        
        self.assertEqual((configuration_input_gui.get_x(), configuration_input_gui.get_y()), (20-INPUT_WIDTH, 20+CLASS_HEIGHT))
        
        drag_to(configuration_input_gui, self.configuration_view, 20+CLASS_WIDTH, 20+CLASS_HEIGHT)
        drag_to(configuration_class_gui, self.configuration_view, 5, 5)
        
        self.assertEqual((configuration_input_gui.get_x(), configuration_input_gui.get_y()), (5+CLASS_WIDTH, 5+CLASS_HEIGHT))
        self.assertTrue(configuration_input_gui.is_attached())
        
        drag_to(configuration_input_gui, self.configuration_view, 15, 15)
        self.assertFalse(configuration_input_gui.is_attached())
        
    def test_setup_class(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        
        drag_to(configuration_class_gui, self.configuration_view, 15, 15)
        drag_to(setup_class_gui, self.setup_view, 17, 17)
        drag_to(configuration_class_gui, self.configuration_view, 20, 20)
        
        self.assertEqual((setup_class_gui.get_x(), setup_class_gui.get_y()), (17, 17))
        
    def test_setup_attribute(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        
        for i in range(3):
            configuration_class_gui.create_attribute()
            
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        drag_to(setup_class_gui, self.setup_view, 15, 15)
        
        for i in range(2):
            configuration_class_gui.create_attribute()
            
        drag_to(configuration_class_gui, self.setup_view, 20, 20)
        
        for i in range(5):
            setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[i]
            self.assertEqual((setup_attribute_gui.get_x(), setup_attribute_gui.get_y()), (setup_class_gui.get_x(), setup_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
        
class TestNameChange(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.model = Model(self.root, True)
        process_changes(self.root)
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        self.root.destroy()
        
    def test_class(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        
        configuration_name = "CONFIGURATION CLASS 123"
        setup_name = "SETUP CLASS 123"
        
        configuration_options = configuration_class_gui.open_options()
        setup_options = setup_class_gui.open_options()
        
        configuration_options.set_name(configuration_name)
        setup_options.set_name(setup_name)
        
        self.assertEqual(configuration_class_gui.get_name(), configuration_name)
        self.assertEqual(configuration_class_gui.get_configuration_class().get_name(), configuration_name)
        
        self.assertEqual(setup_class_gui.get_name(), setup_name)
        self.assertEqual(setup_class_gui.get_configuration_name(), configuration_name)
        self.assertEqual(setup_class_gui.get_setup_class().get_instance_name(), setup_name)
        self.assertEqual(setup_class_gui.get_setup_class().get_configuration_name(), configuration_name)
        
    def test_attribute(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        configuration_class_gui.create_attribute()
        setup_class_gui = self.setup_view.create_setup_class_gui(configuration_class_gui)
        
        configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[-1]
        setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[-1]
        
        name = "ATTRIBUTE 123"
        
        options = configuration_attribute_gui.open_options()
        options.set_name(name)
        
        self.assertEqual(configuration_attribute_gui.get_name(), name)
        self.assertEqual(configuration_attribute_gui.get_configuration_attribute().get_name(), name)
        self.assertEqual(setup_attribute_gui.get_name(), name)
        self.assertEqual(setup_attribute_gui.get_setup_attribute().get_name(), name)
        
class TestConnections(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.model = Model(self.root, True)
        process_changes(self.root)
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        self.root.destroy()
        
    def test_configuration_connection(self):
        input_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        input_configuration_class_gui.create_attribute()
        drag_to(input_configuration_class_gui, self.configuration_view, 20, 20)
        
        output_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        output_configuration_class_gui.create_attribute()
        output_configuration_class_gui.create_attribute()
        drag_to(output_configuration_class_gui, self.configuration_view, 10, 10)
        
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        drag_to(configuration_input_gui, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        perform_action(MOUSE_LEFT_PRESS, self.configuration_view, 10, 10+CLASS_HEIGHT)
        perform_action(MOUSE_LEFT_PRESS, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        perform_action(MOUSE_LEFT_PRESS, self.configuration_view, 10, 10+2*CLASS_HEIGHT)
        perform_action(MOUSE_LEFT_PRESS, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        for output_configuration_attribute_gui in output_configuration_class_gui.get_configuration_attributes_gui():
            self.assertEqual(len(output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
            self.assertEqual(len(output_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 0)
            
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 2)
        self.assertEqual(len(configuration_input_gui.get_attached_configuration_attribute_gui().get_configuration_attribute().get_input_configuration_attributes()), 2)
        
    def test_set_calculation_type(self):
        configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        configuration_class_gui.create_attribute()
        drag_to(configuration_class_gui, self.configuration_view, 15, 15)
        
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        drag_to(configuration_input_gui, self.configuration_view, 15-INPUT_WIDTH, 15+CLASS_HEIGHT)
        
        configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[-1]
        configuration_attribute = configuration_attribute_gui.get_configuration_attribute()
        
        self.assertEqual(configuration_input_gui.get_symbol_calculation_type(), None)
        self.assertEqual(configuration_attribute.get_symbol_calculation_type(), None)
        
        configuration_input_gui.set_symbol_calculation_type(SYMBOL_CALCULATION_TYPE_AND)
        self.assertEqual(configuration_input_gui.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_AND)
        self.assertEqual(configuration_attribute.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_AND)
        
        drag_to(configuration_input_gui, self.configuration_view, 10, 10)
        self.assertEqual(configuration_input_gui.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_AND)
        self.assertEqual(configuration_attribute.get_symbol_calculation_type(), None)
        
        configuration_input_gui.set_symbol_calculation_type(SYMBOL_CALCULATION_TYPE_OR)
        self.assertEqual(configuration_input_gui.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_OR)
        self.assertEqual(configuration_attribute.get_symbol_calculation_type(), None)
        
        drag_to(configuration_input_gui, self.configuration_view, 15-INPUT_WIDTH, 15+CLASS_HEIGHT)
        self.assertEqual(configuration_input_gui.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_OR)
        self.assertEqual(configuration_attribute.get_symbol_calculation_type(), SYMBOL_CALCULATION_TYPE_OR)
        
if __name__ == "__main__":
    unittest.main()
