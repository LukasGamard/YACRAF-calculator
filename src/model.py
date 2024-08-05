import os
from view import ConfigurationView, SetupView
from setup_gui import GUISetupAttribute
from connection_gui import GUIConnection
from helper_functions import delete_all
from config import *

class Model:
    def __init__(self, root, new_save, *, num_configuration_views=1, num_setup_views=3):
        self.__root = root
        self.__configuration_views = []
        self.__setup_views = []
        self.__current_view = None
        
        self.__currently_pressed_keys = set()
        
        self.__linked_configuration_groups_per_number = {}
        self.__linked_setup_groups_per_number = {}
        
        self.__root.title("Canvas")
        self.__root.geometry(f"{CANVAS_WIDTH}x{CANVAS_HEIGHT}")
        self.__root.rowconfigure(0, weight=1)
        self.__root.columnconfigure(0, weight=1)
        
        # Create new views
        if new_save:
            for i in range(num_configuration_views):
                self.create_view(True, "Configuration")
                
            for i in range(num_setup_views):
                self.create_view(False, f"Setup {i+1}")
                
        # Restore saved views
        else:
            with open(f"{BASE_PATH}/{FILE_PATHS_SAVES_PATH}", "r") as file_with_paths:
                mapping_configuration_class_gui = {}
                
                for line in file_with_paths:
                    file_path = line.strip()
                    view_directory_path, view_name = os.path.split(file_path)
                    view_name = view_name.replace(".pickle", "")
                    
                    if view_directory_path == CONFIGURATION_SAVES_PATH:
                        configuration_view = self.create_view(True, view_name)
                        mapping_configuration_class_gui.update(configuration_view.restore_save(file_path, self.__linked_configuration_groups_per_number))
                        
                    elif view_directory_path == SETUP_SAVES_PATH:
                        setup_view = self.create_view(False, view_name)
                        setup_view.restore_save(file_path, mapping_configuration_class_gui, self.__linked_setup_groups_per_number)
                        
                self.calculate_values()
                
        if len(self.__configuration_views) > 0:
            self.change_view(self.__configuration_views[0])
            
        elif len(self.__setup_views) > 0:
            self.change_view(self.__setup_views[0])
            
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        
        # self.__configuration_classes_gui_to_copy = []
        
    def on_key_press(self, event):
        key = event.keysym
        self.__currently_pressed_keys.add(key.lower())
        
        print(key)
        
        if key == "BackSpace":
            items_to_delete = []
            
            for selected_item in list(self.__current_view.get_selected_items()):
                if not isinstance(selected_item, GUISetupAttribute):
                    items_to_delete.append(selected_item)
                    
            delete_all(items_to_delete)
            
        elif key == "Escape":
            self.__current_view.reset_held_connection(True)
            
        elif key.lower() == "e":
            selected_items = list(self.__current_view.get_selected_items())
            
            if len(selected_items) > 0:
                for selected_item in selected_items:
                    selected_item.open_options()
                    
            elif self.__root.focus_get() == self.__current_view.get_canvas():
                self.__current_view.open_options()
                
        """
        elif "Control_L" in self.__currently_pressed_keys and ("c" in self.__currently_pressed_keys or "C" in self.__currently_pressed_keys):
            self.__configuration_classes_gui_to_copy = list(self.__current_view.get_selected_items())
            
        elif "Control_L" in self.__currently_pressed_keys and ("v" in self.__currently_pressed_keys or "V" in self.__currently_pressed_keys):
            for configuration_class_gui_to_copy in self.__configuration_classes_gui_to_copy:
                self.__current_view.create_configuration_class_gui_copy(configuration_class_gui_to_copy)
        """
        
    def on_key_release(self, event):
        key = event.keysym
        
        if key.lower() in self.__currently_pressed_keys:
            self.__currently_pressed_keys.remove(key.lower())
            
    def is_currently_pressing_key(self, key):
        return key.lower() in self.__currently_pressed_keys
        
    def create_add_to_setup_buttons(self, current_number_of_buttons, configuration_class_gui):
        for existing_setup_view in self.__setup_views:
            existing_setup_view.create_add_to_setup_button(current_number_of_buttons, configuration_class_gui)
            
    def remove_add_to_setup_buttons(self, to_setup_buttons):
        for to_setup_button in to_setup_buttons:
            to_setup_button.get_view().remove_add_to_setup_button(to_setup_button)
            
    def get_linked_configuration_classes_gui(self, configuration_class_gui):
        linked_group_number = configuration_class_gui.get_linked_group_number()
        
        if linked_group_number == None:
            return []
            
        linked_configuration_classes_gui = self.__linked_configuration_groups_per_number[linked_group_number].copy()
        linked_configuration_classes_gui.remove(configuration_class_gui)
            
        return linked_configuration_classes_gui
        
    def get_linked_configuration_attributes_gui(self, configuration_attribute_gui):
        if configuration_attribute_gui.get_configuration_class_gui().get_linked_group_number() == None:
            return []
            
        linked_configuration_attributes_gui = []
        attribute_index = configuration_attribute_gui.get_configuration_class_gui().get_configuration_attributes_gui().index(configuration_attribute_gui)
        
        for linked_configuration_class_gui in self.get_linked_configuration_classes_gui(configuration_attribute_gui.get_configuration_class_gui()):
            linked_configuration_attributes_gui.append(linked_configuration_class_gui.get_configuration_attributes_gui()[attribute_index])
            
        return linked_configuration_attributes_gui
        
    def create_linked_configuration_class_gui(self, configuration_class_gui_to_copy, view_to_copy_to):
        self.attempt_to_create_linked_group(configuration_class_gui_to_copy, view_to_copy_to, self.__linked_configuration_groups_per_number)
        
        linked_configuration_class_gui = view_to_copy_to.create_configuration_class_gui_copy(configuration_class_gui_to_copy)
        self.__linked_configuration_groups_per_number[linked_configuration_class_gui.get_linked_group_number()].append(linked_configuration_class_gui)
            
        return linked_configuration_class_gui
        
    def get_linked_setup_classes_gui(self, setup_class_gui):
        linked_group_number = setup_class_gui.get_linked_group_number()
        
        if linked_group_number == None:
            return []
            
        linked_setup_classes_gui = self.__linked_setup_groups_per_number[linked_group_number].copy()
        linked_setup_classes_gui.remove(setup_class_gui)
        
        return linked_setup_classes_gui
        
    def create_linked_setup_class_gui(self, setup_class_gui_to_copy, configuration_class_gui, view_to_copy_to, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        self.attempt_to_create_linked_group(setup_class_gui_to_copy, view_to_copy_to, self.__linked_setup_groups_per_number)
            
        # Create new linked copy and add it to the group
        linked_setup_class_gui = view_to_copy_to.create_setup_class_gui(configuration_class_gui, x=x, y=y, setup_class=setup_class_gui_to_copy.get_setup_class(), linked_group_number=setup_class_gui_to_copy.get_linked_group_number())
        self.__linked_setup_groups_per_number[linked_setup_class_gui.get_linked_group_number()].append(linked_setup_class_gui)
        
        return linked_setup_class_gui
        
    def attempt_to_create_linked_group(self, class_gui_to_copy, view_to_copy_to, linked_groups_per_number):
        # Need to create a new group
        if class_gui_to_copy.get_linked_group_number() == None:
            linked_group_number = len(linked_groups_per_number)
            
            linked_groups_per_number[linked_group_number] = [class_gui_to_copy]
            class_gui_to_copy.set_linked_group_number(linked_group_number)
        
    def remove_class_gui_from_linked_group(self, linked_class_gui, is_configuration_view):
        linked_group_number = linked_class_gui.get_linked_group_number()
        
        if is_configuration_view:
            linked_groups_per_number = self.__linked_configuration_groups_per_number
        else:
            linked_groups_per_number = self.__linked_setup_groups_per_number
        
        linked_groups_per_number[linked_group_number].remove(linked_class_gui)
        
        # Should remove group as there is at most only one class in it
        if len(linked_groups_per_number[linked_group_number]) <= 1:
            for class_gui in linked_groups_per_number[linked_group_number]:
                class_gui.set_linked_group_number(None)
                
            linked_groups_per_number.pop(linked_group_number)
            
            # Decrement all group numbers above the removed one
            for group_number in list(linked_groups_per_number.keys()):
                if group_number > linked_group_number:
                    # Remove and add again with new number
                    group = linked_groups_per_number.pop(group_number)
                    linked_groups_per_number[group_number-1] = group
                    
                    # Set the new number in each setup class
                    for class_gui in group:
                        class_gui.set_linked_group_number(group_number-1)
        
    def get_configuration_classes(self):
        configuration_classes = []
        
        for existing_view in self.__views:
            if isinstance(existing_view, ConfigurationView):
                configuration_classes += existing_view.get_configuration_classes()
                
        return configuration_classes
        
    """
    def get_matching_setup_classes_gui(self, *, view_name=None, class_configuration_name=None, class_instance_name=None):
        matching_setup_classes_gui = []
        
        for setup_view in self.__setup_views:
            if view_name == None or setup_view.get_name() == view_name:
                for setup_class_gui in setup_view.get_matching_setup_classes_gui(class_configuration_name=class_configuration_name, class_instance_name=class_instance_name):
                    matching_setup_classes_gui.append(setup_class_gui)
                    
        return matching_setup_classes_gui
        
    def get_matching_setup_attributes_gui(self, *, view_name=None, class_configuration_name=None, class_instance_name=None, attribute_name=None):
        matching_setup_attributes_gui = []
        
        for matching_setup_class_gui in self.get_matching_setup_classes_gui(view_name=view_name, class_configuration_name=class_configuration_name, class_instance_name=class_instance_name):
            for setup_attribute_gui in matching_setup_class_gui.get_setup_attributes_gui():
                if not setup_attribute_gui.is_hidden():
                    if attribute_name == None or setup_attribute_gui.get_name() == attribute_name:
                        matching_setup_attributes_gui.append(setup_attribute_gui)
                        
        return matching_setup_attributes_gui
    """
    
    def get_root(self):
        return self.__root
        
    def get_configuration_views(self):
        return self.__configuration_views
        
    def get_setup_views(self):
        return self.__setup_views
        
    def swap_view_places(self, view_to_move, move_up):
        views_to_consider_moving = []
        
        if view_to_move in self.__configuration_views:
            views_to_consider_moving = self.__configuration_views
            
        elif view_to_move in self.__setup_views:
            views_to_consider_moving = self.__setup_views
            
        for i in range(len(views_to_consider_moving)):
            if views_to_consider_moving[i] is view_to_move:
                if (move_up and i > 0) or (not move_up and i < len(views_to_consider_moving) - 1):
                    for view in self.__configuration_views + self.__setup_views:
                        if move_up:
                            view.move_change_view_button(views_to_consider_moving[i], True)
                            view.move_change_view_button(views_to_consider_moving[i-1], False)
                            
                        else:
                            view.move_change_view_button(views_to_consider_moving[i], False)
                            view.move_change_view_button(views_to_consider_moving[i+1], True)
                            
                    if move_up:
                        views_to_consider_moving[i], views_to_consider_moving[i-1] = views_to_consider_moving[i-1], views_to_consider_moving[i]
                        
                    else:
                        views_to_consider_moving[i], views_to_consider_moving[i+1] = views_to_consider_moving[i+1], views_to_consider_moving[i]
                        
                    break
                    
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
        
        # Remove button to change to the deleted view from all other views
        for view in self.__configuration_views + self.__setup_views:
            if view != view_to_delete:
                view.remove_change_view_button(view_to_delete)
                
        # Remove reference to button to convert each configuration class to a setup class from each configuration class
        for configuration_view in self.__configuration_views:
            if configuration_view != view_to_delete:
                for configuration_class_gui in configuration_view.get_configuration_classes_gui():
                    configuration_class_gui.remove_to_setup_button(view_to_delete)
                    
        # Remove reference to view
        if view_to_delete in self.__configuration_views:
            self.__configuration_views.remove(view_to_delete)
            
        elif view_to_delete in self.__setup_views:
            self.__setup_views.remove(view_to_delete)
            
    def change_view(self, view):
        self.__current_view = view
        view.tkraise()
        
        self.__current_view.get_canvas().focus_set()
        
    def get_num_configuration_classes(self):
        num_configuration_classes = 0
        
        for view in self.__configuration_views:
            num_configuration_classes += len(view.get_configuration_classes_gui())
            
        return num_configuration_classes
        
    def reset_script_changes(self):
        for setup_view in self.__setup_views:
            for setup_class_gui in setup_view.get_setup_classes_gui():
                setup_class_gui.reset_changes_by_scripts()
                
        self.calculate_values()
        
    def calculate_values(self):
        # Reset all values first
        for setup_view in self.__setup_views:
            setup_view.reset_calculated_values()
            
        # Calculate new values
        for setup_view in self.__setup_views:
            setup_view.calculate_values()
            
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
        
    def update_duplicate_view_name(self, view, existing_view_names):
        added_number = 1
        
        while view.get_name() in existing_view_names:
            view.set_name(f"{view.get_name()} ({added_number})")
        
    def save(self):
        configuration_view_names = set()
        setup_view_names = set()
        
        # Create file where the path and view type of each saved view is stored, also storing the order of the views
        with open(f"{BASE_PATH}/{FILE_PATHS_SAVES_PATH}", "w") as file_with_paths:
            # Need to store configuration views first as they need to be restored before setup views so that they can use their configurations
            for configuration_view in self.__configuration_views:
                self.update_duplicate_view_name(configuration_view, configuration_view_names)
                configuration_view_names.add(configuration_view.get_name())
                
                file_path = configuration_view.save()
                file_with_paths.write(f"{file_path}\n")
                
            for setup_view in self.__setup_views:
                self.update_duplicate_view_name(setup_view, setup_view_names)
                setup_view_names.add(setup_view.get_name())
                
                file_path = setup_view.save()
                file_with_paths.write(f"{file_path}\n")
