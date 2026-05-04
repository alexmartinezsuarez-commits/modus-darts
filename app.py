def tarjeta_jugador(nombre, pr, lam_180, lam_legs, is_left=True):
    """Tarjeta visual SIMÉTRICA con stats del jugador."""
    color = "#1f77b4" if is_left else "#ff7f0e"
    
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
        <h3 style="color: {color}; margin: 0 0 20px 0; text-align: center;">🎯 {nombre}</h3>
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
