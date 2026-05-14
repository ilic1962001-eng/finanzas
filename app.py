import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN PREMIUM Y ESTILOS
# ==========================================
st.set_page_config(page_title="Control Financiero", layout="wide")

# Inyección de CSS para Tema Black & Gold
st.markdown("""
    <style>
    /* Fondo general oscuro */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* Títulos y subtítulos en dorado */
    h1, h2, h3, h4, h5, h6 {
        color: #d4af37 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Barra lateral oscuro carbón */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #332a0d;
    }
    
    /* Cajas de métricas */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 2.5rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="metric-container"] {
        background-color: #171717;
        border: 1px solid #332a0d;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.05);
    }
    
    /* Separadores dorados tenues */
    hr {
        border-color: #d4af37 !important;
        opacity: 0.2;
        margin-top: 40px;
        margin-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Control Financiero: Cascada Pro")
st.markdown("---")

# ==========================================
# PARÁMETROS DEL SISTEMA Y METAS CONSTANTES
# ==========================================
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65
DEUDA_PCT = 0.10
AHORRO_PCT = 0.10
INVERSION_PCT = 0.15

# Metas Mínimas Inamovibles (Hardcoded)
META_RENTA = 875.0
META_TRANSPORTE = 430.0
META_NOVIA = 500.0
META_VIAJES = 300.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

# ==========================================
# SIDEBAR - ENTRADA DE DATOS
# ==========================================
with st.sidebar:
    st.header("Flujo de Efectivo")
    st.markdown("<br>", unsafe_allow_html=True)
    ingreso_fijo_bruto = st.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
    st.markdown("<br>", unsafe_allow_html=True)
    ingreso_var_bruto = st.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

# ==========================================
# LÓGICA DE CÁLCULO (BACKEND)
# ==========================================
# 1. Diezmos
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo

diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

# Inicialización de Sobres
f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

# --- PROCESAMIENTO DEL INGRESO FIJO ---
capacidad_gasto_fijo = fijo_neto * GASTO_PCT

if capacidad_gasto_fijo >= meta_inamovibles_total:
    # MODO DESBLOQUEADO: Crecimiento proporcional
    p_renta = META_RENTA / meta_inamovibles_total
    p_transp = META_TRANSPORTE / meta_inamovibles_total
    p_novia = META_NOVIA / meta_inamovibles_total
    p_viajes = META_VIAJES / meta_inamovibles_total

    f_renta = capacidad_gasto_fijo * p_renta
    f_transp = capacidad_gasto_fijo * p_transp
    f_novia = capacidad_gasto_fijo * p_novia
    f_viajes = capacidad_gasto_fijo * p_viajes
    
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.50
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.50
    f_retiro = fijo_neto * INVERSION_PCT
    modo_actual = "Crecimiento Proporcional"
else:
    # MODO CASCADA: Rellenando huecos
    f_aux = fijo_neto
    f_renta = min(f_aux, META_RENTA); f_aux -= f_renta
    f_transp = min(f_aux, META_TRANSPORTE); f_aux -= f_transp
    f_novia = min(f_aux, META_NOVIA); f_aux -= f_novia
    f_viajes = min(f_aux, META_VIAJES); f_aux -= f_viajes
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux
    modo_actual = "Cascada (Prioridad Mínimos)"

# --- PROCESAMIENTO DEL INGRESO VARIABLE (RESCATE + 50/30/20) ---
v_aux = var_neto

v_renta = min(v_aux, max(0, META_RENTA - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0, META_NOVIA - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0, META_VIAJES - f_viajes)); v_aux -= v_viajes

if v_aux > 0:
    v_ahorro_total = v_aux * 0.50
    v_deuda = v_aux * 0.30
    v_retiro = v_aux * 0.20
    
    v_emerg = v_ahorro_total * 0.50
    v_colchon = v_ahorro_total * 0.50

# ==========================================
# CONSTRUCCIÓN DE LA TABLA Y CÁLCULO DE PROFIT
# ==========================================
data = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Meta": 0, "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Meta": META_RENTA, "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Meta": META_TRANSPORTE, "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Meta": META_NOVIA, "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Meta": META_VIAJES, "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Meta": 0, "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Meta": 0, "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Meta": 0, "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Meta": 0, "Fijo": f_retiro, "Variable": v_retiro},
]

df = pd.DataFrame(data)
df["Total"] = df["Fijo"] + df["Variable"]
df["Profit"] = df.apply(lambda x: max(0, x["Total"] - x["Meta"]) if x["Meta"] > 0 else 0, axis=1)

# ==========================================
# VISUALIZACIÓN FRONTEND
# ==========================================

# --- ALERTA DE DÉFICIT ---
if (fijo_neto + var_neto) < meta_inamovibles_total and (ingreso_fijo_bruto + ingreso_var_bruto) > 0:
    faltante = meta_inamovibles_total - (fijo_neto + var_neto)
    st.error(f"DÉFICIT DETECTADO: Faltan ${faltante:,.2f} para cubrir las metas inamovibles.")
    st.markdown("<br>", unsafe_allow_html=True)

# --- PANEL DE MÉTRICAS (Distribuido y amplio) ---
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Neto Semanal", f"${(fijo_neto + var_neto):,.2f}")
with m2:
    st.metric("Estado del Sistema", modo_actual)
with m3:
    total_profit = df["Profit"].sum()
    st.metric("Profit Total (Excedente)", f"${total_profit:,.2f}")

st.markdown("---")

# --- TABLA PRINCIPAL A ANCHO COMPLETO ---
st.subheader("Desglose de Asignación")
st.markdown("<br>", unsafe_allow_html=True)

# Resaltado sutil en dorado para el profit usando Pandas Styler
def style_profit(val):
    color = '#d4af37' if isinstance(val, (int, float)) and val > 0 else '#e0e0e0'
    return f'color: {color}'

st.dataframe(
    df.style.format({
        "Meta": "${:,.2f}", "Fijo": "${:,.2f}", 
        "Variable": "${:,.2f}", "Total": "${:,.2f}", "Profit": "${:,.2f}"
    }).map(style_profit, subset=["Profit"]),
    use_container_width=True,
    hide_index=True,
    height=350 # Le da más espacio vertical a la tabla
)

st.markdown("---")

# --- DISTRIBUCIÓN POR BANCO Y GRÁFICO (Lado a Lado con mucho respiro) ---
c1, c_espacio, c2 = st.columns([1, 0.2, 1])

df_bancos = df.groupby("Plataforma")["Total"].sum().reset_index()

with c1:
    st.subheader("Transferencias Requeridas")
    st.markdown("<br>", unsafe_allow_html=True)
    # Mostramos los bancos como métricas verticales grandes
    for _, row in df_bancos.iterrows():
        st.metric(row["Plataforma"], f"${row['Total']:,.2f}")
        
with c2:
    st.subheader("Proporción por Destino")
    # Gráfico adaptado al tema oscuro y paleta dorada/tierra
    colores_premium = ['#d4af37', '#aa8c2c', '#ebd57d', '#66541a', '#8a7322', '#f2df96']
    fig = px.pie(
        df_bancos, 
        values='Total', 
        names='Plataforma', 
        hole=0.6,
        color_discrete_sequence=colores_premium
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=0, r=0),
        font=dict(color='#a0a0a0', size=14),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
