import os
import subprocess


def run_python_file(working_directory, file_path):
    ac_file_path = os.path.join(working_directory, file_path)

    if not os.path.abspath(ac_file_path).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(ac_file_path):
        return f'Error: File "{file_path}" not found.'
    
    if not ac_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        subp = subprocess.run(["python3", file_path], capture_output=True, cwd=working_directory, timeout=30)
        sout = subp.stdout.decode('utf-8')
        serr = subp.stderr.decode('utf-8')
        rcode = subp.returncode
        
        if not sout and not serr:
            return f"No output produced"
        output_lines = [f"STDOUT: {sout}", f"STDERR: {serr}"]
        if rcode != 0:
            output_lines.append(f"Process exited with code {rcode}")
            return "\n".join(output_lines)
        else:
            return "\n".join(output_lines)  
    except Exception as e:
        return f"Error: executing Python file: {str(e)}"
        

    




    

