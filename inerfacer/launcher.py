from flask import Flask, jsonify,request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/mix2/p2/v1.0/api', methods=['GET', 'POST'])
def process():
    run_id = request.json['mixid']

    # plant:Plant of the user who is trigerring the process in the application
    plant = request.json['plant']
    status='{} is {}'.format(run_id,plant)
    return jsonify(
        {'status':status})


if __name__ == '__main__':
    app.run(host="0.0.0.0")
    app.debug = True