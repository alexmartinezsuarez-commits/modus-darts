import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, time

st.set_page_config(page_title="Modus Super Series App", layout="wide", page_icon="🎯")

# ═══════════════════════════════════════════════════════════════
# URLs Y CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
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
}

PESTANAS_CON_STATS = list(URLS.keys())
BANDERAS = {
    "GB": "🇬🇧", "NL": "🇳🇱", "BE": "🇧🇪", "PT": "🇵🇹",
    "AU": "🇦🇺", "DE": "🇩🇪", "PL": "🇵🇱", "IE": "🇮🇪",
    "CA": "🇨🇦", "ES": "🇪🇸", "FR": "🇫🇷"
}

JUGADORES_PAISES = {
    "luke littler": "GB", "michael van gerwen": "NL", "gary anderson": "GB",
    "peter wright": "GB", "gerwyn price": "GB", "jonny clayton": "GB",
    "james wade": "GB", "dave chisnall": "GB", "rob cross": "GB",
    "nathan aspinall": "GB", "chris dobey": "GB", "josh rock": "GB",
    "luke humphries": "GB", "michael smith": "GB", "ross smith": "GB",
    "stephen bunting": "GB", "andrew gilding": "GB", "brendan dolan": "GB",
    "ritchie edhouse": "GB", "ryan searle": "GB", "callan rydz": "GB",
    "joe cullen": "GB", "cameron menzies": "GB", "connor scutt": "GB",
    "glenn de bois": "GB", "nick kenny": "GB", "nathan rafferty": "GB",
    "steve west": "GB", "neil duff": "GB", "johnny haines": "GB",
    "joe heywood": "GB", "dirk van duijvenbode": "NL", "danny noppert": "NL",
    "raymond van barneveld": "NL", "wessel nijman": "NL", "jermaine wattimena": "NL",
    "gian van veen": "NL", "benito van de pas": "NL", "jurjen van der velde": "NL",
    "dimitri van den bergh": "BE", "kim huybrechts": "BE", "alexis toylo": "BE",
    "jose de sousa": "PT", "damon heta": "AU", "martin schindler": "DE",
    "gabriel clemens": "DE", "ricardo pietreczko": "DE", "florian hempel": "DE",
    "krzysztof ratajski": "PL", "keane barry": "IE", "william o'connor": "IE",
    "ciaran teeters": "IE", "dylan slevin": "IE", "matt campbell": "CA",
}

HORARIOS = {
    "Grupo A Lunes": {"dia": 0, "inicio": time(10, 0), "fin": time(16, 0)},
    "Grupo A Martes": {"dia": 1, "inicio": time(10, 0), "fin": time(16, 0)},
    "Grupo A Miércoles": {"dia": 2, "inicio": time(10, 0), "fin": time(16, 0)},
    "Grupo C Jueves": {"dia": 3, "inicio": time(13, 0), "fin": time(19, 0)},
    "Grupo B Jueves": {"dia": 3, "inicio": time(22, 0), "fin": time(3, 0), "medianoche": True},
    "Grupo C Viernes": {"dia": 4, "inicio": time(13, 0), "fin": time(19, 0)},
    "Grupo B Viernes": {"dia": 4, "inicio": time(22, 0), "fin": time(3, 0), "medianoche": True},
    "Final Sábado": {"dia": 5, "inicio": time(22, 0), "fin": time(3, 0), "medianoche": True},
}

ESTADISTICAS_MOSTRAR = [
    "Media 180 por partida",
    "Promedio puntos total",
    "Legs por partido",
    "Promedio Checkouts",
    "Número victorias",
    "Número derrotas",
    "Porcentaje victoria",
    "PUNTIACIÓN GLOBAL (0-100)"
]

METRICAS_CON_TENDENCIA = ["promedio checkouts", "promedio dardos", "180"]

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "last_update" not in st.session_state:
    st.session_state.last_update = {}
if "vb_j1" not in st.session_state:
    st.session_state.vb_j1 = None
if "vb_j2" not in st.session_state:
    st.session_state.vb_j2 = None
if "vb_calcular" not in st.session_state:
    st.session_state.vb_calcular = False

# ═══════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════

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
                der_f = corte["der_nombres"]
                der_c = corte["der_cols"]
                stats = extraer_stats_diarias(df, der_f, der_c)
                jugadores = {}
                for nombre, s in stats.items():
                    pr = safe_float(_buscar_stat(s, ["global", "puntuación", "puntuacion"]))
                    lam_180 = safe_float(_buscar_stat(s, ["180", "ciento"]))
                    lam_legs = safe_float(_buscar_stat(s, ["leg"]))
                    jugadores[nombre.lower()] = {
                        "nombre_original": nombre,
                        "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs
                    }
                return jugadores
            return {}

        headers = [str(v).strip() for v in df.iloc[fila_header].values]
        data = df.iloc[fila_header + 1:].copy()
        data.columns = headers
        data = data.reset_index(drop=True)

        def buscar_col(keywords):
            for h in headers:
                if any(kw.lower() in h.lower() for kw in keywords):
                    return h
            return None

        col_jugador = buscar_col(["jugador", "nombre"])
        col_pr = buscar_col(["puntuación global", "puntuacion global", "global", "power"])
        col_180 = buscar_col(["180"])
        col_legs = buscar_col(["legs", "leg"])

        jugadores = {}
        for _, fila in data.iterrows():
            nombre = str(fila.get(col_jugador, "")).strip() if col_jugador else ""
            if not nombre or nombre.lower() in ["nan", "jugador", ""]:
                continue
            pr = safe_float(fila.get(col_pr, 0)) if col_pr else 0.0
            lam_180 = safe_float(fila.get(col_180, 0)) if col_180 else 0.0
            lam_legs = safe_float(fila.get(col_legs, 0)) if col_legs else 0.0
            jugadores[nombre.lower()] = {
                "nombre_original": nombre,
                "PR": pr, "lam_180": lam_180, "lam_legs": lam_legs
            }
        return jugadores
    except Exception as e:
        st.error(f"Error cargando {pestana}: {e}")
        return {}

def obtener_bandera(nombre_jugador):
    nombre_lower = nombre_jugador.lower().strip().replace("_", " ")
    codigo_pais = JUGADORES_PAISES.get(nombre_lower, None)
    if codigo_pais and codigo_pais in BANDERAS:
        return BANDERAS[codigo_pais]
    return None

def calcular_legs_por_partido_dia(df_partidos, nombre_jugador):
    """Calcula Legs por Partido SOLO para este día específico."""
    if df_partidos is None or len(df_partidos) == 0:
        return None
    
    nombre_lower = nombre_jugador.lower().strip().replace("_", " ")
    legs_totales = 0
    partidos_jugados = 0
    
    try:
        for i in range(0, len(df_partidos) - 1, 2):
            fila_j1 = df_partidos.iloc[i]
            fila_j2 = df_partidos.iloc[i + 1]
            
            nombre_j1 = str(fila_j1.iloc[0]).lower().strip().replace("_", " ")
            nombre_j2 = str(fila_j2.iloc[0]).lower().strip().replace("_", " ")
            
            resultado_str = str(fila_j1.iloc[1]) if len(fila_j1) > 1 else ""
            
            es_j1 = nombre_lower in nombre_j1 or nombre_j1 in nombre_lower
            es_j2 = nombre_lower in nombre_j2 or nombre_j2 in nombre_lower
            
            if es_j1 or es_j2:
                resultado_limpio = resultado_str.strip().replace(" ", "")
                
                if "-" in resultado_limpio:
                    try:
                        partes = resultado_limpio.split("-")
                        nums = [int(p.strip()) for p in partes if p.strip().isdigit()]
                        
                        if len(nums) >= 2:
                            legs_j1 = nums[0]
                            legs_j2 = nums[1]
                            legs_totales += legs_j1 + legs_j2
                            partidos_jugados += 1
                    except (ValueError, IndexError):
                        pass
        
        if partidos_jugados > 0:
            resultado = legs_totales / partidos_jugados
            return round(resultado, 2)
        return None
    except:
        return None

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

def detectar_jornada_activa():
    ahora = datetime.now()
    dia_actual = ahora.weekday()
    hora_actual = ahora.time()
    
    for nombre_jornada, horario in HORARIOS.items():
        dia_jornada = horario["dia"]
        hora_inicio = horario["inicio"]
        hora_fin = horario["fin"]
        medianoche = horario.get("medianoche", False)
        
        if medianoche:
            if (dia_actual == dia_jornada and hora_actual >= hora_inicio) or \
               (dia_actual == (dia_jornada + 1) % 7 and hora_actual < hora_fin):
                return nombre_jornada
        else:
            if dia_actual == dia_jornada and hora_inicio <= hora_actual < hora_fin:
                return nombre_jornada
    
    return None

# ═══════════════════════════════════════════════════════════════
# WIDGETS VISUALES - FASE 2
# ═══════════════════════════════════════════════════════════════

def widget_barras_enfrentadas(j1_nombre, j1_prob, j2_nombre, j2_prob, idx_base):
    """Barras horizontales enfrentadas - Victoria, Total Legs, etc."""
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"<p style='font-weight: bold; color: #1f77b4; font-size: 1.1em;'>{j1_nombre}</p>", unsafe_allow_html=True)
        pct_j1 = int(j1_prob * 100)
        st.progress(j1_prob, text=f"{pct_j1}%")
        
        cuota_j1 = st.number_input(
            f"Cuota", min_value=1.01, max_value=50.0, value=None, step=0.05,
            key=f"cuota_j1_{idx_base}", label_visibility="collapsed", placeholder="Cuota"
        )
        if cuota_j1 and cuota_j1 > 0:
            st.caption(badge_yield(calcular_yield(j1_prob, cuota_j1)))
    
    with col2:
        st.markdown("<div style='text-align: center; padding: 15px 0;'><p style='color: #999; font-weight: bold;'>vs</p></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<p style='font-weight: bold; color: #ff7f0e; font-size: 1.1em; text-align: right;'>{j2_nombre}</p>", unsafe_allow_html=True)
        pct_j2 = int(j2_prob * 100)
        st.progress(j2_prob, text=f"{pct_j2}%")
        
        cuota_j2 = st.number_input(
            f"Cuota", min_value=1.01, max_value=50.0, value=None, step=0.05,
            key=f"cuota_j2_{idx_base}", label_visibility="collapsed", placeholder="Cuota"
        )
        if cuota_j2 and cuota_j2 > 0:
            st.caption(badge_yield(calcular_yield(j2_prob, cuota_j2)))

def widget_180s_bloques(j1_nombre, j1_05, j1_15, j2_nombre, j2_05, j2_15, ambos_15, ambos_25):
    """180s en bloques separados por jugador."""
    col1, col2, col3 = st.columns(3)
    
    # J1
    with col1:
        st.markdown(f"<h4 style='color: #1f77b4; margin: 0;'>{j1_nombre}</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_05 = st.number_input(f"+0.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"j1_05", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(j1_05, text=f"{int(j1_05*100)}%")
        if cuota_05:
            st.caption(badge_yield(calcular_yield(j1_05, cuota_05)), unsafe_allow_html=False)
        
        st.markdown("", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_15 = st.number_input(f"+1.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"j1_15", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(j1_15, text=f"{int(j1_15*100)}%")
        if cuota_15:
            st.caption(badge_yield(calcular_yield(j1_15, cuota_15)))
    
    # J2
    with col2:
        st.markdown(f"<h4 style='color: #ff7f0e; margin: 0;'>{j2_nombre}</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_j2_05 = st.number_input(f"+0.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"j2_05", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(j2_05, text=f"{int(j2_05*100)}%")
        if cuota_j2_05:
            st.caption(badge_yield(calcular_yield(j2_05, cuota_j2_05)))
        
        st.markdown("", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_j2_15 = st.number_input(f"+1.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"j2_15", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(j2_15, text=f"{int(j2_15*100)}%")
        if cuota_j2_15:
            st.caption(badge_yield(calcular_yield(j2_15, cuota_j2_15)))
    
    # AMBOS
    with col3:
        st.markdown(f"<h4 style='color: #6c757d; margin: 0;'>Ambos</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_ambos_15 = st.number_input(f"+1.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"ambos_15", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(ambos_15, text=f"{int(ambos_15*100)}%")
        if cuota_ambos_15:
            st.caption(badge_yield(calcular_yield(ambos_15, cuota_ambos_15)))
        
        st.markdown("", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota_ambos_25 = st.number_input(f"+2.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"ambos_25", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(ambos_25, text=f"{int(ambos_25*100)}%")
        if cuota_ambos_25:
            st.caption(badge_yield(calcular_yield(ambos_25, cuota_ambos_25)))

def widget_barras_con_empate(j1_nombre, j1_prob, empate_prob, j2_nombre, j2_prob, idx_base):
    """Barras con empate en el centro."""
    col1, col_emp, col2 = st.columns([1.5, 1, 1.5])
    
    with col1:
        st.markdown(f"<p style='font-weight: bold; color: #1f77b4;'>{j1_nombre}</p>", unsafe_allow_html=True)
        st.progress(j1_prob, text=f"{int(j1_prob*100)}%")
        cuota_j1 = st.number_input(f"Cuota", min_value=1.01, max_value=50, value=None, step=0.05,
            key=f"empate_j1_{idx_base}", label_visibility="collapsed", placeholder="Cuota")
        if cuota_j1:
            st.caption(badge_yield(calcular_yield(j1_prob, cuota_j1)))
    
    with col_emp:
        st.markdown(f"<p style='font-weight: bold; color: #6c757d; text-align: center;'>Empate</p>", unsafe_allow_html=True)
        st.progress(empate_prob, text=f"{int(empate_prob*100)}%")
        cuota_emp = st.number_input(f"Cuota", min_value=1.01, max_value=50, value=None, step=0.05,
            key=f"empate_mid_{idx_base}", label_visibility="collapsed", placeholder="Cuota")
        if cuota_emp:
            st.caption(badge_yield(calcular_yield(empate_prob, cuota_emp)))
    
    with col2:
        st.markdown(f"<p style='font-weight: bold; color: #ff7f0e; text-align: right;'>{j2_nombre}</p>", unsafe_allow_html=True)
        st.progress(j2_prob, text=f"{int(j2_prob*100)}%")
        cuota_j2 = st.number_input(f"Cuota", min_value=1.01, max_value=50, value=None, step=0.05,
            key=f"empate_j2_{idx_base}", label_visibility="collapsed", placeholder="Cuota")
        if cuota_j2:
            st.caption(badge_yield(calcular_yield(j2_prob, cuota_j2)))

def widget_handicaps_bloques(j1_nombre, j2_nombre, hcaps_dict):
    """Hándicaps en bloques por jugador."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h4 style='color: #1f77b4;'>{j1_nombre}</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota = st.number_input(f"-1.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"hcap_j1_m15", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(hcaps_dict["J1 -1.5 Legs"], text=f"{int(hcaps_dict['J1 -1.5 Legs']*100)}%")
        if cuota:
            st.caption(badge_yield(calcular_yield(hcaps_dict["J1 -1.5 Legs"], cuota)))
        
        st.markdown("", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota = st.number_input(f"-2.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"hcap_j1_m25", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(hcaps_dict["J1 -2.5 Legs"], text=f"{int(hcaps_dict['J1 -2.5 Legs']*100)}%")
        if cuota:
            st.caption(badge_yield(calcular_yield(hcaps_dict["J1 -2.5 Legs"], cuota)))
    
    with col2:
        st.markdown(f"<h4 style='color: #ff7f0e;'>{j2_nombre}</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota = st.number_input(f"-1.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"hcap_j2_m15", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(hcaps_dict["J2 -1.5 Legs"], text=f"{int(hcaps_dict['J2 -1.5 Legs']*100)}%")
        if cuota:
            st.caption(badge_yield(calcular_yield(hcaps_dict["J2 -1.5 Legs"], cuota)))
        
        st.markdown("", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            cuota = st.number_input(f"-2.5", min_value=1.01, max_value=50, value=None, step=0.05,
                key=f"hcap_j2_m25", label_visibility="collapsed", placeholder="Cuota")
        with c2:
            st.progress(hcaps_dict["J2 -2.5 Legs"], text=f"{int(hcaps_dict['J2 -2.5 Legs']*100)}%")
        if cuota:
            st.caption(badge_yield(calcular_yield(hcaps_dict["J2 -2.5 Legs"], cuota)))

def tarjeta_jugador(nombre, pr, lam_180, lam_legs, is_left=True):
    color = "#1f77b4" if is_left else "#ff7f0e"
    bandera = obtener_bandera(nombre)
    nombre_display = f"{bandera} {nombre}" if bandera else f"🎯 {nombre}"
    
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
            {nombre_display}
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

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
st.sidebar.title("🎯 Menú")

opcion = st.sidebar.selectbox(
    "Selecciona sección:",
    ["🔴 LIVE", "💰 VALUE BETS", "📊 RESULTADOS"],
    key="menu_nav"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Actualización")
st.sidebar.caption("Caché: 30 segundos")

if st.sidebar.button("♻️ Forzar Refresh", use_container_width=True):
    st.cache_data.clear()
    st.session_state.last_update = {}
    st.rerun()

# ═══════════════════════════════════════════════════════════════
# CONTENIDO PRINCIPAL
# ═══════════════════════════════════════════════════════════════

# 🔴 LIVE
if opcion == "🔴 LIVE":
    jornada_activa = detectar_jornada_activa()
    
    if jornada_activa:
        st.title(f"🔴 {jornada_activa}")
        
        if jornada_activa in URLS:
            d1, d2 = cargar_todo(URLS[jornada_activa], jornada_activa, CORTES[jornada_activa])
            
            if d1 is not None and len(d1) > 0:
                st.subheader("Partidos en vivo")
                st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
            else:
                st.warning("No hay datos disponibles")
    else:
        st.title("🔴 LIVE")
        st.info("⏳ No hay partidos en juego ahora")

# 💰 VALUE BETS - FASE 2
elif opcion == "💰 VALUE BETS":
    st.title("💰 VALUE BETS")
    
    with st.expander("⚙️ Configuración", expanded=True):
        fuente = st.selectbox(
            "📂 Fuente de datos:",
            list(URLS.keys()),
            key="vb_fuente"
        )
    
    with st.spinner(f"Cargando datos de '{fuente}'..."):
        db_jugadores = cargar_jugadores_desde(fuente)
    
    if not db_jugadores:
        st.warning(f"⚠️ No se encontraron jugadores en '{fuente}'.")
    else:
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
            if st.button("🔢 Calcular", type="primary", use_container_width=True):
                st.session_state.vb_calcular = True
        
        if st.session_state.vb_calcular:
            j1 = buscar_jugador(j1_sel, db_jugadores)
            j2 = buscar_jugador(j2_sel, db_jugadores)
            
            if j1 and j2:
                pr1, pr2 = j1["PR"], j2["PR"]
                lam1, lam2 = j1["lam_180"], j2["lam_180"]
                legs1, legs2 = j1["lam_legs"], j2["lam_legs"]
                
                st.markdown("---")
                st.markdown("### 📊 Comparativa")
                
                col_j1, col_vs, col_j2 = st.columns([10, 2, 10])
                with col_j1:
                    tarjeta_jugador(j1['nombre_original'], pr1, lam1, legs1, is_left=True)
                with col_vs:
                    st.markdown("<div style='height: 100%; display: flex; align-items: center; justify-content: center;'><h1 style='margin: 0; color: #666; font-size: 2.5em; font-weight: bold;'>VS</h1></div>", unsafe_allow_html=True)
                with col_j2:
                    tarjeta_jugador(j2['nombre_original'], pr2, lam2, legs2, is_left=False)
                
                st.markdown("---")
                st.markdown("### 🎲 Mercados - FASE 2 (Visual Mejorado)")
                
                v1, v2 = prob_victoria(pr1, pr2)
                m180 = prob_180s(lam1, lam2)
                p_j1_mas, p_emp, p_j2_mas = quien_hace_mas_180s(lam1, lam2)
                hcaps = handicaps_legs(v1, v2)
                legs_dict = legs_totales(legs1, legs2)
                
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Victoria", "🎯 180s", "🥇 Más 180s", "📐 Hándicaps", "📊 Legs"])
                
                with tab1:
                    st.markdown("#### 🏆 Mercado Victoria - Barras Enfrentadas")
                    widget_barras_enfrentadas(j1['nombre_original'], v1, j2['nombre_original'], v2, "victoria")
                
                with tab2:
                    st.markdown("#### 🎯 Mercado 180s - Bloques por Jugador")
                    widget_180s_bloques(j1['nombre_original'], m180["J1 +0.5"], m180["J1 +1.5"],
                                       j2['nombre_original'], m180["J2 +0.5"], m180["J2 +1.5"],
                                       m180["Ambos +1.5"], m180["Ambos +2.5"])
                
                with tab3:
                    st.markdown("#### 🥇 ¿Quién hace más 180s? - Con Empate")
                    widget_barras_con_empate(j1['nombre_original'], p_j1_mas, p_emp, j2['nombre_original'], p_j2_mas, "mas180")
                
                with tab4:
                    st.markdown("#### 📐 Hándicaps - Bloques por Jugador")
                    widget_handicaps_bloques(j1['nombre_original'], j2['nombre_original'], hcaps)
                
                with tab5:
                    st.markdown("#### 📊 Total Legs - Barras Enfrentadas")
                    widget_barras_enfrentadas(f"Más de 5.5", legs_dict["Más de 5.5"], f"Menos de 5.5", legs_dict["Menos de 5.5"], "totallegs")

# 📊 RESULTADOS
elif opcion == "📊 RESULTADOS":
    st.title("📊 Resultados y Estadísticas")
    
    sel = st.selectbox(
        "Selecciona una jornada:",
        PESTANAS_CON_STATS,
        key="selector_jornada"
    )
    
    d1, d2 = cargar_todo(URLS[sel], sel, CORTES[sel])
    
    if sel in st.session_state.last_update:
        tiempo = (datetime.now() - st.session_state.last_update[sel]).seconds
        st.caption(f"⏱️ Datos actualizados hace {tiempo} segundos")
    
    if sel != "Resumen Semanal" and d1 is not None and len(d1) > 0:
        st.subheader("⚔️ Resultados")
        st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
    
    if d2 is not None and len(d2) > 0:
        if sel == "Resumen Semanal":
            st.subheader("📈 Resumen Semanal")
        else:
            st.subheader("📈 Estadísticas por Jugador")
        
        for player, stats in d2.items():
            bandera = obtener_bandera(player)
            player_display = f"{bandera} {player}" if bandera else f"👤 {player}"
            
            with st.expander(player_display, expanded=False):
                if sel == "Resumen Semanal":
                    for k, v in stats.items():
                        st.write(f"**{k}:** {v}")
                else:
                    for etiqueta in ESTADISTICAS_MOSTRAR:
                        
                        if "legs" in etiqueta.lower() and "partido" in etiqueta.lower():
                            legs_dia = calcular_legs_por_partido_dia(d1, player)
                            if legs_dia is not None:
                                st.write(f"**{etiqueta}:** {legs_dia}")
                            else:
                                st.write(f"**{etiqueta}:** -")
                            continue
                        
                        valor = "-"
                        keywords = [kw for kw in etiqueta.lower().split() if len(kw) > 3]
                        
                        for k, v in stats.items():
                            if any(kw in k.lower() for kw in keywords):
                                valor = v
                                break
                        
                        if valor != "-":
                            st.write(f"**{etiqueta}:** {valor}")
                        else:
                            st.write(f"**{etiqueta}:** -")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9em;">
<p>🎯 Modus Darts | FASE 2: Value Bets Visual Mejorado ✓</p>
</div>
""", unsafe_allow_html=True)
