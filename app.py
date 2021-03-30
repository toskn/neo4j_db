from flask import Flask, request, render_template
from collections import defaultdict
from neo4j import GraphDatabase, basic_auth
import json
app = Flask(__name__)


features = {'Word': ['lemma', 'pos'],
            'Meaning': ['id', 'Top5'],
            'IS_HYPONYM_OF': ['freq'],
            'HAS_MEANING': []}


@app.route('/')
def index():
    if request.args:
        req = request.args
        action = parse_action(req)
        arguments = parse_arguments(req)
        result = action(arguments)
        result = postprocc_result(result)
        return render_template('index.html', result=result)
    return render_template('index.html')


def postprocc_result(result):
    if result:
        result = result.data()
    return json.dumps(result, ensure_ascii=False)


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
        if '-' in entity:
            node, label = entity.split('-')
            args['label'] = label
            args['entity'] = node
        else:
            args['entity'] = entity
        args[value_name] = v
    return args


def delete(arg_dict):
    node_type = arg_dict.get('type', 'Word')
    node_prop = features[node_type][0]
    node_value = arg_dict['value'] if node_prop == 'id' else f"'{arg_dict['value']}'"
    prop = arg_dict['prop']
    if prop == '_':
        req = "MATCH (x:" + node_type + " {" + node_prop + ": " + node_value + "})\n" + \
              "DETACH DELETE x"
    else:
        req = "MATCH (x:" + node_type + " {" + node_prop + ": " + node_value + "})\n" + \
              "REMOVE x." + prop
    result = session.run(req)
    return result


def create(arg_dict):
    result = []
    params = []
    ent = arg_dict.get('entity')
    if ent is not None and ent == 'node':
        for k, v in arg_dict.items():
            if k == 'label' or k == 'entity':
                continue
            elif k == 'id':
                params.append(k + ': ' + v)
            else:
                params.append(k + ': "' + v + '"')
        req = "CREATE (r:" + arg_dict['label'].capitalize() + " {" + ", ".join(params) + "})"
        req += "\nRETURN r"
        result = session.run(req)
    elif ent is not None and ent == 'rel':
        prop_value = arg_dict.get('prop-value')
        if 'MEANING' in arg_dict['type']:
            req = "MATCH (s:Word {lemma: '" + arg_dict['source'] + "'})\n" + \
                  "MATCH (t:Meaning {id: " + arg_dict['target'] + "})\n"
        else:
            req = "MATCH (s:Word {lemma: '" + arg_dict['source'] + "'})\n" + \
                  "MATCH (t:Word {lemma: '" + arg_dict['target'] + "'})\n"
        if prop_value is not None:
            req += "CREATE (s)-[rel:" + arg_dict['type'] + " {" + arg_dict['prop'] + ": " + prop_value + "}]->(t)\n"
        else:
            req += "CREATE (s)-[rel:" + arg_dict['type'] + "]->(t)\n"
        req += "RETURN rel"
        result = session.run(req)
    return result


def update(arg_dict):
    node_type = arg_dict.get('type', 'Word')
    node_prop = features[node_type][0]
    prop = arg_dict['prop']
    node_value = arg_dict['value'] if node_prop == 'id' else f"'{arg_dict['value']}'"
    prop_value = arg_dict['prop-value'] if prop == 'id' else f"'{arg_dict['prop-value']}'"
    req = "MATCH (x:" + node_type + " {" + node_prop + ": " + node_value + "})\n" + \
          "SET x." + prop + " = " + prop_value + "\n"\
          "RETURN x"
    result = session.run(req)
    return result


def search(arg_dict):
    node_type = arg_dict.get('type', 'Word')
    prop = arg_dict['prop']

    prop_value = arg_dict['prop-value'] if prop == 'id' else f"'{arg_dict['prop-value']}'"
    req = "MATCH (x:" + node_type + " {" + prop + ": " + prop_value + "})\n"
    if arg_dict['limit'] != 'no limit':
        req += "LIMIT " + arg_dict['limit'] + "\n"
    req += "RETURN x"
    result = session.run(req)
    return result


if __name__ == '__main__':
    driver = GraphDatabase.driver(
        "bolt://3.219.31.221:7687",
        auth=basic_auth("neo4j", "petroleum-honor-flare"))
    global session
    session = driver.session()
    app.run(debug=True)
