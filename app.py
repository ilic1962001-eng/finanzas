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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES FINANCIERAS (Ajustado con 10% Ocio)
# ==========================================
DIEZMO_PCT = 0.10
DEUDA_PCT = 0.30
INVERSION_PCT = 0.20
OCIO_PCT = 0.10
AHORRO_PCT = 0.40  # (20% Emergencias + 20% Colchón)

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

f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = f_ocio = 0.0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = v_ocio = 0.0

if omitir_fijo:
    v_aux = var_neto
    if v_aux > 0:
        v_deuda = v_aux * DEUDA_PCT
        v_retiro = v_aux * INVERSION_PCT
        v_ocio = v_aux * OCIO_PCT
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
        f_ocio = f_aux * OCIO_PCT
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
    v_ocio = v_aux * OCIO_PCT
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
t_ocio = f_ocio + v_ocio

# ==========================================
# MÉTRICAS VISUALES SUPERIORES
# ==========================================
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("NETO DISPONIBLE", f"${(fijo_disponible + var_neto):,.2f}")
with c2: st.metric("CRECIMIENTO/AHORRO", f"${(t_emerg + t_colchon + t_deuda + t_ocio):,.2f}")
with c3: st.metric("PATRIMONIO PROYECTADO", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo or deficit_total <= 0.01:
        st.metric("ESTADO INAMOVIBLES", "CUBIERTOS ✅")
    else:
        st.metric("DÉFICIT INAMOVIBLES", f"-${deficit_total:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. TABLA ORIGINAL DE DESGLOSE (MATEMÁTICA)
# ==========================================
st.markdown("### 📊 DESGLOSE POR SOBRE")
df_data = [
    {"Sobre": "⛪ Diezmo", "Meta": "10%", "Fijo": f"${diezmo_fijo:,.2f}", "Variable": f"${diezmo_var:,.2f}", "Total": f"${t_diezmo:,.2f}", "Estado": "⚪ OK"},
    {"Sobre": "🏠 Renta", "Meta": f"${META_RENTA:,.2f}", "Fijo": f"${f_renta:,.2f}", "Variable": f"${v_renta:,.2f}", "Total": f"${t_renta:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_renta>=META_RENTA else f"🔴 -${META_RENTA-t_renta:,.2f}")},
    {"Sobre": "🚗 Transporte", "Meta": f"${META_TRANSPORTE:,.2f}", "Fijo": f"${f_transp:,.2f}", "Variable": f"${v_transp:,.2f}", "Total": f"${t_transp:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_transp>=META_TRANSPORTE else f"🔴 -${META_TRANSPORTE-t_transp:,.2f}")},
    {"Sobre": "💖 Novia", "Meta": f"${META_NOVIA:,.2f}", "Fijo": f"${f_novia:,.2f}", "Variable": f"${v_novia:,.2f}", "Total": f"${t_novia:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_novia>=META_NOVIA else f"🔴 -${META_NOVIA-t_novia:,.2f}")},
    {"Sobre": "✈️ Viajes", "Meta": f"${META_VIAJES:,.2f}", "Fijo": f"${f_viajes:,.2f}", "Variable": f"${v_viajes:,.2f}", "Total": f"${t_viajes:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_viajes>=META_VIAJES else f"🔴 -${META_VIAJES-t_viajes:,.2f}")},
    {"Sobre": "💳 Deuda (30%)", "Meta": "S/M", "Fijo": f"${f_deuda:,.2f}", "Variable": f"${v_deuda:,.2f}", "Total": f"${t_deuda:,.2f}", "Estado": "🔥 Acelerando"},
    {"Sobre": "🚨 Emergencias (20%)", "Meta": "S/M", "Fijo": f"${f_emerg:,.2f}", "Variable": f"${v_emerg:,.2f}", "Total": f"${t_emerg:,.2f}", "Estado": "🛡️ OK"},
    {"Sobre": "🛌 Colchón (20%)", "Meta": "S/M", "Fijo": f"${f_colchon:,.2f}", "Variable": f"${v_colchon:,.2f}", "Total": f"${t_colchon:,.2f}", "Estado": "🛡️ OK"},
    {"Sobre": "📈 Retiro (20%)", "Meta": "S/M", "Fijo": f"${f_retiro:,.2f}", "Variable": f"${v_retiro:,.2f}", "Total": f"${t_retiro:,.2f}", "Estado": "🚀 S&P 500"},
    {"Sobre": "🍿 Ocio (10%)", "Meta": "S/M", "Fijo": f"${f_ocio:,.2f}", "Variable": f"${v_ocio:,.2f}", "Total": f"${t_ocio:,.2f}", "Estado": "🎮 A disfrutar"}
]
st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 2. NUEVA TABLA: GUÍA DE DEPÓSITOS CONSOLIDADOS
# ==========================================
st.markdown("### 🏦 GUÍA DE DEPÓSITOS (¿A dónde mando el dinero?)")

# Variable consolidada para Nu
t_nu_total = t_renta + t_transp + t_emerg + t_colchon

df_bancos = [
    {"Destino": "⛪ Diezmo", "Monto a Transferir": f"${t_diezmo:,.2f}", "Institución": "Revolut", "CLABE / Cuenta": "% %"},
    {"Destino": "🟣 Consolidado Nu (Renta, Transp, Emerg, Colchón)", "Monto a Transferir": f"${t_nu_total:,.2f}", "Institución": "Nu", "CLABE / Cuenta": "638180000126660124"},
    {"Destino": "📈 Retiro", "Monto a Transferir": f"${t_retiro:,.2f}", "Institución": "GBM", "CLABE / Cuenta": "% %"},
    {"Destino": "💳 Deuda", "Monto a Transferir": f"${t_deuda:,.2f}", "Institución": "Otra Cuenta", "CLABE / Cuenta": "% %"},
    {"Destino": "✈️ Viajes", "Monto a Transferir": f"${t_viajes:,.2f}", "Institución": "Otra Cuenta", "CLABE / Cuenta": "% %"},
    {"Destino": "💖 Novia", "Monto a Transferir": f"${t_novia:,.2f}", "Institución": "Apartado Libre", "CLABE / Cuenta": "% %"},
    {"Destino": "🍿 Ocio", "Monto a Transferir": f"${t_ocio:,.2f}", "Institución": "Cuenta Uso Diario", "CLABE / Cuenta": "% %"}
]
st.dataframe(pd.DataFrame(df_bancos), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BOTÓN DE ACCIÓN CON ANIMACIÓN Y SONIDO
# ==========================================
col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:
    if st.button("CONFIRMO QUE YA DEPOSITÉ TODO COMO DEBE SER 💸"):
        st.balloons()
        st.toast('¡Distribución enviada con éxito a los sobres! 🤑', icon='🎉')
        sonido_html = """
            <audio autoplay>
                <source src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg" type="audio/ogg">
            </audio>
        """
        st.components.v1.html(sonido_html, width=0, height=0)
