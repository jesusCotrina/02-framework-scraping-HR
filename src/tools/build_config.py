import os
import json
from google.cloud import storage

BASE_PATH = "../../src/cloud-run-scraping"
OUTPUT_FILE = "config_consolidado.json"
path_env = "../../env.json"
# Cambia este bucket y folder:

with open(path_env, "r", encoding="utf-8") as f:
    env= json.load(f)
BUCKET_NAME = env["bucket_tf_state"]
BUCKET_PATH = "config/config_consolidado.json"
print("BUCKET_NAME",BUCKET_NAME)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    cloud_run_final = {}
    cloud_scheduler_final = {}

    # Recorrer cada carpeta de scraper
    for folder in os.listdir(BASE_PATH):
        folder_path = os.path.join(BASE_PATH, folder)

        if not os.path.isdir(folder_path):
            continue

        config_path = os.path.join(folder_path, "config")

        config_file_01 = os.path.join(config_path, "01_config.json")
        schema_file_02 = os.path.join(config_path, "02_schema-bigquery.json")

        if not os.path.exists(config_file_01):
            print(f"No existe 01_config.json en {folder}")
            continue

        # Cargar el config
        config_data = load_json(config_file_01)
        cloud_run = config_data.get("cloud_run_config")
        cloud_sch = config_data.get("cloud_scheduler_config")

        if not cloud_run or not cloud_sch:
            print(f"Estructura inválida en {folder}")
            continue

        code = str(cloud_run.get("code"))

        # Normalizar nombre
        name_scrap = cloud_run["name_scrap"].replace("cr-scrp-", "")

        # Agregar al JSON consolidado
        cloud_run_final[code] = {
            "name_scrap": name_scrap,
            "code": code,
            "ram": cloud_run["ram"],
            "parameters": cloud_run.get("env_vars", {})
        }

        cloud_scheduler_final[code] = {
            "name": cloud_sch["name_cloud_scheduler"],
            "description": f"Scheduler para iniciar el Cloud Run de {name_scrap}",
            "schedule": cloud_sch["schedule"],
            "time_zone": cloud_sch["time_zone"],
            "enabled": True
        }

        print(f"Procesado: {folder} (code={code})")

    # JSON final
    final_json = {
        "cloud_run_config": cloud_run_final,
        "cloud_scheduler_config": cloud_scheduler_final
    }

    # Guardar local
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=4, ensure_ascii=False)

    print(f"Archivo generado: {OUTPUT_FILE}")

    # Subir a bucket
    upload_to_bucket(OUTPUT_FILE, BUCKET_NAME, BUCKET_PATH)


def upload_to_bucket(local_path, bucket, blob_path):
    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(blob_path)

    blob.upload_from_filename(local_path)
    print(f"☁️ Subido a gs://{bucket.name}/{blob_path}")


if __name__ == "__main__":
    main()