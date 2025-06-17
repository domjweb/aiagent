import os

def write_file(working_directory, file_path, content):
    ac_file_path = os.path.join(working_directory, file_path)

    if not os.path.abspath(ac_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(os.path.dirname(ac_file_path)):
        os.makedirs(os.path.dirname(ac_file_path))
    
    try:
        with open(ac_file_path, "w") as f:
            writ_file = f.write(content)
            return f'Successfully wrote to "{file_path}" ({writ_file} characters written)'
    except Exception as e:
        return f"Error: {str(e)}"

    

    

