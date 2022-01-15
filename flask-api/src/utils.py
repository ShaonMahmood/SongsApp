from flask import jsonify, make_response

def build_response(data, status_code):
    return make_response(jsonify(data), status_code)