from flask import Flask, render_template, request, jsonify
from http import HTTPStatus
from utils import Covid19APIUtils, Covid19WebScrapperDataUtils


app = Flask(__name__)

API_UTILS = Covid19APIUtils()
WEB_SCRAPPER = Covid19WebScrapperDataUtils()

@app.route('/')
def showIndexPage():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()