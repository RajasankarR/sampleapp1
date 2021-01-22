from flask import Flask,jsonify,request
app = Flask(__name__)

@app.route('/')
def hello2():
   print('a')
   return "hello test"

@app.route('/myroute')
def hello():
    print('b')
    data=request.get_json(force=True)
    print(data)
    run_id = request.get_json()['mixid']
    plant = request.get_json()['plant']
    status='{} is {}'.format(run_id,plant)
    return jsonify(
        {'status':status})