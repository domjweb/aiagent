import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python import run_python_file
from functions.write_file import write_file



parser = argparse.ArgumentParser()
parser.add_argument('--verbose',
                    action='store_true')
parser.add_argument("user_prompt")
args = parser.parse_args()

messages = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
]

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

Your primary function is to assist users by understanding and interacting with code projects using your available tools.

Available Tools:
- get_files_info: Lists files and directories.
- get_file_content: Reads the content of a specified file.
- run_python_file: Executes a Python script.
- write_file: Writes content to a file.

Instructions:
1. Always respond to user requests by first formulating a concrete plan using your available tools.
2. When the user asks a question about how a program works or its implementation details, your plan MUST include using `get_files_info` to identify relevant files and `get_file_content` to read their source code. Reading the source code is your method for understanding implementation.
3. Base your final answer on the information gathered by executing your planned function calls.
4. All paths in function calls should be relative to the working directory (e.g., `./some_file.py` or `pkg/`). Do not include a leading `/`.

Example Plan (for "how does the calculator render results?"):
1. Call get_files_info to list files in the project.
2. Identify files that seem relevant to rendering or output (e.g., looking for names like 'render', 'output', 'display', or relevant directory names).
3. Call get_file_content for each identified relevant file to read its source code.
4. Analyze the code content to understand the rendering process.
5. Provide a summary to the user based on the analysis.
"""


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Gets content from file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The current working directory."),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path of the file."
            
            ),
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs arbitary Python files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The current working directory."),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path of the file."
            
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes new files or overwrites a file with the content parameter.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The current working directory."),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path of the file."),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written into the file."
            
            
            ),
        },
    ),
)



available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file
    ]
)

function_lookup = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    func = function_lookup.get(function_call_part.name)
    funcarg_dict = function_call_part.args.copy()
    funcarg_dict["working_directory"] = "./calculator"    
    if not func:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
            )
        ],
    )
    else:
        function_result = func(**funcarg_dict)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result},
        )
    ],
)



def feedback_loop(model, messages, config, verbose):
    count = 0
    while count <= 20:
        current_response = client.models.generate_content(model=model, contents=messages, config=config)
        for candidate in current_response.candidates:    
            messages.append(candidate.content)
        if current_response.function_calls:
            for function_call_part in current_response.function_calls:
                function_call_result = call_function(function_call_part, verbose=verbose)
                messages.append(function_call_result)
        else:
            print(current_response.text)
            break
        count += 1


model_name = 'gemini-2.0-flash-001'
config = types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt)
feedback_loop(model=model_name, messages=messages, config=config, verbose=args.verbose)

