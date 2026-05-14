import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN PREMIUM Y ESTILOS
# ==========================================
st.set_page_config(page_title="Waterfall Pro | Financial Dashboard", layout="wide", page_icon="💎")

# Inyección de CSS para un look Premium
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
    }
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
    }
    h1, h2, h3 {
        color: #1a202c;
        font-family: 'Inter', sans-serif;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 Control Financiero: Cascada Pro")
st.markdown("---")

# ==========================================
# SIDEBAR - ENTRADA DE DATOS
# ==========================================
with st.sidebar:
    st.header("💰 Flujo de Efectivo")
    ingreso_fijo_bruto = st.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
    ingreso_var_bruto = st.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)
    
    st.divider()
    st.header("🎯 Metas Inamovibles")
    m_renta = st.number_input("Meta Renta", value=875.0)
    m_transp = st.number_input("Meta Transporte", value=430.0)
    m_novia = st.number_input("Meta Novia", value=500.0)
    m_viajes = st.number_input("Meta Viajes", value=300.0)
    
    meta_inamovibles_total = m_renta + m_transp + m_novia + m_viajes

# Constantes de Distribución
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65
DEUDA_PCT = 0.10
AHORRO_PCT = 0.10
INVERSION_PCT = 0.15

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
    p_renta = m_renta / meta_inamovibles_total
    p_transp = m_transp / meta_inamovibles_total
    p_novia = m_novia / meta_inamovibles_total
    p_viajes = m_viajes / meta_inamovibles_total

    f_renta = capacidad_gasto_fijo * p_renta
    f_transp = capacidad_gasto_fijo * p_transp
    f_novia = capacidad_gasto_fijo * p_novia
    f_viajes = capacidad_gasto_fijo * p_viajes
    
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.50
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.50
    f_retiro = fijo_neto * INVERSION_PCT
    modo_actual = "🚀 Crecimiento Proporcional"
else:
    # MODO CASCADA: Rellenando huecos
    f_aux = fijo_neto
    f_renta = min(f_aux, m_renta); f_aux -= f_renta
    f_transp = min(f_aux, m_transp); f_aux -= f_transp
    f_novia = min(f_aux, m_novia); f_aux -= f_novia
    f_viajes = min(f_aux, m_viajes); f_aux -= f_viajes
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux
    modo_actual = "⚠️ Cascada (Prioridad Mínimos)"

# --- PROCESAMIENTO DEL INGRESO VARIABLE (RESCATE + 50/30/20) ---
v_aux = var_neto

# 1. Rescate de inamovibles (si el fijo no alcanzó)
v_renta = min(v_aux, max(0, m_renta - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0, m_transp - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0, m_novia - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0, m_viajes - f_viajes)); v_aux -= v_viajes

# 2. Distribución de excedente (50/30/20)
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
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Meta": m_renta, "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Meta": m_transp, "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Meta": m_novia, "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Meta": m_viajes, "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Meta": 0, "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Meta": 0, "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Meta": 0, "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Meta": 0, "Fijo": f_retiro, "Variable": v_retiro},
]

df = pd.DataFrame(data)
df["Total"] = df["Fijo"] + df["Variable"]
df["Profit"] = df.apply(lambda x: max(0, x["Total"] - x["Meta"]) if x["Meta"] > 0 else 0, axis=1)

# ==========================================
# VISUALIZACIÓN FRONtend
# ==========================================

# Fila 1: Métricas Principales
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Neto Semanal", f"${(fijo_neto + var_neto):,.2f}")
with m2:
    st.metric("Estado de Gastos", modo_actual)
with m3:
    total_profit = df["Profit"].sum()
    st.metric("Profit Total (Excedente)", f"${total_profit:,.2f}", delta=f"{total_profit:,.2f}")
with m4:
    total_var_excedente = v_aux
    st.metric("Var. 50/30/20 Disponible", f"${total_var_excedente:,.2f}")

# Fila 2: Tabla de Transferencias y Gráfico
c1, c2 = st.columns([1.2, 0.8])

with c1:
    st.subheader("📋 Desglose de Asignación")
    # Estilizado condicional para Profit
    def highlight_profit(s):
        return ['background-color: #e6fffa' if v > 0 else '' for v in s]
    
    st.dataframe(
        df.style.format({
            "Meta": "${:,.2f}", "Fijo": "${:,.2f}", 
            "Variable": "${:,.2f}", "Total": "${:,.2f}", "Profit": "${:,.2f}"
        }).apply(highlight_profit, subset=["Profit"]),
        use_container_width=True,
        hide_index=True
    )

with c2:
    st.subheader("📊 Distribución por Banco")
    df_bancos = df.groupby("Plataforma")["Total"].sum().reset_index()
    fig = px.pie(df_bancos, values='Total', names='Plataforma', hole=0.5,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# Fila 3: Transferencias Rápidas
st.subheader("💳 Transferencias Requeridas (Resumen)")
cols = st.columns(len(df_bancos))
for i, row in df_bancos.iterrows():
    cols[i].metric(row["Plataforma"], f"${row['Total']:,.2f}")

# Alerta de Déficit (si aplica)
if (fijo_neto + var_neto) < meta_inamovibles_total and (ingreso_fijo_bruto + ingreso_var_bruto) > 0:
    faltante = meta_inamovibles_total - (fijo_neto + var_neto)
    st.error(f"🚨 **DÉFICIT CRÍTICO:** Te faltan **${faltante:,.2f}** para cubrir tus metas mínimas inamovibles.")
