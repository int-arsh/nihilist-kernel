import os
from google import genai
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# load env variable
load_dotenv()

# configure api key
client = genai.Client()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# for cache response new file
CACHE_FILE = 'cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        if os.path.getsize(CACHE_FILE) > 0:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=4)



def generate_gemini_prompt(user_input):
    """
    Crafts the prompt for the Gemini API based on the user's input.
    """
    return f"""
Generate a dialogue between two characters, a nihilistic philosopher named Rust and a pragmatic, slightly-nervous partner named Marty, in the style of True Detective. The conversation should be about the following tech concept: "{user_input}".

Rust will start with a profound, dark, and existential take on the concept. He sees code, technology, and all of existence as a meaningless, recursive loop or a system without a true author. Marty, being more grounded and practical, will react with confusion or attempt to bring the conversation back to a technical understanding. Rust will then counter with an even more unsettling philosophical perspective.

The dialogue should be formatted with each character's name followed by their dialogue on a new line.

Example structure:
Marty: What are you thinking about?
Rust: The source. Not of the system—of everything.

If the topic "{user_input}" is not related to computer science, programming, or technology, provide a single, haunting response as
Rust and Marty didn't seek beyond Computers.
"""


@app.route('/api/generate', methods=['POST'])
def generate_dialogue():
    data = request.get_json()
    user_input = data.get('userInput', '').strip()

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # chwck in cache
    cache = load_cache()
    if user_input.lower() in cache:
        return jsonify({'dialogue': cache[user_input.lower()]})

    try:
        # Generate the prompt for the Gemini API
        prompt = generate_gemini_prompt(user_input)

        # # Create the model instance
        # model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate content using the crafted prompt
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents = prompt

        )
        
        # Extract the dialogue text from the response
        dialogue = response.text
        
        # Some API responses might start with unwanted characters, clean them up
        if dialogue.startswith('```') or dialogue.startswith('json'):
            dialogue = dialogue.replace('```', '').strip()

        # store cache
        cache[user_input.lower()] = dialogue
        save_cache(cache)

        return jsonify({'dialogue': dialogue})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to generate dialogue'}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)