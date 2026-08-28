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
# CONSTANTES FINANCIERAS
# ==========================================
DIEZMO_PCT = 0.10

# Proporciones de Crecimiento (Suman 100% del bloque restante)
P_DEUDA = 0.30
P_RETIRO = 0.20
P_OCIO = 0.10
P_EMERG = 0.20
P_COLCHON = 0.20

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
# NUEVO CEREBRO MATEMÁTICO (FONDO UNIFICADO)
# ==========================================
fijo_disponible = max(0.0, ingreso_fijo_bruto - deducciones)

diezmo_fijo = fijo_disponible * DIEZMO_PCT if not omitir_fijo else 0.0
fijo_neto = fijo_disponible - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

total_neto = fijo_neto + var_neto

# 1. Definir los "Targets" (Metas) de esta semana evaluando el total
if omitir_fijo:
    t_meta_renta = t_meta_transp = t_meta_novia = t_meta_viajes = 0.0
else:
    # EL GATILLO: Si el 50% de tu dinero TOTAL supera los mínimos, entras en ABUNDANCIA
    if (total_neto * 0.50) > meta_inamovibles_total:
        factor = (total_neto * 0.50) / meta_inamovibles_total
        t_meta_renta = META_RENTA * factor
        t_meta_transp = META_TRANSPORTE * factor
        t_meta_novia = META_NOVIA * factor
        t_meta_viajes = META_VIAJES * factor
    else:
        # SUPERVIVENCIA: Se quedan en lo mínimo necesario
        t_meta_renta = META_RENTA
        t_meta_transp = META_TRANSPORTE
        t_meta_novia = META_NOVIA
        t_meta_viajes = META_VIAJES

# 2. Función para llenar un sobre priorizando el Fijo y luego el Variable
def llenar_sobre(meta, disp_fijo, disp_var):
    uso_fijo = min(meta, disp_fijo)
    disp_fijo -= uso_fijo
    
    faltante = meta - uso_fijo
    uso_var = min(faltante, disp_var)
    disp_var -= uso_var
    
    return uso_fijo, uso_var, disp_fijo, disp_var

# 3. Llenamos los inamovibles en cascada
f_restante = fijo_neto
v_restante = var_neto

f_renta, v_renta, f_restante, v_restante = llenar_sobre(t_meta_renta, f_restante, v_restante)
f_transp, v_transp, f_restante, v_restante = llenar_sobre(t_meta_transp, f_restante, v_restante)
f_novia, v_novia, f_restante, v_restante = llenar_sobre(t_meta_novia, f_restante, v_restante)
f_viajes, v_viajes, f_restante, v_restante = llenar_sobre(t_meta_viajes, f_restante, v_restante)

# 4. Lo que sobre se va al bloque de Crecimiento con porcentajes puros
f_deuda = f_restante * P_DEUDA; v_deuda = v_restante * P_DEUDA
f_retiro = f_restante * P_RETIRO; v_retiro = v_restante * P_RETIRO
f_ocio = f_restante * P_OCIO; v_ocio = v_restante * P_OCIO
f_emerg = f_restante * P_EMERG; v_emerg = v_restante * P_EMERG
f_colchon = f_restante * P_COLCHON; v_colchon = v_restante * P_COLCHON

# ==========================================
# TOTALES EXACTOS
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

deficit_total = max(0.0, meta_inamovibles_total - (t_renta + t_transp + t_novia + t_viajes))
proyeccion = t_retiro * (((1 + (0.07 / 52))**(30 * 52)) - 1) / (0.07 / 52) if t_retiro > 0 else 0.0

# ==========================================
# MÉTRICAS VISUALES SUPERIORES
# ==========================================
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("NETO DISPONIBLE", f"${total_neto:,.2f}")
with c2: st.metric("CRECIMIENTO/AHORRO", f"${(t_emerg + t_colchon + t_deuda + t_ocio):,.2f}")
with c3: st.metric("PATRIMONIO PROYECTADO", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo:
        st.metric("ESTADO INAMOVIBLES", "CUBIERTOS ✅")
    elif (total_neto * 0.50) > meta_inamovibles_total:
        st.metric("ESTADO INAMOVIBLES", "EXPANDIDOS 🔥")
    elif deficit_total <= 0.01:
        st.metric("ESTADO INAMOVIBLES", "AL RAS ⚖️")
    else:
        st.metric("DÉFICIT INAMOVIBLES", f"-${deficit_total:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. TABLA ORIGINAL DE DESGLOSE (MATEMÁTICA)
# ==========================================
st.markdown("### 📊 DESGLOSE POR SOBRE")
df_data = [
    {"Sobre": "⛪ Diezmo", "Meta": "10%", "Fijo": f"${diezmo_fijo:,.2f}", "Variable": f"${diezmo_var:,.2f}", "Total": f"${t_diezmo:,.2f}", "Estado": "⚪ OK"},
    {"Sobre": "🏠 Renta", "Meta": f"${t_meta_renta:,.2f}", "Fijo": f"${f_renta:,.2f}", "Variable": f"${v_renta:,.2f}", "Total": f"${t_renta:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_renta>=t_meta_renta else f"🔴 -${t_meta_renta-t_renta:,.2f}")},
    {"Sobre": "🚗 Transporte", "Meta": f"${t_meta_transp:,.2f}", "Fijo": f"${f_transp:,.2f}", "Variable": f"${v_transp:,.2f}", "Total": f"${t_transp:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_transp>=t_meta_transp else f"🔴 -${t_meta_transp-t_transp:,.2f}")},
    {"Sobre": "💖 Novia", "Meta": f"${t_meta_novia:,.2f}", "Fijo": f"${f_novia:,.2f}", "Variable": f"${v_novia:,.2f}", "Total": f"${t_novia:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_novia>=t_meta_novia else f"🔴 -${t_meta_novia-t_novia:,.2f}")},
    {"Sobre": "✈️ Viajes", "Meta": f"${t_meta_viajes:,.2f}", "Fijo": f"${f_viajes:,.2f}", "Variable": f"${v_viajes:,.2f}", "Total": f"${t_viajes:,.2f}", "Estado": "🔵 Listo" if omitir_fijo else (f"🟢 OK" if t_viajes>=t_meta_viajes else f"🔴 -${t_meta_viajes-t_viajes:,.2f}")},
    {"Sobre": "💳 Deuda (30%)", "Meta": "Crecimiento", "Fijo": f"${f_deuda:,.2f}", "Variable": f"${v_deuda:,.2f}", "Total": f"${t_deuda:,.2f}", "Estado": "🔥 Acelerando"},
    {"Sobre": "🚨 Emergencias (20%)", "Meta": "Crecimiento", "Fijo": f"${f_emerg:,.2f}", "Variable": f"${v_emerg:,.2f}", "Total": f"${t_emerg:,.2f}", "Estado": "🛡️ OK"},
    {"Sobre": "🛌 Colchón (20%)", "Meta": "Crecimiento", "Fijo": f"${f_colchon:,.2f}", "Variable": f"${v_colchon:,.2f}", "Total": f"${t_colchon:,.2f}", "Estado": "🛡️ OK"},
    {"Sobre": "📈 Retiro (20%)", "Meta": "Crecimiento", "Fijo": f"${f_retiro:,.2f}", "Variable": f"${v_retiro:,.2f}", "Total": f"${t_retiro:,.2f}", "Estado": "🚀 S&P 500"},
    {"Sobre": "🍿 Ocio (10%)", "Meta": "Crecimiento", "Fijo": f"${f_ocio:,.2f}", "Variable": f"${v_ocio:,.2f}", "Total": f"${t_ocio:,.2f}", "Estado": "🎮 A disfrutar"}
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
