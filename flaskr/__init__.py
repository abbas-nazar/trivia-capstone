import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    setup_db(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTION')
        return response

    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in categories}
        return jsonify({
            'categories': categories
        })

    @app.route('/questions')
    def retrieve_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        categories = Category.query.order_by(Category.id).all()
        categories = {category.id: category.type for category in categories}

        return jsonify({
            'questions': current_questions,
            'totalQuestions': len(questions),
            'categories': categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
          Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()

        return jsonify({}), 200

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            question = Question(question=question, answer=answer,
                                difficulty=difficulty, category=category)
            question.insert()

            return jsonify({}), 201

        except Exception as exp:
            print(str(exp))
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('searchTerm', '')
        search_term = "%{}%".format(search_term)
        questions = Question.query.filter(
          Question.question.like(search_term)).all()
        questions = [question.format() for question in questions]

        return jsonify({
            'questions': questions,
            'totalQuestions': len(questions)
        }), 200

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_category_questions(category_id):
        questions = Question.query.filter(
          Question.category == str(category_id)).order_by(Question.id).all()
        questions = [question.format() for question in questions]

        if len(questions):
            return jsonify({
                'questions': questions,
                'totalQuestions': len(questions),
                'currentCategory': Category.query.get(category_id).type
            })

        abort(404)

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)
        if not quiz_category:
            abort(400)

        category_id = quiz_category.get('id')
        questions = Question.query.filter(~Question.id.in_(previous_questions))
        if not category_id == 0:
            questions = questions.filter(Question.category == str(category_id))

        if not questions:
            abort(404)

        questions = questions.all()
        question = questions[random.randrange(0, len(questions))]

        return jsonify({
            'question': question.format(),
        }), 200

    @app.errorhandler(400)
    def bad_request(error):
        """
        Error handler for bad request with status code 400.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """
        Error handler for unauthorized with status code 401.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 401,
            'message': 'Unauthorized Request'
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """
        Error handler for forbidden with status code 403.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 403,
            'message': 'Forbidden Request'
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """
        Error handler for not found with status code 404.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        Error handler for method not allowed with status code 405.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """
        Error handler for unprocessable entity with status code 422.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Error handler for internal server error with status code 500.
        :param: error
        :return:
        """
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    return app
