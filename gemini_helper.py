import google.generativeai as genai
from config import Config
import json
import re

# Configure the API key
if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)

MODEL_NAME = 'gemini-3.6-flash'

def get_model():
    return genai.GenerativeModel(MODEL_NAME)

def generate_normal_response(prompt):
    """
    Sends a standard prompt to the Gemini API.
    """
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def extract_json_block(text):
    """Attempts to extract JSON from markdown code blocks or plain text."""
    match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try to find { } or [ ] blocks directly
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def generate_json_with_refinement(prompt, max_retries=2):
    """
    Attempts to generate valid JSON. If it fails to parse, it prompts the model again with the syntax error.
    Returns (json_data, final_raw_text, was_refined, success).
    """
    model = get_model()
    current_prompt = prompt
    was_refined = False
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(current_prompt)
            raw_text = response.text
            
            extracted_json = extract_json_block(raw_text)
            
            # Try to parse it
            parsed_data = json.loads(extracted_json)
            
            # If successful
            return parsed_data, raw_text, was_refined, True
            
        except json.JSONDecodeError as e:
            # It failed. If we have retries left, refine the prompt.
            was_refined = True
            current_prompt = f"{prompt}\n\nThe previous attempt produced invalid JSON. Error: {str(e)}. Please provide ONLY valid, parseable JSON without extra text."
        except Exception as e:
            return None, f"Error: {str(e)}", was_refined, False

    return None, raw_text, was_refined, False
