# weather-ingesta

Proyecto para la ingesta horaria de datos climaticos de los 123 municipios de Boyaca usando la API de OpenWeatherMap.

## Requisito de secreto en GitHub

Agrega `OWM_API_KEY` en el repositorio:

Settings -> Secrets -> Actions -> New repository secret

Nombre del secreto:

- `OWM_API_KEY`

## Ejecucion local

```bash
OWM_API_KEY=tu_key python fetch_weather.py
```

El script consulta estas ciudades (country code `CO`):

- 123 municipios de Boyaca

y guarda resultados en `data/weather_boyaca.csv`.

Tambien guarda cache de geocodificacion en `data/boyaca_geocoding_cache.json` para reducir llamadas repetidas al endpoint de geocoding.

## Ejecucion manual del workflow

1. Ve a la pestana Actions del repositorio.
2. Abre el workflow **Update Weather Data**.
3. Haz clic en **Run workflow** (workflow_dispatch).

## Flujo automatico

El workflow en GitHub Actions se ejecuta cada hora con el cron:

- `0 * * * *`

Esto significa que la actualizacion es periodica (cada hora), no en tiempo real continuo por segundo.
En cada corrida se consulta la API de OpenWeather, se agregan nuevos registros y se guarda el resultado en modo append.

## Campos del CSV generado

El archivo `data/weather_boyaca.csv` se genera o actualiza en modo append con estos campos:

- `timestamp_utc` (UTC ISO)
- `municipio`
- `municipio_api`
- `departamento`
- `pais`
- `lat`
- `lon`
- `temp`
- `sensacion`
- `temp_min`
- `temp_max`
- `humedad`
- `presion`
- `presion_nivel_mar`
- `presion_suelo`
- `viento`
- `viento_direccion`
- `viento_racha`
- `nubosidad`
- `visibilidad`
- `lluvia_1h`
- `lluvia_3h`
- `nieve_1h`
- `nieve_3h`
- `amanecer_utc`
- `atardecer_utc`
- `timezone_seg`
- `clima_id`
- `clima_principal`
- `descripcion`
- `icono`
- `dt_utc`
- `base`
- `cod`

## Nota para Docker

El companero encargado del contenedor Docker tomara `fetch_weather.py` y `requirements.txt` para empaquetar la imagen.
Si se despliega en contenedor, el comportamiento esperado es el mismo: ejecutar el script con una frecuencia de 1 hora para mantener actualizado el dataset.
