import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime
import requests

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
    "Resumen Semanal": {"filas": (5, 20), "cols": (1, 8)},
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
# MAPEO DE JUGADORES A PAÍSES
# ═══════════════════════════════════════════════════════════════
JUGADORES_PAISES = {
    "luke littler": "GB",
    "michael van gerwen": "NL",
    "gary anderson": "GB",
    "peter wright": "GB",
    "gerwyn price": "GB",
    "jonny clayton": "GB",
    "james wade": "GB",
    "dave chisnall": "GB",
    "rob cross": "GB",
    "nathan aspinall": "GB",
    "dimitri van den bergh": "BE",
    "jose de sousa": "PT",
    "dirk van duijvenbode": "NL",
    "danny noppert": "NL",
    "chris dobey": "GB",
    "josh rock": "GB",
    "luke humphries": "GB",
    "raymond van barneveld": "NL",
    "michael smith": "GB",
    "ross smith": "GB",
    "stephen bunting": "GB",
    "damon heta": "AU",
    "martin schindler": "DE",
    "gabriel clemens": "DE",
    "andrew gilding": "GB",
    "brendan dolan": "GB",
    "kim huybrechts": "BE",
    "ritchie edhouse": "GB",
    "ryan searle": "GB",
    "callan rydz": "GB",
    "joe cullen": "GB",
    "cameron menzies": "GB",
    "connor scutt": "GB",
    "matt campbell": "CA",
    "wessel nijman": "NL",
    "jermaine wattimena": "NL",
    "gian van veen": "NL",
    "ricardo pietreczko": "DE",
    "florian hempel": "DE",
    "krzysztof ratajski": "PL",
    "keane barry": "IE",
    "william o'connor": "IE",
    "ciaran teeters": "IE",
    "benito van de pas": "NL",
    "glenn de bois": "GB",
    "nick kenny": "GB",
    "nathan rafferty": "GB",
    "alexis toylo": "BE",
    "dylan slevin": "IE",
    "jurjen van der velde": "NL",
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
            while curr_f + 1 < len(df) and curr_f < fila_n + 30:
                tit = str(df.iloc[curr_f, col_rango[0]]).strip()
                if tit != 'nan' and tit != '':
                    val = str(df.iloc[curr_f + 1, col_rango[0] + i]).strip()
                    stats[tit] = val
                curr_f += 1
            data_final[j] = stats
        return data_final
    except:
        return {}

def extraer_stats_resumen(df):
    titulos = df.columns.tolist()
    data_final = {}
    for _, fila in df.iterrows():
        nombre_jugador = str(fila[titulos[0]])
        if nombre_jugador not in ['nan', 'Jugador', '']:
            stats = {}
            for i in range(1, len(titulos)):
                stats[titulos[i]] = fila[titulos[i]]
            data_final[nombre_jugador] = stats
    return data_final

@st.cache_data(ttl=30)
def cargar_todo(url, opcion, cortes):
    try:
        df = pd.read_csv(url, header=None)
        st.session_state.last_update[opcion] = datetime.now()
        
        if opcion == "Resumen Semanal":
            f, c = cortes["filas"], cortes["cols"]
            res = df.iloc[f[0]:f[1], c[0]:c[1]]
            res.columns = res.iloc[0]; res = res[1:]
            res = arreglar_columnas(res.dropna(how='all'))
            return None, extraer_stats_resumen(res)
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

@st.cache_data(ttl=30)
def cargar_jugadores_desde(pestana: str):
    try:
        url = URLS[pestana]
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
                    lam_legs = safe_float(_buscar_stat(s, ["leg"]))
                    jugadores[nombre.lower()] = {
                        "nombre_original": nombre,
                        "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs
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

        jugadores = {}
        for _, fila in data.iterrows():
            nombre = str(fila.get(col_jugador, "")).strip() if col_jugador else ""
            if not nombre or nombre.lower() in ["nan", "jugador", ""]:
                continue
            pr       = safe_float(fila.get(col_pr,    0)) if col_pr    else 0.0
            lam_180  = safe_float(fila.get(col_180,   0)) if col_180   else 0.0
            lam_legs = safe_float(fila.get(col_legs,  0)) if col_legs  else 0.0
            jugadores[nombre.lower()] = {
                "nombre_original": nombre,
                "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs
            }
        return jugadores
    except Exception as e:
        st.error(f"Error cargando {pestana}: {e}")
        return {}

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE BANDERAS Y H2H
# ═══════════════════════════════════════════════════════════════

def obtener_bandera(nombre_jugador):
    """Obtiene la bandera del jugador usando el mapeo manual."""
    nombre_lower = nombre_jugador.lower().strip().replace("_", " ")
    codigo_pais = JUGADORES_PAISES.get(nombre_lower, None)
    
    if codigo_pais:
        return f"https://flagcdn.com/w40/{codigo_pais.lower()}.png"
    
    return None

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

@st.cache_data(ttl=300)
def extraer_h2h_semanal(j1_nombre, j2_nombre):
    """
    Extrae el historial H2H de todos los días de la semana.
    ESTRUCTURA: Cada partido son 2 filas consecutivas (J1 en par, J2 en impar).
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
            
            # Leer cada 2 filas como un partido
            for i in range(0, len(df_partidos) - 1, 2):
                # Fila i = Jugador 1
                # Fila i+1 = Jugador 2
                fila_j1 = df_partidos.iloc[i]
                fila_j2 = df_partidos.iloc[i + 1]
                
                # Extraer nombres (primera columna)
                nombre_j1 = str(fila_j1.iloc[0]).strip().lower().replace("_", " ")
                nombre_j2 = str(fila_j2.iloc[0]).strip().lower().replace("_", " ")
                
                # Verificar si es el enfrentamiento buscado
                es_enfrentamiento = (
                    (j1_lower in nombre_j1 or nombre_j1 in j1_lower) and
                    (j2_lower in nombre_j2 or nombre_j2 in j2_lower)
                ) or (
                    (j2_lower in nombre_j1 or nombre_j1 in j2_lower) and
                    (j1_lower in nombre_j2 or nombre_j2 in j1_lower)
                )
                
                if es_enfrentamiento:
                    # Extraer resultados (segunda columna típicamente)
                    resultado_j1 = str(fila_j1.iloc[1]).strip() if len(fila_j1) > 1 else ""
                    resultado_j2 = str(fila_j2.iloc[1]).strip() if len(fila_j2) > 1 else ""
                    
                    # Determinar ganador: quien tiene "4" gana
                    ganador = None
                    marcador = f"{resultado_j1}-{resultado_j2}"
                    
                    if "4" in resultado_j1:
                        ganador = nombre_j1.title()
                        # Verificar si ganó j1 o j2
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
    return {
        "J1 +0.5": sanitize_prob(1 - poisson.cdf(0, lam1)),
        "J1 +1.5": sanitize_prob(1 - poisson.cdf(1, lam1)),
        "J2 +0.5": sanitize_prob(1 - poisson.cdf(0, lam2)),
        "J2 +1.5": sanitize_prob(1 - poisson.cdf(1, lam2)),
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

def tarjeta_jugador(nombre, pr, lam_180, lam_legs, is_left=True):
    """Tarjeta visual SIMÉTRICA con stats del jugador Y BANDERA."""
    color = "#1f77b4" if is_left else "#ff7f0e"
    
    bandera_url = obtener_bandera(nombre)
    bandera_html = f'<img src="{bandera_url}" style="width: 30px; height: 20px; margin-left: 10px; vertical-align: middle; border-radius: 3px;">' if bandera_url else ''
    
    st.markdown(f"""
    <div style="
        border: 2px solid {color};
        border-radius: 10px;
        padding: 20px;
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        height: 100%;
        display: flex;
        flex-direction: column;
    ">
        <h3 style="color: {color}; margin: 0 0 20px 0; text-align: center;">
            🎯 {nombre} {bandera_html}
        </h3>
        <div style="
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            flex: 1;
            align-items: center;
        ">
            <div style="text-align: center;">
                <p style="margin: 0 0 8px 0; font-size: 0.85em; color: #666; font-weight: 500;">Power Ranking</p>
                <p style="margin: 0; font-size: 2em; font-weight: bold; color: {color};">{pr:.1f}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0 0 8px 0; font-size: 0.85em; color: #666; font-weight: 500;">λ 180s</p>
                <p style="margin: 0; font-size: 2em; font-weight: bold; color: {color};">{lam_180:.2f}</p>
            </div>
            <div style="text-align: center; grid-column: 1 / -1;">
                <p style="margin: 0 0 8px 0; font-size: 0.85em; color: #666; font-weight: 500;">λ Legs</p>
                <p style="margin: 0; font-size: 2em; font-weight: bold; color: {color};">{lam_legs:.2f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        if st.button("🔢 Calcular Probabilidades", type="primary", use_container_width=True):
            st.session_state.vb_calcular = True

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
        tarjeta_jugador(j1['nombre_original'], pr1, lam1, legs1, is_left=True)
    
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
        tarjeta_jugador(j2['nombre_original'], pr2, lam2, legs2, is_left=False)

    # ── HEAD TO HEAD SEMANAL CORREGIDO ──
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
        c1 = widget_mercado_compacto(f"Gana {j1['nombre_original']}", v1, "vic_j1")
        vb = procesar_mercado(f"Gana {j1['nombre_original']}", v1, c1)
        if vb: value_bets_list.append(vb)
        
        c2 = widget_mercado_compacto(f"Gana {j2['nombre_original']}", v2, "vic_j2")
        vb = procesar_mercado(f"Gana {j2['nombre_original']}", v2, c2)
        if vb: value_bets_list.append(vb)
    
    with tab2:
        st.markdown("#### 🎯 Mercado de 180s (Poisson)")
        mercados_180 = [
            (f"{j1['nombre_original']} +0.5", m180["J1 +0.5"]),
            (f"{j1['nombre_original']} +1.5", m180["J1 +1.5"]),
            (f"{j2['nombre_original']} +0.5", m180["J2 +0.5"]),
            (f"{j2['nombre_original']} +1.5", m180["J2 +1.5"]),
            ("Ambos +1.5", m180["Ambos +1.5"]),
            ("Ambos +2.5", m180["Ambos +2.5"]),
        ]
        for idx, (mercado, prob) in enumerate(mercados_180):
            cuota = widget_mercado_compacto(mercado, prob, f"180_{idx}")
            vb = procesar_mercado(mercado, prob, cuota)
            if vb: value_bets_list.append(vb)
    
    with tab3:
        st.markdown("#### 🥇 ¿Quién hace más 180s?")
        c1 = widget_mercado_compacto(f"Más: {j1['nombre_original']}", p_j1_mas, "mas_j1")
        vb = procesar_mercado(f"Más: {j1['nombre_original']}", p_j1_mas, c1)
        if vb: value_bets_list.append(vb)
        
        c2 = widget_mercado_compacto("Empate en 180s", p_emp, "mas_emp")
        vb = procesar_mercado("Empate en 180s", p_emp, c2)
        if vb: value_bets_list.append(vb)
        
        c3 = widget_mercado_compacto(f"Más: {j2['nombre_original']}", p_j2_mas, "mas_j2")
        vb = procesar_mercado(f"Más: {j2['nombre_original']}", p_j2_mas, c3)
        if vb: value_bets_list.append(vb)
    
    with tab4:
        st.markdown("#### 📐 Hándicaps de Legs")
        handicaps_lista = [
            (f"{j1['nombre_original']} -1.5", hcaps["J1 -1.5 Legs"]),
            (f"{j1['nombre_original']} -2.5", hcaps["J1 -2.5 Legs"]),
            (f"{j1['nombre_original']} +1.5", hcaps["J1 +1.5 Legs"]),
            (f"{j1['nombre_original']} +2.5", hcaps["J1 +2.5 Legs"]),
            (f"{j2['nombre_original']} -1.5", hcaps["J2 -1.5 Legs"]),
            (f"{j2['nombre_original']} -2.5", hcaps["J2 -2.5 Legs"]),
            (f"{j2['nombre_original']} +1.5", hcaps["J2 +1.5 Legs"]),
            (f"{j2['nombre_original']} +2.5", hcaps["J2 +2.5 Legs"]),
        ]
        for idx, (mercado, prob) in enumerate(handicaps_lista):
            cuota = widget_mercado_compacto(mercado, prob, f"hcap_{idx}")
            vb = procesar_mercado(mercado, prob, cuota)
            if vb: value_bets_list.append(vb)
    
    with tab5:
        st.markdown("#### 📊 Total Legs (First to 4)")
        st.caption("Basado en distribución binomial negativa — Under 5.5 = marcadores 4-0 y 4-1")
        c1 = widget_mercado_compacto("Más de 5.5 Legs", legs_total_dict["Más de 5.5"], "legs_mas")
        vb = procesar_mercado("Más de 5.5 Legs", legs_total_dict["Más de 5.5"], c1)
        if vb: value_bets_list.append(vb)
        
        c2 = widget_mercado_compacto("Menos de 5.5 Legs", legs_total_dict["Menos de 5.5"], "legs_menos")
        vb = procesar_mercado("Menos de 5.5 Legs", legs_total_dict["Menos de 5.5"], c2)
        if vb: value_bets_list.append(vb)

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
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
st.sidebar.title("🎯 Menú Modus")
sel = st.sidebar.radio("Ir a:", list(URLS.keys()), key="menu_principal")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Actualización")
st.sidebar.caption("Caché: 30 segundos")

if st.sidebar.button("♻️ Forzar Refresh", help="Recarga inmediata"):
    st.cache_data.clear()
    st.session_state.last_update = {}
    st.rerun()

if sel in st.session_state.last_update:
    ultima_act = st.session_state.last_update[sel]
    tiempo_trans = (datetime.now() - ultima_act).seconds
    st.sidebar.info(f"📅 **{sel}**\n\n⏱️ Actualizado hace **{tiempo_trans}s**")

# ─────────────────────────────────────────────
# INTERFAZ PRINCIPAL CON BANDERAS EN TODAS LAS PESTAÑAS
# ─────────────────────────────────────────────
if sel == "Value Bets":
    render_value_bets()
else:
    d1, d2 = cargar_todo(URLS[sel], sel, CORTES[sel])
    st.title(f"📊 {sel}")

    if sel in st.session_state.last_update:
        tiempo = (datetime.now() - st.session_state.last_update[sel]).seconds
        st.caption(f"⏱️ Datos actualizados hace {tiempo} segundos")

    orden_diario = [
        "Media 180 por partida", "Promedio puntos total", "Diferencia de legs",
        "Legs por partido", "Promedio Checkouts", "Número victorias",
        "Número derrotas", "Porcentaje victoria", "PUNTIACIÓN GLOBAL (0-100)"
    ]

    if d2 is not None:
        st.subheader("📈 Estadísticas por Jugador")
        for player, stats in d2.items():
            # ✅ BANDERAS EN TODAS LAS PESTAÑAS
            bandera_url = obtener_bandera(player)
            if bandera_url:
                bandera_html = f'<img src="{bandera_url}" style="width: 20px; height: 14px; margin-right: 8px; vertical-align: middle; border-radius: 2px;">'
                player_display = f"{bandera_html} {player}"
            else:
                player_display = f"👤 {player}"
            
            with st.expander(player_display, expanded=False):
                if sel == "Resumen Semanal":
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
        if sel not in ["Resumen Semanal", "Value Bets"]:
            st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
        else:
            st.dataframe(d1, use_container_width=True, hide_index=True)
