import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time

st.set_page_config(page_title="Modus Darts", layout="wide", page_icon="🎯")

# ═══════════════════════════════════════════════════════════════
# URLS DE GOOGLE SHEETS
# ═══════════════════════════════════════════════════════════════
URLS = {
    "Grupo A Lunes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=770660826&single=true&output=csv",
    "Grupo A Martes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=1188400317&single=true&output=csv",
    "Grupo A Miércoles": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=611921899&single=true&output=csv",
    "Grupo C Jueves": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=1451632905&single=true&output=csv",
    "Grupo B Jueves": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=838707746&single=true&output=csv",
    "Grupo C Viernes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=951305991&single=true&output=csv",
    "Grupo B Viernes": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=895443076&single=true&output=csv",
    "Grupo B Sábado": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=843639863&single=true&output=csv",
    "Resumen Semanal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRpzkL3TKUdIptc202-w-A0ifJtiFIIP9rI0q0zQzn_I4VKX8qUi_-r1XXfPkwefN03rIQzYUNyg9xP/pub?gid=701394558&single=true&output=csv",
}

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE HORARIOS POR JORNADA
# ═══════════════════════════════════════════════════════════════
HORARIOS_JORNADAS = {
    "Grupo A Lunes": {
        "dia": 0,  # 0=Lunes
        "hora_inicio": time(10, 0),
        "hora_fin": time(16, 0)
    },
    "Grupo A Martes": {
        "dia": 1,  # 1=Martes
        "hora_inicio": time(10, 0),
        "hora_fin": time(16, 0)
    },
    "Grupo A Miércoles": {
        "dia": 2,  # 2=Miércoles
        "hora_inicio": time(10, 0),
        "hora_fin": time(16, 0)
    },
    "Grupo C Jueves": {
        "dia": 3,  # 3=Jueves
        "hora_inicio": time(13, 0),
        "hora_fin": time(19, 0)
    },
    "Grupo B Jueves": {
        "dia": 3,  # 3=Jueves
        "hora_inicio": time(22, 0),
        "hora_fin": time(3, 0),
        "medianoche": True  # Cruza a día siguiente
    },
    "Grupo C Viernes": {
        "dia": 4,  # 4=Viernes
        "hora_inicio": time(13, 0),
        "hora_fin": time(19, 0)
    },
    "Grupo B Viernes": {
        "dia": 4,  # 4=Viernes
        "hora_inicio": time(22, 0),
        "hora_fin": time(3, 0),
        "medianoche": True
    },
    "Grupo B Sábado": {
        "dia": 5,  # 5=Sábado
        "hora_inicio": time(22, 0),
        "hora_fin": time(3, 0),
        "medianoche": True
    },
}

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 0

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────

def arreglar_columnas(df):
    """Renombra columnas para evitar duplicados."""
    nuevas_cols = []
    for i, col in enumerate(df.columns):
        nombre = str(col).strip()
        if nombre == 'nan' or nombre == '':
            nombre = f"Dato_{i}"
        while nombre in nuevas_cols:
            nombre = f"{nombre}_{i}"
        nuevas_cols.append(nombre)
    df.columns = nuevas_cols
    return df

def pintar_partidos(fila):
    """Alterna colores en las filas de partidos."""
    if (fila.name // 2) % 2 == 0:
        return ['background-color: rgba(150, 150, 150, 0.15)'] * len(fila)
    return ['background-color: transparent'] * len(fila)

@st.cache_data(ttl=30)
def cargar_datos_hoja(url):
    """Carga datos de una hoja de Google Sheets."""
    try:
        df = pd.read_csv(url, header=None)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

def extraer_tabla_partidos(df):
    """Extrae la tabla de partidos de la hoja."""
    if df is None or len(df) < 5:
        return None
    
    try:
        # Buscar donde empieza la tabla (típicamente fila 5)
        filas_inicio = 5
        filas_fin = len(df)
        
        tabla = df.iloc[filas_inicio:filas_fin].copy()
        tabla.columns = df.iloc[filas_inicio].values
        tabla = tabla[1:].reset_index(drop=True)
        
        return arreglar_columnas(tabla.dropna(how='all'))
    except:
        return None

def detectar_jornada_activa():
    """
    Detecta qué jornada está activa ahora mismo.
    Retorna (nombre_jornada, está_activa) o None si no hay jornada activa.
    """
    ahora = datetime.now()
    dia_actual = ahora.weekday()  # 0=Lunes, 6=Domingo
    hora_actual = ahora.time()
    
    for nombre_jornada, horario in HORARIOS_JORNADAS.items():
        dia_jornada = horario["dia"]
        hora_inicio = horario["hora_inicio"]
        hora_fin = horario["hora_fin"]
        medianoche = horario.get("medianoche", False)
        
        if medianoche:
            # Caso especial: cruza la medianoche (22:00 - 03:00)
            # Activo si es el día correcto DESPUÉS de las 22:00
            # O si es el día siguiente ANTES de las 03:00
            if (dia_actual == dia_jornada and hora_actual >= hora_inicio) or \
               (dia_actual == (dia_jornada + 1) % 7 and hora_actual < hora_fin):
                return nombre_jornada, True
        else:
            # Caso normal: mismo día entre hora_inicio y hora_fin
            if dia_actual == dia_jornada and hora_inicio <= hora_actual < hora_fin:
                return nombre_jornada, True
    
    return None, False

def obtener_todas_jornadas_pasadas():
    """Retorna lista de todas las jornadas (excepto la actual si está activa)."""
    jornada_activa, _ = detectar_jornada_activa()
    
    jornadas = list(HORARIOS_JORNADAS.keys())
    if jornada_activa and jornada_activa in jornadas:
        jornadas.remove(jornada_activa)
    
    return jornadas

# ═══════════════════════════════════════════════════════════════
# COMPONENTES PRINCIPALES
# ═══════════════════════════════════════════════════════════════

def render_live():
    """Renderiza la pestaña LIVE."""
    st.title("🔴 LIVE")
    
    jornada_activa, hay_jornada = detectar_jornada_activa()
    
    if not hay_jornada:
        st.info("⏳ No hay partidos en juego ahora")
        st.markdown("""
        **Próximas jornadas:**
        - Grupo A Lunes: 10:00 - 16:00
        - Grupo A Martes: 10:00 - 16:00
        - Grupo A Miércoles: 10:00 - 16:00
        - Grupo C Jueves: 13:00 - 19:00
        - Grupo B Jueves: 22:00 - 03:00
        - Grupo C Viernes: 13:00 - 19:00
        - Grupo B Viernes: 22:00 - 03:00
        - Grupo B Sábado: 22:00 - 03:00
        """)
        return
    
    st.success(f"✅ **{jornada_activa}** en vivo")
    
    # Cargar datos de la jornada activa
    if jornada_activa in URLS:
        df = cargar_datos_hoja(URLS[jornada_activa])
        tabla_partidos = extraer_tabla_partidos(df)
        
        if tabla_partidos is not None and len(tabla_partidos) > 0:
            st.subheader("Partidos en juego")
            st.dataframe(
                tabla_partidos.style.apply(pintar_partidos, axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No hay datos disponibles para esta jornada")
    else:
        st.error(f"No se encontró URL para {jornada_activa}")

def render_value_bets():
    """Renderiza la pestaña VALUE BETS."""
    st.title("💰 VALUE BETS")
    
    st.info("⚠️ FASE 2: Esta sección será mejorada visualmente después de completar FASE 1")
    
    st.markdown("""
    **Próximamente:**
    - Mercado Victoria (barras enfrentadas)
    - Mercado 180s (bloques por jugador)
    - Quién hace más 180s (con empate en centro)
    - Hándicaps (bloques por jugador)
    - Total Legs (barras enfrentadas)
    """)

def render_resultados():
    """Renderiza la pestaña RESULTADOS Y ESTADÍSTICAS."""
    st.title("📊 RESULTADOS Y ESTADÍSTICAS")
    
    # Selector de jornada
    jornadas = obtener_todas_jornadas_pasadas()
    
    if not jornadas:
        st.info("No hay jornadas disponibles")
        return
    
    jornada_seleccionada = st.selectbox(
        "Selecciona una jornada:",
        jornadas,
        key="selector_jornada"
    )
    
    # Cargar y mostrar datos
    if jornada_seleccionada in URLS:
        df = cargar_datos_hoja(URLS[jornada_seleccionada])
        tabla_partidos = extraer_tabla_partidos(df)
        
        if tabla_partidos is not None and len(tabla_partidos) > 0:
            st.subheader(f"📋 {jornada_seleccionada}")
            st.dataframe(
                tabla_partidos.style.apply(pintar_partidos, axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No hay datos disponibles para esta jornada")

# ═══════════════════════════════════════════════════════════════
# NAVEGACIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

st.markdown("---")

# Crear 3 columnas para las pestañas
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔴 LIVE", use_container_width=True, key="btn_live"):
        st.session_state.selected_tab = 0

with col2:
    if st.button("💰 VALUE BETS", use_container_width=True, key="btn_vb"):
        st.session_state.selected_tab = 1

with col3:
    if st.button("📊 RESULTADOS", use_container_width=True, key="btn_res"):
        st.session_state.selected_tab = 2

st.markdown("---")

# Renderizar pestaña seleccionada
if st.session_state.selected_tab == 0:
    render_live()
elif st.session_state.selected_tab == 1:
    render_value_bets()
elif st.session_state.selected_tab == 2:
    render_resultados()

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9em;">
<p>🎯 Modus Darts Super Series | FASE 1: Navegación + LIVE</p>
</div>
""", unsafe_allow_html=True)
