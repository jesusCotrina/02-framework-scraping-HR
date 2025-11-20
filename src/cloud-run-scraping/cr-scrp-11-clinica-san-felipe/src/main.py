import json,time,requests,datetime,traceback
from os import environ

from flask import Flask, jsonify
import google.auth.transport.requests
import google.oauth2.id_token
from google.cloud import storage 

from utils.gcp_redis import redis_connection
from utils.scraper_fitchrating import read_reaseguradoras,scraping_fitch_rating,save_data

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main_scraper():
    try:
        # Lectura de variables de entorno
        param_source    = json.loads(environ['_SOURCE'])
        outcome_source  = json.loads(environ['_OUTCOME'])
        env_redis       = environ['_REDIS']
        service_name    = environ['_INSTANCE_NAME']
        project_id      = environ['PROJECT_ID']
        url_control     = environ['url_control']
        bucket_input    = environ['_BQ_STORAGE_BUCKET_INPUT']
        bucket_output   = environ['_BQ_STORAGE_BUCKET_OUTPUT']

        # Obtenemos variables
        agrupacion          = param_source.get('agrupacion', '') 
        prefix_key          = project_id.split('-')[3] if '-' in project_id else 'UNK'
        key_control         = f"{agrupacion}-{prefix_key}"
        input_file_path     = param_source.get("input_file_path","")
        url                 = param_source.get("source_url","")   
        output_file_path    = outcome_source.get("output_file_path","")

        # Iniciamos clientes
        server_ip, server_port = env_redis.split('@')
        redis_client = redis_connection(server_ip, server_port)
        storage_client = storage.Client()

        # Ejecutar scraping
        reaseguradoras=read_reaseguradoras(bucket_input,input_file_path,storage_client)
        scraping_fitch_rating(reaseguradoras,redis_client,url,agrupacion)
        save_data(redis_client,agrupacion,storage_client,bucket_output,output_file_path)


        # Actualizar estado en Redis y notificar control externo
        reporte_control(redis_client,key_control,service_name,url_control,agrupacion)

    except Exception as e:
        print("Error en main_scraper:", e)
        tb= traceback.format_exc()
        print(tb)
        print("Notificando error al control externo, se procede a terminar el proceso")
        
        payload = {
                    "agrupacion": agrupacion,
                    "tipo": "E",
                    "estado": "Cloud Run",
                    "status_code": 400,
                    "message": f"Error en el cloud run {service_name}\nerror: {e}\n{tb}"
                }
        make_authorized_get_request(url_control, payload)
        

    return 'Proceso finalizado.'


def reporte_control(redis_client,key_control,service_name,url_control,agrupacion):
    try:
        raw = redis_client.get(key_control)
        control = json.loads(raw or '{}')
        estado = control.get('estado_proceso')
    

        payload = {"agrupacion": agrupacion, "tipo": "finish", "estado": "finish_crun"}

        if estado == 'ACTIVO':
            control.setdefault('cruns', {})[service_name] = 1
            control['last_update'] = time.time()
            redis_client.set(key_control, json.dumps(control))
            
            make_authorized_get_request(url_control,payload)
        
    except Exception as e:
        print(f"Error en reporte_control: {e}")
        raise



def make_authorized_get_request(endpoint,payload):
    """
    Realiza una petición POST autorizada con ID token de Google.
    """
    try:
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(auth_req, endpoint)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.text
    
    except Exception as e:
        print(f"Error en make_authorized_get_request: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(environ.get("PORT", 8080)))
