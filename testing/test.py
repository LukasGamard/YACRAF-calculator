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
    
def set_up():
    root = tk.Tk()
    model = Model(root, True, num_configuration_views=2, num_setup_views=2)
    process_changes(root)
    
    return root, model
    
def tear_down(root):
    # time.sleep(0.4)
    root.destroy()
    # time.sleep(0.1)
    
class TestCreatingBlocks(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        tear_down(self.root)
        
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
        self.root, self.model = set_up()
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        tear_down(self.root)
        
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
        self.root, self.model = set_up()
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        tear_down(self.root)
        
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
        self.assertEqual(setup_attribute_gui.get_setup_attribute().get_name(), name)
        
    def test_configuration_view(self):
        options = self.configuration_view.open_options()
        new_view_name = "CONFIGURATION VIEW 123"
        options.set_name(new_view_name)
        
        self.assertEqual(self.configuration_view.get_name(), new_view_name)
        
    def test_setup_view(self):
        options = self.setup_view.open_options()
        new_view_name = "SETUP VIEW 123"
        options.set_name(new_view_name)
        
        self.assertEqual(self.setup_view.get_name(), new_view_name)
        
class TestConnections(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        tear_down(self.root)
        
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
        
    def test_configuration_connection(self):
        input_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        input_configuration_class_gui.create_attribute()
        drag_to(input_configuration_class_gui, self.configuration_view, 20, 20)
        
        output_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        output_configuration_class_gui.create_attribute()
        output_configuration_class_gui.create_attribute()
        drag_to(output_configuration_class_gui, self.configuration_view, 10, 10)
        
        # Create and attach input block to attribute
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        drag_to(configuration_input_gui, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        # Add connection
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 10, 10+CLASS_HEIGHT)
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        output_configuration_attributes = output_configuration_class_gui.get_configuration_attributes_gui()
        input_configuration_attribute_gui = input_configuration_class_gui.get_configuration_attributes_gui()[-1]
        
        self.assertEqual(len(output_configuration_attributes[0]._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(output_configuration_attributes[1]._GUIConfigurationAttribute__connections), 0)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 1)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 1)
        
        # Disconnect input block from attribute
        drag_to(configuration_input_gui, self.configuration_view, 15, 15)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 1)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 0)
        
        # Add connection to disconnected input block
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 10, 10+2*CLASS_HEIGHT)
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 15, 15)
        
        self.assertEqual(len(output_configuration_attributes[0]._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(output_configuration_attributes[1]._GUIConfigurationAttribute__connections), 1)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 2)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 0)
        
        # Reconnect input block to attribute
        drag_to(configuration_input_gui, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        self.assertEqual(len(output_configuration_attributes[0]._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(output_configuration_attributes[1]._GUIConfigurationAttribute__connections), 1)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 2)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 2)
        
    def test_setup_connections(self):
        pass
        
    def test_external_configuration_connection(self):
        pass
        
class TestSwitchPlaces(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
        self.configuration_view = self.model.get_configuration_views()[0]
        self.setup_view = self.model.get_setup_views()[0]
        
    def tearDown(self):
        tear_down(self.root)
        
    def check_configuration_attribute_order(self, class_gui, top_attribute_gui, bottom_attribute_gui, connections_top, connections_bottom):
        input_attributes_gui_top = top_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()
        input_attributes_gui_bottom = bottom_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()
        
        self.assertEqual(len(input_attributes_gui_top), connections_top)
        self.assertEqual(len(input_attributes_gui_bottom), connections_bottom)
        self.assertTrue(top_attribute_gui.get_y() < bottom_attribute_gui.get_y())
        
        input_configuration_attribute_gui_1, input_configuration_attribute_gui_2 = class_gui.get_configuration_attributes_gui()
        input_configuration_attribute_1, input_configuration_attribute_2 = class_gui.get_configuration_class().get_configuration_attributes()
        
        self.assertEqual((input_configuration_attribute_gui_1, input_configuration_attribute_gui_2), (top_attribute_gui, bottom_attribute_gui))
        self.assertEqual((input_configuration_attribute_1, input_configuration_attribute_2), (input_configuration_attribute_gui_1.get_configuration_attribute(), input_configuration_attribute_gui_2.get_configuration_attribute()))
        
    def check_setup_attribute_order(self, configuration_class_gui, top_configuration_attribute_gui, bottom_configuration_attribute_gui):
        for setup_class_gui in configuration_class_gui.get_setup_classes_gui():
            setup_attribute_gui_1, setup_attribute_gui_2 = setup_class_gui.get_setup_attributes_gui()
            configuration_attribute_gui_1 = setup_attribute_gui_1._GUISetupAttribute__configuration_attribute_gui
            configuration_attribute_gui_2 = setup_attribute_gui_2._GUISetupAttribute__configuration_attribute_gui
            
            self.assertEqual((configuration_attribute_gui_1, configuration_attribute_gui_2), (top_configuration_attribute_gui, bottom_configuration_attribute_gui))
            self.assertEqual(setup_attribute_gui_1.get_y() < setup_attribute_gui_2.get_y())
            
    def test_switch_attributes(self):
        input_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        input_configuration_class_gui.create_attribute()
        input_configuration_class_gui.create_attribute()
        drag_to(input_configuration_class_gui, self.configuration_view, 20, 20)
        
        output_configuration_class_gui = self.configuration_view.create_configuration_class_gui()
        output_configuration_class_gui.create_attribute()
        drag_to(output_configuration_class_gui, self.configuration_view, 10, 10)
        
        # Create and attach input block to attribute
        configuration_input_gui = self.configuration_view.create_configuration_input_gui()
        drag_to(configuration_input_gui, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        # Add connection
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 10, 10+CLASS_HEIGHT)
        perform_action(MOUSE_RIGHT_PRESS, self.configuration_view, 20-INPUT_WIDTH, 20+CLASS_HEIGHT)
        
        input_configuration_attribute_gui_1, input_configuration_attribute_gui_2 = input_configuration_class_gui.get_configuration_attributes_gui()
        options = input_configuration_attribute_gui_1.open_options()
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2, 1, 0)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2)
        
        options.move(False)
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_2, input_configuration_attribute_gui_1, 0, 1)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_2, input_configuration_attribute_gui_1)
        
        options.move(True)
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2, 1, 0)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2)
        
    def check_view_order(self, views, top_view, bottom_view):
        view_1, view_2 = views
        self.assertEqual((view_1, view_2), (top_view, bottom_view))
        
    def check_change_view_button_positions(self, is_configuration_view, top_view, bottom_view):
        for view in self.model.get_configuration_views() + self.model.get_setup_views():
            if is_configuration_view:
                change_view_buttons = view._View__configuration_change_view_buttons
            else:
                change_view_buttons = view._View__setup_change_view_buttons
                
            top_button = change_view_buttons[top_view]
            bottom_button = change_view_buttons[bottom_view]
            
            self.assertTrue(top_button.get_y() < bottom_button.get_y())
        
    def test_switch_change_configuration_views(self):
        configuration_view_1, configuration_view_2 = self.model.get_configuration_views()
        options = configuration_view_1.open_options()
        
        self.check_change_view_button_positions(True, configuration_view_1, configuration_view_2)
        
        options.move(False)
        
        self.check_view_order(self.model.get_configuration_views(), configuration_view_2, configuration_view_1)
        self.check_change_view_button_positions(True, configuration_view_2, configuration_view_1)
        
        options.move(True)
        
        self.check_view_order(self.model.get_configuration_views(), configuration_view_1, configuration_view_2)
        self.check_change_view_button_positions(True, configuration_view_1, configuration_view_2)
        
    def test_switch_change_setup_views(self):
        setup_view_1, setup_view_2 = self.model.get_setup_views()
        options = setup_view_1.open_options()
        
        self.check_change_view_button_positions(False, setup_view_1, setup_view_2)
        
        options.move(False)
        
        self.check_view_order(self.model.get_setup_views(), setup_view_2, setup_view_1)
        self.check_change_view_button_positions(False, setup_view_2, setup_view_1)
        
        options.move(True)
        
        self.check_view_order(self.model.get_setup_views(), setup_view_1, setup_view_2)
        self.check_change_view_button_positions(False, setup_view_1, setup_view_2)
        
class TestLinkedBlocks(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
    def tearDown(self):
        tear_down(self.root)
        
    def test_configuration_input(self):
        pass
        
class TestHideAttribute(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
    def tearDown(self):
        tear_down(self.root)
        
class TestDeleteBlocks(unittest.TestCase):
    def setUp(self):
        self.root, self.model = set_up()
        
    def tearDown(self):
        tear_down(self.root)
        
if __name__ == "__main__":
    unittest.main()
