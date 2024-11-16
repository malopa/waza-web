from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qa_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the QuestionAnswer model
class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        return {"id": self.id, "question": self.question, "answer": self.answer}

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    # qa_list = QuestionAnswer.query.all()
    return render_template('home.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Receive a question, find the answer, or respond with 'Answer not found'."""
    data = request.json  # Get JSON payload
    question = data.get('question')  # Extract the question from the payload

    # Validate input
    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Search for an answer in the database
    answer_entry = QuestionAnswer.query.filter(
        QuestionAnswer.question.ilike(f"%{question}%")
    ).first()

    # Respond with the answer if found, otherwise indicate 'Answer not found'
    if answer_entry:
        return jsonify({
            "question": answer_entry.question,
            "answer": answer_entry.answer
        })
    else:
        return jsonify({"answer": "I didn't find an aswer for your question please contact system admin","status":'custom'}), 404



@app.route('/questions', methods=['GET'])
def get_questions():
    qa_list = QuestionAnswer.query.all()
    return jsonify([qa.to_dict() for qa in qa_list])

@app.route('/question', methods=['POST'])
def add_question():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or not answer:
        return jsonify({"error": "Both question and answer are required"}), 400

    new_qa = QuestionAnswer(question=question, answer=answer)
    db.session.add(new_qa)
    db.session.commit()

    return jsonify(new_qa.to_dict()), 201

@app.route('/question/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    qa_entry = QuestionAnswer.query.get(question_id)
    if not qa_entry:
        return jsonify({"error": "Question not found"}), 404

    if question:
        qa_entry.question = question
    if answer:
        qa_entry.answer = answer

    db.session.commit()
    return jsonify(qa_entry.to_dict())

@app.route('/question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    qa_entry = QuestionAnswer.query.get(question_id)
    if not qa_entry:
        return jsonify({"error": "Question not found"}), 404

    db.session.delete(qa_entry)
    db.session.commit()
    return jsonify({"message": "Question deleted"}), 200

@app.route('/question/search', methods=['GET'])
def search_question():
    query = request.args.get('q', '').lower()
    results = QuestionAnswer.query.filter(
        QuestionAnswer.question.ilike(f"%{query}%")
    ).all()
    return jsonify([qa.to_dict() for qa in results])







if __name__ == '__main__':
    app.run(debug=True)
