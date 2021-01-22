from flask import Flask,jsonify,request
import pandas as pd
from azureml.core import Run,Model,Workspace
import joblib
from azureml.core.authentication import ServicePrincipalAuthentication


app = Flask(__name__)

@app.route('/')
def hello2():
   print('a')
   return "hello test you"

@app.route('/myroute')
def hello3():
    print('b')
    data=request.get_json(force=True)
    print(data)
    run_id = request.get_json()['mixid']
    plant = request.get_json()['plant']
    status='{} is {}'.format(run_id,plant)
    return jsonify(
        {'status':status})


@app.route('/myroutepred')
def hello():
    op=fn_forecast()
    return  jsonify(op)

def fn_forecast():
    try:

        sp = ServicePrincipalAuthentication(tenant_id="0ae51e19-07c8-4e4b-bb6d-648ee58410f4", # tenantID
                                            service_principal_id="32c47267-f6f9-491f-b8f9-a70ebeba575c", # clientId
                                            service_principal_password="mMY7F2QwflKqF_ekcr3smOe6EGH.0R..tn") # clientSecret
        print('a')
        ws=Workspace.get(name='retailsalesforecast_ml',subscription_id='5c3aba40-8476-49f7-a5a3-455051233138',resource_group='retailsalesforecast_RG',auth=sp)
        model_path = Model.get_model_path('model28_13881.pkl',_workspace=ws)
        print(model_path)
        model = joblib.load(model_path)
        print('b')
        future = model.make_future_dataframe(periods=5, freq='MS')
        forecast = model.predict(future)
    except Exception as e:
        print(e)
    return forecast[['ds', 'yhat']].iloc[-1].to_dict()