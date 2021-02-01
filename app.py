from flask import Flask,jsonify,request
import traceback
import pandas as pd
from azureml.core import Run,Model,Workspace
import joblib
from azureml.core.authentication import ServicePrincipalAuthentication
import pyodbc
from datetime import date

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
        future = list()
        future = pd.DataFrame(pd.date_range('2014-01-01', periods=24, freq='MS'))
        print(future)
        future.columns = ['ds']
        future['ds'] = pd.to_datetime(future['ds'])

        forecast = model.predict(future)
    except Exception as e:
        print(e)
    return forecast[['ds', 'yhat']].iloc[-1].to_dict()

@app.route('/cleandata',methods=['GET','POST'])
def fn_clean():
    try:
        print(request)
        data = request.get_json()['data']
        forecast_id = request.get_json()['forecast_id']
        if type(data)==list:
            print('in if')
            print(type(data))
            res = pd.DataFrame(list(data))
        else:
            print(type(data))
            print('in else')
            data=(data.replace("\\","")).replace("n","")
            res = pd.DataFrame(list(eval(data)))
        res['timestamp']=str(date.today())
        res['forecast_id'] = forecast_id
        print(res)

        drivers = [item for item in pyodbc.drivers()]
        driver = drivers[-1]
        print("driver:{}".format(driver))
        # Some other example server values are
        server = 'tcp:retailsales-server.database.windows.net'
        # server = 'myserver,port' # to specify an alternate port
        # server = 'tcp:myserver.database.windows.net'
        database = 'retailsales'
        username = 'retailadmin'
        password = 'welcome$123'
        cnxn = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        # cursor = cnxn.cursor()
        # select 26 rows from SQL table to insert in dataframe.
        print('2')
        with cnxn.cursor() as cursor:
            pass
            cursor.executemany("""
                                insert into retail_sales_prediction(forecast_timestamp,forecast_value,shop_id,item_id,timestamp,forecast_id)
                                values(?,?,?,?,?,?)""",
                               [tuple(x) for x in res[['ds', 'yhat','shop_id','item_id','timestamp','forecast_id']].values])
            cnxn.commit()
        print('3')
        status='success'
        print(res)
    except Exception as e:
        status='error'
        print('in error')
        print(status)
        print(str(traceback.format_exc()))
    finally:
        print('final')
    return jsonify({"status":status})
@app.route('/abcanalysis')
def fn_abcanalysis():
    try:

        drivers = [item for item in pyodbc.drivers()]
        driver = drivers[-1]
        print("driver:{}".format(driver))
        # Some other example server values are
        server = 'tcp:retailsales-server.database.windows.net'
        # server = 'myserver,port' # to specify an alternate port
        # server = 'tcp:myserver.database.windows.net'
        database = 'retailsales'
        username = 'retailadmin'
        password = 'welcome$123'
        cnxn = pyodbc.connect(
            'DRIVER=' + driver + ';SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
        data=pd.read_sql('select * from retailsales',cnxn)

        #data=pd.read_csv('sampledata.csv')
        data['salevalue'] = data.apply(lambda a: a['item_cnt_day'] * a['item_price'], axis=1)
        agg_data=data.groupby('item_id')['salevalue'].sum()
        totalsales = data['salevalue'].sum()
        sales_data_ann_cons = ((agg_data/totalsales)*100).sort_values(ascending=False)
        sales_cumsum = sales_data_ann_cons.cumsum().reset_index()
        sales_cumsum['assortment_category']= sales_cumsum.apply(lambda a:'A' if a['salevalue'] <=80 else 'B' if (a['salevalue']>80 and a['salevalue']<=95) else 'C',axis=1)

        with cnxn.cursor() as cursor:
            pass
            cursor.execute("""delete from abc_category""")
            cnxn.commit()

        with cnxn.cursor() as cursor:
            pass
            cursor.executemany("""
                                      insert into abc_category(item_id,salesvalue,assortment_category)
                                      values(?,?,?)""",
                               [tuple(x) for x in
                                sales_cumsum[[ 'item_id', 'salevalue', 'assortment_category']].values])
            cnxn.commit()


        status='success'

    except Exception as e:
        status='error'
        print('in error')
        print(status)
        print(str(traceback.format_exc()))
    finally:
        print('final')
    return jsonify({"status":status})


if __name__ == '__main__':
    app.run(host="0.0.0.0")
    app.debug = True
