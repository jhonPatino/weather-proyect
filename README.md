# weather-ingesta

Proyecto para la ingesta diaria de datos climaticos de los 123 municipios de Boyaca usando la API de OpenWeatherMap.

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

El workflow en GitHub Actions se ejecuta una vez al dia con el cron:

- `0 0 * * *`

Esto significa que la actualizacion es periodica (diaria), no en tiempo real continuo por segundo.
En cada corrida se consulta la API de OpenWeather, se agregan nuevos registros y se guarda el resultado en modo append.

## Como corre en GitHub Actions

Cada ejecucion del workflow crea una maquina temporal en GitHub, construye el contenedor Docker y ejecuta la ingesta dentro de ese contenedor.
Cuando termina el job, tanto la maquina como el contenedor se destruyen (son efimeros).

Flujo de cada corrida:

1. Trigger por cron diario o ejecucion manual.
2. Checkout del repositorio.
3. Build de imagen Docker.
4. Run del contenedor con `OWM_API_KEY` desde Secrets.
5. Actualizacion de `data/weather_boyaca.csv` y cache de geocodificacion.
6. Commit y push si hubo cambios.

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
Si se despliega en contenedor, el comportamiento esperado es el mismo: ejecutar el script con una frecuencia diaria para mantener actualizado el dataset.
