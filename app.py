import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

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
# INICIALIZACIÓN DE SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "vb_fuente" not in st.session_state:
    st.session_state.vb_fuente = "Resumen Semanal"
if "vb_j1" not in st.session_state:
    st.session_state.vb_j1 = None
if "vb_j2" not in st.session_state:
    st.session_state.vb_j2 = None
if "vb_calcular" not in st.session_state:
    st.session_state.vb_calcular = False

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

@st.cache_data(ttl=600)
def cargar_todo(url, opcion, cortes):
    try:
        df = pd.read_csv(url, header=None)
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
    except:
        return None, None

# ─────────────────────────────────────────────
# MATEMÁTICAS VALUE BETS — CON VALIDACIÓN ROBUSTA
# ─────────────────────────────────────────────
def safe_float(val, default=0.0):
    """Convierte a float validando NaN/inf."""
    try:
        v = float(str(val).replace(',', '.').strip())
        if not np.isfinite(v):
            return default
        return v
    except:
        return default

def sanitize_prob(p):
    """
    Clampea probabilidad a rango [0.0001, 0.9999]
    para evitar divisiones por 0 o cuotas infinitas.
    """
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
    """
    CORRECCIÓN: Lambda total = SUMA de legs esperados
    (cada leg lo gana uno u otro, por lo que se suman)
    """
    lam_total = lam_legs1 + lam_legs2  # SUMA, no media
    
    prob_mas_5_5 = sanitize_prob(1 - poisson.cdf(5, lam_total))
    prob_menos_5_5 = sanitize_prob(poisson.cdf(5, lam_total))
    
    return {
        "Más de 5.5": prob_mas_5_5,
        "Menos de 5.5": prob_menos_5_5
    }

def prob_a_cuota(p):
    """
    Convierte probabilidad a cuota decimal.
    Clampea el resultado entre 1.01 y 999.0 para evitar valores extremos.
    """
    p_safe = sanitize_prob(p)
    cuota = 1.0 / p_safe
    return max(1.01, min(999.0, cuota))

def pct(p):
    return f"{p * 100:.1f}%"

def calcular_yield(prob, cuota_bookie):
    """Yield = (prob * cuota_bookie) - 1"""
    return (prob * cuota_bookie) - 1

def badge_yield(y):
    if y > 0:
        return f"✅ +{y*100:.1f}% VALUE"
    elif y < -0.05:
        return f"❌ {y*100:.1f}% sin valor"
    else:
        return f"➖ {y*100:.1f}% neutro"

# ─────────────────────────────────────────────
# CARGA DINÁMICA — fuente seleccionable
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def cargar_jugadores_desde(pestana: str):
    try:
        url = URLS[pestana]
        df = pd.read_csv(url, header=None)

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

# ─────────────────────────────────────────────
# WIDGET DE CUOTA BOOKIE — Con claves únicas persistentes
# ─────────────────────────────────────────────
def widget_cuota(mercado, prob, idx):
    """
    idx: índice único para evitar colisiones de keys
    """
    cuota_justa = prob_a_cuota(prob)
    
    col_a, col_b, col_c = st.columns([3, 2, 2])
    with col_a:
        st.write(f"**{mercado}**")
        st.caption(f"Prob: {pct(prob)}  |  Cuota justa: {cuota_justa:.2f}")
    with col_b:
        cuota_input = st.number_input(
            "Cuota bookie",
            min_value=1.01,
            max_value=50.0,
            value=min(cuota_justa, 50.0),  # Clamp para evitar error
            step=0.05,
            key=f"cuota_{idx}"
        )
    with col_c:
        y = calcular_yield(prob, cuota_input)
        st.markdown(f"<br><span style='font-size:1.1em'>{badge_yield(y)}</span>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RENDER VALUE BETS — CON PERSISTENCIA DE ESTADO
# ─────────────────────────────────────────────
def render_value_bets():
    st.title("💰 Value Bets — Motor de Probabilidades")
    
    # ── SELECTOR DE FUENTE (con session_state) ──
    st.markdown("### ⚙️ Configuración")
    fuente_idx = PESTANAS_CON_STATS.index(st.session_state.vb_fuente)
    fuente = st.selectbox(
        "📂 Usar estadísticas de:",
        PESTANAS_CON_STATS,
        index=fuente_idx,
        key="selector_fuente"
    )
    st.session_state.vb_fuente = fuente

    with st.spinner(f"Cargando datos de '{fuente}'..."):
        db_jugadores = cargar_jugadores_desde(fuente)

    if not db_jugadores:
        st.warning(f"⚠️ No se encontraron jugadores en '{fuente}'.")
        return

    nombres_disponibles = sorted([v["nombre_original"] for v in db_jugadores.values()])
    st.success(f"✅ {len(nombres_disponibles)} jugadores cargados")

    # ── SELECTOR DE JUGADORES (con session_state) ──
    st.markdown("### 🥊 Seleccionar Enfrentamiento")
    
    # Inicializar valores por defecto si es la primera vez
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
        if st.button("🔢 Calcular", type="primary"):
            st.session_state.vb_calcular = True

    # ── MOSTRAR CÁLCULOS SOLO SI SE HA PULSADO EL BOTÓN ──
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

    # ── CABECERA ──
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{j1['nombre_original']}**")
        st.caption(f"PR: {pr1:.1f} | λ 180s: {lam1:.2f} | λ Legs: {legs1:.2f}")
    with c2:
        st.markdown(f"**{j2['nombre_original']}**")
        st.caption(f"PR: {pr2:.1f} | λ 180s: {lam2:.2f} | λ Legs: {legs2:.2f}")

    v1, v2 = prob_victoria(pr1, pr2)

    # ── 1. VICTORIA ──
    st.markdown("---")
    st.markdown("#### 🏆 Victoria")
    widget_cuota(f"Gana {j1['nombre_original']}", v1, "vic_j1")
    widget_cuota(f"Gana {j2['nombre_original']}", v2, "vic_j2")

    # ── 2. 180s ──
    st.markdown("---")
    st.markdown("#### 🎯 180s")
    m180 = prob_180s(lam1, lam2)
    idx = 0
    for mercado_key, prob in [
        (f"{j1['nombre_original']} +0.5", m180["J1 +0.5"]),
        (f"{j1['nombre_original']} +1.5", m180["J1 +1.5"]),
        (f"{j2['nombre_original']} +0.5", m180["J2 +0.5"]),
        (f"{j2['nombre_original']} +1.5", m180["J2 +1.5"]),
        ("Ambos +1.5", m180["Ambos +1.5"]),
        ("Ambos +2.5", m180["Ambos +2.5"]),
    ]:
        widget_cuota(mercado_key, prob, f"180_{idx}")
        idx += 1

    # ── 3. QUIÉN HACE MÁS ──
    st.markdown("---")
    st.markdown("#### 🥇 ¿Quién hace más 180s?")
    p_j1_mas, p_emp, p_j2_mas = quien_hace_mas_180s(lam1, lam2)
    widget_cuota(f"Más: {j1['nombre_original']}", p_j1_mas, "mas_j1")
    widget_cuota("Empate", p_emp, "mas_emp")
    widget_cuota(f"Más: {j2['nombre_original']}", p_j2_mas, "mas_j2")

    # ── 4. HÁNDICAPS ──
    st.markdown("---")
    st.markdown("#### 📐 Hándicaps de Legs")
    hcaps = handicaps_legs(v1, v2)
    idx = 0
    for k, etiq in [
        ("J1 -1.5 Legs", f"{j1['nombre_original']} -1.5"),
        ("J1 -2.5 Legs", f"{j1['nombre_original']} -2.5"),
        ("J1 +1.5 Legs", f"{j1['nombre_original']} +1.5"),
        ("J1 +2.5 Legs", f"{j1['nombre_original']} +2.5"),
        ("J2 -1.5 Legs", f"{j2['nombre_original']} -1.5"),
        ("J2 -2.5 Legs", f"{j2['nombre_original']} -2.5"),
        ("J2 +1.5 Legs", f"{j2['nombre_original']} +1.5"),
        ("J2 +2.5 Legs", f"{j2['nombre_original']} +2.5"),
    ]:
        widget_cuota(etiq, hcaps[k], f"hcap_{idx}")
        idx += 1

    # ── 5. LEGS TOTALES (CORREGIDO) ──
    st.markdown("---")
    st.markdown("#### 📊 Legs Totales")
    legs_total_dict = legs_totales(legs1, legs2)
    widget_cuota("Más de 5.5 Legs", legs_total_dict["Más de 5.5"], "legs_mas")
    widget_cuota("Menos de 5.5 Legs", legs_total_dict["Menos de 5.5"], "legs_menos")

# ─────────────────────────────────────────────
# INTERFAZ PRINCIPAL
# ─────────────────────────────────────────────
st.sidebar.title("🎯 Menú Modus")
sel = st.sidebar.radio("Ir a:", list(URLS.keys()), key="menu_principal")

if sel == "Value Bets":
    render_value_bets()
else:
    d1, d2 = cargar_todo(URLS[sel], sel, CORTES[sel])
    st.title(f"📊 {sel}")

    orden_diario = [
        "Media 180 por partida", "Promedio puntos total", "Diferencia de legs",
        "Legs por partido", "Promedio Checkouts", "Número victorias",
        "Número derrotas", "Porcentaje victoria", "PUNTIACIÓN GLOBAL (0-100)"
    ]

    if d2 is not None:
        st.subheader("📈 Estadísticas por Jugador")
        for player, stats in d2.items():
            with st.expander(f"👤 {player}"):
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
