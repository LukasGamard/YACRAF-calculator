from view import ConfigurationView, SetupView
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
        
        # Create new views
        if new_save:
            self.create_view(True, "Configuration")
            
            for i in range(3):
                self.create_view(False, f"Setup {i+1}")
            
        # Restore saved views
        else:
            with open(FILE_PATHS_SAVES_PATH, "r") as file_with_paths:
                mapping_configuration_class_gui = {}
                
                for line in file_with_paths:
                    view_type, file_path = line.strip().split(",")
                    view_name = file_path.replace(".pickle", "").split("/")[-1]
                    
                    if view_type == "configuration":
                        configuration_view = self.create_view(True, view_name)
                        mapping_configuration_class_gui.update(configuration_view.restore_save(file_path))
                        
                    elif view_type == "setup":
                        setup_view = self.create_view(False, view_name)
                        setup_view.restore_save(file_path, mapping_configuration_class_gui, self.__linked_groups_per_number)
                            
                for setup_view in self.__setup_views:
                    setup_view.calculate_values()
                    
        self.change_view(self.__configuration_views[0])
        
    def create_add_to_setup_buttons(self, current_number_of_buttons, configuration_class_gui):
        for existing_setup_view in self.__setup_views:
            existing_setup_view.create_add_to_setup_button(current_number_of_buttons, configuration_class_gui)
            
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
        
        # Add button to change to other view from the new view
        for i, configuration_view in enumerate(self.__configuration_views):
            new_view.add_change_view_button(CHANGE_VIEW_CONFIGURATION_START_POSITION[0], CHANGE_VIEW_CONFIGURATION_START_POSITION[1]+i*CHANGE_VIEW_HEIGHT, configuration_view, False)
            
        for i, setup_view in enumerate(self.__setup_views):
            new_view.add_change_view_button(CHANGE_VIEW_SETUP_START_POSITION[0], CHANGE_VIEW_SETUP_START_POSITION[1]+i*CHANGE_VIEW_HEIGHT, setup_view, True)
            
        # Add the new view to the existing ones
        if is_configuration_view:
            self.__configuration_views.append(new_view)
        else:
            self.__setup_views.append(new_view)
            
        # Add button to change to the new view to all existing views
        for view in self.__configuration_views + self.__setup_views:
            if is_configuration_view:
                view.add_change_view_button(CHANGE_VIEW_CONFIGURATION_START_POSITION[0], (len(self.__configuration_views)-1)*CHANGE_VIEW_HEIGHT, new_view, False)
                
            else:
                view.add_change_view_button(CHANGE_VIEW_SETUP_START_POSITION[0], (len(self.__setup_views)-1)*CHANGE_VIEW_HEIGHT, new_view, True)
                
        if not is_configuration_view:
            for configuration_view in self.__configuration_views:
                for i, configuration_class_gui in enumerate(configuration_view.get_configuration_classes_gui()):
                    new_view.create_add_to_setup_button(i, configuration_class_gui)
                     
        return new_view
        
    def delete_view(self, view_to_delete):
        view_to_delete.delete()
        
        for view in self.__configuration_views + self.__setup_views:
            if view != view_to_delete:
                view.remove_change_view_button(view_to_delete)
                
        if view_to_delete in self.__configuration_views:
            self.__configuration_views.remove(view_to_delete)
            
        elif view_to_delete in self.__setup_views:
            self.__setup_views.remove(view_to_delete)
            
    def change_view(self, view):
        view.tkraise()
        
    def reset_calculated_values_all_setup_views(self):
        for setup_view in self.__setup_views:
            setup_view.reset_calculated_values()
        
    def get_setup_view_names(self):
        return [view.get_name() for view in self.__setup_views]
        
    def set_text_change_view_buttons(self, view_with_changed_name, text):
        # Go through all views and update the text of the corresponding change view button
        for view in self.__configuration_views + self.__setup_views:
            view.set_text_change_view_button(view_with_changed_name, text)
        
    def create_connection(self, block, direction):
        connection = GUIConnection(self, block.get_view(), block, direction)
        block.get_view().set_held_connection(connection)
        
        return connection
        
    def get_matching_setup_classes_gui(self, class_configuration_name, class_instance_name=None):
        matching_setup_classes = []
        
        for setup_view in self.__setup_views:
            matching_setup_classes += setup_view.get_matching_setup_classes_gui(class_configuration_name, class_instance_name)
            
        return matching_setup_classes
        
    def get_matching_setup_attributes_gui(self, attribute_name, class_configuration_name, class_instance_name=None):
        matching_setup_attributes = []
        
        for setup_view in self.__setup_views:
            matching_setup_attributes += setup_view.get_matching_setup_attributes_gui(attribute_name, class_configuration_name, class_instance_name)
            
        return matching_setup_attributes
        
    def save(self):
        # Create file where the path and view type of each saved view is stored, also storing the order of the views
        with open(FILE_PATHS_SAVES_PATH, "w") as file_with_paths:
            # Need to store configuration views first as they need to be restored before setup views so that they can use their configurations
            for view in self.__configuration_views + self.__setup_views:
                view_type, file_path = view.save()
                file_with_paths.write(f"{view_type},{file_path}\n")
