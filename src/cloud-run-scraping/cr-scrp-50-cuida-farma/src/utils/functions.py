import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
import json
from google.cloud import bigquery
from datetime import datetime

def subir_archivo_bucket(data,client,bucket_name,destination_blob):
    print("subiendo archivo parquet")
    periodo=datetime.now().replace(day=1).strftime('%Y-%m-%d')
    filename_bucket=datetime.now().strftime('%d-%m-%Y_%H-%M')
    destination_blob_periodo=f"{destination_blob}/periodo={periodo}/{filename_bucket}.parquet"

    table = pa.Table.from_pylist(data)

    # Crear buffer en memoria
    buffer = BytesIO()
    pq.write_table(table, buffer)

    # Posicionar al inicio para leer
    buffer.seek(0)

    # Subir a GCS
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_periodo)

    blob.upload_from_file(buffer, content_type='application/octet-stream')
    print("se subio el archivo parquet en la ruta:",destination_blob_periodo)

def crear_tabla_externa(bq_client,project_id,dataset,table_name,bucket,path_blob):

    table_id=f"{project_id}.{dataset}.{table_name}"
    try:
        table=bq_client.get_table(table_id)
        return f"Tabla {table_id} ya existe"
    
    except Exception as e:
        print("Creando tabla externa")
        f = open(f'02_schema-bigquery.json')
        config_schema = json.load(f)
        schema_dict = config_schema["schema"]
        formato_archivo= config_schema.get("format","PARQUET")

        schema_fields = [bigquery.SchemaField.from_api_repr(field) for field in schema_dict]
        
        #Crea un objeto Table
        table = bigquery.Table(table_id)

        #Configura las opciones de partición
        external_config = bigquery.ExternalConfig(formato_archivo)
        
        #Especifica las URIs de los archivos en GCS
        uri=f"gs://{bucket}/{path_blob}"
        
        #Configure the external data source
        external_config = bigquery.ExternalConfig(formato_archivo)
        external_config.source_uris = [uri+"/*"]
        external_config.autodetect = False
        external_config.schema=schema_fields
        if formato_archivo=="CSV":
            external_config.options.skip_leading_rows = 1
            external_config.options.field_delimiter = ","
            external_config.options.quote = '"'

        #Configure partitioning options
        hive_partitioning_opts = bigquery.HivePartitioningOptions()
        hive_partitioning_opts.mode = "CUSTOM"
        hive_partitioning_opts.require_partition_filter = False
        hive_partitioning_opts.source_uri_prefix = uri+"/{periodo:DATE}"
        hive_partitioning_opts.field_names = ["periodo"]
        external_config.hive_partitioning = hive_partitioning_opts
        
        table = bigquery.Table(table_id)
        table.external_data_configuration = external_config
        table = bq_client.create_table(table)  # Make an API request.
        return f"Tabla {table_id} creada correctamente"