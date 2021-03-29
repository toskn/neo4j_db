import os
from flask import Flask, request, render_template, Response
from collections import defaultdict
from neo4j import GraphDatabase, basic_auth
app = Flask(__name__)


@app.route('/')
def index():
    if request.args:
        req = request.args
        action = parse_action(req)
        arguments = parse_arguments(req)
        result = action(arguments)
        return render_template('index.html', result=result)
    return render_template('index.html')


def parse_action(req):
    for k, v in req.items():
        action = k.split('_')[0]
        if 'add' in action:
            return create
        elif 'del' in action:
            return delete
        elif 'update' in action:
            return update
        elif 'search' in action:
            return search


def parse_arguments(req):
    args = defaultdict(dict)
    for k, v in req.items():
        _, entity, value_name = k.split('_')
        args[entity][value_name] = v
    return args


def delete(arg_dict):
    # TODO: cypher delete
    result=''
    return result


def create(arg_dict):
    # TODO: cypher create
    result = ''
    return result


def update(arg_dict):
    # TODO: cypher update
    result = ''
    return result


def search(arg_dict):
    # TODO: cypher search
    result = ''
    return result


if __name__ == '__main__':
    # driver = GraphDatabase.driver(
    #     "bolt://54.237.90.173:33444",
    #     auth=basic_auth("neo4j", "lockers-label-soldiers"))
    # session = driver.session()

    # un comment if move to heroku
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(debug=True)
