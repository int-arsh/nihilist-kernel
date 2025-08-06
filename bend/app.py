import os
from google import genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# load env variable
load_dotenv()

# configure api key
client = genai.Client()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dialogue_cache.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db = SQLAlchemy(app) # Initialize SQLAlchemy



CORS(app, resources={r"/api/*": {"origins": "https://nihilist-kernel.vercel.app"}})


class DialogueEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_text = db.Column(db.String(200), unique=True, nullable=False)
    dialogue_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<DialogueEntry {self.input_text}>'




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
"""


@app.route('/api/generate', methods=['POST'])
def generate_dialogue():
    data = request.get_json()
    user_input = data.get('userInput', '').strip().lower()

    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # chwck in cache
    cached_entry = DialogueEntry.query.filter_by(input_text=user_input).first()
    if cached_entry:
        print(f"Returning from SQLite cache for input: {user_input}")
        return jsonify({'dialogue': cached_entry.dialogue_response})

    try:
        prompt = generate_gemini_prompt(user_input)

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents = prompt
        )
        
        dialogue = response.text
        
        # Some API responses might start with unwanted characters, clean them up
        if dialogue.startswith('```') or dialogue.startswith('json'):
            dialogue = dialogue.replace('```', '').strip()

        # store cache
        new_entry = DialogueEntry(input_text=user_input, dialogue_response=dialogue)
        db.session.add(new_entry)
        db.session.commit()
        print(f"Stored new entry in SQLite for input: {user_input}")

        return jsonify({'dialogue': dialogue})

    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback() 
        return jsonify({'error': 'Failed to generate dialogue'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created/checked.")
    app.run(port=5000, debug=True)