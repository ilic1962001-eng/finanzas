import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ==========================================
# GESTIÓN DE ESTADOS (MEMORIA DE LA APP)
# ==========================================
if "val_fijo" not in st.session_state:
    st.session_state.val_fijo = 0.0
if "val_var" not in st.session_state:
    st.session_state.val_var = 0.0
if "mostrar_celebracion" not in st.session_state:
    st.session_state.mostrar_celebracion = False

def confirmar_deposito():
    # Reiniciar a cero las entradas
    st.session_state.val_fijo = 0.0
    st.session_state.val_var = 0.0
    # Activar la animación
    st.session_state.mostrar_celebracion = True

# ==========================================
# CONFIGURACIÓN ELITE Y ESTILOS
# ==========================================
st.set_page_config(page_title="Mi vida Mirssa", layout="wide", page_icon="👑")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');

    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
    }
    
    p, label, div, li { color: #ffffff !important; }

    h1, h2, h3, h4, h5, h6 {
        color: #d4af37 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    .app-title {
        color: #FF0000 !important;
        font-size: 50px;
        font-weight: 800;
        text-align: center;
        letter-spacing: 4px;
        margin-bottom: 5px;
    }

    .dedicatoria {
        color: #d4af37 !important;
        text-align: center;
        font-style: italic;
        font-size: 1.2rem;
        margin-bottom: 40px;
    }
    
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: #0a0a0a;
        border: 1px solid #d4af3766;
        padding: 20px;
        border-radius: 8px;
    }
    
    /* ESTILO DEL BOTÓN DE CÁLCULO */
    .stButton>button {
        background-color: #d4af37 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        width: 100%;
        border-radius: 4px;
        border: none;
        padding: 15px;
        margin-top: 15px;
        transition: all 0.3s ease;
        white-space: normal !important;
        line-height: 1.3 !important;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #FF0000 !important;
        color: #ffffff !important;
        transform: scale(1.02);
    }
    
    /* CLABES: NEGRAS EN FONDO BLANCO */
    div[data-testid="stCodeBlock"] {
        background-color: #FFFFFF !important;
        border: 2px solid #d4af37 !important;
    }
    div[data-testid="stCodeBlock"] code, 
    div[data-testid="stCodeBlock"] span,
    div[data-testid="stCodeBlock"] pre {
        color: #000000 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    .stDataFrame [data-testid="stTable"] {
        background-color: #000000 !important;
    }
    
    /* Borde dorado para el panel fijo izquierdo */
    .panel-izquierdo {
        border-right: 1px solid #d4af3744;
        padding-right: 20px;
    }
    
    /* ANIMACIÓN LLUVIA DE BILLETES */
    .dinero-cayendo {
        position: fixed;
        top: -10%;
        z-index: 999999;
        user-select: none;
        pointer-events: none;
        animation-name: caida_dinero;
        animation-timing-function: linear;
        animation-fill-mode: forwards;
    }
    @keyframes caida_dinero {
        to { transform: translateY(110vh) rotate(720deg); }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="app-title">MI VIDA MIRSSA</h1>', unsafe_allow_html=True)
st.markdown('<p class="dedicatoria">"Porque cada peso bien administrado es un ladrillo más para nuestra mansión y cada ahorro una promesa de seguridad para nuestra vida juntos."</p>', unsafe_allow_html=True)

# ==========================================
# PARÁMETROS FINANCIEROS
# ==========================================
DIEZMO_PCT = 0.10; GASTO_PCT = 0.65; DEUDA_PCT = 0.10; AHORRO_PCT = 0.10; INVERSION_PCT = 0.15
META_RENTA = 875.0; META_TRANSPORTE = 430.0; META_NOVIA = 500.0; META_VIAJES = 300.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

CUENTAS = {
    "NU (Cajita)": "638180000126660124", 
    "NU (Gasto)": "638180000126660124",
    "GBM+": "601180400073884389", 
    "SPIN": "728969000033664690",
    "Cuenta Diezmo": "POR DEFINIR", 
    "Pago Deuda": "POR DEFINIR", 
    "CETES": "POR DEFINIR"
}

# ==========================================
# DIVISIÓN DE PANTALLA: PANEL FIJO (25%) Y DASHBOARD (75%)
# ==========================================
col_izq, col_der = st.columns([1, 3], gap="large")

with col_izq:
    st.markdown("<div class='panel-izquierdo'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#d4af37; font-size: 1.5rem;'>Flujo de Capital</h3>", unsafe_allow_html=True)
    
    # Inputs vinculados a session_state
    ingreso_fijo_bruto = st.number_input("INGR. FIJO ($)", min_value=0.0, step=100.0, key="val_fijo")
    ingreso_var_bruto = st.number_input("INGR. VARIABLE ($)", min_value=0.0, step=100.0, key="val_var")
    
    # Botón con Callback para reiniciar valores
    st.button("CONFIRMO QUE YA DEPOSITÉ TODO COMO DEBE SER", on_click=confirmar_deposito)
    
    st.divider()
    st.markdown("<p style='font-size:0.8rem; color:#888888; text-align:center;'>Diseñado para el futuro de Ilich & Mirssa</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Inyección de Animación y Sonido (Se ejecuta solo si mostrar_celebracion es True)
    if st.session_state.mostrar_celebracion:
        iconos = ['💸', '💵', '💰', '💶', '👑']
        animacion_html = ""
        
        # Generar 50 billetes cayendo con tiempos y posiciones aleatorias
        for _ in range(50):
            left = random.randint(0, 100)
            delay = random.uniform(0, 1.5)
            duration = random.uniform(2, 4)
            size = random.uniform(2, 4)
            icono = random.choice(iconos)
            animacion_html += f'<div class="dinero-cayendo" style="left: {left}%; font-size: {size}rem; animation-duration: {duration}s; animation-delay: {delay}s;">{icono}</div>'
        
        # Audio autoplay (Campanita de Caja Registradora)
        animacion_html += """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3" type="audio/mpeg">
        </audio>
        """
        st.markdown(animacion_html, unsafe_allow_html=True)
        # Apagamos la animación para que no se repita en la siguiente interacción
        st.session_state.mostrar_celebracion = False

with col_der:
    # ==========================================
    # LÓGICA DE DISTRIBUCIÓN
    # ==========================================
    diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT; fijo_neto = ingreso_fijo_bruto - diezmo_fijo
    diezmo_var = ingreso_var_bruto * DIEZMO_PCT; var_neto = ingreso_var_bruto - diezmo_var

    f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
    v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

    capacidad_gasto_fijo = fijo_neto * GASTO_PCT
    if capacidad_gasto_fijo >= meta_inamovibles_total:
        p_renta, p_transp = META_RENTA/meta_inamovibles_total, META_TRANSPORTE/meta_inamovibles_total
        p_novia, p_viajes = META_NOVIA/meta_inamovibles_total, META_VIAJES/meta_inamovibles_total
        f_renta, f_transp = capacidad_gasto_fijo*p_renta, capacidad_gasto_fijo*p_transp
        f_novia, f_viajes = capacidad_gasto_fijo*p_novia, capacidad_gasto_fijo*p_viajes
        f_deuda, f_retiro = fijo_neto*DEUDA_PCT, fijo_neto*INVERSION_PCT
        f_emerg, f_colchon = (fijo_neto*AHORRO_PCT)*0.5, (fijo_neto*AHORRO_PCT)*0.5
    else:
        f_aux = fijo_neto
        f_renta = min(f_aux, META_RENTA); f_aux -= f_renta
        f_transp = min(f_aux, META_TRANSPORTE); f_aux -= f_transp
        f_novia = min(f_aux, META_NOVIA); f_aux -= f_novia
        f_viajes = min(f_aux, META_VIAJES); f_aux -= f_viajes
        f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
        f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
        f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
        f_retiro = f_aux

    v_aux = var_neto
    v_renta = min(v_aux, max(0, META_RENTA - f_renta)); v_aux -= v_renta
    v_transp = min(v_aux, max(0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
    v_novia = min(v_aux, max(0, META_NOVIA - f_novia)); v_aux -= v_novia
    v_viajes = min(v_aux, max(0, META_VIAJES - f_viajes)); v_aux -= v_viajes

    if v_aux > 0:
        v_ahorro_t = v_aux * 0.50
        v_deuda, v_retiro = v_aux * 0.30, v_aux * 0.20
        v_emerg, v_colchon = v_ahorro_t * 0.50, v_ahorro_t * 0.50

    rescate_total = v_renta + v_transp + v_novia + v_viajes
    texto_rescate = f"{(rescate_total / var_neto) * 100:.1f}%" if var_neto > 0 and rescate_total > 0 else "Nada"
    deficit_total = meta_inamovibles_total - (f_renta + v_renta + f_transp + v_transp + f_novia + v_novia + f_viajes + v_viajes)

    retiro_total = f_retiro + v_retiro
    proyeccion = retiro_total * (((1 + (0.10/52))**(30 * 52)) - 1) / (0.10/52) if retiro_total > 0 else 0

    # ==========================================
    # RENDERIZADO VISUAL DEL DASHBOARD
    # ==========================================
    st.markdown("### RESUMEN SEMANAL")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("INGRESO BRUTO TOTAL", f"${(ingreso_fijo_bruto + ingreso_var_bruto):,.2f}")
    with c2: st.metric("AHORRO TOTAL GENERADO", f"${(f_emerg + v_emerg + f_colchon + v_colchon):,.2f}")
    with c3: 
        st.markdown(f"<div data-testid='metric-container'><label data-testid='stMetricLabel'>PATRIMONIO 30 AÑOS (S&P 500)</label><div data-testid='stMetricValue' style='color: #00E676 !important;'>${proyeccion:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    c4, c5, c6 = st.columns(3)
    with c4: st.metric("CAPITAL NETO", f"${(fijo_neto + var_neto):,.2f}")
    with c5: st.metric("% VAR. PARA RESCATE", texto_rescate)
    with c6: 
        profit_final = max(0, capacidad_gasto_fijo - meta_inamovibles_total) if capacidad_gasto_fijo > meta_inamovibles_total else 0
        if deficit_total > 0.01:
            st.markdown(f"<div data-testid='metric-container' style='border-color: #FF000066;'><label data-testid='stMetricLabel' style='color: #FF0000 !important;'>DÉFICIT DE MÍNIMOS</label><div data-testid='stMetricValue' style='color: #FF0000 !important;'>-${deficit_total:,.2f}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div data-testid='metric-container'><label data-testid='stMetricLabel'>PROFIT EN SOBRES</label><div data-testid='stMetricValue' style='color: #00E676 !important;'>${profit_final:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Desglose de Capital")
    df_data = [
        {"Sobre": "Diezmo", "Meta": "S/M", "Fijo": f"${diezmo_fijo:,.2f}", "Variable": f"${diezmo_var:,.2f}", "Total": f"${(diezmo_fijo+diezmo_var):,.2f}", "Fit": "⚪ OK"},
        {"Sobre": "Renta", "Meta": f"${META_RENTA:,.2f}", "Fijo": f"${f_renta:,.2f}", "Variable": f"${v_renta:,.2f}", "Total": f"${(f_renta+v_renta):,.2f}", "Fit": f"🟢 +${max(0, (f_renta+v_renta)-META_RENTA):,.2f}" if (f_renta+v_renta)>=META_RENTA else f"🔴 -${META_RENTA-(f_renta+v_renta):,.2f}"},
        {"Sobre": "Transporte", "Meta": f"${META_TRANSPORTE:,.2f}", "Fijo": f"${f_transp:,.2f}", "Variable": f"${v_transp:,.2f}", "Total": f"${(f_transp+v_transp):,.2f}", "Fit": f"🟢 +${max(0, (f_transp+v_transp)-META_TRANSPORTE):,.2f}" if (f_transp+v_transp)>=META_TRANSPORTE else f"🔴 -${META_TRANSPORTE-(f_transp+v_transp):,.2f}"},
        {"Sobre": "Novia", "Meta": f"${META_NOVIA:,.2f}", "Fijo": f"${f_novia:,.2f}", "Variable": f"${v_novia:,.2f}", "Total": f"${(f_novia+v_novia):,.2f}", "Fit": f"🟢 +${max(0, (f_novia+v_novia)-META_NOVIA):,.2f}" if (f_novia+v_novia)>=META_NOVIA else f"🔴 -${META_NOVIA-(f_novia+v_novia):,.2f}"},
        {"Sobre": "Viajes", "Meta": f"${META_VIAJES:,.2f}", "Fijo": f"${f_viajes:,.2f}", "Variable": f"${v_viajes:,.2f}", "Total": f"${(f_viajes+v_viajes):,.2f}", "Fit": f"🟢 +${max(0, (f_viajes+v_viajes)-META_VIAJES):,.2f}" if (f_viajes+v_viajes)>=META_VIAJES else f"🔴 -${META_VIAJES-(f_viajes+v_viajes):,.2f}"},
        {"Sobre": "Deuda", "Meta": "S/M", "Fijo": f"${f_deuda:,.2f}", "Variable": f"${v_deuda:,.2f}", "Total": f"${(f_deuda+v_deuda):,.2f}", "Fit": "⚪ OK"},
        {"Sobre": "Emergencias", "Meta": "S/M", "Fijo": f"${f_emerg:,.2f}", "Variable": f"${v_emerg:,.2f}", "Total": f"${(f_emerg+v_emerg):,.2f}", "Fit": "⚪ OK"},
        {"Sobre": "Colchón", "Meta": "S/M", "Fijo": f"${f_colchon:,.2f}", "Variable": f"${v_colchon:,.2f}", "Total": f"${(f_colchon+v_colchon):,.2f}", "Fit": "⚪ OK"},
        {"Sobre": "Retiro/Bolsa", "Meta": "S/M", "Fijo": f"${f_retiro:,.2f}", "Variable": f"${v_retiro:,.2f}", "Total": f"${(f_retiro+v_retiro):,.2f}", "Fit": "⚪ OK"},
    ]
    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    c_trans, c_pie = st.columns([1, 1.2])
    with c_trans:
        st.subheader("🏦 CLABEs (Copiables)")
        transf = [
            ("NU (Cajita/Gasto)", f_renta+v_renta+f_novia+v_novia+f_colchon+v_colchon+f_transp+v_transp),
            ("GBM+ (Bolsa/Retiro)", f_retiro+v_retiro),
            ("SPIN (Viajes/Ocio)", f_viajes+v_viajes)
        ]
        for banco, monto in transf:
            if monto > 0:
                st.markdown(f"<p style='color:#d4af37; font-weight:600; margin-bottom:2px;'>{banco}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:1.1rem; margin-top:0px;'>Transferir: <b style='color:#00E676;'>${monto:,.2f}</b></p>", unsafe_allow_html=True)
                st.code(CUENTAS.get(banco.split(" ")[0]), language=None)
                st.markdown("<br>", unsafe_allow_html=True)

    with c_pie:
        st.subheader("Distribución de Patrimonio")
        fig = px.pie(values=[diezmo_fijo+diezmo_var, f_renta+v_renta+f_novia+v_novia+f_transp+v_transp, f_deuda+v_deuda, f_emerg+v_emerg+f_colchon+v_colchon, f_retiro+v_retiro], 
                     names=['Diezmo', 'Gastos Mirssa', 'Deuda', 'Ahorro', 'Inversión'], hole=0.7,
                     color_discrete_sequence=['#d4af37', '#FF0000', '#ffffff', '#444444', '#00E676'])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#ffffff"))
        st.plotly_chart(fig, use_container_width=True)
