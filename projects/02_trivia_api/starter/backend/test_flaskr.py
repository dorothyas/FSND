import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import random

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:{}@{}:{}/{}".format(
            os.environ.get("DB_PASSWORD"),
            os.environ.get("DB_HOST"),
            os.environ.get("DB_PORT"),
            self.database_name
        )
        setup_db(self.app, self.database_path)
        self.question = {
            "id": 1,
            "question":"who invented the light bulb",
            "answer": "Thomas Edison",
            "category": "1",
            "difficulty": 2
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])

    def test_create_question(self):
        response = self.client().post('/questions',
                                    content_type='application/json',
                                    data=json.dumps(self.question))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], 'Question Added')

    def test_search_questions(self):
        res = json.loads(self.client().get('/questions').data)
        body = {"search_term": "who"}
        response = self.client().post('/search',
                                    content_type='application/json',
                                    data=json.dumps(body))
        data = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_nonexistent_question(self):
        body = {"search_term": "00"}
        response = self.client().post('/search',
                                    content_type='application/json',
                                    data=json.dumps(body))

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['current_category'])

    def test_get_questions_with_wrong_category_id(self):
        response = self.client().get('/categories/0/questions')
        data = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['message'], "Not Found")

    def test_get_quiz_questions(self):
        body = {
            "quiz_category": {
                "type": "", 
                "id": 0
                },
            "previous_questions": []
        }
        response = self.client().post('/quizzes',
                                    content_type='application/json',
                                    data=json.dumps(body))
        body = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)

    def test_delete_question(self):
        response = self.client().delete(
            '/questions/1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Question has been deleted")

    def test_delete_nonexistent_question(self):
        response = self.client().delete('/questions/0')
        body = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(body['message'], "Not Found")


    def test_calling_wrong_method(self):
        response = self.client().get('/search')
        self.assertEqual(response.status_code, 405)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()