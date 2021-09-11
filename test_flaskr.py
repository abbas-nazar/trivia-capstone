import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.question = {
            "question": "Test 1",
            "answer": "Answer 1",
            "category": 1,
            "difficulty": 1
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

    def test_categories(self):
        """
        Success test case for get categories route.
        :return:
        """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 6)

    def test_method_not_allowed_categories(self):
        """
        Failure test case for get categories route.
        :return:
        """
        res = self.client().post('/categories', json={})
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Method Not Allowed'
        )

    def test_paginated_questions(self):
        """
        Success test case for get paginated questions.
        :return:
        """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_method_not_paginated_questions(self):
        """
        Failure test case for get paginated questions.
        :return:
        """
        res = self.client().put('/questions', json={})
        json_data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Method Not Allowed'
        )

    def test_delete_questions(self):
        res = self.client().delete('/questions/1')

        self.assertEqual(res.status_code, 200)

    def test_invalid_delete_questions(self):
        res = self.client().delete('/questions/0')

        self.assertEqual(res.status_code, 404)

    def test_create_questions(self):
        response = self.client().post('/questions', json=self.question)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json_data.get('success'), True)
        self.assertTrue(json_data.get('id'))

    def test_add_question_failed_method_not_allowed(self):
        """
        Fail case of add question test case with method not allowed error.
        :return:
        """
        response = self.client().put('/questions', json={})
        json_data = response.get_json()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Method Not Allowed'
        )

    def test_search_questions_success(self):
        """
        Success case of search questions api.
        :return:
        """
        data = {
            "searchTerm": "What"
        }
        response = self.client().post('questions/search', json=data)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json_data.get('questions')))
        self.assertTrue(json_data.get('totalQuestions'))

    def test_get_questions_by_category_success(self):
        """
        Success case for get questions by category.
        :return:
        """
        response = self.client().get('/categories/2/questions')
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json_data.get('questions')))
        self.assertTrue(json_data.get('totalQuestions'))
        self.assertTrue(len(json_data.get('currentCategory')))

    def test_get_questions_by_category_failed_method_not_allowed(self):
        """
        Fail case for get questions by category with method not allowed error.
        :return:
        """
        response = self.client().post('/categories/1/questions')
        json_data = response.get_json()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Method Not Allowed'
        )

    def test_get_questions_by_category_not_found(self):
        """
        Fail case for get questions by category with method not found.
        :return:
        """
        response = self.client().get('/categories/1000/questions')
        json_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Not Found'
        )

    def test_play_quiz_success(self):
        """
        Success case for play quiz api.
        :return:
        """
        data = {
            "quiz_category": {
                "id": 1
            },
            "previous_questions": []
        }
        response = self.client().post('/quizzes', json=data)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(json_data.get('question')))

    def test_play_quiz_failed_method_not_allowed(self):
        """
        Fail case for play quiz api with method not allowed error.
        :return:
        """
        response = self.client().get('/quizzes', json={})
        json_data = response.get_json()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Method Not Allowed'
        )

    def test_play_quiz_failed_bad_request(self):
        """
        Fail case for play quiz api with method bad request.
        :return:
        """
        response = self.client().post('/quizzes', json={})
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_data.get('success'), False)
        self.assertEqual(
            json_data.get('message'), 'Bad request'
        )


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()