import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# INICIALIZACIÓN DE MEMORIA
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
    st.session_state.exito_trigger = True
    st.session_state.fijo_val = 0.0
    st.session_state.deduc_val = 0.0
    st.session_state.var_val = 0.0

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO "CLEAN"
# ==========================================
st.set_page_config(page_title="Gestión Financiera", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #f8f9fa;
        color: #2b2d42;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .titulo-pro {
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        padding-top: 10px;
    }
    
    .subtitulo {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        font-weight: 500;
        letter-spacing: 2px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4e4376;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="metric-container"] label {
        color: #6c757d !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2b2d42 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 15px 0;
        border: none;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(78, 67, 118, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 8px 15px rgba(78, 67, 118, 0.4);
        color: #ffffff;
    }
    
    .link-banco {
        display: inline-block;
        padding: 8px 15px;
        background-color: #e9ecef;
        color: #4e4376 !important;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: background 0.3s;
    }
    .link-banco:hover {
        background-color: #4e4376;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES FINANCIERAS
# ==========================================
DIEZMO_PCT = 0.10
OCIO_VAR_PCT = 0.10  

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
st.markdown("<div class='titulo-pro'>Distribución de Capital</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Finanzas con Mirsa 💡</div>", unsafe_allow_html=True)

with st.container():
    c_in1, c_in2, c_in3 = st.columns(3)
    with c_in1:
        ingreso_fijo_bruto = st.number_input("💵 Ingreso Fijo ($)", min_value=0.0, step=100.0, key="fijo_val")
    with c_in2:
        deducciones = st.number_input("✂️ Deducciones ($)", min_value=0.0, step=10.0, key="deduc_val")
    with c_in3:
        ingreso_var_bruto = st.number_input("📈 Ingreso Variable ($)", min_value=0.0, step=100.0, key="var_val")

    st.markdown("<br>", unsafe_allow_html=True)
    omitir_fijo = st.checkbox("✅ Omitir Ingreso Fijo (Gastos semanales ya cubiertos)", value=False)

st.markdown("---")

# ==========================================
# CEREBRO MATEMÁTICO 
# ==========================================
fijo_disponible = max(0.0, ingreso_fijo_bruto - deducciones)
total_ingreso_real = fijo_disponible + ingreso_var_bruto 

diezmo_fijo = fijo_disponible * DIEZMO_PCT if not omitir_fijo else 0.0
fijo_neto = fijo_disponible - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto_inicial = ingreso_var_bruto - diezmo_var

v_ocio = var_neto_inicial * OCIO_VAR_PCT
f_ocio = 0.0  
var_neto = var_neto_inicial - v_ocio  

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
    st.metric("💵 Liquidez Neta", f"${total_ingreso_real:,.2f}")
with c2: 
    st.metric("📈 Crecimiento / Ahorro", f"${(t_emerg + t_colchon + t_deuda + t_ocio):,.2f}")
with c3: 
    st.metric("🎯 Proyección (30 Años)", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo:
        st.metric("📌 Estado Fijos", "CUBIERTOS ✅")
    elif (total_neto_para_repartir * 0.50) > meta_inamovibles_total:
        st.metric("📌 Estado Fijos", "ÓPTIMO 🚀")
    elif deficit_total <= 0.01:
        st.metric("📌 Estado Fijos", "AL LÍMITE ⚖️")
    else:
        st.metric("⚠️ Déficit", f"-${deficit_total:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. TABLA ORIGINAL DE DESGLOSE
# ==========================================
st.markdown("<h3 style='color: #2b5876;'>📊 Desglose de Categorías</h3>", unsafe_allow_html=True)
df_data = [
    {"Categoría": "⛪ Diezmo", "Objetivo": "10%", "Fijo": f"${diezmo_fijo:,.2f}", "Variable": f"${diezmo_var:,.2f}", "Total": f"${t_diezmo:,.2f}", "Estado": "⚪ Listo"},
    {"Categoría": "🏠 Renta", "Objetivo": f"${t_meta_renta:,.2f}", "Fijo": f"${f_renta:,.2f}", "Variable": f"${v_renta:,.2f}", "Total": f"${t_renta:,.2f}", "Estado": "🔒 Bloqueado" if omitir_fijo else (f"✅ Cubierto" if t_renta>=t_meta_renta else f"⚠️ Faltan ${t_meta_renta-t_renta:,.0f}")},
    {"Categoría": "🚗 Transporte", "Objetivo": f"${t_meta_transp:,.2f}", "Fijo": f"${f_transp:,.2f}", "Variable": f"${v_transp:,.2f}", "Total": f"${t_transp:,.2f}", "Estado": "🔒 Bloqueado" if omitir_fijo else (f"✅ Cubierto" if t_transp>=t_meta_transp else f"⚠️ Faltan ${t_meta_transp-t_transp:,.0f}")},
    {"Categoría": "💡 Novia", "Objetivo": f"${t_meta_novia:,.2f}", "Fijo": f"${f_novia:,.2f}", "Variable": f"${v_novia:,.2f}", "Total": f"${t_novia:,.2f}", "Estado": "🔒 Bloqueado" if omitir_fijo else (f"✅ Cubierto" if t_novia>=t_meta_novia else f"⚠️ Faltan ${t_meta_novia-t_novia:,.0f}")},
    {"Categoría": "✈️ Viajes", "Objetivo": f"${t_meta_viajes:,.2f}", "Fijo": f"${f_viajes:,.2f}", "Variable": f"${v_viajes:,.2f}", "Total": f"${t_viajes:,.2f}", "Estado": "🔒 Bloqueado" if omitir_fijo else (f"✅ Cubierto" if t_viajes>=t_meta_viajes else f"⚠️ Faltan ${t_meta_viajes-t_viajes:,.0f}")},
    {"Categoría": "💳 Deuda (30%)", "Objetivo": "Variable", "Fijo": f"${f_deuda:,.2f}", "Variable": f"${v_deuda:,.2f}", "Total": f"${t_deuda:,.2f}", "Estado": "🔥 Reduciendo"},
    {"Categoría": "🚨 Emergencias (25%)", "Objetivo": "Variable", "Fijo": f"${f_emerg:,.2f}", "Variable": f"${v_emerg:,.2f}", "Total": f"${t_emerg:,.2f}", "Estado": "🛡️ Acumulando"},
    {"Categoría": "🛌 Colchón (25%)", "Objetivo": "Variable", "Fijo": f"${f_colchon:,.2f}", "Variable": f"${v_colchon:,.2f}", "Total": f"${t_colchon:,.2f}", "Estado": "🛡️ Acumulando"},
    {"Categoría": "📈 Retiro (20%)", "Objetivo": "Variable", "Fijo": f"${f_retiro:,.2f}", "Variable": f"${v_retiro:,.2f}", "Total": f"${t_retiro:,.2f}", "Estado": "🚀 S&P 500"},
    {"Categoría": "🍿 Ocio", "Objetivo": "10% Var.", "Fijo": f"${f_ocio:,.2f}", "Variable": f"${v_ocio:,.2f}", "Total": f"${t_ocio:,.2f}", "Estado": "🎮 Disponible"}
]
st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 2. GUÍA DE DEPÓSITOS (UI INTERACTIVA CON CLABES Y LINKS)
# ==========================================
st.markdown("<h3 style='color: #2b5876;'>🏦 Guía de Transferencias</h3>", unsafe_allow_html=True)

# Acceso rápido a la Central
st.markdown("<div style='text-align: center; margin-bottom: 25px;'><a href='https://banco.hey.inc/' target='_blank' class='link-banco'>🌐 Abrir Hey Banco (Central)</a></div>", unsafe_allow_html=True)

# Sumas Consolidadas
t_nu_operativo = t_renta + t_transp
t_revolut_rendimiento = t_diezmo + t_emerg + t_colchon
t_santander = t_deuda + t_ocio
t_spin = t_viajes
t_hey = t_novia

destinos = [
    {"Nombre": "⚫ Revolut (Diezmo, Emergencias, Colchón)", "Monto": t_revolut_rendimiento, "CLABE": "646990404064534378", "Link": "https://app.revolut.com/"},
    {"Nombre": "🟣 Nu (Renta, Transporte)", "Monto": t_nu_operativo, "CLABE": "638180000126660124", "Link": "https://app.nu.com.mx/"},
    {"Nombre": "📈 GBM (Retiro S&P 500)", "Monto": t_retiro, "CLABE": "601180400073884389", "Link": "https://app.gbm.com/"},
    {"Nombre": "🔴 Santander LikeU (Deuda, Ocio)", "Monto": t_santander, "CLABE": "014180140158246414", "Link": "https://www.santander.com.mx/"},
    {"Nombre": "🏪 Spin by Oxxo (Viajes)", "Monto": t_spin, "CLABE": "728969000033664690", "Link": "https://spinbyoxxo.com.mx/"},
    {"Nombre": "🔵 Hey Banco (Novia)", "Monto": t_hey, "CLABE": "APARTADO INTERNO", "Link": "https://banco.hey.inc/"}
]

# Diseño de lista de transferencias interactiva
for d in destinos:
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
        col1.markdown(f"<div style='font-size: 1.1rem; font-weight: 600; color: #2b2d42; margin-top: 10px;'>{d['Nombre']}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='font-size: 1.4rem; font-weight: 800; color: #4e4376; margin-top: 5px;'>${d['Monto']:,.2f}</div>", unsafe_allow_html=True)
        
        with col3:
            if d['CLABE'] != "APARTADO INTERNO":
                st.code(d['CLABE'], language="text")
            else:
                st.markdown("<div style='margin-top: 10px; color: #6c757d; font-style: italic;'>Sin CLABE (Traspaso interno)</div>", unsafe_allow_html=True)
                
        col4.markdown(f"<div style='margin-top: 10px;'><a href='{d['Link']}' target='_blank' class='link-banco'>Abrir App</a></div>", unsafe_allow_html=True)
        
    st.markdown("<hr style='margin: 0.5em 0; border: 0.5px solid #e9ecef;'>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BOTÓN DE ACCIÓN Y SONIDO
# ==========================================
col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:
    st.button("🚀 CONFIRMAR TRANSFERENCIAS", on_click=confirmar_deposito)

if st.session_state.exito_trigger:
    st.balloons()
    st.toast('Distribución completada correctamente.', icon='✅')
    
    st.components.v1.html(
        '''
        <iframe src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg" allow="autoplay" style="display:none" id="iframeAudio">
        </iframe>
        <audio autoplay="true" src="https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg"></audio>
        <script>
            var audio = new Audio('https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg');
            audio.play().catch(function(error) {
                console.log("Autoplay bloqueado por el navegador: ", error);
            });
        </script>
        ''', 
        width=0, height=0
    )
    
    st.session_state.exito_trigger = False
