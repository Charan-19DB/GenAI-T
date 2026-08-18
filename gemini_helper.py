import google.generativeai as genai
from config import Config
import json
import re

# Candidate models in order of preference for high compatibility
CANDIDATE_MODELS = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp', 'gemini-3.6-flash']

def configure_api():
    key = Config.GEMINI_API_KEY
    if key:
        clean_key = str(key).strip().strip("'").strip('"')
        genai.configure(api_key=clean_key)
    else:
        raise Exception("GEMINI_API_KEY environment variable is not configured.")

def generate_content_with_fallback(prompt):
    """
    Attempts to generate content trying candidate Gemini models.
    """
    configure_api()
    last_exception = None

    for model_name in CANDIDATE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text
        except Exception as e:
            last_exception = e
            continue
            
    raise Exception(f"Gemini API Error: {str(last_exception)}")

def generate_normal_response(prompt):
    """
    Sends a standard prompt to the Gemini API with automatic model fallbacks.
    """
    try:
        return generate_content_with_fallback(prompt)
    except Exception as e:
        return f"Error generating response: {str(e)}"

def extract_json_block(text):
    """Attempts to extract JSON from markdown code blocks or plain text."""
    match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    
    match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def generate_json_with_refinement(prompt, max_retries=2):
    """
    Attempts to generate valid JSON. If it fails to parse, it prompts the model again with the syntax error.
    Returns (json_data, final_raw_text, was_refined, success).
    """
    current_prompt = prompt
    was_refined = False
    raw_text = ""
    
    for attempt in range(max_retries):
        try:
            raw_text = generate_content_with_fallback(current_prompt)
            extracted_json = extract_json_block(raw_text)
            
            # Try to parse it
            parsed_data = json.loads(extracted_json)
            return parsed_data, raw_text, was_refined, True
            
        except json.JSONDecodeError as e:
            was_refined = True
            current_prompt = f"{prompt}\n\nThe previous attempt produced invalid JSON. Error: {str(e)}. Please provide ONLY valid, parseable JSON without extra text."
        except Exception as e:
            return None, f"Error: {str(e)}", was_refined, False

    return None, raw_text, was_refined, False
