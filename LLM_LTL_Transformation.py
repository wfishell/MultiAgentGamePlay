import openai
import os
from dotenv import load_dotenv
import requests
import mimetypes
from typing import Optional, List
import json 
import re
def configure():
    load_dotenv()
def extract_python_codeblocks(text):
  pattern = r"```<JSON FILE>(.*?)\n```"
  matches = re.findall(pattern, text, re.DOTALL)
  return matches
def clean_json_string(json_string):
    # Remove newline characters and extra whitespace
    cleaned_string = json_string.replace('\n', '').replace('\\', '').strip()
    return cleaned_string
class ChatGPTClient:
    def __init__(self):
        configure()
        openai.api_key=os.getenv('api_key')

    def get_response(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # or "gpt-4" if you have access
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_token_completions=100
        )
        return response['choices'][0]['message']['content']

load_dotenv('Claude.env')

class ClaudeAIClient:
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

    def get_response(self, prompt: str, files: Optional[List[str]] = None, max_tokens: int = 1024):
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
    def FormalizeGame(self,Game_File):
        #Game_File Should be of the form "GameN_Description.txt"
        #This outputs an LTL specification and JSON file for system requirements
        try:
            prompt = """Generate an LTL formulation of the game based on the provided game description.
            Make sure to also specify the following in the JSON output:
            - "ltl_formulation": The complete LTL formulation.
            - "System_Player": An object containing:
                - "name": The name of the system player.
                - "init": System initialization conditions (if any).
                - "safety": System safety conditions (if any).
                - "prog": System progress conditions (if any).
            - "Environment_Player": An object containing:
                - "name": The name of the environment player.
                - "init": Environment initialization conditions (if any).
                - "safety": Environment safety conditions (if any).
                - "prog": Environment progress conditions (if any).
            - "Inputs": A non-empty list of inputs.
            - "Outputs": A non-empty list of outputs.

            Return the output as a JSON file formatted exactly as below, enclosed within the markers ```<JSON FILE>``` (do not include the markers in your output):

            ```<JSON FILE>
            {
                "ltl_formulation": "<LTL Formulation>",
                "System_Player": {
                    "name": "<System Player Name>",
                    "init": "<System Initialization Conditions>",
                    "safety": "<System Safety Conditions>",
                    "prog": "<System Progress Conditions>"
                },
                "Environment_Player": {
                    "name": "<Environment Player Name>",
                    "init": "<Environment Initialization Conditions>",
                    "safety": "<Environment Safety Conditions>",
                    "prog": "<Environment Progress Conditions>"
                },
                "Inputs": [<list of inputs>],
                "Outputs": [<list of outputs>]
            }
            ```<JSON FILE>

            Additionally, provide context explaining the JSON file and ensure that none of the fields are empty."""
        
            files = [f"./Games/{Game_File}"]
            
            if not os.path.exists(files[0]):
                raise FileNotFoundError(f"Game description file not found at {files[0]}")
                
            print(f"Sending request with file: {files[0]}")
            response = self.get_response(prompt, files=files)
            print("Claude Response:", response)
            json_file=extract_python_codeblocks(response)
            try:
                json_file = json_file[0]
            except (IndexError, TypeError):
                # If an error occurs, keep json_file as it is
                pass  # 
            json_file=clean_json_string(json_file)
            json_file = json.loads(json_file)
            with open('Reactive_Synthesis_Input.json','w') as file:
                json.dump(json_file,file)
        except FileNotFoundError as e:
            print(f"File error: {e}")
        except Exception as e:
            print(f"Error: {e}")
if __name__=='__main__':
    LLM=ClaudeAIClient()
    LLM.FormalizeGame('Game2_Description.txt')