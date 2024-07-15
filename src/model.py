from view import ConfigurationView, SetupView
from blocks_buttons import GUIChangeViewButton
from connection_gui import GUIConnection
from config import *

class Model:
    def __init__(self, root, new_save):
        self.__root = root
        self.__configuration_views = []
        self.__setup_views = []
        
        self.__linked_groups_per_number = {}
        
        self.__root.title("Canvas")
        self.__root.geometry(f"{CANVAS_WIDTH}x{CANVAS_HEIGHT}")
        self.__root.rowconfigure(0, weight=1)
        self.__root.columnconfigure(0, weight=1)
        
        self.create_view(True, "Configuration")
        
        for i in range(5):
            self.create_view(False, f"Setup {i+1}")
        
        self.change_view(self.__configuration_views[0])
        
        # Restore saved views
        if not new_save:
            mapping_configuration_class_gui = {}
            
            for i, configuration_view in enumerate(self.__configuration_views):
                mapping_configuration_class_gui.update(configuration_view.restore_save(i))
                
            for i, setup_view in enumerate(self.__setup_views):
                setup_view.restore_save(len(self.__configuration_views)+i, mapping_configuration_class_gui, self.__linked_groups_per_number).items()
                
            for setup_view in self.__setup_views:
                setup_view.calculate_values()
    
    def create_add_to_setup_buttons(self, current_number_of_buttons, configuration_class_gui):
        for existing_view in self.__setup_views:
            existing_view.create_add_to_setup_button(current_number_of_buttons, configuration_class_gui)
            
    def remove_add_to_setup_buttons(self, to_setup_buttons):
        for to_setup_button in to_setup_buttons:
            to_setup_button.get_view().remove_add_to_setup_button(to_setup_button)
            
    def create_linked_setup_class_gui(self, setup_class_gui_to_copy, configuration_class_gui, view_number_to_copy_to):
        view_to_copy_to = self.__setup_views[int(view_number_to_copy_to)]
        
        # Need to create a new group
        if setup_class_gui_to_copy.get_linked_group_number() == None:
            linked_group_number = len(self.__linked_groups_per_number)
            
            self.__linked_groups_per_number[linked_group_number] = [setup_class_gui_to_copy]
            setup_class_gui_to_copy.set_linked_group_number(linked_group_number)
            
        # Create new linked copy and add it to the group
        linked_setup_class_gui = view_to_copy_to.create_setup_class_gui(configuration_class_gui, setup_class=setup_class_gui_to_copy.get_setup_class(), linked_group_number=setup_class_gui_to_copy.get_linked_group_number())
        self.__linked_groups_per_number[linked_setup_class_gui.get_linked_group_number()].append(linked_setup_class_gui)
        
    def remove_setup_class_gui_from_linked_group(self, linked_setup_class_gui):
        linked_group_number = linked_setup_class_gui.get_linked_group_number()
        
        self.__linked_groups_per_number[linked_group_number].remove(linked_setup_class_gui)
        
        if len(self.__linked_groups_per_number[linked_group_number]) <= 1:
            for setup_class_gui in self.__linked_groups_per_number[linked_group_number]:
                setup_class_gui.set_linked_group_number(None)
                
            self.__linked_groups_per_number.pop(linked_group_number)
            
            # Decrement all group numbers above the removed one
            group_numbers = list(self.__linked_groups_per_number.keys())
            
            for group_number in group_numbers:
                if group_number > linked_group_number:
                    # Remove and add again with new number
                    group = self.__linked_groups_per_number.pop(group_number)
                    self.__linked_groups_per_number[group_number-1] = group
                    
                    # Set the new number in each setup class
                    for setup_class_gui in group:
                        setup_class_gui.set_linked_group_number(group_number-1)
        
    def get_configuration_classes(self):
        configuration_classes = []
        
        for existing_view in self.__views:
            if isinstance(existing_view, ConfigurationView):
                configuration_classes += existing_view.get_configuration_classes()
                
        return configuration_classes
        
    def get_root(self):
        return self.__root
        
    def create_view(self, is_configuration_view, view_name):
        if is_configuration_view:
            new_view = ConfigurationView(self, view_name)
        else:
            new_view = SetupView(self, view_name)
            
        new_view.grid(row=0, column=0, sticky="nswe")
        
        configuration_view_x = CANVAS_WIDTH // LENGTH_UNIT - 2 * CHANGE_VIEW_WIDTH
        setup_view_x = CANVAS_WIDTH // LENGTH_UNIT - CHANGE_VIEW_WIDTH
        
        # Add button to change to other views to the new view
        for i, configuration_view in enumerate(self.__configuration_views):
            GUIChangeViewButton(self, new_view, configuration_view_x, i*CHANGE_VIEW_HEIGHT, configuration_view.get_name(), configuration_view)
            
        for i, setup_view in enumerate(self.__setup_views):
            GUIChangeViewButton(self, new_view, setup_view_x, i*CHANGE_VIEW_HEIGHT, setup_view.get_name(), setup_view)
            
        # Add the new view to the existing ones
        if is_configuration_view:
            self.__configuration_views.append(new_view)
            
        else:
            self.__setup_views.append(new_view)
            
        # Add button to change to the new view to all existing views
        for view in self.__configuration_views + self.__setup_views:
            if is_configuration_view:
                GUIChangeViewButton(self, view, configuration_view_x, (len(self.__configuration_views)-1)*CHANGE_VIEW_HEIGHT, view_name, new_view)
                
            else:
                GUIChangeViewButton(self, view, setup_view_x, (len(self.__setup_views)-1)*CHANGE_VIEW_HEIGHT, view_name, new_view)
                        
    def change_view(self, view):
        view.tkraise()
        
    def reset_calculated_values_all_setup_views(self):
        for setup_view in self.__setup_views:
            setup_view.reset_calculated_values()
        
    def get_setup_view_names(self):
        return [view.get_name() for view in self.__setup_views]
        
    def create_connection(self, block, direction):
        connection = GUIConnection(self, block.get_view(), block, direction)
        block.get_view().set_held_connection(connection)
        
        return connection
        
    def save(self):
        for i, view in enumerate(self.__configuration_views + self.__setup_views):
            view.save(i)
