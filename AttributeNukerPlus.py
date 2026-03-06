#Author-Ed Johnson - Making With An EdJ
#Description-Search attributes, parse JSON, and selectively nuke keys or whole attributes.

import adsk.core, adsk.fusion, adsk.cam, traceback
import json

# Global list to store our custom "Row Objects" so we track what each table row represents
row_items = []
# Global list to keep handlers alive
_handlers = []

class RowItem:
    """Helper class to track what a specific table row points to."""
    def __init__(self, attr_id, attr, is_root=True, key_name=None, value_display=""):
        self.attr_id = attr_id      # Unique integer ID for the attribute (to use as dict key)
        self.attr = attr
        self.is_root = is_root      # True if this row deletes the WHOLE attribute
        self.key_name = key_name    # If not root, this is the specific JSON key (str) or index (int) to delete
        self.value_display = value_display

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        
        if not design:
            ui.messageBox('No active design found.')
            return

        cmd_def = ui.commandDefinitions.itemById('AttributeNukerCmd')
        if cmd_def:
            cmd_def.deleteMe()

        cmd_def = ui.commandDefinitions.addButtonDefinition(
            'AttributeNukerCmd', 
            'Attribute Nuke Tool', 
            'Search and delete attributes/keys', 
            ''
        )

        on_command_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        _handlers.append(on_command_created)

        cmd_def.execute()
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            app = adsk.core.Application.get()
            design = app.activeProduct

            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            _handlers.append(on_execute)

            on_destroy = CommandDestroyHandler()
            cmd.destroy.add(on_destroy)
            _handlers.append(on_destroy)
            
            # 1. Search for ALL attributes
            raw_attributes = design.findAttributes('', '')
            
            if len(raw_attributes) == 0:
                inputs.addTextBoxCommandInput('noAttrs', '', 'No attributes found.', 2, True)
                return

            # 2. Process Attributes into RowItems (Handling JSON parsing)
            global row_items
            row_items = []
            
            # Enumerate to get a unique integer ID for each attribute
            for attr_id, attr in enumerate(raw_attributes):
                attr_val = str(attr.value)
                is_json_container = False
                json_data = None

                # Try parsing as JSON
                try:
                    parsed = json.loads(attr_val)
                    # Check for Dict OR List
                    if isinstance(parsed, (dict, list)):
                        is_json_container = True
                        json_data = parsed
                except:
                    pass

                # Add the "Root" item (The attribute itself)
                root_display = "{ JSON Container }" if is_json_container else attr_val
                row_items.append(RowItem(attr_id, attr, is_root=True, value_display=root_display))

                # If it was a container, add rows for keys/indices
                if is_json_container:
                    if isinstance(json_data, dict):
                        for key, val in json_data.items():
                            row_items.append(RowItem(attr_id, attr, is_root=False, key_name=key, value_display=str(val)))
                    elif isinstance(json_data, list):
                        for i, val in enumerate(json_data):
                            row_items.append(RowItem(attr_id, attr, is_root=False, key_name=i, value_display=str(val)))

            # 3. Create Table
            table = inputs.addTableCommandInput('attrTable', 'Attributes', 5, '1:2:4:5:2')
            table.maximumVisibleRows = 20
            table.minimumVisibleRows = 5
            table.columnSpacing = 1
            
            inputs.addTextBoxCommandInput('info', '', f'Found {len(raw_attributes)} attributes. Expanded JSON items are indented.', 2, True)

            # 4. Populate Table from row_items
            for i, item in enumerate(row_items):
                # Checkbox
                check_input = table.commandInputs.addBoolValueInput(f'check_{i}', '', True, '', False)
                table.addCommandInput(check_input, i, 0)
                
                # Group
                group_text = item.attr.groupName if item.is_root else ""
                group_input = table.commandInputs.addStringValueInput(f'group_{i}', '', group_text)
                group_input.isReadOnly = True
                table.addCommandInput(group_input, i, 1)
                
                # Name (Indented if key/item)
                if item.is_root:
                    name_text = item.attr.name
                else:
                    # Differentiate display for List Items vs Dict Keys
                    if isinstance(item.key_name, int):
                        name_text = f"   ↳ Item [{item.key_name}]"
                    else:
                        name_text = f"   ↳ Key: {item.key_name}"
                    
                name_input = table.commandInputs.addStringValueInput(f'name_{i}', '', name_text)
                name_input.isReadOnly = True
                table.addCommandInput(name_input, i, 2)
                
                # Value (Cleaned for display)
                raw_val = item.value_display
                flat_val = raw_val.replace('\n', ' ').replace('\r', '')
                if len(flat_val) > 60: 
                    flat_val = flat_val[:57] + "..."
                
                val_input = table.commandInputs.addStringValueInput(f'val_{i}', '', flat_val)
                val_input.isReadOnly = True
                val_input.tooltip = raw_val 
                table.addCommandInput(val_input, i, 3)
                
                # Parent Type (Only show on root to reduce noise)
                parent_type = ""
                if item.is_root:
                    try:
                        if item.attr.parent:
                            parent_type = item.attr.parent.objectType.split('::')[-1]
                    except:
                        pass
                
                parent_input = table.commandInputs.addStringValueInput(f'parent_{i}', '', parent_type)
                parent_input.isReadOnly = True
                table.addCommandInput(parent_input, i, 4)

        except:
            if app.userInterface:
                app.userInterface.messageBox('Panel Create Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            inputs = args.command.commandInputs
            
            global row_items
            
            # Map attributes to the actions we need to take
            # Use 'attr_id' (int) as the dictionary key since Attributes are not hashable
            operations = {}
            
            for i, item in enumerate(row_items):
                check_input = inputs.itemById(f'check_{i}')
                if not check_input: continue
                
                if item.attr_id not in operations:
                    operations[item.attr_id] = {'attr': item.attr, 'delete_root': False, 'keys_to_remove': []}
                
                if check_input.value:
                    if item.is_root:
                        operations[item.attr_id]['delete_root'] = True
                    else:
                        operations[item.attr_id]['keys_to_remove'].append(item.key_name)
            
            deleted_count = 0
            updated_count = 0
            
            for op in operations.values():
                attr = op['attr']
                if not attr.isValid: continue
                
                if op['delete_root']:
                    # Nuke the whole thing
                    attr.deleteMe()
                    deleted_count += 1
                elif len(op['keys_to_remove']) > 0:
                    # Partial Nuke: Read, Remove Keys/Items, Save
                    try:
                        current_val = json.loads(attr.value)
                        
                        if isinstance(current_val, dict):
                            for k in op['keys_to_remove']:
                                if k in current_val:
                                    del current_val[k]
                                    
                        elif isinstance(current_val, list):
                            # CRITICAL: When deleting from a list by index, we must delete 
                            # from largest index to smallest, otherwise indices shift!
                            # Filter for ints (just in case) and sort descending
                            indices_to_pop = sorted([k for k in op['keys_to_remove'] if isinstance(k, int)], reverse=True)
                            
                            for idx in indices_to_pop:
                                if 0 <= idx < len(current_val):
                                    current_val.pop(idx)
                        
                        attr.value = json.dumps(current_val)
                        updated_count += 1
                    except Exception as e:
                        print(f"Failed to update attribute: {e}")

            ui.messageBox(f'Operation Complete:\nAttributes Deleted: {deleted_count}\nAttributes Updated (Items/Keys Removed): {updated_count}')

        except:
            if app.userInterface:
                app.userInterface.messageBox('Execute Failed:\n{}'.format(traceback.format_exc()))

class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            pass