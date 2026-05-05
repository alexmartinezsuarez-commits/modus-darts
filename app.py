import subprocess
import sys
import os

# ⚡ INSTALAR PLAYWRIGHT AUTOMÁTICAMENTE
try:
    import playwright
except ImportError:
    print("📥 Instalando Playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "playwright"])
    print("✅ Playwright instalado")

# Descargar Chromium si no existe
playwright_dir = os.path.expanduser("~/.cache/ms-playwright")
if not os.path.exists(playwright_dir):
    print("📥 Descargando Chromium (primera vez, puede tardar ~1 min)...")
    try:
        subprocess.check_call(["playwright", "install", "chromium"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print("✅ Chromium descargado")
    except:
        pass

# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import time

st.set_page_config(page_title="Modus Super Series App", layout="wide", page_icon="🎯")

URLS = {
    "Grupo A Lunes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=770660826&single=true&output=csv",
    "Grupo A Martes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=1188400317&single=true&output=csv",
    "Grupo A Miércoles": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=611921899&single=true&output=csv",
    "Grupo C Jueves": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=1451632905&single=true&output=csv",
    "Grupo B Jueves": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=838707746&single=true&output=csv",
    "Grupo C Viernes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=951305991&single=true&output=csv",
    "Grupo B Viernes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=895443076&single=true&output=csv",
    "Final Sábado": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=843639863&single=true&output=csv",
    "Resumen Semanal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=701394558&single=true&output=csv",
    "Value Bets": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=2019911134&single=true&output=csv"
}

CORTES = {
    "Resumen Semanal": {"filas": (5, 20), "cols": (1, 10), "der_nombres": 5, "der_cols": (1, 10)},
    "Grupo A Lunes":      {"izq_filas": (5, 36), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo A Martes":     {"izq_filas": (5, 36), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo A Miércoles":  {"izq_filas": (5, 36), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo C Jueves":     {"izq_filas": (5, 36), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo B Jueves":     {"izq_filas": (5, 26), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo C Viernes":    {"izq_filas": (5, 36), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Grupo B Viernes":    {"izq_filas": (5, 26), "izq_cols": (0, 5), "der_nombres": 5,  "der_cols": (6, 12)},
    "Final Sábado":       {"izq_filas": (5, 24), "izq_cols": (0, 5), "der_nombres": 6,  "der_cols": (6, 12)},
    "Value Bets":         {"unica_filas": (6, 28), "unica_cols": (0, 10)}
}

PESTANAS_CON_STATS = [k for k in URLS if k not in ("Value Bets",)]

# ═══════════════════════════════════════════════════════════════
# DICCIONARIO DE EMOJIS DE BANDERAS
# ═══════════════════════════════════════════════════════════════
BANDERAS = {
    "GB": "🇬🇧",
    "NL": "🇳🇱",
    "BE": "🇧🇪",
    "PT": "🇵🇹",
    "AU": "🇦🇺",
    "DE": "🇩🇪",
    "PL": "🇵🇱",
    "IE": "🇮🇪",
    "CA": "🇨🇦",
}

# ═══════════════════════════════════════════════════════════════
# MAPEO DE JUGADORES A PAÍSES (REVISADO Y LIMPIADO)
# ═══════════════════════════════════════════════════════════════
JUGADORES_PAISES = {
    # Reino Unido
    "luke littler": "GB",
    "gary anderson": "GB",
    "peter wright": "GB",
    "gerwyn price": "GB",
    "jonny clayton": "GB",
    "james wade": "GB",
    "dave chisnall": "GB",
    "rob cross": "GB",
    "nathan aspinall": "GB",
    "chris dobey": "GB",
    "josh rock": "GB",
    "luke humphries": "GB",
    "michael smith": "GB",
    "ross smith": "GB",
    "stephen bunting": "GB",
    "andrew gilding": "GB",
    "brendan dolan": "GB",
    "ritchie edhouse": "GB",
    "ryan searle": "GB",
    "callan rydz": "GB",
    "joe cullen": "GB",
    "cameron menzies": "GB",
    "connor scutt": "GB",
    "glenn de bois": "GB",
    "nick kenny": "GB",
    "nathan rafferty": "GB",
    "steve west": "GB",
    "neil duff": "GB",
    "johnny haines": "GB",
    "joe heywood": "GB",
    
    # Países Bajos
    "michael van gerwen": "NL",
    "dirk van duijvenbode": "NL",
    "danny noppert": "NL",
    "raymond van barneveld": "NL",
    "wessel nijman": "NL",
    "jermaine wattimena": "NL",
    "gian van veen": "NL",
    "benito van de pas": "NL",
    "jurjen van der velde": "NL",
    
    # Bélgica
    "dimitri van den bergh": "BE",
    "kim huybrechts": "BE",
    "alexis toylo": "BE",
    
    # Portugal
    "jose de sousa": "PT",
    
    # Australia
    "damon heta": "AU",
    
    # Alemania
    "martin schindler": "DE",
    "gabriel clemens": "DE",
    "ricardo pietreczko": "DE",
    "florian hempel": "DE",
    
    # Polonia
    "krzysztof ratajski": "PL",
    
    # Irlanda
    "keane barry": "IE",
    "william o'connor": "IE",
    "ciaran teeters": "IE",
    "dylan slevin": "IE",
    
    # Canadá
    "matt campbell": "CA",
}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "vb_fuente" not in st.session_state:
    st.session_state.vb_fuente = "Resumen Semanal"
if "vb_j1" not in st.session_state:
    st.session_state.vb_j1 = None
if "vb_j2" not in st.session_state:
    st.session_state.vb_j2 = None
if "vb_calcular" not in st.session_state:
    st.session_state.vb_calcular = False
if "last_update" not in st.session_state:
    st.session_state.last_update = {}
if "selected_jornada" not in st.session_state:
    st.session_state.selected_jornada = "Grupo A Lunes"
if "selected_url" not in st.session_state:
    st.session_state.selected_url = URLS.get("Grupo A Lunes")

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES GENERALES
# ─────────────────────────────────────────────
def arreglar_columnas(df):
    nuevas_cols = []
    for i, col in enumerate(df.columns):
        nombre = str(col)
        if nombre == 'nan' or nombre.strip() == '':
            nombre = f"Dato_{i}"
        while nombre in nuevas_cols:
            nombre = f"{nombre}_{i}"
        nuevas_cols.append(nombre)
    df.columns = nuevas_cols
    return df

def pintar_partidos(fila):
    if (fila.name // 2) % 2 == 0:
        return ['background-color: rgba(150, 150, 150, 0.15)'] * len(fila)
    return ['background-color: transparent'] * len(fila)

def extraer_stats_diarias(df, fila_n, col_rango):
    try:
        nombres = df.iloc[fila_n, col_rango[0]:col_rango[1]].values
        jugadores = [str(n).strip() for n in nombres if str(n).strip() not in ['nan', '']]
        data_final = {}
        for i, j in enumerate(jugadores):
            stats = {}
            curr_f = fila_n + 1
            while curr_f + 1 < len(df) and curr_f < fila_n + 35:
                tit = str(df.iloc[curr_f, col_rango[0]]).strip()
                
                if tit != 'nan' and tit != '':
                    val_fila1 = str(df.iloc[curr_f + 1, col_rango[0] + i]).strip() if curr_f + 1 < len(df) else 'nan'
                    val_fila2 = str(df.iloc[curr_f + 2, col_rango[0] + i]).strip() if curr_f + 2 < len(df) else 'nan'
                    
                    val = val_fila1 if val_fila1 != 'nan' else val_fila2
                    if val != 'nan' and val != '':
                        stats[tit] = val
                curr_f += 1
            data_final[j] = stats
        return data_final
    except:
        return {}

def extraer_stats_resumen_semanal(df):
    """Extrae stats de Resumen Semanal con estructura especial (columnas separadas por =)"""
    try:
        headers = [str(v).strip() for v in df.iloc[5].values if str(v).strip() not in ['', 'nan']]
        
        data = df.iloc[6:].copy()
        
        jugadores = {}
        
        for idx, row in data.iterrows():
            nombre = str(row.iloc[1]).strip() if len(row) > 1 else ""
            
            if nombre in ['nan', '', '=']:
                continue
                
            stats = {}
            
            col_idx = 2
            header_idx = 1
            
            while col_idx < len(row) and header_idx < len(headers):
                valor = row.iloc[col_idx]
                header = headers[header_idx]
                
                if header.strip() == '=':
                    col_idx += 1
                    header_idx += 1
                    continue
                
                if str(valor).strip() not in ['nan', '', '=']:
                    stats[header.lower().strip()] = valor
                
                col_idx += 1
                header_idx += 1
            
            if stats:
                jugadores[nombre.lower()] = stats
        
        return jugadores
    except Exception as e:
        st.error(f"Error extrayendo Resumen Semanal: {e}")
        return {}

@st.cache_data(ttl=5)
def cargar_jugadores_desde(pestana: str):
    """Carga jugadores desde Google Sheets con stats"""
    try:
        url = URLS.get(pestana, "")
        if not url:
            return {}
        
        df = pd.read_csv(url, header=None)
        st.session_state.last_update[pestana] = datetime.now()

        fila_header = None
        for i, row in df.iterrows():
            if any(str(v).strip().lower() == "jugador" for v in row.values):
                fila_header = i
                break

        if fila_header is None:
            corte = CORTES.get(pestana, {})
            if "der_nombres" in corte:
                der_f  = corte["der_nombres"]
                der_c  = corte["der_cols"]
                stats  = extraer_stats_diarias(df, der_f, der_c)
                jugadores = {}
                for nombre, s in stats.items():
                    pr       = safe_float(_buscar_stat(s, ["global", "puntuación", "puntuacion"]))
                    lam_180  = safe_float(_buscar_stat(s, ["180", "ciento"]))
                    lam_legs = safe_float(_buscar_stat(s, ["legs por partido", "promedio legs", "leg por partido"]))
                    promedio_dardos = safe_float(_buscar_stat(s, ["promedio puntos", "average", "promedio dardos", "ppd", "media puntos"]))
                    checkouts = safe_float(str(_buscar_stat(s, ["checkout"])).replace("%", ""))
                    pct_vic = safe_float(str(_buscar_stat(s, ["porcentaje victoria", "% victoria"])).replace("%", ""))
                    jugadores[nombre.lower()] = {
                        "nombre_original": nombre,
                        "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs,
                        "promedio_dardos": promedio_dardos,
                        "checkouts": checkouts, "pct_victorias": pct_vic
                    }
                return jugadores
            return {}

        headers = [str(v).strip() for v in df.iloc[fila_header].values]
        data    = df.iloc[fila_header + 1:].copy()
        data.columns = headers
        data = data.reset_index(drop=True)

        def buscar_col(keywords):
            for h in headers:
                if any(kw.lower() in h.lower() for kw in keywords):
                    return h
            return None

        col_jugador = buscar_col(["jugador", "nombre"])
        col_pr      = buscar_col(["puntuación global", "puntuacion global", "global", "power"])
        col_180     = buscar_col(["180"])
        col_legs    = buscar_col(["legs", "leg"])
        col_promedio_dardos = buscar_col(["promedio puntos", "average", "promedio dardos", "ppd", "media puntos"])
        col_checkouts = buscar_col(["checkout"])
        col_pct_vic = buscar_col(["porcentaje victoria", "% victoria", "% victoria", "%victoria"])

        jugadores = {}
        for _, fila in data.iterrows():
            nombre = str(fila.get(col_jugador, "")).strip() if col_jugador else ""
            if not nombre or nombre.lower() in ["nan", "jugador", ""]:
                continue
            pr       = safe_float(fila.get(col_pr,    0)) if col_pr    else 0.0
            lam_180  = safe_float(fila.get(col_180,   0)) if col_180   else 0.0
            lam_legs = safe_float(fila.get(col_legs,  0)) if col_legs  else 0.0
            promedio_dardos = safe_float(fila.get(col_promedio_dardos, 0)) if col_promedio_dardos else 0.0
            checkouts = safe_float(str(fila.get(col_checkouts, 0)).replace("%", "")) if col_checkouts else 0.0
            pct_vic = safe_float(str(fila.get(col_pct_vic, 0)).replace("%", "")) if col_pct_vic else 0.0
            jugadores[nombre.lower()] = {
                "nombre_original": nombre,
                "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs,
                "promedio_dardos": promedio_dardos,
                "checkouts": checkouts, "pct_victorias": pct_vic
            }
        return jugadores
    except Exception as e:
        st.error(f"Error cargando {pestana}: {e}")
        return {}

@st.cache_data(ttl=5)
def cargar_todo(url, opcion, cortes):
    try:
        df = pd.read_csv(url, header=None)
        st.session_state.last_update[opcion] = datetime.now()
        
        if opcion == "Resumen Semanal":
            stats = extraer_stats_resumen_semanal(df)
            
            df_list = []
            for nombre_lower, stat_dict in stats.items():
                fila = {"Jugador": nombre_lower}
                
                orden_columnas = [
                    "legs por partido", "media 180 por partida", "promedio puntos",
                    "diferencia legs", "promedio checkouts", "número victorias",
                    "número derrotas", "porcentaje victoria"
                ]
                
                for col in orden_columnas:
                    for k, v in stat_dict.items():
                        if col in k.lower():
                            fila[k] = v
                
                for k, v in stat_dict.items():
                    if "puntuación" in k.lower() or "puntacion" in k.lower():
                        fila[k] = v
                
                df_list.append(fila)
            
            df_display = pd.DataFrame(df_list) if df_list else pd.DataFrame()
            
            return df_display, stats
        
        elif opcion == "Value Bets":
            f, c = cortes["unica_filas"], cortes["unica_cols"]
            res = df.iloc[f[0]:f[1], c[0]:c[1]]
            res.columns = res.iloc[0]; res = res[1:]
            return arreglar_columnas(res.dropna(how='all')), None
        else:
            f, c = cortes["izq_filas"], cortes["izq_cols"]
            izq = df.iloc[f[0]:f[1], c[0]:c[1]]
            izq.columns = izq.iloc[0]; izq = izq[1:]
            s = extraer_stats_diarias(df, cortes["der_nombres"], cortes["der_cols"])
            return arreglar_columnas(izq.dropna(how='all')), s
    except Exception as e:
        st.error(f"Error cargando {opcion}: {e}")
        return None, None

@st.cache_data(ttl=10)
def obtener_partidos_vivos_api():
    """Obtiene partidos en vivo directamente desde la API de MODUS"""
    try:
        base_url = "https://api-igamedc.igamemedia.com/api/mss-web"
        
        response = requests.get(f"{base_url}/results-fixtures", timeout=5)
        if response.status_code != 200:
            return None
        
        data = response.json()
        week_activa = data.get("selected", {}).get("week", "")
        grupos = data.get("selected", {}).get("groups", [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 8}])
        
        partidos_vivos = []
        
        for grupo in grupos:
            url = f"{base_url}/results-fixtures?group={grupo['id']}"
            if week_activa:
                url += f"&week={week_activa}"
            
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    fixtures = resp.json().get("Fixtures", resp.json().get("fixtures", []))
                    
                    for fixture in fixtures:
                        if fixture.get("status", "").lower() != "not started":
                            fixture_id = fixture.get("gameId") or fixture.get("Id") or fixture.get("id")
                            
                            if fixture_id:
                                try:
                                    detail_resp = requests.get(f"{base_url}/fixtures/{fixture_id}", timeout=5)
                                    if detail_resp.status_code == 200:
                                        detail = detail_resp.json()
                                        stats = detail.get("playersStatistics", {}).get("statistics", [])
                                        
                                        if stats and len(stats) >= 2:
                                            partidos_vivos.append({
                                                "id": fixture_id,
                                                "fecha": fixture.get("fixture", ""),
                                                "j1": fixture.get("playerHome", ""),
                                                "j2": fixture.get("playerAway", ""),
                                                "score_j1": fixture.get("scorePlayerHome", ""),
                                                "score_j2": fixture.get("scorePlayerAway", ""),
                                                "j1_average": stats[0].get("average", ""),
                                                "j2_average": stats[1].get("average", ""),
                                                "j1_180s": stats[0].get("turns180", ""),
                                                "j2_180s": stats[1].get("turns180", ""),
                                                "j1_checkout": stats[0].get("checkoutPercentage", ""),
                                                "j2_checkout": stats[1].get("checkoutPercentage", "")
                                            })
                                except:
                                    pass
            except:
                continue
        
        return partidos_vivos if partidos_vivos else None
        
    except Exception as e:
        st.warning(f"⚠️ Error obteniendo datos de MODUS: {e}")
        return None

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE BANDERAS Y H2H
# ═══════════════════════════════════════════════════════════════

def get_jornada_actual():
    """
    Detecta la jornada activa según día y hora actual.
    Maneja correctamente las jornadas nocturnas que cruzan medianoche.
    
    Retorna: (nombre_jornada, url, es_activa) o (None, None, False)
    """
    ahora = datetime.now()
    hora_actual = ahora.hour + ahora.minute / 60
    dia_semana = ahora.weekday()
    
    if dia_semana in [0, 1, 2]:
        if 10.0 <= hora_actual < 16.0:
            jornadas_grupo_a = {
                0: ("Grupo A Lunes", URLS["Grupo A Lunes"]),
                1: ("Grupo A Martes", URLS["Grupo A Martes"]),
                2: ("Grupo A Miércoles", URLS["Grupo A Miércoles"])
            }
            nombre, url = jornadas_grupo_a[dia_semana]
            return nombre, url, True
    
    if dia_semana in [3, 4]:
        if 13.0 <= hora_actual < 19.0:
            jornadas_grupo_c = {
                3: ("Grupo C Jueves", URLS["Grupo C Jueves"]),
                4: ("Grupo C Viernes", URLS["Grupo C Viernes"])
            }
            nombre, url = jornadas_grupo_c[dia_semana]
            return nombre, url, True
    
    if hora_actual >= 22.0:
        if dia_semana == 3:
            return "Grupo B Jueves", URLS["Grupo B Jueves"], True
        elif dia_semana == 4:
            return "Grupo B Viernes", URLS["Grupo B Viernes"], True
    
    if dia_semana == 5 and hora_actual >= 20.0:
        return "Final Sábado", URLS["Final Sábado"], True
    
    elif hora_actual < 3.0:
        ayer = ahora - timedelta(days=1)
        dia_ayer = ayer.weekday()
        
        if dia_ayer == 3:
            return "Grupo B Jueves", URLS["Grupo B Jueves"], True
        elif dia_ayer == 4:
            return "Grupo B Viernes", URLS["Grupo B Viernes"], True
        elif dia_ayer == 5:
            return "Final Sábado", URLS["Final Sábado"], True
    
    return None, None, False

def get_proxima_jornada():
    """Retorna la próxima jornada después de la actual."""
    
    jornadas_orden = [
        ("Grupo A Lunes", URLS["Grupo A Lunes"], 0, 10.0),
        ("Grupo A Martes", URLS["Grupo A Martes"], 1, 10.0),
        ("Grupo A Miércoles", URLS["Grupo A Miércoles"], 2, 10.0),
        ("Grupo C Jueves", URLS["Grupo C Jueves"], 3, 13.0),
        ("Grupo B Jueves", URLS["Grupo B Jueves"], 3, 22.0),
        ("Grupo C Viernes", URLS["Grupo C Viernes"], 4, 13.0),
        ("Grupo B Viernes", URLS["Grupo B Viernes"], 4, 22.0),
        ("Final Sábado", URLS["Final Sábado"], 5, 20.0),
    ]
    
    ahora = datetime.now()
    hora_actual = ahora.hour + ahora.minute / 60
    dia_semana = ahora.weekday()
    
    for nombre, url, dia, hora_inicio in jornadas_orden:
        if dia > dia_semana or (dia == dia_semana and hora_inicio > hora_actual):
            return nombre, url
    
    return jornadas_orden[0][0], jornadas_orden[0][1]

def obtener_bandera(nombre_jugador):
    """Obtiene el emoji de bandera del jugador."""
    nombre_lower = nombre_jugador.lower().strip().replace("_", " ")
    codigo_pais = JUGADORES_PAISES.get(nombre_lower, None)
    
    if codigo_pais and codigo_pais in BANDERAS:
        return BANDERAS[codigo_pais]
    
    return None

def similitud_nombres(nombre1, nombre2, umbral=0.6):
    """
    Compara dos nombres con fuzzy matching.
    Retorna True si la similitud es mayor al umbral.
    """
    nombre1_lower = nombre1.lower().strip()
    nombre2_lower = nombre2.lower().strip()
    
    nombre1_clean = nombre1_lower.replace(" ", "").replace(".", "")
    nombre2_clean = nombre2_lower.replace(" ", "").replace(".", "")
    
    similitud = SequenceMatcher(None, nombre1_clean, nombre2_clean).ratio()
    
    if " " in nombre1_lower and " " in nombre2_lower:
        partes1 = nombre1_lower.split()
        partes2 = nombre2_lower.split()
        
        if partes1[0][0] == partes2[0][0] and SequenceMatcher(None, partes1[-1], partes2[-1]).ratio() > 0.8:
            return True
    
    return similitud >= umbral

@st.cache_data(ttl=30, show_spinner=False)
def obtener_cuotas_winamax(j1_nombre, j2_nombre):
    """
    Obtiene cuotas de Winamax (requiere playwright instalado).
    """
    
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
    except ImportError:
        return {
            "error": "⚠️ Playwright no instalado. La función de Winamax está deshabilitada.",
            "victoria": {}, "180s": {}, "mas_180s": {}, 
            "handi_j1": {}, "handi_j2": {}, "total_legs": {}
        }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "es-ES,es;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            
            page = context.new_page()
            
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """)
            
            try:
                page.goto("https://www.winamax.es/apuestas", timeout=30000, wait_until="domcontentloaded")
                time.sleep(2)
                
                try:
                    page.click("text=Dardos", timeout=10000)
                    time.sleep(2)
                except:
                    try:
                        page.click('a:has-text("Dardos")')
                        time.sleep(2)
                    except:
                        return {
                            "error": "❌ No se encontró sección de Dardos",
                            "victoria": {}, "180s": {}, "mas_180s": {}, 
                            "handi_j1": {}, "handi_j2": {}, "total_legs": {}
                        }
                
                try:
                    page.click("text=MODUS", timeout=10000)
                    time.sleep(2)
                except:
                    try:
                        page.click('text=Modus')
                        time.sleep(2)
                    except:
                        return {
                            "error": "❌ No se encontró MODUS Super Series",
                            "victoria": {}, "180s": {}, "mas_180s": {}, 
                            "handi_j1": {}, "handi_j2": {}, "total_legs": {}
                        }
                
                page.wait_for_selector("[class*='match'], [data-testid*='match'], .game-row, [class*='event']", timeout=15000)
                time.sleep(2)
                
                html = page.content()
                
                soup = BeautifulSoup(html, "html.parser")
                
                partidos = soup.find_all("div", recursive=True, limit=50)
                
                partido_encontrado = None
                for partido in partidos:
                    texto = partido.get_text()
                    
                    has_j1 = similitud_nombres(j1_nombre, texto, umbral=0.5)
                    has_j2 = similitud_nombres(j2_nombre, texto, umbral=0.5)
                    
                    if has_j1 and has_j2:
                        partido_encontrado = partido
                        break
                
                if not partido_encontrado:
                    return {
                        "error": f"❌ Partido {j1_nombre} vs {j2_nombre} no encontrado",
                        "victoria": {}, "180s": {}, "mas_180s": {}, 
                        "handi_j1": {}, "handi_j2": {}, "total_legs": {}
                    }
                
                cuotas = {
                    "victoria": {"j1": None, "j2": None},
                    "180s": {
                        "j1_05": None,
                        "j1_15": None,
                        "j2_05": None,
                        "j2_15": None,
                        "ambos_05": None,
                        "ambos_15": None,
                        "ambos_25": None,
                    },
                    "mas_180s": {"j1": None, "j2": None, "empate": None},
                    "handi_j1": {
                        "minus_15": None,
                        "plus_15": None,
                        "minus_25": None,
                        "plus_25": None,
                    },
                    "handi_j2": {
                        "minus_15": None,
                        "plus_15": None,
                        "minus_25": None,
                        "plus_25": None,
                    },
                    "total_legs": {"over": None, "under": None},
                    "error": None
                }
                
                browser.close()
                
                return cuotas
            
            except Exception as e:
                browser.close()
                return {
                    "error": f"❌ Error durante scraping: {str(e)[:50]}",
                    "victoria": {}, "180s": {}, "mas_180s": {}, 
                    "handi_j1": {}, "handi_j2": {}, "total_legs": {}
                }
    
    except Exception as e:
        return {
            "error": f"❌ Error: {str(e)[:50]}",
            "victoria": {}, "180s": {}, "mas_180s": {}, 
            "handi_j1": {}, "handi_j2": {}, "total_legs": {}
        }

def calcular_tendencia(valor_actual, valor_anterior):
    """Calcula la tendencia comparando valor actual con anterior."""
    if valor_anterior == 0:
        return '→'
    
    diferencia = ((valor_actual - valor_anterior) / valor_anterior) * 100
    
    if diferencia > 2:
        return '↑'
    elif diferencia < -2:
        return '↓'
    else:
        return '→'

@st.cache_data(ttl=5)
def extraer_h2h_semanal(j1_nombre, j2_nombre):
    """
    Extrae el historial H2H de todos los días de la semana.
    """
    h2h_data = {
        "victorias_j1": 0,
        "victorias_j2": 0,
        "partidos": []
    }
    
    dias_semana = [
        "Grupo A Lunes", "Grupo A Martes", "Grupo A Miércoles",
        "Grupo C Jueves", "Grupo B Jueves",
        "Grupo C Viernes", "Grupo B Viernes",
        "Final Sábado"
    ]
    
    j1_lower = j1_nombre.lower().strip().replace("_", " ")
    j2_lower = j2_nombre.lower().strip().replace("_", " ")
    
    for dia in dias_semana:
        try:
            df_partidos, _ = cargar_todo(URLS[dia], dia, CORTES[dia])
            
            if df_partidos is None or len(df_partidos) < 2:
                continue
            
            for i in range(0, len(df_partidos) - 1, 2):
                fila_j1 = df_partidos.iloc[i]
                fila_j2 = df_partidos.iloc[i + 1]
                
                nombre_j1 = str(fila_j1.iloc[0]).strip().lower().replace("_", " ")
                nombre_j2 = str(fila_j2.iloc[0]).strip().lower().replace("_", " ")
                
                es_enfrentamiento = (
                    (j1_lower in nombre_j1 or nombre_j1 in j1_lower) and
                    (j2_lower in nombre_j2 or nombre_j2 in j2_lower)
                ) or (
                    (j2_lower in nombre_j1 or nombre_j1 in j2_lower) and
                    (j1_lower in nombre_j2 or nombre_j2 in j1_lower)
                )
                
                if es_enfrentamiento:
                    resultado_j1 = str(fila_j1.iloc[1]).strip() if len(fila_j1) > 1 else ""
                    resultado_j2 = str(fila_j2.iloc[1]).strip() if len(fila_j2) > 1 else ""
                    
                    ganador = None
                    marcador = f"{resultado_j1}-{resultado_j2}"
                    
                    if "4" in resultado_j1:
                        ganador = nombre_j1.title()
                        if j1_lower in nombre_j1 or nombre_j1 in j1_lower:
                            h2h_data["victorias_j1"] += 1
                        else:
                            h2h_data["victorias_j2"] += 1
                    elif "4" in resultado_j2:
                        ganador = nombre_j2.title()
                        if j1_lower in nombre_j2 or nombre_j2 in j1_lower:
                            h2h_data["victorias_j1"] += 1
                        else:
                            h2h_data["victorias_j2"] += 1
                    
                    if ganador:
                        h2h_data["partidos"].append({
                            "dia": dia,
                            "jugador1": nombre_j1.title(),
                            "jugador2": nombre_j2.title(),
                            "marcador": marcador,
                            "ganador": ganador
                        })
        except Exception as e:
            continue
    
    return h2h_data

# ─────────────────────────────────────────────
# MATEMÁTICAS VALUE BETS
# ─────────────────────────────────────────────
def safe_float(val, default=0.0):
    try:
        v = float(str(val).replace(',', '.').strip())
        if not np.isfinite(v):
            return default
        return v
    except:
        return default

def sanitize_prob(p):
    if not np.isfinite(p) or p <= 0:
        return 0.0001
    if p >= 1:
        return 0.9999
    return max(0.0001, min(0.9999, p))

def prob_victoria(pr1, pr2):
    if pr1 <= 0 and pr2 <= 0:
        return 0.5, 0.5
    num = (pr1 ** 4.5) * 1.12
    den = num + (pr2 ** 4.5)
    if den == 0:
        return 0.5, 0.5
    p1 = num / den
    return sanitize_prob(p1), sanitize_prob(1 - p1)

def prob_180s(lam1, lam2):
    lam_total = lam1 + lam2
    ambos_05 = sanitize_prob((1 - poisson.cdf(0, lam1)) * (1 - poisson.cdf(0, lam2)))
    
    return {
        "J1 +0.5": sanitize_prob(1 - poisson.cdf(0, lam1)),
        "J1 +1.5": sanitize_prob(1 - poisson.cdf(1, lam1)),
        "J2 +0.5": sanitize_prob(1 - poisson.cdf(0, lam2)),
        "J2 +1.5": sanitize_prob(1 - poisson.cdf(1, lam2)),
        "Ambos +0.5": ambos_05,
        "Ambos +1.5": sanitize_prob(1 - poisson.cdf(1, lam_total)),
        "Ambos +2.5": sanitize_prob(1 - poisson.cdf(2, lam_total)),
    }

def quien_hace_mas_180s(lam1, lam2):
    p_empate = sum(poisson.pmf(k, lam1) * poisson.pmf(k, lam2) for k in range(3))
    lam_sum = lam1 + lam2
    if lam_sum == 0:
        return 1/3, 1/3, 1/3
    p_j1 = (1 - p_empate) * (lam1 / lam_sum)
    p_j2 = (1 - p_empate) * (lam2 / lam_sum)
    return sanitize_prob(p_j1), sanitize_prob(p_empate), sanitize_prob(p_j2)

def handicaps_legs(v1, v2):
    denom = v1 * (1 - v2) + v2 * (1 - v1)
    if denom == 0:
        return {k: 0.5 for k in ["J1 -1.5 Legs", "J1 -2.5 Legs", "J1 +1.5 Legs", 
                                  "J1 +2.5 Legs", "J2 -1.5 Legs", "J2 -2.5 Legs",
                                  "J2 +1.5 Legs", "J2 +2.5 Legs"]}
    R = (v1 * (1 - v2)) / denom
    R2 = 1 - R
    return {
        "J1 -1.5 Legs": sanitize_prob(R * 0.75),
        "J1 -2.5 Legs": sanitize_prob(R * 0.50),
        "J1 +1.5 Legs": sanitize_prob(R + (1 - R) * 0.40),
        "J1 +2.5 Legs": sanitize_prob(R + (1 - R) * 0.70),
        "J2 -1.5 Legs": sanitize_prob(R2 * 0.75),
        "J2 -2.5 Legs": sanitize_prob(R2 * 0.50),
        "J2 +1.5 Legs": sanitize_prob(R2 + (1 - R2) * 0.40),
        "J2 +2.5 Legs": sanitize_prob(R2 + (1 - R2) * 0.70),
    }

def legs_totales(lam_legs1, lam_legs2):
    """
    Calcula probabilidades de total de legs usando MEDIA DE LEGS.
    """
    if lam_legs1 + lam_legs2 == 0:
        p = 0.5
    else:
        p = lam_legs1 / (lam_legs1 + lam_legs2)
    
    q = 1 - p
    prob_4_0_j1 = p ** 4
    prob_4_1_j1 = 4 * (p ** 4) * q
    prob_4_0_j2 = q ** 4
    prob_4_1_j2 = 4 * (q ** 4) * p
    
    prob_under_5_5 = prob_4_0_j1 + prob_4_1_j1 + prob_4_0_j2 + prob_4_1_j2
    prob_over_5_5 = 1 - prob_under_5_5
    
    return {
        "Más de 5.5": sanitize_prob(prob_over_5_5),
        "Menos de 5.5": sanitize_prob(prob_under_5_5)
    }

def prob_a_cuota(p):
    p_safe = sanitize_prob(p)
    cuota = 1.0 / p_safe
    return max(1.01, min(999.0, cuota))

def pct(p):
    return f"{p * 100:.1f}%"

def calcular_yield(prob, cuota_bookie):
    return (prob * cuota_bookie) - 1

def badge_yield(y):
    if y > 0:
        return f"✅ +{y*100:.1f}%"
    elif y < -0.05:
        return f"❌ {y*100:.1f}%"
    else:
        return f"➖ {y*100:.1f}%"

def _buscar_stat(stats_dict, keywords):
    for k, v in stats_dict.items():
        if any(kw in k.lower() for kw in keywords):
            return v
    return 0.0

def buscar_jugador(nombre, db):
    nombre_lower = nombre.strip().lower()
    if nombre_lower in db:
        return db[nombre_lower]
    for k, v in db.items():
        if nombre_lower in k or k in nombre_lower:
            return v
    return None

# ═══════════════════════════════════════════════════════════════
# WIDGETS VISUALES
# ═══════════════════════════════════════════════════════════════

def render_pentagon_habilidades(nombre, pr, lam_180, promedio_dardos, checkouts, pct_vic, color="#1f77b4"):
    """Renderiza un pentágono de habilidades (radar chart) para un jugador con SVG."""
    
    pr_norm = min(100, max(0, pr))
    lam_180_norm = min(100, max(0, (lam_180 / 3.0) * 100))
    promedio_dardos_norm = min(100, max(0, (promedio_dardos / 100) * 100))
    checkouts_norm = min(100, max(0, checkouts))
    pct_vic_norm = min(100, max(0, pct_vic))
    
    values = [pr_norm, lam_180_norm, promedio_dardos_norm, checkouts_norm, pct_vic_norm]
    labels = ["Power\nRanking", "λ 180s", "Promedio\nDardos", "Checkouts", "Victorias"]
    
    center_x, center_y = 200, 200
    radius = 150
    angle_offset = -90
    
    points = []
    for i in range(5):
        angle = angle_offset + (i * 72)
        rad = np.radians(angle)
        x = center_x + radius * np.cos(rad)
        y = center_y + radius * np.sin(rad)
        points.append((x, y))
    
    data_points = []
    for i in range(5):
        angle = angle_offset + (i * 72)
        rad = np.radians(angle)
        data_radius = (values[i] / 100) * radius
        x = center_x + data_radius * np.cos(rad)
        y = center_y + data_radius * np.sin(rad)
        data_points.append((x, y))
    
    svg_parts = []
    
    svg_parts.append('<svg width="400" height="450" xmlns="http://www.w3.org/2000/svg">')
    
    svg_parts.append('<rect width="400" height="450" fill="white"/>')
    
    for r_pct in [20, 40, 60, 80, 100]:
        r = (r_pct / 100) * radius
        svg_parts.append(f'<circle cx="{center_x}" cy="{center_y}" r="{r}" fill="none" stroke="rgba(200,200,200,0.3)" stroke-width="1"/>')
    
    for point in points:
        svg_parts.append(f'<line x1="{center_x}" y1="{center_y}" x2="{point[0]}" y2="{point[1]}" stroke="rgba(200,200,200,0.2)" stroke-width="1"/>')
    
    pentagon_path = "M " + " L ".join([f"{p[0]},{p[1]}" for p in points]) + " Z"
    svg_parts.append(f'<path d="{pentagon_path}" fill="none" stroke="rgba(100,100,100,0.2)" stroke-width="1"/>')
    
    data_path = "M " + " L ".join([f"{p[0]},{p[1]}" for p in data_points]) + " Z"
    rgb_color = color.lstrip('#')
    rgb_tuple = tuple(int(rgb_color[i:i+2], 16) for i in (0, 2, 4))
    svg_parts.append(f'<path d="{data_path}" fill="rgba({rgb_tuple[0]},{rgb_tuple[1]},{rgb_tuple[2]},0.2)" stroke="{color}" stroke-width="2"/>')
    
    for point in data_points:
        svg_parts.append(f'<circle cx="{point[0]}" cy="{point[1]}" r="4" fill="{color}" stroke="white" stroke-width="2"/>')
    
    label_positions = [
        (center_x, center_y - radius - 30),
        (center_x + radius * 0.9, center_y - radius * 0.3 - 20),
        (center_x + radius * 0.55, center_y + radius * 0.75 - 15),
        (center_x - radius * 0.55, center_y + radius * 0.75 - 15),
        (center_x - radius * 0.9, center_y - radius * 0.3 - 20),
    ]
    
    for i, (x, y) in enumerate(label_positions):
        svg_parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-size="11" font-family="Arial" fill="#333" font-weight="500">{labels[i]}</text>')
    
    for i, (x, y) in enumerate(data_points):
        offset_x = (x - center_x) * 0.3
        offset_y = (y - center_y) * 0.3
        val_x = x + offset_x
        val_y = y + offset_y
        svg_parts.append(f'<text x="{val_x}" y="{val_y}" text-anchor="middle" font-size="9" font-family="Arial" fill="{color}" font-weight="bold">{values[i]:.0f}</text>')
    
    svg_parts.append('</svg>')
    
    svg_html = "\n".join(svg_parts)
    st.markdown(svg_html, unsafe_allow_html=True)

def tarjeta_jugador(nombre, pr, lam_180, lam_legs, is_left=True, jugador_data=None):
    """Tarjeta visual del jugador con pentágono de habilidades."""
    color = "#1f77b4" if is_left else "#ff7f0e"
    
    bandera = obtener_bandera(nombre)
    nombre_display = f"{bandera} {nombre}" if bandera else f"🎯 {nombre}"
    
    checkouts_prom = jugador_data.get("checkouts", 0) if jugador_data else 0
    pct_victorias = jugador_data.get("pct_victorias", 0) if jugador_data else 0
    promedio_dardos = jugador_data.get("promedio_dardos", 0) if jugador_data else 0
    
    st.markdown(f"<h3 style='color: {color}; text-align: center;'>{nombre_display}</h3>", unsafe_allow_html=True)
    
    render_pentagon_habilidades(nombre, pr, lam_180, promedio_dardos, checkouts_prom, pct_victorias, color)
    
    st.markdown("---")
    
    html_metrics = f"""
    <div style="text-align: center; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin: 20px 0;">
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">Power Ranking</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{pr:.1f}</p>
        </div>
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">λ 180s</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{lam_180:.2f}</p>
        </div>
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">Promedio Dardos</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{promedio_dardos:.1f}</p>
        </div>
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">λ Legs</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{lam_legs:.2f}</p>
        </div>
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">Checkouts</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{checkouts_prom:.0f}%</p>
        </div>
        <div>
            <p style="font-size: 11px; color: #666; margin: 0;">% Victorias</p>
            <p style="font-size: 22px; font-weight: bold; color: {color}; margin: 3px 0;">{pct_victorias:.0f}%</p>
        </div>
    </div>
    """
    st.markdown(html_metrics, unsafe_allow_html=True)

def render_barras_enfrentadas(j1_nombre, j1_prob, j2_nombre, j2_prob, j1_color="#1f77b4", j2_color="#ff7f0e"):
    """Renderiza dos barras horizontales enfrentadas (tipo comparación)."""
    total = j1_prob + j2_prob
    if total == 0:
        j1_prob = j2_prob = 0.5
    
    j1_pct = (j1_prob / total * 100) if total > 0 else 50
    j2_pct = (j2_prob / total * 100) if total > 0 else 50
    
    st.markdown(f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
            <div style="flex: 0 0 25%; text-align: right;">
                <p style="margin: 0; font-weight: bold; font-size: 1.1em; color: {j1_color};">{j1_nombre}</p>
                <p style="margin: 5px 0 0 0; font-size: 1.3em; font-weight: bold; color: {j1_color};">{j1_pct:.1f}%</p>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; height: 45px; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="width: {j1_pct}%; background: linear-gradient(90deg, {j1_color}, {j1_color}dd); display: flex; align-items: center; justify-content: flex-end; padding-right: 10px;">
                        <span style="color: white; font-weight: bold; font-size: 0.9em;">{j1_prob*100:.1f}%</span>
                    </div>
                    <div style="width: {j2_pct}%; background: linear-gradient(90deg, {j2_color}dd, {j2_color}); display: flex; align-items: center; justify-content: flex-start; padding-left: 10px;">
                        <span style="color: white; font-weight: bold; font-size: 0.9em;">{j2_prob*100:.1f}%</span>
                    </div>
                </div>
            </div>
            <div style="flex: 0 0 25%; text-align: left;">
                <p style="margin: 0; font-weight: bold; font-size: 1.1em; color: {j2_color};">{j2_nombre}</p>
                <p style="margin: 5px 0 0 0; font-size: 1.3em; font-weight: bold; color: {j2_color};">{j2_pct:.1f}%</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_bloque_mercado(titulo, prob, cuota_justa, cuota_input, idx):
    """Renderiza un bloque visual para un mercado individual."""
    cuota_num = cuota_input if cuota_input is not None and cuota_input > 0 else None
    if cuota_num:
        yield_val = calcular_yield(prob, cuota_num)
        yield_color = "#28a745" if yield_val > 0 else ("#dc3545" if yield_val < -0.05 else "#6c757d")
        yield_text = f"+{yield_val*100:.1f}%" if yield_val > 0 else f"{yield_val*100:.1f}%"
    else:
        yield_color = "#6c757d"
        yield_text = "−"
    
    st.markdown(f"""
    <div style="
        padding: 16px;
        background: linear-gradient(135deg, rgba(31,119,180,0.08), rgba(31,119,180,0.03));
        border: 1px solid rgba(31,119,180,0.2);
        border-radius: 8px;
        margin-bottom: 12px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px;">
            <div style="flex: 1;">
                <p style="margin: 0 0 8px 0; font-size: 0.9em; font-weight: 600; color: #333;">{titulo}</p>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div>
                        <p style="margin: 0 0 4px 0; font-size: 0.7em; color: #999; text-transform: uppercase;">Probabilidad</p>
                        <p style="margin: 0; font-size: 1.3em; font-weight: bold; color: #1f77b4;">{prob*100:.1f}%</p>
                    </div>
                    <div>
                        <p style="margin: 0 0 4px 0; font-size: 0.7em; color: #999; text-transform: uppercase;">Cuota Justa</p>
                        <p style="margin: 0; font-size: 1.2em; font-weight: bold;">{cuota_justa:.2f}</p>
                    </div>
                </div>
            </div>
            <div style="flex: 0 0 auto; text-align: right;">
                <p style="margin: 0 0 8px 0; font-size: 0.7em; color: #999; text-transform: uppercase;">Tu cuota</p>
                <input type="number" id="cuota_{idx}" min="1.01" max="50" step="0.05" placeholder="−" 
                    style="width: 80px; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 1.1em; font-weight: bold; text-align: center;"
                />
            </div>
            <div style="flex: 0 0 auto; text-align: center; min-width: 80px;">
                <p style="margin: 0 0 4px 0; font-size: 0.7em; color: #999; text-transform: uppercase;">Yield</p>
                <p style="margin: 0; font-size: 1.3em; font-weight: bold; color: {yield_color};">{yield_text}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_bloques_jugador(j_nombre, mercados_lista, color="#1f77b4"):
    """Renderiza bloques de mercados para un jugador."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}08, {color}03); padding: 16px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid {color};">
        <h4 style="margin: 0 0 16px 0; color: {color}; font-size: 1.1em;">🎯 {j_nombre}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for idx, (titulo, prob) in enumerate(mercados_lista):
        with cols[idx % 2]:
            cuota_justa = prob_a_cuota(prob)
            cuota_input = st.number_input(
                f"Cuota {titulo.split('+')[1] if '+' in titulo else ''}",
                min_value=1.01,
                max_value=50.0,
                value=None,
                step=0.05,
                key=f"cuota_{j_nombre}_{idx}",
                label_visibility="collapsed",
                placeholder="Introduce cuota"
            )
            render_bloque_mercado(titulo, prob, cuota_justa, cuota_input, f"{j_nombre}_{idx}")

def mostrar_cuota_justa(cuota):
    """Muestra la cuota justa de forma pequeña y discreta."""
    st.caption(f"💡 Cuota justa: **{cuota:.2f}**")

def render_mas_180s_barras(j1_nombre, p_j1, j2_nombre, p_j2, p_emp, j1_color="#1f77b4", j2_color="#ff7f0e"):
    """Renderiza barras para 'quién hace más 180s' con empate en el centro."""
    p_j1 = sanitize_prob(p_j1)
    p_j2 = sanitize_prob(p_j2)
    p_emp = sanitize_prob(p_emp)
    
    total = p_j1 + p_emp + p_j2
    if total <= 0:
        total = 1.0
    
    pct_j1 = (p_j1 / total * 100)
    pct_emp = (p_emp / total * 100)
    pct_j2 = (p_j2 / total * 100)
    
    html_str = f"""
    <div style="margin: 20px 0;">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
            <div style="flex: 0 0 20%; text-align: right;">
                <p style="margin: 0; font-weight: bold; font-size: 0.95em; color: {j1_color};">{j1_nombre}</p>
                <p style="margin: 5px 0 0 0; font-size: 1.1em; font-weight: bold; color: {j1_color};">{pct_j1:.1f}%</p>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; height: 45px; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="width: {pct_j1}%; background: linear-gradient(90deg, {j1_color}, {j1_color}dd); display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                        <span style="color: white; font-weight: bold; font-size: 0.8em;">{p_j1*100:.1f}%</span>
                    </div>
                    <div style="width: {pct_emp}%; background: linear-gradient(90deg, #999, #777); display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold; font-size: 0.8em;">{p_emp*100:.1f}%</span>
                    </div>
                    <div style="width: {pct_j2}%; background: linear-gradient(90deg, {j2_color}dd, {j2_color}); display: flex; align-items: center; justify-content: flex-start; padding-left: 8px;">
                        <span style="color: white; font-weight: bold; font-size: 0.8em;">{p_j2*100:.1f}%</span>
                    </div>
                </div>
            </div>
            <div style="flex: 0 0 20%; text-align: left;">
                <p style="margin: 0; font-weight: bold; font-size: 0.95em; color: {j2_color};">{j2_nombre}</p>
                <p style="margin: 5px 0 0 0; font-size: 1.1em; font-weight: bold; color: {j2_color};">{pct_j2:.1f}%</p>
            </div>
        </div>
    </div>
    """
    st.markdown(html_str, unsafe_allow_html=True)

def widget_mercado_compacto(mercado, prob, idx):
    """Widget compacto que DEVUELVE la cuota introducida."""
    cuota_justa = prob_a_cuota(prob)
    
    col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1.5])
    
    with col1:
        porcentaje = int(prob * 100)
        st.markdown(f"**{mercado}**")
        st.progress(prob, text=f"{porcentaje}%")
    
    with col2:
        st.metric("Cuota justa", f"{cuota_justa:.2f}", label_visibility="collapsed")
        st.caption("Cuota justa")
    
    with col3:
        cuota_input = st.number_input(
            "Cuota bookie",
            min_value=1.01,
            max_value=50.0,
            value=None,
            step=0.05,
            key=f"cuota_{idx}",
            label_visibility="collapsed",
            placeholder="Introduce cuota"
        )
        st.caption("Cuota bookie")
    
    with col4:
        if cuota_input is not None and cuota_input > 0:
            y = calcular_yield(prob, cuota_input)
            color = "#28a745" if y > 0 else ("#dc3545" if y < -0.05 else "#6c757d")
            st.markdown(f"<p style='font-size: 1.3em; font-weight: bold; color: {color}; margin: 0;'>{badge_yield(y)}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='font-size: 1.3em; font-weight: bold; color: #6c757d; margin: 0;'>➖ 0.0%</p>", unsafe_allow_html=True)
        
        st.caption("Yield")
    
    return cuota_input

def render_value_bets():
    st.title("💰 Value Bets — Motor de Probabilidades")
    
    value_bets_list = []
    
    with st.expander("⚙️ Configuración", expanded=True):
        fuente = st.selectbox(
            "📂 Fuente de datos",
            PESTANAS_CON_STATS,
            index=PESTANAS_CON_STATS.index(st.session_state.vb_fuente),
            key="selector_fuente"
        )
        st.session_state.vb_fuente = fuente

    with st.spinner(f"Cargando datos de '{fuente}'..."):
        db_jugadores = cargar_jugadores_desde(fuente)

    if not db_jugadores:
        st.warning(f"⚠️ No se encontraron jugadores en '{fuente}'.")
        return

    nombres_disponibles = sorted([v["nombre_original"] for v in db_jugadores.values()])
    
    if fuente in st.session_state.last_update:
        tiempo_transcurrido = (datetime.now() - st.session_state.last_update[fuente]).seconds
        st.info(f"📊 {len(nombres_disponibles)} jugadores | ⏱️ Actualizado hace {tiempo_transcurrido}s")

    st.markdown("### 🥊 Seleccionar Enfrentamiento")
    
    if st.session_state.vb_j1 is None or st.session_state.vb_j1 not in nombres_disponibles:
        st.session_state.vb_j1 = nombres_disponibles[0]
    if st.session_state.vb_j2 is None or st.session_state.vb_j2 not in nombres_disponibles:
        opciones_j2 = [n for n in nombres_disponibles if n != st.session_state.vb_j1]
        st.session_state.vb_j2 = opciones_j2[0] if opciones_j2 else nombres_disponibles[0]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        j1_sel = st.selectbox(
            "Jugador 1",
            nombres_disponibles,
            index=nombres_disponibles.index(st.session_state.vb_j1),
            key="sel_j1"
        )
        st.session_state.vb_j1 = j1_sel
    
    with col2:
        opciones_j2 = [n for n in nombres_disponibles if n != j1_sel]
        if st.session_state.vb_j2 not in opciones_j2:
            st.session_state.vb_j2 = opciones_j2[0] if opciones_j2 else nombres_disponibles[0]
        
        j2_sel = st.selectbox(
            "Jugador 2",
            opciones_j2,
            index=opciones_j2.index(st.session_state.vb_j2) if st.session_state.vb_j2 in opciones_j2 else 0,
            key="sel_j2"
        )
        st.session_state.vb_j2 = j2_sel
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        col3_1, col3_2 = st.columns([1, 1])
        with col3_1:
            if st.button("🔢 Calcular", type="primary", use_container_width=True, help="Calcular probabilidades"):
                st.session_state.vb_calcular = True
        with col3_2:
            if st.button("🌐 Winamax", help="Obtener cuotas de Winamax (requiere Playwright)"):
                try:
                    with st.spinner("🔄 Obteniendo cuotas de Winamax..."):
                        cuotas = obtener_cuotas_winamax(j1_sel, j2_sel)
                        if cuotas.get("error"):
                            st.info(f"ℹ️ {cuotas['error']}\n\n💡 **Solución:** Rellena las cuotas manualmente en los campos de entrada.")
                        else:
                            st.session_state.cuotas_winamax = cuotas
                            st.success("✅ Cuotas cargadas desde Winamax")
                except Exception as e:
                    st.warning(f"⚠️ No se pudo conectar a Winamax: {str(e)[:50]}\n\n💡 **Rellena las cuotas manualmente en los campos de entrada.**")

    if not st.session_state.vb_calcular:
        st.info("👆 Selecciona los jugadores y pulsa **Calcular**")
        return

    j1 = buscar_jugador(j1_sel, db_jugadores)
    j2 = buscar_jugador(j2_sel, db_jugadores)

    if not j1 or not j2:
        st.error("No se encontraron datos para uno de los jugadores.")
        return

    pr1, pr2     = j1["PR"],       j2["PR"]
    lam1, lam2   = j1["lam_180"],  j2["lam_180"]
    legs1, legs2 = j1["lam_legs"], j2["lam_legs"]

    st.markdown("---")
    st.markdown("### 📊 Comparativa de Jugadores")
    
    col_j1, col_vs, col_j2 = st.columns([10, 2, 10])
    
    with col_j1:
        tarjeta_jugador(j1['nombre_original'], pr1, lam1, legs1, is_left=True, jugador_data=j1)
    
    with col_vs:
        st.markdown("""
        <div style="
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <h1 style="
                margin: 0;
                color: #666;
                font-size: 2.5em;
                font-weight: bold;
            ">VS</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col_j2:
        tarjeta_jugador(j2['nombre_original'], pr2, lam2, legs2, is_left=False, jugador_data=j2)

    st.markdown("---")
    st.markdown("### 🔥 Head to Head Semanal")
    
    with st.spinner("Analizando enfrentamientos directos..."):
        h2h = extraer_h2h_semanal(j1['nombre_original'], j2['nombre_original'])
    
    if h2h["partidos"]:
        col_h1, col_h2, col_h3 = st.columns([1, 1, 1])
        
        with col_h1:
            st.metric(f"Victorias {j1['nombre_original']}", h2h["victorias_j1"])
        
        with col_h2:
            total_partidos = len(h2h["partidos"])
            st.metric("Partidos Totales", total_partidos)
        
        with col_h3:
            st.metric(f"Victorias {j2['nombre_original']}", h2h["victorias_j2"])
        
        with st.expander("📋 Ver historial de enfrentamientos"):
            for partido in h2h["partidos"]:
                st.markdown(f"**{partido['dia']}**: {partido['jugador1']} vs {partido['jugador2']} - **{partido['marcador']}** (Ganador: {partido['ganador']})")
    else:
        st.info("ℹ️ No se encontraron enfrentamientos directos esta semana")

    v1, v2 = prob_victoria(pr1, pr2)
    m180 = prob_180s(lam1, lam2)
    p_j1_mas, p_emp, p_j2_mas = quien_hace_mas_180s(lam1, lam2)
    hcaps = handicaps_legs(v1, v2)
    legs_total_dict = legs_totales(legs1, legs2)

    def procesar_mercado(mercado, prob, cuota_input):
        if cuota_input is not None and cuota_input > 0:
            y = calcular_yield(prob, cuota_input)
            if y > 0:
                cuota_justa = prob_a_cuota(prob)
                return {
                    "Mercado": mercado,
                    "Probabilidad": prob,
                    "Cuota Justa": cuota_justa,
                    "Cuota Bookie": cuota_input,
                    "Yield": y
                }
        return None

    st.markdown("---")
    st.markdown("### 🎲 Mercados Disponibles")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Victoria", "🎯 180s", "🥇 ¿Quién hace más 180?", "📐 Hándicaps", "📊 Total Legs"])
    
    with tab1:
        st.markdown("#### 🏆 Mercado de Victoria")
        st.markdown("**Comparación directa de probabilidades**")
        
        render_barras_enfrentadas(
            j1['nombre_original'], v1,
            j2['nombre_original'], v2,
            j1_color="#1f77b4", j2_color="#ff7f0e"
        )
        
        st.markdown("---")
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.markdown(f"**🎯 Gana {j1['nombre_original']}**")
            cuota_justa = prob_a_cuota(v1)
            mostrar_cuota_justa(cuota_justa)
            c1 = st.number_input(
                f"Tu cuota",
                min_value=1.01, max_value=50.0, value=None, step=0.05,
                key="vic_j1", label_visibility="collapsed", placeholder="Introduce cuota"
            )
            st.caption(f"{v1*100:.1f}% probabilidad")
            if c1 and c1 > 0:
                y = calcular_yield(v1, c1)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                vb = {"Mercado": f"Gana {j1['nombre_original']}", "Probabilidad": v1, "Cuota Justa": cuota_justa, "Cuota Bookie": c1, "Yield": y}
                if y > 0:
                    value_bets_list.append(vb)
        
        with col_v2:
            st.markdown(f"**🎯 Gana {j2['nombre_original']}**")
            cuota_justa = prob_a_cuota(v2)
            mostrar_cuota_justa(cuota_justa)
            c2 = st.number_input(
                f"Tu cuota",
                min_value=1.01, max_value=50.0, value=None, step=0.05,
                key="vic_j2", label_visibility="collapsed", placeholder="Introduce cuota"
            )
            st.caption(f"{v2*100:.1f}% probabilidad")
            if c2 and c2 > 0:
                y = calcular_yield(v2, c2)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                vb = {"Mercado": f"Gana {j2['nombre_original']}", "Probabilidad": v2, "Cuota Justa": prob_a_cuota(v2), "Cuota Bookie": c2, "Yield": y}
                if y > 0:
                    value_bets_list.append(vb)
    
    with tab2:
        st.markdown("#### 🎯 Mercado de 180s (Distribución Poisson)")
        st.markdown("**Organizados por jugador y nivel de amenaza**")
        
        st.markdown(f"##### 🔵 {j1['nombre_original']}")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**+0.5 180s** (Al menos 1 180)")
            cuota_justa = prob_a_cuota(m180["J1 +0.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_j1_05", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['J1 +0.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["J1 +0.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"{j1['nombre_original']} +0.5 180s", "Probabilidad": m180["J1 +0.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_b:
            st.markdown("**+1.5 180s** (Al menos 2 180s)")
            cuota_justa = prob_a_cuota(m180["J1 +1.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_j1_15", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['J1 +1.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["J1 +1.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"{j1['nombre_original']} +1.5 180s", "Probabilidad": m180["J1 +1.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        st.markdown("---")
        
        st.markdown(f"##### 🟠 {j2['nombre_original']}")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**+0.5 180s** (Al menos 1 180)")
            cuota_justa = prob_a_cuota(m180["J2 +0.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_j2_05", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['J2 +0.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["J2 +0.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"{j2['nombre_original']} +0.5 180s", "Probabilidad": m180["J2 +0.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_b:
            st.markdown("**+1.5 180s** (Al menos 2 180s)")
            cuota_justa = prob_a_cuota(m180["J2 +1.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_j2_15", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['J2 +1.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["J2 +1.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"{j2['nombre_original']} +1.5 180s", "Probabilidad": m180["J2 +1.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        st.markdown("---")
        
        st.markdown("##### 🤝 Ambos Jugadores")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("**Ambos +0.5 180s**")
            cuota_justa = prob_a_cuota(m180["Ambos +0.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_ambos_05", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['Ambos +0.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["Ambos +0.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Ambos +0.5 180s", "Probabilidad": m180["Ambos +0.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_b:
            st.markdown("**Ambos +1.5 180s**")
            cuota_justa = prob_a_cuota(m180["Ambos +1.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_ambos_15", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['Ambos +1.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["Ambos +1.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Ambos +1.5 180s", "Probabilidad": m180["Ambos +1.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_c:
            st.markdown("**Ambos +2.5 180s**")
            cuota_justa = prob_a_cuota(m180["Ambos +2.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"180_ambos_25", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{m180['Ambos +2.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(m180["Ambos +2.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Ambos +2.5 180s", "Probabilidad": m180["Ambos +2.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
    
    with tab3:
        st.markdown("#### 🥇 ¿Quién hace más 180s?")
        st.markdown("**Comparación visual con posibilidad de empate**")
        
        render_mas_180s_barras(
            j1['nombre_original'], p_j1_mas,
            j2['nombre_original'], p_j2_mas,
            p_emp,
            j1_color="#1f77b4", j2_color="#ff7f0e"
        )
        
        st.markdown("---")
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"**{j1['nombre_original']}**")
            cuota_justa = prob_a_cuota(p_j1_mas)
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota {j1['nombre_original']}", min_value=1.01, max_value=50.0, value=None, step=0.05, key="mas_j1", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{p_j1_mas*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(p_j1_mas, c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"Más 180s: {j1['nombre_original']}", "Probabilidad": p_j1_mas, "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_m2:
            st.markdown("**Empate**")
            cuota_justa = prob_a_cuota(p_emp)
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota empate", min_value=1.01, max_value=50.0, value=None, step=0.05, key="mas_emp", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{p_emp*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(p_emp, c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Empate 180s", "Probabilidad": p_emp, "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_m3:
            st.markdown(f"**{j2['nombre_original']}**")
            cuota_justa = prob_a_cuota(p_j2_mas)
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota {j2['nombre_original']}", min_value=1.01, max_value=50.0, value=None, step=0.05, key="mas_j2", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{p_j2_mas*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(p_j2_mas, c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": f"Más 180s: {j2['nombre_original']}", "Probabilidad": p_j2_mas, "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
    
    with tab4:
        st.markdown("#### 📐 Hándicaps de Legs")
        st.markdown("**Organizados por jugador**")
        
        col_h1, col_h2 = st.columns(2)
        
        with col_h1:
            st.markdown(f"##### {j1['nombre_original']}")
            for hcap_name in ["J1 -1.5 Legs", "J1 -2.5 Legs", "J1 +1.5 Legs", "J1 +2.5 Legs"]:
                prob = hcaps[hcap_name]
                label = hcap_name.replace("J1 ", "").replace("Legs", "").strip()
                st.markdown(f"**{label}**")
                cuota_justa = prob_a_cuota(prob)
                mostrar_cuota_justa(cuota_justa)
                c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"hcap_{hcap_name}", label_visibility="collapsed", placeholder="Introduce cuota")
                st.caption(f"{prob*100:.1f}% probabilidad")
                if c and c > 0:
                    y = calcular_yield(prob, c)
                    yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                    st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                    if y > 0:
                        value_bets_list.append({"Mercado": f"{j1['nombre_original']} {label}", "Probabilidad": prob, "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
                st.divider()
        
        with col_h2:
            st.markdown(f"##### {j2['nombre_original']}")
            for hcap_name in ["J2 -1.5 Legs", "J2 -2.5 Legs", "J2 +1.5 Legs", "J2 +2.5 Legs"]:
                prob = hcaps[hcap_name]
                label = hcap_name.replace("J2 ", "").replace("Legs", "").strip()
                st.markdown(f"**{label}**")
                cuota_justa = prob_a_cuota(prob)
                mostrar_cuota_justa(cuota_justa)
                c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key=f"hcap_{hcap_name}_j2", label_visibility="collapsed", placeholder="Introduce cuota")
                st.caption(f"{prob*100:.1f}% probabilidad")
                if c and c > 0:
                    y = calcular_yield(prob, c)
                    yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                    st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                    if y > 0:
                        value_bets_list.append({"Mercado": f"{j2['nombre_original']} {label}", "Probabilidad": prob, "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
                st.divider()
    
    with tab5:
        st.markdown("#### 📊 Total Legs (First to 4)")
        st.markdown("Basado en distribución binomial negativa — Usa **MEDIA DE LEGS** para calcular probabilidades")
        
        render_barras_enfrentadas(
            "Más de 5.5", legs_total_dict["Más de 5.5"],
            "Menos de 5.5", legs_total_dict["Menos de 5.5"],
            j1_color="#28a745", j2_color="#dc3545"
        )
        
        st.markdown("---")
        col_l1, col_l2 = st.columns(2)
        
        with col_l1:
            st.markdown("**Más de 5.5 Legs**")
            cuota_justa = prob_a_cuota(legs_total_dict["Más de 5.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key="legs_mas", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{legs_total_dict['Más de 5.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(legs_total_dict["Más de 5.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Más de 5.5 Legs", "Probabilidad": legs_total_dict["Más de 5.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})
        
        with col_l2:
            st.markdown("**Menos de 5.5 Legs**")
            cuota_justa = prob_a_cuota(legs_total_dict["Menos de 5.5"])
            mostrar_cuota_justa(cuota_justa)
            c = st.number_input(f"Tu cuota", min_value=1.01, max_value=50.0, value=None, step=0.05, key="legs_menos", label_visibility="collapsed", placeholder="Introduce cuota")
            st.caption(f"{legs_total_dict['Menos de 5.5']*100:.1f}% probabilidad")
            if c and c > 0:
                y = calcular_yield(legs_total_dict["Menos de 5.5"], c)
                yield_color = "🟢" if y > 0 else ("🔴" if y < -0.05 else "⚪")
                st.metric("Yield", f"{yield_color} {'+' if y > 0 else ''}{y*100:.1f}%")
                if y > 0:
                    value_bets_list.append({"Mercado": "Menos de 5.5 Legs", "Probabilidad": legs_total_dict["Menos de 5.5"], "Cuota Justa": cuota_justa, "Cuota Bookie": c, "Yield": y})

    if value_bets_list:
        st.markdown("---")
        st.markdown("### 💎 Resumen de Value Bets Encontradas")
        
        value_bets_list.sort(key=lambda x: x["Yield"], reverse=True)
        
        for vb in value_bets_list:
            yield_pct = vb["Yield"] * 100
            
            st.markdown(f"""
            <div style="
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(90deg, rgba(40,167,69,0.1) 0%, rgba(40,167,69,0.02) 100%);
                border-radius: 5px;
            ">
                <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 1fr 1fr; gap: 15px; align-items: center;">
                    <div>
                        <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: #333;">{vb["Mercado"]}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="margin: 0; font-size: 0.8em; color: #666;">Probabilidad</p>
                        <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: #1f77b4;">{vb["Probabilidad"]*100:.1f}%</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="margin: 0; font-size: 0.8em; color: #666;">Cuota Justa</p>
                        <p style="margin: 0; font-size: 1.1em; font-weight: bold;">{vb["Cuota Justa"]:.2f}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="margin: 0; font-size: 0.8em; color: #666;">Cuota Bookie</p>
                        <p style="margin: 0; font-size: 1.1em; font-weight: bold; color: #ff7f0e;">{vb["Cuota Bookie"]:.2f}</p>
                    </div>
                    <div style="text-align: center;">
                        <p style="margin: 0; font-size: 0.8em; color: #666;">Yield</p>
                        <p style="margin: 0; font-size: 1.3em; font-weight: bold; color: #28a745;">+{yield_pct:.1f}%</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.success(f"✅ Se encontraron **{len(value_bets_list)}** mercados con value positivo")
    else:
        st.info("ℹ️ No se encontraron value bets con las cuotas introducidas")

# ═══════════════════════════════════════════════════════════════
# SIDEBAR CON CONTROL DEL SCRIPT
# ═══════════════════════════════════════════════════════════════

st.sidebar.title("🎯 MODUS SUPER SERIES")
st.sidebar.markdown("---")

# Opciones principales
opcion_principal = st.sidebar.radio(
    "Selecciona sección:",
    ["🔴 LIVE", "💰 VALUE BETS", "📊 RESULTADOS Y ESTADÍSTICAS"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Actualización")
st.sidebar.caption("Caché: 30 segundos")

if st.sidebar.button("♻️ Forzar Refresh", help="Recarga inmediata"):
    st.cache_data.clear()
    st.session_state.last_update = {}
    st.rerun()

# ═══════════════════════════════════════════════════════════════
# 🎯 CONTROL DEL SCRIPT (OPCIÓN 2 - CON TU URL)
# ═══════════════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Ejecutar Script")

# ✅ TU URL DE GOOGLE APPS SCRIPT
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwNQnY-jfmOGZSN0D1cNPFyijkNtrzWSBzUs0mByzQl0mCDRvhn6MOMInDZ9yXw0cf9/exec"

if st.sidebar.button("▶️ Ejecutar Actualización", type="primary", use_container_width=True, help="Ejecuta el script de actualización de datos"):
    
    st.sidebar.info("🔄 Ejecutando script...")
    
    try:
        # Llamar al script vía HTTP POST
        response = requests.post(SCRIPT_URL, timeout=120)
        
        if response.status_code == 200:
            st.sidebar.success("✅ Script ejecutado correctamente")
            st.sidebar.info("📊 Los datos se actualizarán en breve...")
            st.balloons()
            
            # Esperar 2 segundos y refrescar caché
            time.sleep(2)
            st.cache_data.clear()
            st.session_state.last_update = {}
            st.rerun()
        
        else:
            st.sidebar.warning(f"⚠️ Respuesta HTTP {response.status_code}")
            st.sidebar.info("💡 El script podría estar ejecutándose. Intenta refrescar en 5 segundos.")
    
    except requests.exceptions.Timeout:
        st.sidebar.warning("⏱️ Tiempo de espera agotado (>120s)")
        st.sidebar.info("💡 El script está ejecutándose en segundo plano. Los datos se actualizarán en breve.")
    
    except requests.exceptions.ConnectionError:
        st.sidebar.error("🔗 Error de conexión")
        st.sidebar.error("Verifica tu conexión a internet")
    
    except Exception as e:
        st.sidebar.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# INFORMACIÓN DEL SCRIPT
# ─────────────────────────────────────────────

with st.sidebar.expander("ℹ️ Información del Script", expanded=False):
    st.markdown("""
    ### 📊 Función: `actualizarDatosCompletos()`
    
    **¿Qué hace?**
    - ✅ Obtiene datos de la API
    - ✅ Actualiza estadísticas de jugadores
    - ✅ Limpia datos viejos
    - ✅ Rellena hojas de Excel
    
    **Ejecución Automática:**
    - ⏰ Cada 10 minutos
    - 📅 Lunes-Sábado en horarios de juego
    - 🗑️ Domingos ≥ 5 AM (limpieza completa)
    
    **Horarios:**
    - Grupo A: Lun-Mié 10:00-16:00
    - Grupo C: Jue-Vie 13:00-19:00
    - Grupo B + Final: 22:00-03:00
    
    **Este botón:** Ejecuta el script de inmediato
    """)

# ─────────────────────────────────────────────
# ESTADO DEL SCRIPT
# ─────────────────────────────────────────────

with st.sidebar.expander("📈 Estado", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Automático", "✅ Activo")
    
    with col2:
        st.metric("Intervalo", "10 minutos")
    
    st.divider()
    st.markdown("**Estado:** Script en ejecución automática")
    st.markdown("**Última ejecución:** Ver en Google Apps Script → Logs")

# ─────────────────────────────────────────────
# MAIN - NAVEGACIÓN
# ─────────────────────────────────────────────

if "🔴 LIVE" in opcion_principal:
    st.title("🔴 LIVE")
    
    jornada_actual, url_actual, es_activa = get_jornada_actual()
    
    if es_activa and jornada_actual:
        st.success(f"✅ Jornada activa: **{jornada_actual}** (datos en tiempo real)")
        st.markdown("---")
        
        partidos_vivos = obtener_partidos_vivos_api()
        
        if partidos_vivos:
            st.subheader("⚔️ Partidos en Vivo (Actualización cada 10 segundos)")
            
            tabla_partidos = []
            for p in partidos_vivos:
                tabla_partidos.append({
                    "🎮 Jugador 1": p.get("j1", ""),
                    "Legs": p.get("score_j1", ""),
                    "Ø Dardos": p.get("j1_average", ""),
                    "180s": p.get("j1_180s", ""),
                    "Checkout %": p.get("j1_checkout", ""),
                    "VS": "⚔️",
                    "🎮 Jugador 2": p.get("j2", ""),
                    "Legs": p.get("score_j2", ""),
                    "Ø Dardos": p.get("j2_average", ""),
                    "180s": p.get("j2_180s", ""),
                    "Checkout %": p.get("j2_checkout", "")
                })
            
            if tabla_partidos:
                df_vivo = pd.DataFrame(tabla_partidos)
                st.dataframe(df_vivo, use_container_width=True, hide_index=True)
                st.caption("🔄 Datos actualizados cada 10 segundos")
            else:
                st.info("📺 No hay partidos en vivo en este momento")
        else:
            st.warning("⚠️ No se pudieron obtener datos de la API")
            
            st.info("📊 Usando datos guardados en Google Sheets...")
            d1, d2 = cargar_todo(url_actual, jornada_actual, CORTES.get(jornada_actual, 2))
            
            if d1 is not None:
                st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
    
    else:
        proxima, url_proxima = get_proxima_jornada()
        
        st.info(f"📅 **Próxima jornada:** {proxima}")
        st.markdown("---")
        
        d1, d2 = cargar_todo(url_proxima, proxima, CORTES.get(proxima, 2))
        
        if proxima in st.session_state.last_update:
            tiempo = (datetime.now() - st.session_state.last_update[proxima]).seconds
            st.caption(f"⏱️ Datos actualizados hace {tiempo} segundos")
        
        orden_diario = [
            "Media 180 por partida", "Promedio puntos total",
            "Legs por partido", "Promedio Checkouts", "Número victorias",
            "Número derrotas", "Porcentaje victoria", "PUNTIACIÓN GLOBAL (0-100)"
        ]
        
        if d2 is not None:
            st.subheader("📈 Estadísticas")
            for player, stats in d2.items():
                bandera = obtener_bandera(player)
                player_display = f"{bandera} {player}" if bandera else f"👤 {player}"
                
                with st.expander(player_display, expanded=False):
                    for etiqueta in orden_diario:
                        valor = "-"
                        for k, v in stats.items():
                            if etiqueta.lower() in k.lower():
                                valor = v
                                break
                        st.write(f"**{etiqueta}:** {valor}")
        
        if d1 is not None:
            st.subheader("⚔️ Partidos")
            st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)

elif "💰 VALUE BETS" in opcion_principal:
    render_value_bets()

elif "📊 RESULTADOS Y ESTADÍSTICAS" in opcion_principal:
    st.title("📊 RESULTADOS Y ESTADÍSTICAS")
    
    jornadas_dict = {
        "Grupo A Lunes": URLS["Grupo A Lunes"],
        "Grupo A Martes": URLS["Grupo A Martes"],
        "Grupo A Miércoles": URLS["Grupo A Miércoles"],
        "Grupo C Jueves": URLS["Grupo C Jueves"],
        "Grupo C Viernes": URLS["Grupo C Viernes"],
        "Grupo B Jueves": URLS["Grupo B Jueves"],
        "Grupo B Viernes": URLS["Grupo B Viernes"],
        "Final Sábado": URLS["Final Sábado"],
        "Resumen Semanal": URLS["Resumen Semanal"],
    }
    
    selected = st.selectbox("Selecciona una jornada:", list(jornadas_dict.keys()), key="jornada_select")
    selected_url = jornadas_dict[selected]
    
    st.markdown("---")
    
    d1, d2 = cargar_todo(selected_url, selected, CORTES.get(selected, 2))
    
    if selected in st.session_state.last_update:
        tiempo = (datetime.now() - st.session_state.last_update[selected]).seconds
        st.caption(f"⏱️ Datos actualizados hace {tiempo} segundos")
    
    orden_diario = [
        "Media 180 por partida", "Promedio puntos total",
        "Legs por partido", "Promedio Checkouts", "Número victorias",
        "Número derrotas", "Porcentaje victoria", "PUNTIACIÓN GLOBAL (0-100)"
    ]
    
    if d2 is not None:
        st.subheader("📈 Estadísticas por Jugador")
        for player, stats in d2.items():
            bandera = obtener_bandera(player)
            player_display = f"{bandera} {player}" if bandera else f"👤 {player}"
            
            with st.expander(player_display, expanded=False):
                if selected == "Resumen Semanal":
                    for k, v in stats.items():
                        st.write(f"**{k}:** {v}")
                else:
                    for etiqueta in orden_diario:
                        valor = "-"
                        for k, v in stats.items():
                            if etiqueta.lower() in k.lower():
                                valor = v
                                break
                        st.write(f"**{etiqueta}:** {valor}")
    
    if d1 is not None:
        st.subheader("⚔️ Detalles")
        if selected not in ["Resumen Semanal", "Value Bets"]:
            st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
        else:
            st.dataframe(d1, use_container_width=True, hide_index=True)
