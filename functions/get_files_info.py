import os

def get_files_info(working_directory, directory=None):
    actual_directory = os.path.join(working_directory, directory)

    if not os.path.abspath(actual_directory).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'


    if not os.path.isdir(actual_directory):
        return f'Error: "{directory}" is not a directory'
    try:
        items = os.listdir(actual_directory)
        result_list = []
        for item in items:
            full_path = os.path.join(actual_directory, item)
            form_line = f"- {item}: file_size={os.path.getsize(full_path)} bytes, is_dir={os.path.isdir(full_path)}"
            result_list.append(form_line)
    
        result_lines = "\n".join(result_list)
        return result_lines
    except Exception as e:
        return f"Error: {str(e)}"
    
        
   