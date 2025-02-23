import openai
import os
from dotenv import load_dotenv
import requests
import mimetypes
from typing import Optional, List
import json 
import re
import textwrap
import autopep8

def configure():
    load_dotenv()
def extract_python_codeblocks(text):
    # First, try to find code blocks with ```<python>```
    pattern1 = r"```<python>(.*?)\n```"
    matches = re.findall(pattern1, text, re.DOTALL)

    # If no matches found, try to find code blocks with ```python```
    if not matches:
        pattern2 = r"```python(.*?)\n```"
        matches = re.findall(pattern2, text, re.DOTALL)

    return matches
def clean_json_string(json_string):
    # Remove newline characters and extra whitespace
    cleaned_string = json_string.replace('\n', '').replace('\\', '').strip()
    return cleaned_string

load_dotenv('Claude.env')

class ClaudeMainGeneration:
    def __init__(self):
        self.api_key = os.getenv('Claude_Key')
        self.api_url = "https://api.anthropic.com/v1/messages"

    def _read_text_file(self, file_path: str) -> dict:
        """Read a text file and return it in the correct format for the API."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r') as file:
            text_content = file.read()

        return {
            "type": "text",
            "text": text_content
        }

    def get_response(self, prompt: str, files: Optional[List[str]] = None, max_tokens: int = 4096):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Prepare message content
        message_content = []

        # Add text prompt
        message_content.append({
            "type": "text",
            "text": prompt
        })

        # Process files if provided
        if files:
            print(f"Processing {len(files)} files...")
            for file_path in files:
                try:
                    print(f"Processing file: {file_path}")
                    file_data = self._read_text_file(file_path)
                    message_content.append(file_data)
                    print(f"Successfully read file: {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    raise

        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        }

        try:
            print("Sending request to Claude API...")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            print("Successfully received response from API")
            return response.json()['content'][0]['text']
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
    def GenerateMain(self, Game_File, Enviorment_File, ReactiveSynthesis_File, MultiPathPlanning_Template_File):
        # Game_File Should be of the form "GameN_Description.txt"
        # This outputs an LTL specification and JSON file for system requirements
        try:
            prompt = """
            Given the description of this game and the reactive synthesis inputs, use the MultiPathPlanning_Template and Environment python files to implement a continuous run of this game ensuring all liveness and system constraints. Do not leave functions empty with only comments; ensure all functions have a purpose. Ensure that this simulation runs continuously. Generate a python file and have the python surrounded by ```<python>```. Furthermore, give an explanation as to why this code satisfies all liveness and safety constraints laid out in the json file in two sentences.
            """
            
            files = [f"./Games/{Game_File}", f"{Enviorment_File}", f"{ReactiveSynthesis_File}", f"{MultiPathPlanning_Template_File}"]
            
            if not os.path.exists(files[0]):
                raise FileNotFoundError(f"Game description file not found at {files[0]}")
                
            print(f"Sending request with file: {files[0]}")
            response = self.get_response(prompt, files=files)
            print("Claude Response:", response)
            
            # Extract Python code blocks
            python_code_blocks = extract_python_codeblocks(response)

            # Check if the list is not empty before accessing the first element
            if python_code_blocks:
                python_code = python_code_blocks[0]  # Safely access the first code block
            else:
                raise ValueError("No Python code blocks found in the response.")

            # Clean the extracted Python code
            python_code = clean_json_string(python_code)

            # Indent the code properly
            indented_code = textwrap.indent(python_code, '    ')  # Indent with 4 spaces

            # Write the indented code to a file
            with open('Main_Test.py', 'w') as file:
                file.write(indented_code)

        except FileNotFoundError as e:
            print(f"File error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    
    def FineTuneGame(self, Game_File, Main_Test_File, Reactive_Synthesis_File):
        # Game_File Should be of the form "GameN_Description.txt"
        # This outputs a fully implemented game for a theoretical infinite number of states
        try:
            prompt = """
            Given the Main_Test File template, fully implement the todos and empty functions for this game for a theoretical infinite number of states. 
            Check the Reactive_Synthesis_Input JSON to ensure all safety constraints are satisfied, 
            and cross-check with the game description that the final code satisfies the game. 
            Generate a python file and have the python surrounded by ```<python>```. 
            Furthermore, give an explanation as to why this code satisfies all liveness and safety constraints and runs without user interaction.
            """
            
            files = [f"./Games/{Game_File}", f"{Main_Test_File}", f"{Reactive_Synthesis_File}"]
            
            if not os.path.exists(files[0]):
                raise FileNotFoundError(f"Game description file not found at {files[0]}")
                
            print(f"Sending request with file: {files[0]}")
            response = self.get_response(prompt, files=files)
            print("Claude Response:", response)
            
            # Extract Python code blocks
            python_code_blocks = extract_python_codeblocks(response)

            # Check if the list is not empty before accessing the first element
            if python_code_blocks:
                python_code = python_code_blocks[0]  # Safely access the first code block
            else:
                raise ValueError("No Python code blocks found in the response.")

            # Clean the extracted Python code
            python_code = clean_json_string(python_code)

            # Indent the code properly
            indented_code = textwrap.indent(python_code, '    ')  # Indent with 4 spaces

            # Write the indented code to a file
            with open('FineTuned_Game.py', 'w') as file:
                file.write(indented_code)

        except FileNotFoundError as e:
            print(f"File error: {e}")
        except Exception as e:
            print(f"Error: {e}")
if __name__=='__main__':
    LLM=ClaudeMainGeneration()
    LLM.GenerateMain('Game2_Description.txt','Enviorment1.py','Reactive_Synthesis_Input.json', 'MultiPathPlanning_Template.py')
    LLM.FineTuneGame('Game2_Description.txt','Main_Test.py','Reactive_Synthesis_Input.json')