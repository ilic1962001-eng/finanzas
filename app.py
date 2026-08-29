import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# INICIALIZACIÓN DE MEMORIA (Para el reseteo)
# ==========================================
if 'fijo_val' not in st.session_state:
    st.session_state.fijo_val = 2329.0
if 'deduc_val' not in st.session_state:
    st.session_state.deduc_val = 0.0
if 'var_val' not in st.session_state:
    st.session_state.var_val = 1000.0
if 'exito_trigger' not in st.session_state:
    st.session_state.exito_trigger = False

def confirmar_deposito():
    # Activa la animación y resetea los inputs
    st.session_state.exito_trigger = True
    st.session_state.fijo_val = 0.0
    st.session_state.deduc_val = 0.0
    st.session_state.var_val = 0.0

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS "FINTECH PREMIUM"
# ==========================================
st.set_page_config(page_title="Flujo de Capital | Sistema O.S.", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit para modo "App Nativa" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fondo General Tecnológico */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #161b22 0%, #0d1117 100%);
        color: #c9d1d9;
    }

    /* Títulos Efecto Neón/Cyber */
    .titulo-pro {
        background: linear-gradient(to right, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 0px;
        padding-top: 20px;
    }
    
    .subtitulo {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 3px;
        margin-bottom: 40px;
        text-transform: uppercase;
    }

    /* Efecto Glassmorphism para las Tarjetas de Métricas */
    div[data-testid="metric-container"] {
        background: rgba(33, 38, 45, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 20px 25px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        border-top: 2px solid #4facfe;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-top 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(0, 242, 254, 0.2);
        border-top: 2px solid #00f2fe;
    }
    div[data-testid="metric-container"] label {
        color: #8b949e !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        font-family: 'Courier New', Courier, monospace; /* Fuente estilo Terminal/Trading */
    }

    /* Botón Tecnológico Principal */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #000000;
        font-weight: 900;
        font-size: 1.1rem;
        letter-spacing: 2px;
        padding: 18px 0;
        border: none;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.3);
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.6);
        color: #ffffff;
    }
    
    /* Pequeños ajustes a los Dataframes para que se vean integrados */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES FINANCIERAS
# ==========================================
DIEZMO_PCT = 0.10
OCIO_VAR_PCT = 0.10  # 10% DIRECTO del Ingreso Variable para disfrutar

# Proporciones de Crecimiento del resto del dinero
P_DEUDA = 0.30
P_RETIRO = 0.20
P_EMERG = 0.25
P_COLCHON = 0.25

META_RENTA = 1000.0
META_TRANSPORTE = 300.0
META_NOVIA = 300.0
META_VIAJES = 200.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

# ==========================================
# HEADER E INPUTS
# ==========================================
st.markdown("<div class='titulo-pro'>⚡ CAPITAL FLOW O.S.</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Motor de Distribución Algorítmica</div>", unsafe_allow_html=True)

with st.container():
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1:
        ingreso_fijo_bruto = st.number_input("💵 INGRESO FIJO NETO ($)", min_value=0.0, step=100.0, key="fijo_val")
    with c_in2:
        deducciones = st.number_input("✂️ DEDUCCIONES EXACTAS ($)", min_value=0.0, step=10.0, key="deduc_val")
    with c_in3:
        ingreso_var_bruto = st.number_input("📈 INGRESO VARIABLE NETO ($)", min_value=0.0, step=100.0, key="var_val")

    st.markdown("<br>", unsafe_allow_html=True)
    omitir_fijo = st.checkbox("🔐 OMITIR INGRESO FIJO (Mínimos ya cubiertos)", value=False)

st.markdown("---")

# ==========================================
# CEREBRO MATEMÁTICO (FONDO UNIFICADO)
# ==========================================
fijo_disponible = max(0.0, ingreso_fijo_bruto - deducciones)
total_ingreso_real = fijo_disponible + ingreso_var_bruto 

diezmo_fijo = fijo_disponible * DIEZMO_PCT if not omitir_fijo else 0.0
fijo_neto = fijo_disponible - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto_inicial = ingreso_var_bruto - diezmo_var

# 🔥 PREMIO DIRECTO: El Ocio toma el 10% del variable libre inmediatamente
v_ocio = var_neto_inicial * OCIO_VAR_PCT
f_ocio = 0.0  # Ya no toma del fijo
var_neto = var_neto_inicial - v_ocio  # Lo que queda del variable pasa a la cascada

total_neto_para_repartir = fijo_neto + var_neto 

if omitir_fijo:
    t_meta_renta = t_meta_transp = t_meta_novia = t_meta_viajes = 0.0
else:
    if (total_neto_para_repartir * 0.50) > meta_inamovibles_total:
        factor = (total_neto_para_repartir * 0.50) / meta_inamovibles_total
        t_meta_renta = META_RENTA * factor
        t_meta_transp = META_TRANSPORTE * factor
        t_meta_novia = META_NOVIA * factor
        t_meta_viajes = META_VIAJES * factor
    else:
        t_meta_renta = META_RENTA
        t_meta_transp = META_TRANSPORTE
        t_meta_novia = META_NOVIA
        t_meta_viajes = META_VIAJES

def llenar_sobre(meta, disp_fijo, disp_var):
    uso_fijo = min(meta, disp_fijo)
    disp_fijo -= uso_fijo
    
    faltante = meta - uso_fijo
    uso_var = min(faltante, disp_var)
    disp_var -= uso_var
    
    return uso_fijo, uso_var, disp_fijo, disp_var

f_restante = fijo_neto
v_restante = var_neto

f_renta, v_renta, f_restante, v_restante = llenar_sobre(t_meta_renta, f_restante, v_restante)
f_transp, v_transp, f_restante, v_restante = llenar_sobre(t_meta_transp, f_restante, v_restante)
f_novia, v_novia, f_restante, v_restante = llenar_sobre(t_meta_novia, f_restante, v_restante)
f_viajes, v_viajes, f_restante, v_restante = llenar_sobre(t_meta_viajes, f_restante, v_restante)

f_deuda = f_restante * P_DEUDA; v_deuda = v_restante * P_DEUDA
f_retiro = f_restante * P_RETIRO; v_retiro = v_restante * P_RETIRO
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
with c1: 
    st.metric("LIQUIDEZ NETA TOTAL", f"${total_ingreso_real:,.2f}")
with c2: 
    st.metric("CRECIMIENTO/AHORRO", f"${(t_emerg + t_colchon + t_deuda + t_ocio):,.2f}")
with c3: 
    st.metric("PATRIMONIO (30 AÑOS)", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo:
        st.metric("ESTATUS SISTEMA", "MÍNIMOS 100% ✅")
    elif (total_neto_para_repartir * 0.50) > meta_inamovibles_total:
        st.metric("ESTATUS SISTEMA", "ABUNDANCIA ACTIVA 🔥")
    elif deficit_total <= 0.01:
        st.metric("ESTATUS SISTEMA", "EQUILIBRIO ⚖️")
    else:
        st.metric("ALERTA DÉFICIT", f"-${deficit_total:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. TABLA ORIGINAL DE DESGLOSE (MATEMÁTICA)
# ==========================================
st.markdown("### 📊 MATRIZ DE DISTRIBUCIÓN")
df_data = [
    {"Sobre": "⛪ Diezmo", "Target": "10%", "Origen Fijo": f"${diezmo_fijo:,.2f}", "Origen Variable": f"${diezmo_var:,.2f}", "Total Asignado": f"${t_diezmo:,.2f}", "Status": "⚪ OK"},
    {"Sobre": "🏠 Renta", "Target": f"${t_meta_renta:,.2f}", "Origen Fijo": f"${f_renta:,.2f}", "Origen Variable": f"${v_renta:,.2f}", "Total Asignado": f"${t_renta:,.2f}", "Status": "🔵 Bloqueado" if omitir_fijo else (f"🟢 Cubierto" if t_renta>=t_meta_renta else f"🔴 -${t_meta_renta-t_renta:,.2f}")},
    {"Sobre": "🚗 Transporte", "Target": f"${t_meta_transp:,.2f}", "Origen Fijo": f"${f_transp:,.2f}", "Origen Variable": f"${v_transp:,.2f}", "Total Asignado": f"${t_transp:,.2f}", "Status": "🔵 Bloqueado" if omitir_fijo else (f"🟢 Cubierto" if t_transp>=t_meta_transp else f"🔴 -${t_meta_transp-t_transp:,.2f}")},
    {"Sobre": "💖 Novia", "Target": f"${t_meta_novia:,.2f}", "Origen Fijo": f"${f_novia:,.2f}", "Origen Variable": f"${v_novia:,.2f}", "Total Asignado": f"${t_novia:,.2f}", "Status": "🔵 Bloqueado" if omitir_fijo else (f"🟢 Cubierto" if t_novia>=t_meta_novia else f"🔴 -${t_meta_novia-t_novia:,.2f}")},
    {"Sobre": "✈️ Viajes", "Target": f"${t_meta_viajes:,.2f}", "Origen Fijo": f"${f_viajes:,.2f}", "Origen Variable": f"${v_viajes:,.2f}", "Total Asignado": f"${t_viajes:,.2f}", "Status": "🔵 Bloqueado" if omitir_fijo else (f"🟢 Cubierto" if t_viajes>=t_meta_viajes else f"🔴 -${t_meta_viajes-t_viajes:,.2f}")},
    {"Sobre": "💳 Deuda (30%)", "Target": "Variable", "Origen Fijo": f"${f_deuda:,.2f}", "Origen Variable": f"${v_deuda:,.2f}", "Total Asignado": f"${t_deuda:,.2f}", "Status": "🔥 Acelerado"},
    {"Sobre": "🚨 Emergencias (25%)", "Target": "Variable", "Origen Fijo": f"${f_emerg:,.2f}", "Origen Variable": f"${v_emerg:,.2f}", "Total Asignado": f"${t_emerg:,.2f}", "Status": "🛡️ Acumulando"},
    {"Sobre": "🛌 Colchón (25%)", "Target": "Variable", "Origen Fijo": f"${f_colchon:,.2f}", "Origen Variable": f"${v_colchon:,.2f}", "Total Asignado": f"${t_colchon:,.2f}", "Status": "🛡️ Acumulando"},
    {"Sobre": "📈 Retiro (20%)", "Target": "Variable", "Origen Fijo": f"${f_retiro:,.2f}", "Origen Variable": f"${v_retiro:,.2f}", "Total Asignado": f"${t_retiro:,.2f}", "Status": "🚀 S&P 500"},
    {"Sobre": "🍿 Ocio (Premio)", "Target": "10% Var.", "Origen Fijo": f"${f_ocio:,.2f}", "Origen Variable": f"${v_ocio:,.2f}", "Total Asignado": f"${t_ocio:,.2f}", "Status": "🎮 Libre"}
]
st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 2. NUEVA TABLA: GUÍA DE DEPÓSITOS CONSOLIDADOS
# ==========================================
st.markdown("### 🏦 ENRUTAMIENTO DE CAPITAL (Transferencias)")

t_nu_total = t_renta + t_transp + t_emerg + t_colchon

df_bancos = [
    {"Vector de Destino": "⛪ Diezmo", "Monto a Transferir": f"${t_diezmo:,.2f}", "Institución": "Revolut", "CLABE / Cuenta": "% %"},
    {"Vector de Destino": "🟣 Consolidado Nu (Renta, Transp, Emerg, Colchón)", "Monto a Transferir": f"${t_nu_total:,.2f}", "Institución": "Nu", "CLABE / Cuenta": "638180000126660124"},
    {"Vector de Destino": "📈 Retiro", "Monto a Transferir": f"${t_retiro:,.2f}", "Institución": "GBM", "CLABE / Cuenta": "601180400073884389"},
    {"Vector de Destino": "💳 Deuda", "Monto a Transferir": f"${t_deuda:,.2f}", "Institución": "Otra Cuenta", "CLABE / Cuenta": "% %"},
    {"Vector de Destino": "✈️ Viajes", "Monto a Transferir": f"${t_viajes:,.2f}", "Institución": "Otra Cuenta", "CLABE / Cuenta": "% %"},
    {"Vector de Destino": "💖 Novia", "Monto a Transferir": f"${t_novia:,.2f}", "Institución": "Apartado Libre", "CLABE / Cuenta": "% %"},
    {"Vector de Destino": "🍿 Ocio", "Monto a Transferir": f"${t_ocio:,.2f}", "Institución": "Cuenta Uso Diario", "CLABE / Cuenta": "% %"}
]
st.dataframe(pd.DataFrame(df_bancos), use_container_width=True, hide_index=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# BOTÓN DE ACCIÓN CON ANIMACIÓN, SONIDO Y RESET
# ==========================================
col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:
    st.button("🚀 EJECUTAR DISPERSIÓN DE CAPITAL", on_click=confirmar_deposito)

if st.session_state.exito_trigger:
    st.balloons()
    st.toast('Sistemas actualizados. Dispersión enviada a sobres.', icon='✅')
    
    # Audio forzado por JavaScript
    st.components.v1.html(
        """
        <audio id="kaching" src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg"></audio>
        <script>
            var audio = document.getElementById("kaching");
            audio.volume = 1.0;
            audio.play().catch(function(error) {
                console.log("Autoplay bloqueado por el navegador");
            });
        </script>
        """, 
        width=0, height=0
    )
    
    st.session_state.exito_trigger = False
