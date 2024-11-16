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
