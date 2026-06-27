#!/usr/bin/env python3
import csv
import json
import os
from datetime import datetime, timezone
import unicodedata

import requests

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
GEOCODING_API_URL = "https://api.openweathermap.org/geo/1.0/direct"
COUNTRY_CODE = "CO"
DEPARTMENT_NAME = "Boyaca"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "weather_boyaca.csv")
GEOCODING_CACHE_FILE = os.path.join(OUTPUT_DIR, "boyaca_geocoding_cache.json")
TIMEOUT_SECONDS = 20
GEOCODING_LIMIT = 5

# Listado de los 123 municipios de Boyaca en formato ASCII para evitar
# problemas de codificacion en entornos de ejecucion distintos.
MUNICIPALITIES = [
    "Chiquiza",
    "Chivata",
    "Combita",
    "Cucaita",
    "Motavita",
    "Oicata",
    "Samaca",
    "Siachoque",
    "Sora",
    "Soraca",
    "Sotaquira",
    "Toca",
    "Tunja",
    "Tuta",
    "Ventaquemada",
    "Chiscas",
    "El Cocuy",
    "El Espino",
    "Guacamayas",
    "Guican",
    "Panqueba",
    "Labranzagrande",
    "Pajarito",
    "Paya",
    "Pisba",
    "Berbeo",
    "Campohermoso",
    "Miraflores",
    "Paez",
    "San Eduardo",
    "Zetaquira",
    "Boyaca",
    "Cienega",
    "Jenesano",
    "Nuevo Colon",
    "Ramiriqui",
    "Rondon",
    "Tibana",
    "Turmeque",
    "Umbita",
    "Viracacha",
    "Chinavita",
    "Garagoa",
    "Macanal",
    "Pachavita",
    "San Luis de Gaceno",
    "Santa Maria",
    "Boavita",
    "Covarachia",
    "La Uvita",
    "San Mateo",
    "Sativanorte",
    "Sativasur",
    "Soata",
    "Susacon",
    "Tipacoque",
    "Briceno",
    "Buenavista",
    "Caldas",
    "Chiquinquira",
    "Coper",
    "La Victoria",
    "Maripi",
    "Muzo",
    "Otanche",
    "Pauna",
    "Quipama",
    "Saboya",
    "San Miguel de Sema",
    "San Pablo de Borbur",
    "Tunungua",
    "Almeida",
    "Chivor",
    "Guateque",
    "Guayata",
    "La Capilla",
    "Somondoco",
    "Sutatenza",
    "Tenza",
    "Arcabuco",
    "Chitaraque",
    "Gachantiva",
    "Moniquira",
    "Raquira",
    "Sachica",
    "San Jose de Pare",
    "Santa Sofia",
    "Santana",
    "Sutamarchan",
    "Tinjaca",
    "Togui",
    "Villa de Leyva",
    "Aquitania",
    "Cuitiva",
    "Firavitoba",
    "Gameza",
    "Iza",
    "Mongua",
    "Mongui",
    "Nobsa",
    "Pesca",
    "Sogamoso",
    "Tibasosa",
    "Topaga",
    "Tota",
    "Belen",
    "Busbanza",
    "Cerinza",
    "Corrales",
    "Duitama",
    "Floresta",
    "Paipa",
    "Santa Rosa de Viterbo",
    "Tutaza",
    "Beteitiva",
    "Chita",
    "Jerico",
    "Paz de Rio",
    "Socha",
    "Socota",
    "Tasco",
    "Cubara",
    "Puerto Boyaca",
]


def normalize_text(value):
    if not value:
        return ""
    return "".join(
        ch
        for ch in unicodedata.normalize("NFKD", str(value).lower())
        if not unicodedata.combining(ch)
    )


def unix_to_utc_iso(unix_value):
    if unix_value is None:
        return None
    return datetime.fromtimestamp(unix_value, tz=timezone.utc).isoformat(timespec="seconds")


def load_geocoding_cache(path):
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save_geocoding_cache(path, cache):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def geocode_municipality(session, api_key, municipality):
    params = {
        "q": f"{municipality},{DEPARTMENT_NAME},{COUNTRY_CODE}",
        "appid": api_key,
        "limit": GEOCODING_LIMIT,
    }

    response = session.get(GEOCODING_API_URL, params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise RuntimeError("Sin resultados de geocodificacion")

    normalized_department = normalize_text(DEPARTMENT_NAME)

    best = None
    for item in results:
        if item.get("country") != COUNTRY_CODE:
            continue
        if normalized_department in normalize_text(item.get("state", "")):
            best = item
            break

    if best is None:
        best = next((item for item in results if item.get("country") == COUNTRY_CODE), results[0])

    return {
        "lat": best.get("lat"),
        "lon": best.get("lon"),
        "name": best.get("name", municipality),
        "state": best.get("state", DEPARTMENT_NAME),
        "country": best.get("country", COUNTRY_CODE),
    }


def fetch_weather_by_coordinates(session, api_key, municipality, location):
    params = {
        "lat": location["lat"],
        "lon": location["lon"],
        "appid": api_key,
        "units": "metric",
        "lang": "es",
    }

    response = session.get(WEATHER_API_URL, params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    weather = (data.get("weather") or [{}])[0]
    main = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    rain = data.get("rain", {})
    snow = data.get("snow", {})
    sys_data = data.get("sys", {})

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "municipio": municipality,
        "municipio_api": data.get("name") or location.get("name") or municipality,
        "departamento": location.get("state") or DEPARTMENT_NAME,
        "pais": location.get("country") or COUNTRY_CODE,
        "lat": data.get("coord", {}).get("lat", location.get("lat")),
        "lon": data.get("coord", {}).get("lon", location.get("lon")),
        "temp": main.get("temp"),
        "sensacion": main.get("feels_like"),
        "temp_min": main.get("temp_min"),
        "temp_max": main.get("temp_max"),
        "humedad": main.get("humidity"),
        "presion": main.get("pressure"),
        "presion_nivel_mar": main.get("sea_level"),
        "presion_suelo": main.get("grnd_level"),
        "viento": wind.get("speed"),
        "viento_direccion": wind.get("deg"),
        "viento_racha": wind.get("gust"),
        "nubosidad": clouds.get("all"),
        "visibilidad": data.get("visibility"),
        "lluvia_1h": rain.get("1h"),
        "lluvia_3h": rain.get("3h"),
        "nieve_1h": snow.get("1h"),
        "nieve_3h": snow.get("3h"),
        "amanecer_utc": unix_to_utc_iso(sys_data.get("sunrise")),
        "atardecer_utc": unix_to_utc_iso(sys_data.get("sunset")),
        "timezone_seg": data.get("timezone"),
        "clima_id": weather.get("id"),
        "clima_principal": weather.get("main"),
        "descripcion": weather.get("description"),
        "icono": weather.get("icon"),
        "dt_utc": unix_to_utc_iso(data.get("dt")),
        "base": data.get("base"),
        "cod": data.get("cod"),
    }


def main():
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        raise RuntimeError("La variable de entorno OWM_API_KEY no esta definida")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    geocoding_cache = load_geocoding_cache(GEOCODING_CACHE_FILE)

    fieldnames = [
        "timestamp_utc",
        "municipio",
        "municipio_api",
        "departamento",
        "pais",
        "lat",
        "lon",
        "temp",
        "sensacion",
        "temp_min",
        "temp_max",
        "humedad",
        "presion",
        "presion_nivel_mar",
        "presion_suelo",
        "viento",
        "viento_direccion",
        "viento_racha",
        "nubosidad",
        "visibilidad",
        "lluvia_1h",
        "lluvia_3h",
        "nieve_1h",
        "nieve_3h",
        "amanecer_utc",
        "atardecer_utc",
        "timezone_seg",
        "clima_id",
        "clima_principal",
        "descripcion",
        "icono",
        "dt_utc",
        "base",
        "cod",
    ]

    file_exists = os.path.exists(OUTPUT_FILE)

    with requests.Session() as session:
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()

            for municipality in MUNICIPALITIES:
                try:
                    location = geocoding_cache.get(municipality)
                    if not location or "lat" not in location or "lon" not in location:
                        location = geocode_municipality(session, api_key, municipality)
                        geocoding_cache[municipality] = location

                    row = fetch_weather_by_coordinates(session, api_key, municipality, location)
                    writer.writerow(row)
                    print(f"OK: {municipality}")
                except Exception as exc:
                    print(f"ERROR en {municipality}: {exc}")

    save_geocoding_cache(GEOCODING_CACHE_FILE, geocoding_cache)


if __name__ == "__main__":
    main()
