import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})  
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories')
  def categories():
    """ Get all categories """
    categories = Category.query.all()
    results = []
    for category in categories:
      results.append(category.type)
      return jsonify({'categories': results}), 200

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def questions():
    """ Get all questions """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.all()
    if len(questions) == 0:
      abort(404)
    formatted_qns = [question.format() for question in questions]
    categories = []
    for category in Category.query.all():
        categories.append(category.type)

    return jsonify({
      'success': True,
      'questions': formatted_qns[start:end],
      'total_questions': len(questions),
      'categories': categories,
      'current_category': "All Categories"
      }), 200

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods =['DELETE'])
  def delete_question(question_id):
    """ Delete a Question """
    question = Question.query.filter_by(id=question_id).first()
    if question is None:
      abort(404)
    question.delete()
    return jsonify({
      "message": "Question has been deleted"
    }) 

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods =['POST'])
  def create_question():
    """ Create a question """

    body = request.get_json()
    new_question = Question(
      question=body.get("question"),
      answer=body.get("answer"),
      category=int(body.get("category")),
      difficulty=int(body.get("difficulty"))
    )
    new_question.insert()
    return jsonify({
      "message": "Question Added"
    }), 201

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods = ['POST'])
  def search_questions():
    """ Searching Questions """

    body =  request.get_json()
    search_param = body.get("search_term")
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.join(
            Category, Category.id == Question.category
        ).add_columns(Category.type).all()
    current_questions = [question.Question.format() for question in questions]

    found_questions = []
    for question in current_questions:
      if search_param.lower() in question['question'].lower():
        found_questions.append(question)
    if len(found_questions) == 0:
        abort(404)

    categories = []
    for category in Category.query.all():
        categories.append(category.type)

    return jsonify({
        'success': True,
        'questions': found_questions[start:end],
        'total_questions': len(questions),
        'categories': categories,
        'current_category': None
    }), 200


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def question_by_category(id):
    """ get questions by category """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = Question.query.filter_by(category=id).join(
        Category,
        Category.id == Question.category
    ).add_columns(Category.type).all()
    if len(questions)==0:
      abort(404)
    current_questions = [question.Question.format() for question in questions]

    category = Category.query.filter_by(id=id).first()
    categories = []
    for item in Category.query.all():
      categories.append(item.type)
    return jsonify({
        'success': True,
        'questions': current_questions[start:end],
        'total_questions': len(questions),
        'categories': categories,
        'current_category': category.type
    }), 200

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_questions():
    """ Handle querying a random quiz question"""
    body = request.get_json()
    questions = Question.query.filter_by(
        category=body.get('quiz_category')['id']
    ).filter(Question.id.notin_(body.get('previous_questions'))).all()

    if body.get('quiz_category')['id'] == 0:
      questions = Question.query.filter(
        Question.id.notin_(body.get('previous_questions'))).all()

    if questions:
      question = random.choice(questions).format()

    return jsonify({
        'success': True,
        'question': question
    }), 200

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  @app.errorhandler(400)
  def custom400(error): 
      response = jsonify({
          'message': error.description
      })
      return response, 400

  @app.errorhandler(404)
  def custom404(error):
      response = jsonify({
          'message': "Not Found"
      })
      return response, 404

  @app.errorhandler(422)
  def custom422(error):
      response = jsonify({
          'message': error.description
      })
      return response, 422

  @app.errorhandler(405)
  def custom405(error):
      response = jsonify({
          'message': 'Method not allowed.'
      })
      return response, 405

  return app

    