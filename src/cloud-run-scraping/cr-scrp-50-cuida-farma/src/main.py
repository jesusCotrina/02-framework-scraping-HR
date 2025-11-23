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

        url="https://test-strapi.cuida.pe/graphql"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "operationName": "menuWeb",
            "variables": {},
            "query": """
            query menuWeb {
            menuWeb {
                data {
                id
                attributes {
                    menuprograms {
                    titleSection
                    url
                    imgMenu {
                        data {
                        attributes {
                            url
                            __typename
                        }
                        __typename
                        }
                        __typename
                    }
                    menuprogramsitem {
                        titulo
                        descripcion
                        url
                        __typename
                    }
                    __typename
                    }
                    specialty {
                    titleSection
                    url
                    imgMenu {
                        data {
                        attributes {
                            url
                            __typename
                        }
                        __typename
                        }
                        __typename
                    }
                    itemsmenuspeciality {
                        titulo
                        descripcion
                        url
                        __typename
                    }
                    __typename
                    }
                    menucategories {
                    titleSection
                    imgMenu {
                        data {
                        attributes {
                            url
                            __typename
                        }
                        __typename
                        }
                        __typename
                    }
                    itemsmenucategories {
                        titulo
                        descripcion
                        url
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                __typename
                }
                __typename
            }
            }
            """
        }


        response=requests.post(url=url,headers=headers, json=payload)
        data = response.json()
        categorias=data["data"]["menuWeb"]["data"]["attributes"]["menucategories"]
        data_estructurada=[]
        json_file="data_medicamentos.json"

        for categoria in categorias:
            new_row={}
            categoria_title=categoria["titleSection"]
            new_row["categoria"]=categoria_title
            print(categoria["titleSection"],"========================")
            for sub_categoria in categoria["itemsmenucategories"]:
                print(sub_categoria["titulo"])
                url_sub_categoria=sub_categoria["url"]
                categoria=url_sub_categoria.split("/")[2]
                sub_ctegoria=url_sub_categoria.split("/")[3]
                new_row["categoria_slug"]=categoria
                new_row["sub_ctegoria"]=sub_categoria["titulo"]
                new_row["sub_ctegoria_slug"]=sub_ctegoria
                url2=f"https://cuidafarma.pe/_next/data/mnS5AsurIysWBN5wxzsbU{url_sub_categoria}.json?category={categoria}&subcategory={sub_ctegoria}"
                params = {
                    "category": categoria,
                    "subcategory": sub_ctegoria
                }
                response = requests.get(url2,params=params)
                data = response.json()
                subcategories=data["pageProps"]["subcategories"]
                for sub_categoria in subcategories:
                    if sub_ctegoria==sub_categoria["slug"]:
                        id_subcategoria=sub_categoria["id"]
                        url3="https://saleor-api.cuida.pe/graphql/"
                        
                        query = "fragment MetadataFragment on MetadataItem {\n  key\n  value\n  __typename\n}\n\nfragment SelectedAttributeDetailsFragment on SelectedAttribute {\n  attribute {\n    id\n    name\n    slug\n    __typename\n  }\n  values {\n    name\n    slug\n    file {\n      url\n      contentType\n      __typename\n    }\n    value\n    boolean\n    richText\n    __typename\n  }\n  __typename\n}\n\nquery ProductsCollectionAllieNext($filter: ProductFilterInput, $count: Int, $after: String, $channel: String!) {\n  products(first: $count, channel: $channel, filter: $filter, after: $after) {\n    totalCount\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      endCursor\n      __typename\n    }\n    edges {\n      node {\n        id\n        name\n        slug\n        seoTitle\n        seoDescription\n        description\n        isAvailableForPurchase\n        isAvailable\n        defaultVariant {\n          id\n          __typename\n        }\n        attributes {\n          ...SelectedAttributeDetailsFragment\n          __typename\n        }\n        thumbnail(size: 400) {\n          url\n          __typename\n        }\n        media {\n          url\n          __typename\n        }\n        pricing {\n          priceRange {\n            start {\n              currency\n              gross {\n                currency\n                amount\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        isAvailableForPurchase\n        isAvailable\n        category {\n          id\n          name\n          slug\n          parent {\n            id\n            name\n            slug\n            __typename\n          }\n          metadata {\n            ...MetadataFragment\n            __typename\n          }\n          __typename\n        }\n        defaultVariant {\n          id\n          __typename\n        }\n        collections {\n          id\n          name\n          slug\n          metadata {\n            ...MetadataFragment\n            __typename\n          }\n          __typename\n        }\n        variants {\n          sku\n          quantityAvailable\n          __typename\n        }\n        metafields\n        attributes {\n          attribute {\n            id\n            name\n            slug\n            __typename\n          }\n          values {\n            name\n            slug\n            value\n            boolean\n            richText\n            __typename\n          }\n          __typename\n        }\n        metadata {\n          ...MetadataFragment\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"

                        payload = {
                            "operationName": "ProductsCollectionAllieNext",
                            "variables": {
                                "filter": {
                                    "collections": [id_subcategoria],
                                    "stockAvailability": "IN_STOCK",
                                    "attributes": [{"slug": "priority", "boolean": None}]
                                },
                                "count": 20,
                                "channel": "feria-cuida"
                            },
                            "query": query
                        }

                        headers = {"Content-Type": "application/json", "Accept": "application/json"}
                        response = requests.post(url3, headers=headers, json=payload)
                        data = response.json()
                        nodos=data["data"]["products"]["edges"]
                        # print(data["data"]["products"]["edges"])
                        for product in nodos:
                            
                            new_row["name_product"]=product["node"]["name"]
                            new_row["esta_disponible"]=product["node"]["isAvailable"]
                            new_row["url_image"]=product["node"]["thumbnail"]["url"]
                            new_row["precio"]=product["node"]["pricing"]["priceRange"]["start"]["gross"]["amount"]
                            new_row["moneda"]=product["node"]["pricing"]["priceRange"]["start"]["gross"]["currency"]
                            atributos = product["node"]["attributes"]
                            slug_name=product["node"]["slug"]
                            url_compra=f"https://cuidafarma.pe/producto/{categoria_title}/{slug_name}"
                            new_row["url_compra"]=url_compra

                            for atributo in atributos:
                                if atributo["attribute"]["slug"] == "presentation":
                                    new_row["presentacion"]=atributo["values"][0]["name"]
                                    data_estructurada.append(new_row.copy())

                                    with open(json_file, "r", encoding="utf-8") as f:
                                        data = json.load(f)
                                    
                                    # Agregar el nuevo diccionario
                                    data.append(new_row)
                                    
                                    # Guardar de nuevo en el archivo
                                    with open(json_file, "w", encoding="utf-8") as f:
                                        json.dump(data, f, ensure_ascii=False, indent=2)

                                    print("new row",new_row.copy())
                                    break
                



        print("==========================================")
        
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
