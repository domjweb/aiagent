import os

def get_file_content(working_directory, file_path):
    ac_file_path = os.path.join(working_directory, file_path)

    if not os.path.abspath(ac_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(ac_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        max_chars = 10000
        with open(ac_file_path, "r") as fi:
            file_content_string = fi.read(max_chars)
            next_char = fi.read(1)
        
        if next_char:
            return f"{file_content_string} [...File '{file_path}' truncated at 10000 characters]"
        else:
            return file_content_string
    except Exception as e:
        return f"Error:{str(e)}"
    



    

