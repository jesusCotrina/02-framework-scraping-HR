# scraper_consorcios.py

import io,json,requests,time
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo


headers = {
            "sec-fetch-mode":"cors",
            "sec-fetch-site": "same-site",
            "content-type":"application/json",
            "origin": "https://www.fitchratings.com",
            "referer": "https://www.fitchratings.com/",
            "priority": "u=1, i",
            "accept": "*/*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        }


def read_reaseguradoras(bucket,file_path,storage_client):
    """
    Leemos el archivo de reaseguradoras desde GCS y lo devuelve como DataFrame
    """
    try:
        print("=======Iniciando read_reaseguradoras======")

        bucket_obj = storage_client.bucket(bucket)
        blob = bucket_obj.blob(file_path)
        data = blob.download_as_bytes()
        df = pd.read_csv(io.BytesIO(data))

        print("=======archivo leido correctamente======")
        return df
    except Exception as e:
        print(f"Error leyendo el archivo de reaseguradoras desde GCS: {e}")
        raise

def request_url_and_save (url,headers,row,cod_url,redis_client,agrupacion,fecha_scrapeo):
    try:
        paylod = {
                    "operationName": "Entity",
                    "variables" : {"slug":cod_url},
                    "query": "query Entity($slug: String!) {\n  getEntity(slug: $slug) {\n    adjustedFinancialDataExists\n    countryOfAnalyst\n    slug\n    ultimateParent\n    name\n    id\n    agentID\n    countryOfIssuer\n    identifiers {\n      type\n      value\n      __typename\n    }\n    disclosure {\n      solicitationTypeDescription\n      permissibleServices\n      originalRatings {\n        ratingTypeDescription\n        originalDate\n        __typename\n      }\n      solicitations {\n        ratingTypeDescription\n        solicitationType\n        __typename\n      }\n      endorsements {\n        agency\n        status\n        postBrexitRegAgency\n        __typename\n      }\n      __typename\n    }\n    sourceOfSupport {\n      effectiveDate\n      policyBankFlag\n      rtngDrvnByGovSupport\n      rtngExclGovSupportDescription\n      rtngExclGovSupportApplicabilityDescription\n      __typename\n    }\n    marketing {\n      countries {\n        name\n        slug\n        __typename\n      }\n      esgRatingsExist\n      sectors {\n        name\n        slug\n        __typename\n      }\n      regions {\n        name\n        slug\n        __typename\n      }\n      topics {\n        name\n        slug\n        __typename\n      }\n      metadataTags {\n        title\n        description\n        __typename\n      }\n      openGraphTags {\n        title\n        url\n        type\n        regions\n        articleTag\n        sectionTag\n        __typename\n      }\n      analysts {\n        firstName\n        lastName\n        title\n        phoneNumber\n        professional\n        slug\n        __typename\n      }\n      translatedEntityNames {\n        default\n        countries {\n          name\n          slug\n          __typename\n        }\n        language {\n          name\n          slug\n          __typename\n        }\n        translatedValue\n        __typename\n      }\n      __typename\n    }\n    ratings {\n      id\n      orangeDisplay\n      correctionFlag\n      ratingChangeDate\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      recoveryRatingValue\n      __typename\n    }\n    ratingHistory {\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      correctionFlag\n      ratingChangeDate\n      __typename\n    }\n    identifiers {\n      type\n      value\n      __typename\n    }\n    esgScore {\n      issuerScore {\n        name\n        chartLevel\n        __typename\n      }\n      dealScores {\n        name\n        chartLevel\n        __typename\n      }\n      __typename\n    }\n    groupManager {\n      name\n      slug\n      __typename\n    }\n    latestESGNavigator {\n      slug\n      title\n      __typename\n    }\n    relatedCredits {\n      name\n      slug\n      ratings {\n        ratingCode\n        ratingTypeDescription\n        ratingActionDescription\n        ratingAlertCode\n        ratingAlertDescription\n        __typename\n      }\n      __typename\n    }\n    transactionSecurityRatings {\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      transactionSecurityID\n      __typename\n    }\n    __typename\n  }\n  getUspfTransaction(slug: $slug) {\n    id\n    name\n    type\n    slug\n    countryOfAnalyst\n    esgScore {\n      issuerScore {\n        name\n        chartLevel\n        __typename\n      }\n      dealScores {\n        name\n        chartLevel\n        __typename\n      }\n      __typename\n    }\n    otherIssuers {\n      name\n      slug\n      __typename\n    }\n    relatedCredits {\n      name\n      slug\n      ratings {\n        ratingCode\n        ratingTypeDescription\n        ratingActionDescription\n        ratingAlertCode\n        ratingAlertDescription\n        __typename\n      }\n      __typename\n    }\n    latestESGNavigator {\n      slug\n      title\n      __typename\n    }\n    marketing {\n      countries {\n        name\n        slug\n        __typename\n      }\n      esgRatingsExist\n      sectors {\n        name\n        slug\n        __typename\n      }\n      regions {\n        name\n        slug\n        __typename\n      }\n      topics {\n        name\n        slug\n        __typename\n      }\n      metadataTags {\n        title\n        description\n        __typename\n      }\n      openGraphTags {\n        title\n        url\n        type\n        regions\n        articleTag\n        sectionTag\n        __typename\n      }\n      analysts {\n        firstName\n        lastName\n        title\n        phoneNumber\n        professional\n        slug\n        __typename\n      }\n      __typename\n    }\n    keyRatingFactors {\n      description\n      value\n      sortOrder\n      __typename\n    }\n    ratings {\n      id\n      orangeDisplay\n      correctionFlag\n      ratingChangeDate\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      recoveryRatingValue\n      __typename\n    }\n    ratingHistory {\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      correctionFlag\n      ratingChangeDate\n      __typename\n    }\n    transactionSecurityRatings {\n      ratingActionDescription\n      ratingCode\n      ratingAlertCode\n      ratingEffectiveDate\n      ratingTypeDescription\n      ratingLocalValue\n      ratingLocalActionDescription\n      transactionSecurityID\n      __typename\n    }\n    disclosure {\n      solicitationTypeDescription\n      permissibleServices\n      originalRatings {\n        ratingTypeDescription\n        originalDate\n        __typename\n      }\n      solicitations {\n        ratingTypeDescription\n        solicitationType\n        __typename\n      }\n      endorsements {\n        agency\n        status\n        postBrexitRegAgency\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
                }
        
        data=requests.post(url=url,json=paylod,headers=headers)
        row_recuperado=[]
        guardado=False
        print("Status code:", data.status_code)
        if data.status_code == 200:
            json_data=json.loads(data.text)
            ratings=json_data["data"]["getEntity"]["ratings"]

            for rating in ratings:
                if rating["ratingTypeDescription"] == "Long Term Insurer Financial Strength":
                    rating_value=rating["ratingLocalValue"]
                    rating_fec=rating["ratingEffectiveDate"]
                    dt_utc = datetime.strptime(rating_fec, "%Y-%m-%dT%H:%M:%S.%fZ")
                    dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
                    dt_us = dt_utc.astimezone(ZoneInfo("America/New_York"))  # Hora del Este (EST/EDT)
                    fecha_formateada = dt_us.strftime("%d/%m/%Y")

                    row_recuperado=[row["cod_reasegurador"],row["reasegurador"],cod_url,rating_value,fecha_formateada,rating["ratingTypeDescription"],fecha_scrapeo]

                    print("row recuperado",row_recuperado)
                    redis_client.lpush(agrupacion, json.dumps(row_recuperado))
                    guardado = True
                    break
            
            if not guardado:
                row_recuperado=[row["cod_reasegurador"],row["reasegurador"],cod_url,"","","",fecha_scrapeo]
                redis_client.lpush(agrupacion, json.dumps(row_recuperado))
                print("row recuperado por no tener rating de Long Term Insurer Financial Strength==================",row_recuperado)
                

        else:
            row_recuperado=[row["cod_reasegurador"],row["reasegurador"],cod_url,"","","",fecha_scrapeo]
            redis_client.lpush(agrupacion, json.dumps(row_recuperado))  
            print("Error en la solicitud:", data.status_code)
            print(data.text)
            return None
        
    except Exception as e:
        row_recuperado=[row["cod_reasegurador"],row["reasegurador"],cod_url,"","","",fecha_scrapeo]
        redis_client.lpush(agrupacion, json.dumps(row_recuperado))
        print("Error en la solicitud:", e)
        return None


def get_coincidencia (names,entity_final):
    val_final={}
    cod_url=None
    for clave in entity_final:
        count=0
        val_names=entity_final[clave].split(" ")
        for name in names:
            if name in val_names:
                count=count+1
        
        val_final[clave]=count
    
    clave_maxima = max(val_final, key=val_final.get)
    valor_maximo = val_final[clave_maxima]
    print("valores recuperados de coincidencia",clave_maxima,valor_maximo)
    per=valor_maximo/len(names) if len(names)>0 else 0
    if per>0.6:
        cod_url=clave_maxima

    return cod_url

def save_data(redis_client,agrupacion,storage_client,bucket_output,path):

    """
    Leemos el archivo ya scrapado anteriormente para reemplazarlo por los registros scrapeados
    """
    try:
        print("=======Iniciando save data======")
        periodo = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        path_output=f"{path}/periodo={periodo}/fitch_rating.csv"
        columns=   ["cod_reasegurador","reasegurador","cod_url_fitchrating","rating","fecha_rating","tipo_solvencia_crediticia","fecha_scrapeo"]

        try:
            
            bucket_obj = storage_client.bucket(bucket_output)
            blob = bucket_obj.blob(path_output)
            data = blob.download_as_bytes()
            df = pd.read_csv(io.BytesIO(data))

        except Exception as e:
            print(f"Error leyendo el archivo de reaseguradoras desde GCS: {e}")
            df = None

        

        data = redis_client.lrange(agrupacion, 0, -1)
        data.reverse()
        rows = [json.loads(item) for item in data]

        df_redis = pd.DataFrame(rows, columns=columns)

        if df is None or df.empty:
            print("df vacio ==========")
            df=df_redis


        # Ponemos 'cod_reasegurador' como índice para facilitar merge/update
        df.set_index("cod_reasegurador", inplace=True, drop=False)
        df_redis.set_index("cod_reasegurador", inplace=True, drop=False)

        # Reemplazar/actualizar los que están en Redis
        
            
        df.update(df_redis)
        # Agregar los que no existen en el archivo original
        df = pd.concat([df, df_redis.loc[~df_redis.index.isin(df.index)]])

        # --- 4. Guardar el archivo actualizado en GCS ---
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

        redis_client.delete(agrupacion)
        print(f"Archivo actualizado en gs://{bucket_output}/{path_output}")

    except Exception as e:
        print("Error en save_data",e)
        raise


def scraping_fitch_rating(reaseguradoras,redis_client,url,agrupacion):
    print("=======Iniciando scraping_fitch_rating======")
    redis_client.delete(agrupacion)

    fecha_scrapeo = datetime.now().strftime("%Y-%m-%d")
    for index, row in reaseguradoras.iterrows():
        try:
            print("============================ consultando reaseguradora:",row["reasegurador"], "==========================",index)
            cod_url_fitchrating = row["cod_url_fitchrating"]

            row_recuperado = []
            if pd.notna(cod_url_fitchrating) and row["cod_url_fitchrating"]!="" and row["cod_url_fitchrating"] is not None:
                print("la reaseguradora tiene cod_url_fitchrating",row["cod_url_fitchrating"],index)
                request_url_and_save(url,headers,row,row["cod_url_fitchrating"],redis_client,agrupacion,fecha_scrapeo)
                
            else:
                reasegurador=row["cod_url_fitchrating"]
                print(f"No se tiene cod_url_fitchrating de la reaseguradora {reasegurador}, no se procesa==================",index)
                row_recuperado=[row["cod_reasegurador"],row["reasegurador"],row["cod_url_fitchrating"],"","","",fecha_scrapeo]
                redis_client.lpush(agrupacion, json.dumps(row_recuperado))

            print("============================ terminando:",row["reasegurador"])
            time.sleep(2)

        except Exception as e:
            row_recuperado=[row["cod_reasegurador"],row["reasegurador"],row["cod_url_fitchrating"],"","","",fecha_scrapeo]
            redis_client.lpush(agrupacion, json.dumps(row_recuperado))
            print("Error procesando la fila:", row["cod_url_fitchrating"], e)
            print("continuamos...")
    
    print("=======scraping_fitch_rating terminado======")



