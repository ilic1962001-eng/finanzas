import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS "PRO"
# ==========================================
st.set_page_config(page_title="Flujo de Capital | Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .titulo-pro { color: #d4af37; font-size: 2.5rem; font-weight: 800; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0px; text-shadow: 0px 4px 10px rgba(212, 175, 55, 0.3); }
    .subtitulo { text-align: center; color: #888; font-size: 1.1rem; margin-bottom: 30px; }
    div[data-testid="metric-container"] { background-color: #1E1E1E; border: 1px solid #333; padding: 15px 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-left: 4px solid #d4af37; }
    div[data-testid="metric-container"] label { color: #aaa !important; font-weight: 600 !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #fff !important; }
    .stButton > button { width: 100%; background: linear-gradient(135deg, #d4af37 0%, #b58500 100%); color: white; font-weight: 800; font-size: 1.2rem; padding: 15px 0; border: none; border-radius: 10px; box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4); transition: all 0.3s ease; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(212, 175, 55, 0.6); color: white; border: none; }
    .transfer-box { background-color: #2b2b2b; padding: 20px; border-radius: 10px; border: 1px solid #444; margin-bottom: 10px; }
    .transfer-title { font-size: 1.1rem; color: #aaa; margin-bottom: 5px; }
    .transfer-amount { font-size: 1.8rem; font-weight: bold; color: #d4af37; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES FINANCIERAS
# ==========================================
DIEZMO_PCT = 0.10
DEUDA_PCT = 0.30
INVERSION_PCT = 0.20
AHORRO_PCT = 0.50

META_RENTA = 1000.0
META_TRANSPORTE = 300.0
META_NOVIA = 300.0
META_VIAJES = 200.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

# ==========================================
# HEADER E INPUTS
# ==========================================
st.markdown("<div class='titulo-pro'>💰 FLUJO DE CAPITAL</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Distribución Inteligente en Sobres</div>", unsafe_allow_html=True)

with st.container():
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1:
        ingreso_fijo_bruto = st.number_input("💵 INGRESO FIJO NETO ($)", min_value=0.0, step=100.0, value=2329.0)
    with c_in2:
        deducciones = st.number_input("✂️ DEDUCCIONES EXACTAS ($)", min_value=0.0, step=10.0, value=0.0)
    with c_in3:
        ingreso_var_bruto = st.number_input("📈 INGRESO VARIABLE NETO ($)", min_value=0.0, step=100.0, value=1000.0)

    omitir_fijo = st.checkbox("✅ OMITIR INGRESO FIJO (Mínimos ya cubiertos)", value=False)

st.markdown("---")

# ==========================================
# CEREBRO MATEMÁTICO (CASCADA)
# ==========================================
fijo_disponible = max(0.0, ingreso_fijo_bruto - deducciones)

diezmo_fijo = fijo_disponible * DIEZMO_PCT if not omitir_fijo else 0.0
fijo_neto = fijo_disponible - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0.0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0.0

if omitir_fijo:
    v_aux = var_neto
    if v_aux > 0:
        v_deuda = v_aux * DEUDA_PCT
        v_retiro = v_aux * INVERSION_PCT
        v_ahorro_t = v_aux * AHORRO_PCT
        v_emerg = v_ahorro_t * 0.50
        v_colchon = v_ahorro_t * 0.50
else:
    f_aux = fijo_neto
    f_renta = min(f_aux, META_RENTA); f_aux -= f_renta
    f_transp = min(f_aux, META_TRANSPORTE); f_aux -= f_transp
    f_novia = min(f_aux, META_NOVIA); f_aux -= f_novia
    f_viajes = min(f_aux, META_VIAJES); f_aux -= f_viajes
    
    if f_aux > 0:
        f_deuda = f_aux * DEUDA_PCT
        f_retiro = f_aux * INVERSION_PCT
        f_ahorro_t = f_aux * AHORRO_PCT
        f_emerg = f_ahorro_t * 0.50
        f_colchon = f_ahorro_t * 0.50

v_aux = var_neto
v_renta = min(v_aux, max(0.0, META_RENTA - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0.0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0.0, META_NOVIA - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0.0, META_VIAJES - f_viajes)); v_aux -= v_viajes

if v_aux > 0 and not omitir_fijo:
    v_deuda = v_aux * DEUDA_PCT
    v_retiro = v_aux * INVERSION_PCT
    v_ahorro_t = v_aux * AHORRO_PCT
    v_emerg = v_ahorro_t * 0.50
    v_colchon = v_ahorro_t * 0.50

deficit_total = max(0.0, meta_inamovibles_total - (f_renta + v_renta + f_transp + v_transp + f_novia + v_novia + f_viajes + v_viajes))
retiro_total = f_retiro + v_retiro
proyeccion = retiro_total * (((1 + (0.07 / 52))**(30 * 52)) - 1) / (0.07 / 52) if retiro_total > 0 else 0.0

# ==========================================
# TOTALES EXACTOS (VARIABLES FINALES)
# ==========================================
t_diezmo = diezmo_fijo + diezmo_var
t_renta = f_renta + v_renta
t_transp = f_transp + v_transp
t_novia = f_novia + v_novia
t_viajes = f_viajes + v_viajes
t_deuda = f_deuda + v_deuda
t_emerg = f_emerg + v_emerg
t_colchon = f_colchon + v_colchon
t_retiro = f_retiro + v_retiro

# ==========================================
# MÉTRICAS VISUALES SUPERIORES
# ==========================================
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("NETO DISPONIBLE", f"${(fijo_disponible + var_neto):,.2f}")
with c2: st.metric("CRECIMIENTO (Ahorro+Deuda)", f"${(t_emerg + t_colchon + t_deuda):,.2f}")
with c3: st.metric("PATRIMONIO PROYECTADO", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo or deficit_total <= 0.01:
        st.metric("ESTADO INAMOVIBLES", "CUBIERTOS ✅")
    else:
        st.metric("DÉFICIT INAMOVIBLES", f"-${deficit_total:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# INSTRUCCIONES EXACTAS DE TRANSFERENCIA (NUEVO)
# ==========================================
st.markdown("### 🏦 INSTRUCCIONES DE TRANSFERENCIA EXACTAS")
st.markdown("Pasa estas cantidades exactas a tus cuentas o sobres físicos:")

t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>⛪ Diezmo</div><div class='transfer-amount'>${t_diezmo:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>🏠 Renta</div><div class='transfer-amount'>${t_renta:,.2f}</div></div>", unsafe_allow_html=True)
with t2:
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>🚗 Transporte</div><div class='transfer-amount'>${t_transp:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>💳 Deuda</div><div class='transfer-amount'>${t_deuda:,.2f}</div></div>", unsafe_allow_html=True)
with t3:
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>💖 Novia</div><div class='transfer-amount'>${t_novia:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>🚨 Emergencias</div><div class='transfer-amount'>${t_emerg:,.2f}</div></div>", unsafe_allow_html=True)
with t4:
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>✈️ Viajes</div><div class='transfer-amount'>${t_viajes:,.2f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='transfer-box'><div class='transfer-title'>🛌 Colchón + Retiro</div><div class='transfer-amount'>${(t_colchon + t_retiro):,.2f}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BOTÓN DE ACCIÓN CON ANIMACIÓN Y SONIDO
# ==========================================
col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:
    if st.button("CONFIRMO QUE YA DEPOSITÉ TODO COMO DEBE SER 💸"):
        st.balloons()
        st.toast('¡Transferencias completadas con éxito! 🤑', icon='🎉')
        sonido_html = """
            <audio autoplay>
                <source src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg" type="audio/ogg">
            </audio>
        """
        st.components.v1.html(sonido_html, width=0, height=0)
