# ... [todo el código anterior permanece igual hasta render_value_bets] ...

def render_value_bets():
    st.title("💰 Value Bets — Motor de Probabilidades")
    
    # Reset de contadores
    value_bets_list = []  # Lista local para recopilar value bets
    
    # ── CONFIGURACIÓN ──
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

    # ── SELECCIÓN DE JUGADORES ──
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

    # ── COMPARATIVA VISUAL SIMÉTRICA ──
    st.markdown("---")
    st.markdown("### 📊 Comparativa de Jugadores")
    
    # Columnas exactamente iguales con VS centrado
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

    # Calcular todas las probabilidades
    v1, v2 = prob_victoria(pr1, pr2)
    m180 = prob_180s(lam1, lam2)
    p_j1_mas, p_emp, p_j2_mas = quien_hace_mas_180s(lam1, lam2)
    hcaps = handicaps_legs(v1, v2)
    legs_total_dict = legs_totales(legs1, legs2)

    # ── FUNCIÓN AUXILIAR PARA RECOPILAR VALUE BETS ──
    def procesar_mercado(mercado, prob, cuota_input):
        """Procesa un mercado y devuelve datos si tiene value."""
        if cuota_input is not None and cuota_input > 0:
            y = calcular_yield(prob, cuota_input)
            if y > 0:  # Solo registrar si hay value positivo
                cuota_justa = prob_a_cuota(prob)
                return {
                    "Mercado": mercado,
                    "Probabilidad": prob,
                    "Cuota Justa": cuota_justa,
                    "Cuota Bookie": cuota_input,
                    "Yield": y
                }
        return None

    # ── MERCADOS ORGANIZADOS POR TABS ──
    st.markdown("---")
    st.markdown("### 🎲 Mercados Disponibles")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Victoria", "🎯 180s", "🥇 ¿Quién hace más?", "📐 Hándicaps", "📊 Totales"])
    
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
        st.markdown("#### 📊 Legs Totales (First to 4)")
        st.caption("Basado en distribución binomial negativa — Under 5.5 = marcadores 4-0 y 4-1")
        c1 = widget_mercado_compacto("Más de 5.5 Legs", legs_total_dict["Más de 5.5"], "legs_mas")
        vb = procesar_mercado("Más de 5.5 Legs", legs_total_dict["Más de 5.5"], c1)
        if vb: value_bets_list.append(vb)
        
        c2 = widget_mercado_compacto("Menos de 5.5 Legs", legs_total_dict["Menos de 5.5"], "legs_menos")
        vb = procesar_mercado("Menos de 5.5 Legs", legs_total_dict["Menos de 5.5"], c2)
        if vb: value_bets_list.append(vb)

    # ── RESUMEN VISUAL DE VALUE BETS ──
    if value_bets_list:
        st.markdown("---")
        st.markdown("### 💎 Resumen de Value Bets Encontradas")
        
        # Ordenar por yield descendente
        value_bets_list.sort(key=lambda x: x["Yield"], reverse=True)
        
        # Mostrar cada value bet en una tarjeta visual
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
