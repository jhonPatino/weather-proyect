#!/usr/bin/env python3
"""Dashboard de Streamlit para los datos climaticos de Boyaca.

Ejecucion local:

    pip install -r requirements-dashboard.txt
    streamlit run dashboard.py
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = os.path.join("data", "weather_boyaca.csv")

# Columnas numericas que vienen como texto en el CSV.
NUMERIC_COLUMNS = [
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
]

CLIMA_ES = {
    "Clear": "Despejado",
    "Clouds": "Nublado",
    "Rain": "Lluvia",
    "Drizzle": "Llovizna",
    "Thunderstorm": "Tormenta",
    "Snow": "Nieve",
    "Mist": "Neblina",
    "Fog": "Niebla",
}

# --- Paleta de diseno (cielo andino de altura) ---
BG = "#0c1014"
TEXT = "#e8ecf2"
MUTED = "#8a94a6"
AMBER = "#f0a542"
CORAL = "#e8694a"
TEAL = "#58b0bf"
INK = "#3b6f93"
GRID = "rgba(255,255,255,0.06)"

# Escala de temperatura: frio (teal) -> templado (arena) -> calido (brasa).
TEMP_SCALE = [
    [0.0, "#3a6e8f"],
    [0.35, "#6fa6b4"],
    [0.55, "#d8cfa6"],
    [0.78, "#e89a4a"],
    [1.0, "#d8502e"],
]

# Color por condicion de clima, consistente entre graficos.
CLIMA_COLORS = {
    "Despejado": "#f0a542",
    "Nublado": "#5f86a6",
    "Lluvia": "#3b6f93",
    "Llovizna": "#6fa3bf",
    "Tormenta": "#7d6fb0",
    "Nieve": "#cfe0ea",
    "Neblina": "#9aa6b2",
    "Niebla": "#8a94a6",
}

CATEGORICAL = [TEAL, AMBER, CORAL, INK, "#b6c08f", "#a98fb0"]

FONT_STACK = "Archivo, -apple-system, sans-serif"


st.set_page_config(
    page_title="Clima · Boyaca",
    page_icon="🌦️",
    layout="wide",
)


def inject_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,500&family=Archivo:wght@400;500;600;700&family=Spline+Sans+Mono:wght@500;600&display=swap');

:root {
  --bg: #0c1014;
  --panel: #141b24;
  --panel-2: #18212c;
  --border: rgba(255,255,255,0.08);
  --text: #e8ecf2;
  --muted: #8a94a6;
  --amber: #f0a542;
  --coral: #e8694a;
  --teal: #58b0bf;
}

/* Fondo atmosferico con halos de luz */
.stApp {
  background:
    radial-gradient(900px 520px at 12% -8%, rgba(88,176,191,0.10), transparent 60%),
    radial-gradient(820px 600px at 102% 2%, rgba(240,165,66,0.09), transparent 55%),
    radial-gradient(700px 700px at 80% 110%, rgba(59,111,147,0.10), transparent 60%),
    var(--bg);
}
/* Grano sutil */
.stApp::before {
  content: "";
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

html, body, [class*="css"] { font-family: Archivo, sans-serif; }

/* Limpieza del chrome de Streamlit */
[data-testid="stDecoration"], #MainMenu, footer { display: none; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1320px; }

/* ---------- Hero ---------- */
.hero { position: relative; z-index: 1; margin-bottom: 1.6rem; }
.hero .kicker {
  font-family: 'Spline Sans Mono', monospace;
  font-size: 0.72rem; letter-spacing: 0.34em; text-transform: uppercase;
  color: var(--teal); margin-bottom: 0.35rem;
}
.hero h1 {
  font-family: 'Fraunces', serif; font-weight: 600;
  font-size: clamp(2.4rem, 5vw, 3.6rem); line-height: 0.98;
  margin: 0; color: var(--text); letter-spacing: -0.01em;
}
.hero h1 em {
  font-style: italic; font-weight: 500;
  background: linear-gradient(95deg, var(--amber), var(--coral));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p {
  color: var(--muted); font-size: 0.96rem; margin: 0.7rem 0 0; max-width: 56ch;
}
.dateline {
  font-family: 'Spline Sans Mono', monospace; font-size: 0.78rem;
  color: var(--muted); margin-top: 0.9rem;
  display: flex; gap: 1.4rem; flex-wrap: wrap;
}
.dateline b { color: var(--text); font-weight: 600; }

/* ---------- Tarjetas de metrica ---------- */
.metric-card {
  position: relative; z-index: 1;
  background: linear-gradient(180deg, var(--panel-2), var(--panel));
  border: 1px solid var(--border); border-radius: 16px;
  padding: 1.05rem 1.15rem 1.1rem; height: 100%;
  overflow: hidden; transition: transform .18s ease, border-color .18s ease;
}
.metric-card::after {
  content: ""; position: absolute; left: 0; top: 0; height: 3px; width: 100%;
  background: var(--accent, var(--amber)); opacity: 0.9;
}
.metric-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.18); }
.mc-top { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.55rem; }
.mc-icon { font-size: 1.05rem; filter: saturate(1.1); }
.mc-label {
  font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--muted); font-weight: 600;
}
.mc-value {
  font-family: 'Fraunces', serif; font-weight: 600;
  font-size: 2.0rem; line-height: 1; color: var(--text);
}
.mc-unit { font-size: 0.95rem; color: var(--muted); margin-left: 0.18rem; font-family: 'Spline Sans Mono', monospace; }
.mc-sub { margin-top: 0.5rem; font-size: 0.78rem; color: var(--muted); }
.mc-sub b { color: var(--accent, var(--amber)); font-weight: 600; }

/* ---------- Titulos de seccion ---------- */
.section-title {
  font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.35rem;
  color: var(--text); margin: 0.2rem 0 0.1rem; letter-spacing: -0.01em;
}
.section-sub { color: var(--muted); font-size: 0.85rem; margin: 0 0 0.6rem; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
  background: transparent; border-radius: 10px 10px 0 0;
  padding: 0.5rem 1rem; color: var(--muted); font-weight: 600; font-size: 0.9rem;
}
.stTabs [aria-selected="true"] { color: var(--text); background: rgba(255,255,255,0.04); }
.stTabs [data-baseweb="tab-highlight"] { background: var(--amber); height: 2px; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0e151d, #0a0e13);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1 {
  font-family: 'Fraunces', serif; font-weight: 600;
}

/* Plotly contenedor */
[data-testid="stPlotlyChart"] {
  background: linear-gradient(180deg, rgba(24,33,44,0.55), rgba(20,27,36,0.35));
  border: 1px solid var(--border); border-radius: 16px; padding: 0.6rem;
  overflow: hidden;
}
[data-testid="stPlotlyChart"] > div,
[data-testid="stPlotlyChart"] .js-plotly-plot,
[data-testid="stPlotlyChart"] .plot-container { max-width: 100%; border-radius: 12px; overflow: hidden; }

/* DataFrame */
[data-testid="stDataFrame"] { border-radius: 14px; border: 1px solid var(--border); }
.stDownloadButton button {
  border-radius: 10px; border: 1px solid var(--border);
  background: var(--panel-2); color: var(--text); font-weight: 600;
}
.stDownloadButton button:hover { border-color: var(--amber); color: var(--amber); }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp_utc"])

    # Etiqueta legible de cada corrida (redondeada al minuto).
    df["corrida"] = df["timestamp_utc"].dt.strftime("%Y-%m-%d %H:%M UTC")
    df["clima_es"] = df["clima_principal"].map(CLIMA_ES).fillna(df["clima_principal"])
    return df.sort_values("timestamp_utc")


def style_fig(fig, height=None):
    """Aplica el tema oscuro coherente a cualquier figura de Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, color="#c7cedb", size=13),
        margin=dict(l=12, r=12, t=36, b=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
        ),
        colorway=CATEGORICAL,
        hoverlabel=dict(
            bgcolor="#141b24",
            bordercolor="rgba(255,255,255,0.12)",
            font=dict(family=FONT_STACK, color=TEXT),
        ),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def metric_card(col, icon, label, value, unit="", sub="", accent=AMBER):
    col.markdown(
        f"""
<div class="metric-card" style="--accent:{accent}">
  <div class="mc-top"><span class="mc-icon">{icon}</span>
       <span class="mc-label">{label}</span></div>
  <div class="mc-value">{value}<span class="mc-unit">{unit}</span></div>
  <div class="mc-sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def section(title, sub=""):
    st.markdown(
        f'<div class="section-title">{title}</div>'
        + (f'<div class="section-sub">{sub}</div>' if sub else ""),
        unsafe_allow_html=True,
    )


def render_hero(df, corrida_sel, n_muni):
    ultima = df["timestamp_utc"].max().strftime("%d %b %Y · %H:%M UTC")
    n_corridas = df["corrida"].nunique()
    st.markdown(
        f"""
<div class="hero">
  <div class="kicker">Observatorio meteorologico</div>
  <h1>Clima de <em>Boyaca</em></h1>
  <p>Lectura de los municipios del altiplano y los valles boyacenses a partir de
     OpenWeatherMap. Ingesta automatica diaria via GitHub Actions.</p>
  <div class="dateline">
    <span>Ultima captura · <b>{ultima}</b></span>
    <span>Municipios · <b>{n_muni}</b></span>
    <span>Corridas registradas · <b>{n_corridas}</b></span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def main():
    inject_css()

    if not os.path.exists(DATA_FILE):
        st.error(f"No se encontro el archivo de datos: `{DATA_FILE}`")
        st.stop()

    df = load_data(DATA_FILE)
    if df.empty:
        st.warning("El archivo de datos no contiene registros validos.")
        st.stop()

    # --- Sidebar / filtros ---
    st.sidebar.markdown("## 🌦️ Filtros")
    corridas = list(df["corrida"].unique())
    corrida_sel = st.sidebar.selectbox(
        "Corrida (fecha de captura)",
        options=corridas,
        index=len(corridas) - 1,
        help="Cada corrida es una ejecucion del workflow de ingesta.",
    )

    climas = sorted(df["clima_es"].dropna().unique())
    climas_sel = st.sidebar.multiselect(
        "Condicion del clima", options=climas, default=climas
    )

    municipios = sorted(df["municipio"].unique())
    municipios_sel = st.sidebar.multiselect(
        "Municipios (vacio = todos)", options=municipios, default=[]
    )

    snapshot = df[df["corrida"] == corrida_sel].copy()
    if climas_sel:
        snapshot = snapshot[snapshot["clima_es"].isin(climas_sel)]
    if municipios_sel:
        snapshot = snapshot[snapshot["municipio"].isin(municipios_sel)]

    render_hero(df, corrida_sel, snapshot["municipio"].nunique())

    if snapshot.empty:
        st.warning("Ningun registro coincide con los filtros seleccionados.")
        st.stop()

    # --- Tarjetas de metrica ---
    mas_calido = snapshot.loc[snapshot["temp"].idxmax()]
    mas_frio = snapshot.loc[snapshot["temp"].idxmin()]
    cols = st.columns(4)
    metric_card(
        cols[0], "🌡️", "Temp. promedio", f"{snapshot['temp'].mean():.1f}", "°C",
        f"Rango <b>{snapshot['temp'].min():.1f}</b> – <b>{snapshot['temp'].max():.1f}</b> °C",
        accent=AMBER,
    )
    metric_card(
        cols[1], "💧", "Humedad promedio", f"{snapshot['humedad'].mean():.0f}", "%",
        f"Min <b>{snapshot['humedad'].min():.0f}%</b> · Max <b>{snapshot['humedad'].max():.0f}%</b>",
        accent=TEAL,
    )
    metric_card(
        cols[2], "🔥", "Mas calido", f"{mas_calido['temp']:.1f}", "°C",
        f"<b>{mas_calido['municipio']}</b>",
        accent=CORAL,
    )
    metric_card(
        cols[3], "❄️", "Mas frio", f"{mas_frio['temp']:.1f}", "°C",
        f"<b>{mas_frio['municipio']}</b>",
        accent=INK,
    )

    st.write("")
    tab_mapa, tab_rank, tab_dist, tab_evol, tab_datos = st.tabs(
        ["  Mapa  ", "  Rankings  ", "  Distribuciones  ", "  Evolucion  ", "  Datos  "]
    )

    with tab_mapa:
        section("Temperatura por municipio", f"Corrida {corrida_sel}")
        mapa_df = snapshot.dropna(subset=["lat", "lon", "temp"])
        fig = px.scatter_mapbox(
            mapa_df,
            lat="lat",
            lon="lon",
            color="temp",
            size=[9] * len(mapa_df),
            size_max=11,
            opacity=0.7,
            hover_name="municipio",
            hover_data={
                "temp": ":.1f",
                "humedad": True,
                "viento": ":.1f",
                "descripcion": True,
                "lat": False,
                "lon": False,
            },
            color_continuous_scale=TEMP_SCALE,
            zoom=7,
            height=620,
        )
        fig.update_layout(
            mapbox_style="carto-positron",
            autosize=True,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT_STACK, color="#c7cedb"),
            coloraxis_colorbar=dict(title="°C", thickness=12, len=0.7, outlinewidth=0),
            hoverlabel=dict(bgcolor="#141b24", font=dict(family=FONT_STACK, color=TEXT)),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_rank:
        col1, col2 = st.columns(2)
        top = snapshot.nlargest(10, "temp")[["municipio", "temp"]]
        bottom = snapshot.nsmallest(10, "temp")[["municipio", "temp"]]
        with col1:
            section("Los mas calidos", "Top 10 por temperatura")
            fig = px.bar(
                top.sort_values("temp"),
                x="temp",
                y="municipio",
                orientation="h",
                color="temp",
                color_continuous_scale=["#e89a4a", "#d8502e"],
                labels={"temp": "°C", "municipio": ""},
                text="temp",
            )
            fig.update_traces(texttemplate="%{text:.1f}°", textposition="outside",
                              cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig, 420), use_container_width=True)
        with col2:
            section("Los mas frios", "Top 10 por temperatura")
            fig = px.bar(
                bottom.sort_values("temp", ascending=False),
                x="temp",
                y="municipio",
                orientation="h",
                color="temp",
                color_continuous_scale=["#3a6e8f", "#6fa6b4"],
                labels={"temp": "°C", "municipio": ""},
                text="temp",
            )
            fig.update_traces(texttemplate="%{text:.1f}°", textposition="outside",
                              cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_fig(fig, 420), use_container_width=True)

    with tab_dist:
        col1, col2 = st.columns([1.4, 1])
        with col1:
            section("Distribucion de temperatura", "Cuantos municipios en cada rango")
            fig = px.histogram(
                snapshot, x="temp", nbins=20, labels={"temp": "Temperatura (°C)"}
            )
            fig.update_traces(marker_color=AMBER, marker_line_width=0, opacity=0.9)
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)
        with col2:
            section("Condiciones del clima", "Reparto del cielo")
            conteo = snapshot["clima_es"].value_counts().reset_index()
            conteo.columns = ["clima", "municipios"]
            fig = px.pie(
                conteo, names="clima", values="municipios", hole=0.58,
                color="clima", color_discrete_map=CLIMA_COLORS,
            )
            fig.update_traces(textinfo="percent", textfont_size=13,
                              marker=dict(line=dict(color=BG, width=2)))
            st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        section("Humedad frente a temperatura", "Cada punto es un municipio")
        fig = px.scatter(
            snapshot,
            x="temp",
            y="humedad",
            color="clima_es",
            size="viento",
            color_discrete_map=CLIMA_COLORS,
            hover_name="municipio",
            labels={
                "temp": "Temperatura (°C)",
                "humedad": "Humedad (%)",
                "clima_es": "Clima",
                "viento": "Viento (m/s)",
            },
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.25)")))
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)

    with tab_evol:
        section("Evolucion de temperatura", "Comparativa entre corridas del workflow")
        if df["corrida"].nunique() < 2:
            st.info(
                "Aun no hay suficientes corridas para mostrar una evolucion temporal. "
                "Se necesitan al menos dos ejecuciones del workflow."
            )
        else:
            default = municipios_sel or list(snapshot["municipio"].unique())[:5]
            sel = st.multiselect(
                "Municipios a comparar",
                options=municipios,
                default=default,
            )
            evol = df[df["municipio"].isin(sel)]
            fig = px.line(
                evol,
                x="timestamp_utc",
                y="temp",
                color="municipio",
                markers=True,
                labels={"timestamp_utc": "Fecha (UTC)", "temp": "Temperatura (°C)"},
            )
            fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
            st.plotly_chart(style_fig(fig, 460), use_container_width=True)

    with tab_datos:
        section("Registros", f"Corrida {corrida_sel} · {len(snapshot)} municipios")
        st.dataframe(snapshot, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇  Descargar CSV filtrado",
            data=snapshot.to_csv(index=False).encode("utf-8"),
            file_name="clima_boyaca_filtrado.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
