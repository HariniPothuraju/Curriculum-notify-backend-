import os
import openai
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///curriculum.db'  # Use your actual DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up OpenAI (replace with your API key)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Curriculum Model (example)
class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    topic = db.Column(db.String(100))
    deadline = db.Column(db.String(50))
    materials = db.Column(db.Text)

def get_curriculum_context(user_id):
    """Fetch user's curriculum data"""
    curriculum = Curriculum.query.filter_by(user_id=user_id).all()
    return "\n".join([
        f"Topic: {item.topic}, Deadline: {item.deadline}, Materials: {item.materials[:50]}..."
        for item in curriculum
    ])

def generate_tutor_response(prompt, curriculum_context):
    """Generate AI response with curriculum context"""
    system_message = f"""
    You are an AI tutor helping students with their curriculum. 
    Here's the student's current curriculum:
    {curriculum_context}
    
    Your responses should:
    1. Focus on the curriculum topics
    2. Help with understanding concepts
    3. Remind about deadlines
    4. Suggest study plans
    5. Be concise and educational
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

@app.route('/chat', methods=['POST'])
def chat_handler():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({"error": "Missing parameters"}), 400
    
    # Get curriculum context
    context = get_curriculum_context(user_id)
    
    # Generate AI response
    try:
        response = generate_tutor_response(message, context)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    