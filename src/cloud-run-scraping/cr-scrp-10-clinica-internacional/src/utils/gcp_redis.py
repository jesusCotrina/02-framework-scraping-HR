import os
import redis
import json
import re


def redis_connection(host, port):
    print("=======Iniciando conexion a redis======")
    redis_host = host
    redis_port = int(port)
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    print("=======conexion a redis exitosa======")
    return redis_client


def dummy_data(instance_name, server_redis):
    server_redis_ip = server_redis.split("@")[0]
    server_redis_port = server_redis.split("@")[1]
    redis_client = redis_connection(server_redis_ip, server_redis_port)
    # Agregamos elementos a la cola
    for i in range(1, 9):
        redis_client.lpush(instance_name, "['41385953','42385953','43485953','41395953','31395953','41397953']")
    print("========SE CARGA DATA DUMMY")
    return


def get_data_redis(instance_name, server_redis):
    # Obtenemos y eliminamos el primer elemento de la cola
    server_redis_ip = server_redis.split("@")[0]
    server_redis_port = server_redis.split("@")[1]
    redis_client = redis_connection(server_redis_ip, server_redis_port)
    primer_elemento = redis_client.rpop(instance_name)
    retorno = ""
    if not (primer_elemento is None):
        # formato_item = eval(primer_elemento)
        # convertimos esto   "    [02444963@20230426,02151107@20230426,02297227@20230426]"
        # en esto ['02444963@20230426', '02151107@20230426', '02297227@20230426']
        # formato_item = re.findall(r'\d*@\d{8}', primer_elemento)
        formato_item = primer_elemento.strip('[]').replace("'", "").split(',')
        for i in formato_item:
            datos = i.split("@")[0]
            # Separamos el dni y la fecha de nacimiento en un array
            retorno = datos

        print("====== redis obtuvimos de retorno : {}".format(retorno))
    return retorno


def insert_data_reprocess(instance_name_r, redis_client, datos):
    #str_Data_r = '&'.join(datos)
    redis_client.lpush(instance_name_r, datos)


def insert_response_to_redis(id, response, redis_client):
    redis_client.set(id, response)

    