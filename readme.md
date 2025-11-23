# 🏥 Motor de Scrapeo en Cloud Run — `02-framework-scraping-HR`

Este repositorio alberga un motor de scrapeo diseñado para ejecutarse en **Google Cloud Run**.  
La arquitectura es modular, permitiendo desplegar de forma continua tareas de extracción de datos de diferentes clínicas y farmacias listadas.

---

## 🚀 Características Principales

### ✅ Ejecución Serverless
- Ejecutado en **Google Cloud Run**
- Escalabilidad automática
- Modelo de pago por uso

### ✅ Despliegue Continuo (CI/CD)
- Integrado con **Google Cloud Build**
- El build y despliegue se ejecuta **automáticamente al pushear una rama**
- No requiere intervención manual

### ✅ Configurable
Permite ajustar:
- memoria
- concurrencia
- variables de entorno
- parámetros específicos por scraper
- configuración por JSON

### ✅ Salidas de Datos
Tras finalizar el scrapeo:

📁 **Archivo Parquet**
- almacenamiento eficiente en bucket

📊 **Carga automática en BigQuery**
- creación de tabla externa
- disponible para análisis inmediato

---

## ⏰ Activación Programada del Scraping

Este proyecto incluye:

### 🕒 **Cloud Scheduler**
- programa ejecuciones automáticas del scraping
- envía requests al servicio Cloud Run
- permite control por frecuencia, clínica o segmento

---

## 📂 Estructura del Repositorio


---

## 🔄 Flujo de Trabajo

### 1. Configuración
Los parámetros de scrapeo y el esquema de BigQuery se definen en `config/`.

### 2. Desarrollo
La lógica se modifica en:
- `src/main.py`
- módulos de scrapers específicos

### 3. Despliegue
`deploy.yaml` define cómo Cloud Build:
- construye la imagen Docker
- despliega a Cloud Run
- aplica configuración del servicio

### 4. Ejecución del Scraping
Cloud Run:
- ejecuta el scraper
- extrae los datos
- limpia y transforma
- genera archivo Parquet
- crea o actualiza tabla externa en BigQuery

---

## ✅ Uso del Proyecto

Para usarlo:

### ✅ Solo es necesario **pushear la rama**
Automáticamente:
- se construye la imagen
- se despliega a Cloud Run
- se aplica configuración

### ✅ El scraping puede activarse con:
✅ ejecución manual  
✅ Cloud Scheduler programado  

---

## 📌 Próximas mejoras sugeridas (opcionales)

✅ logs centralizados en Cloud Logging  
✅ dashboards de ejecución  
✅ alertas cuando el scraping falla  
✅ métricas de volumen de extracción  

---

## 👤 Autor

**Jesús Cotrina**  
Infraestructura, automatización y despliegue en GCP
