import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, time

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

PESTANAS_CON_STATS = [k for k in URLS if k not in ("Resumen Semanal",)]

# ═══════════════════════════════════════════════════════════════
# BANDERAS
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# HORARIOS PARA DETECTAR LIVE
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# ESTADÍSTICAS A MOSTRAR - SIN DUPLICADOS
# ═══════════════════════════════════════════════════════════════
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

# SOLO ESTAS MÉTRICAS MUESTRAN TENDENCIAS
METRICAS_CON_TENDENCIA = [
    "promedio checkouts",
    "promedio dardos",
    "180"
]

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "last_update" not in st.session_state:
    st.session_state.last_update = {}

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
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
        else:
            f, c = cortes["izq_filas"], cortes["izq_cols"]
            izq = df.iloc[f[0]:f[1], c[0]:c[1]]
            izq.columns = izq.iloc[0]; izq = izq[1:]
            s = extraer_stats_diarias(df, cortes["der_nombres"], cortes["der_cols"])
            return arreglar_columnas(izq.dropna(how='all')), s
    except Exception as e:
        st.error(f"Error cargando {opcion}: {e}")
        return None, None

def obtener_bandera(nombre_jugador):
    nombre_lower = nombre_jugador.lower().strip().replace("_", " ")
    codigo_pais = JUGADORES_PAISES.get(nombre_lower, None)
    if codigo_pais and codigo_pais in BANDERAS:
        return BANDERAS[codigo_pais]
    return None

def calcular_tendencia_stat(valor_actual, media_previa, umbral=10.0):
    """Calcula tendencia, devuelve 'up', 'down' o 'neutral'"""
    if valor_actual is None or media_previa is None or media_previa == 0:
        return 'neutral'
    
    try:
        diferencia_pct = abs((valor_actual - media_previa) / media_previa) * 100
        
        if (valor_actual - media_previa) > 0 and diferencia_pct > umbral:
            return 'up'
        elif (valor_actual - media_previa) < 0 and diferencia_pct > umbral:
            return 'down'
        else:
            return 'neutral'
    except:
        return 'neutral'

def emoji_tendencia(tendencia):
    if tendencia == 'up':
        return '🔼'
    elif tendencia == 'down':
        return '🔽'
    else:
        return ''

def calcular_media_stats(stats_dict, keywords):
    valores = []
    for k, v in stats_dict.items():
        for kw in keywords:
            if kw.lower() in k.lower():
                try:
                    valor = float(str(v).replace(',', '.').strip())
                    if np.isfinite(valor):
                        valores.append(valor)
                except:
                    pass
    
    if valores and len(valores) > 1:
        return np.mean(valores)
    return None

def extraer_ultimo_valor(stats_dict, keywords):
    for k, v in stats_dict.items():
        for kw in keywords:
            if kw.lower() in k.lower():
                try:
                    return float(str(v).replace(',', '.').strip())
                except:
                    pass
    return None

def detectar_jornada_activa():
    """Detecta qué jornada está en vivo ahora."""
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
# SIDEBAR - NAVEGACIÓN
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

# 💰 VALUE BETS
elif opcion == "💰 VALUE BETS":
    st.title("💰 VALUE BETS")
    st.info("⚠️ Sección de Value Bets - Mejora visual en próximas fases")

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
    
    # TABLA DE RESULTADOS
    if d1 is not None and len(d1) > 0:
        st.subheader("⚔️ Resultados")
        st.dataframe(d1.style.apply(pintar_partidos, axis=1), use_container_width=True, hide_index=True)
    
    # ESTADÍSTICAS POR JUGADOR
    if d2 is not None and len(d2) > 0:
        st.subheader("📈 Estadísticas por Jugador")
        
        for player, stats in d2.items():
            bandera = obtener_bandera(player)
            player_display = f"{bandera} {player}" if bandera else f"👤 {player}"
            
            with st.expander(player_display, expanded=False):
                for etiqueta in ESTADISTICAS_MOSTRAR:
                    valor = "-"
                    keywords = [kw for kw in etiqueta.lower().split() if len(kw) > 3]
                    
                    # Buscar el valor en stats
                    for k, v in stats.items():
                        if any(kw in k.lower() for kw in keywords):
                            valor = v
                            break
                    
                    if valor != "-":
                        # VERIFICAR si debe mostrar tendencia
                        debe_tendencia = any(
                            metrica in etiqueta.lower()
                            for metrica in METRICAS_CON_TENDENCIA
                        )
                        
                        if debe_tendencia:
                            valor_actual = extraer_ultimo_valor(stats, keywords)
                            media = calcular_media_stats(stats, keywords)
                            
                            if valor_actual is not None and media is not None:
                                tendencia = calcular_tendencia_stat(valor_actual, media, umbral=10.0)
                                emoji = emoji_tendencia(tendencia)
                                st.write(f"**{etiqueta}:** {valor} {emoji}")
                            else:
                                st.write(f"**{etiqueta}:** {valor}")
                        else:
                            st.write(f"**{etiqueta}:** {valor}")
                    else:
                        st.write(f"**{etiqueta}:** -")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9em;">
<p>🎯 Modus Darts Super Series</p>
</div>
""", unsafe_allow_html=True)
