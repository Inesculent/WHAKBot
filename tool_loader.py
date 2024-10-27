import importlib
import json


def add_tool_to_json(filepath, module_name, function_name):

    # Read the module and function names from the file
    try:
        with open(filepath, 'r') as file:

            try:
                tool_data = json.load(file)
            except json.decoder.JSONDecodeError:
                print("JSON does not contain the specified data")
                tool_data = []


    except FileNotFoundError:
        tool_data = []


    new_entry = {"module": module_name, "function": function_name}

    if (new_entry not in tool_data):
        tool_data.append(new_entry)
    else:
        print("Tool data already exists")
        return

    with open(filepath, 'w') as file:
        json.dump(tool_data, file, indent=4)

    print(f"Successfully added {module_name} {function_name} to JSON")

def remove_tool_from_json(filepath, module_name, function_name):

    with open(filepath, 'r') as file:

        try:
            tool_data = json.load(file)
        except json.decoder.JSONDecodeError:
            print("JSON does not contain the specified data")
            return

    new_entry = {"module": module_name, "function": function_name}
    if (new_entry in tool_data):
        tool_data.remove(new_entry)

    with open(filepath, 'w') as file:
        json.dump(tool_data, file, indent=4)
        print(f"Successfully removed {module_name} {function_name} from JSON")
        return


def load_tool_from_json(filepath, tools):
    with open(filepath, 'r') as file:

        try:
            tool_data = json.load(file)
        except json.decoder.JSONDecodeError:
            print("JSON does not contain the specified data")
            return tools

        for entry in tool_data:


            mod_name = entry["module"]
            func_name = entry["function"]

            try:
                # Dynamically import the module
                module = importlib.import_module(mod_name)

                # Get the function from the module
                function = getattr(module, func_name)

                # Add the function to the list of tools
                tools.append(function)

                print(f"Successfully loaded {mod_name} {func_name} from JSON")
            except (ModuleNotFoundError, AttributeError) as e:
                # Print error but continue to the next tool
                print(f"Error: Could not load {mod_name}:{func_name}. {e}")

    return tools

