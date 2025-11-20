import json,time,requests,datetime,traceback
from os import environ
from flask import Flask, jsonify
from google.cloud import storage 
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import date
from utils.functions import *
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def main_scraper():
    try:
        # Lectura de variables de entorno
        project_id          = environ['PROJECT_ID']
        bucket_output       = environ['BUCKET_OUTPUT']

        url                 = environ['url']
        path_blob           = environ['path_blob']
        dataset             = environ['dataset']
        table_name          = environ['table_name']
        

        path_blob=path_blob.replace("{dataset}",dataset).replace("{table_name}",table_name)

        # Iniciamos clientes
        storage_client = storage.Client()
        bq_client = bigquery.Client()

        # ========================== Ejecutar scraping =======================================
        # ====================================================================================

        url_clinica_internacional=url
        params = {
            "filters[isActive][$eq]": "true",
            "pagination[pageSize]": 10000,
            "populate[schedule]": "true",
            "populate[schedule][populate][sedes]": "true",
            "populate[schedule][populate][sedes][populate][sede]": "true",
            "populate[schedule][populate][sedes][populate][tipo_de_atencion]": "true",
            "populate[schedule][populate][sedes][populate][days]": "true",
            "populate[schedule][populate][especialidad]": "true"
        }

        response= requests.get(url=url_clinica_internacional,params=params,verify=False)
        data=response.json()
        print("Status:", response.status_code)
        data_estructurada=[]

        for i,doctor in enumerate(data["data"]):
            new_row={"clinica":"Clinica Internacional"}
            new_row["nombre_completo"]=doctor["fullname"]
            new_row["cmp"]=doctor["cmp"]
            new_row["codigo_medico"]=doctor["medicalCode"]
            new_row["activo"]=doctor["isActive"]
            new_row["experiencia"]=doctor["expertise"]
            new_row["url_imagen"]=doctor["url_image"]

            for schedule in doctor["schedule"]:
                try:
                    new_row["especialidad_slug"]=schedule["especialidad"]["slug"]
                    new_row["especialidad"]=schedule["especialidad"]["title"]
                    new_row["description_card"]=schedule["especialidad"].get("description_card","")

                    for sedes in schedule["sedes"]:
                        new_row["sede_slug"]=sedes["sede"]["slug"]
                        new_row["sede_title"]=sedes["sede"]["title"]
                        new_row["sede_adress"]=sedes["sede"]["address"]
                        new_row["tipo_atencion_slug"]=sedes["tipo_de_atencion"]["slug"]
                        new_row["tipo_atencion_title"]=sedes["tipo_de_atencion"]["Title"]
                        

                        for day in sedes["days"]:
                            new_row["dia"]=day["day"]
                            new_row["hora_inicio"]=day["start_time"]
                            new_row["hora_fin"]=day["end_time"]
                            new_row["fecha_scraping"]=date.today()
                            print("agregando data",new_row)
                            data_estructurada.append(new_row.copy())
                    
                
                except Exception as e:
                    print("error",new_row["nombre_completo"],e)
                    continue
        
        # ========================== termino scraping =======================================
        # ====================================================================================
        

        subir_archivo_bucket(data_estructurada,storage_client,bucket_output,path_blob)
        crear_tabla_externa(bq_client,project_id,dataset,table_name,bucket_output,path_blob)

        

    except Exception as e:
        print("Error en main_scraper:", e)
        tb= traceback.format_exc()
        print(tb)
        print("Notificando error")

    return 'Proceso finalizado.'





if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(environ.get("PORT", 8080)))
