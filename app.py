import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

# TÍTULO PERSONALIZADO: ROJO, MAYÚSCULAS Y ESTILIZADO
st.markdown("""
    <style>
    .titulo-personalizado {
        color: #FF0000;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding-bottom: 20px;
    }
    </style>
    <h1 class="titulo-personalizado">¿CUÁNTO TE PAGARON ILICH?</h1>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# EL RESTO DE TU CÓDIGO (ENTRADA DE DATOS...)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
# ... continúa el código anterior
# ==========================================
# CONSTANTES Y CLABES
# ==========================================
# Configuración de Porcentajes
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65
DEUDA_PCT = 0.10
AHORRO_PCT = 0.10
INVERSION_PCT = 0.15

# Metas Inamovibles Hardcoded
META_RENTA = 875.0
META_TRANSPORTE = 430.0
META_NOVIA = 500.0
META_VIAJES = 300.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

# 🏦 TUS CLABES REALES
CUENTAS = {
    "NU (Cajita)": "638180000126660124",
    "NU (Gasto)": "638180000126660124",
    "GBM+": "601180400073884389",
    "SPIN": "728969000033664690",
    "Cuenta Diezmo": "PENDIENTE",
    "Pago Deuda": "PENDIENTE",
    "CETES": "PENDIENTE"
}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#d4af37;'>Capital Semanal</h3>", unsafe_allow_html=True)
    ingreso_fijo_bruto = st.number_input("FIJO ($)", min_value=0.0, value=0.0, step=100.0)
    ingreso_var_bruto = st.number_input("VARIABLE ($)", min_value=0.0, value=0.0, step=100.0)

# ==========================================
# LÓGICA (BACKEND)
# ==========================================
# Diezmos
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

# Inicialización
f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

# Distribución FIJO
capacidad_gasto_fijo = fijo_neto * GASTO_PCT
if capacidad_gasto_fijo >= meta_inamovibles_total:
    p_renta, p_transp = META_RENTA/meta_inamovibles_total, META_TRANSPORTE/meta_inamovibles_total
    p_novia, p_viajes = META_NOVIA/meta_inamovibles_total, META_VIAJES/meta_inamovibles_total
    f_renta, f_transp = capacidad_gasto_fijo*p_renta, capacidad_gasto_fijo*p_transp
    f_novia, f_viajes = capacidad_gasto_fijo*p_novia, capacidad_gasto_fijo*p_viajes
    f_deuda, f_retiro = fijo_neto*DEUDA_PCT, fijo_neto*INVERSION_PCT
    f_emerg, f_colchon = (fijo_neto*AHORRO_PCT)*0.5, (fijo_neto*AHORRO_PCT)*0.5
    modo_actual = "Crecimiento"
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
    modo_actual = "Cascada"

# Distribución VARIABLE (Rescate + 50/30/20)
v_aux = var_neto
v_renta = min(v_aux, max(0, META_RENTA - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0, META_NOVIA - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0, META_VIAJES - f_viajes)); v_aux -= v_viajes

if v_aux > 0:
    v_ahorro_t = v_aux * 0.50
    v_deuda, v_retiro = v_aux * 0.30, v_aux * 0.20
    v_emerg, v_colchon = v_ahorro_t * 0.50, v_ahorro_t * 0.50

# Dataframe
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
# FRONTEND
# ==========================================
m1, m2, m3 = st.columns(3)
with m1: st.metric("NETO SEMANAL", f"${(fijo_neto + var_neto):,.2f}")
with m2: st.metric("SISTEMA", modo_actual)
with m3: st.metric("PROFIT GENERADO", f"${df['Profit'].sum():,.2f}")

st.markdown("---")

# Tabla con Estilo Dorado Forzado y Letras Blancas
st.subheader("Desglose de Capital")
def style_table(val):
    if isinstance(val, (int, float)) and val > 0: return 'color: #d4af37'
    return 'color: #ffffff'

st.dataframe(
    df.style.format({"Meta": "${:,.2f}", "Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}", "Profit": "${:,.2f}"})
    .map(style_table, subset=["Profit"])
    .set_properties(**{'background-color': '#000000', 'color': '#ffffff', 'border-color': '#d4af3722'}),
    use_container_width=True, hide_index=True
)

st.markdown("---")

# Transferencias y Gráfico
c1, c_esp, c2 = st.columns([1, 0.1, 1.2])

with c1:
    st.subheader("🏦 CLABEs (Copiables)")
    df_bancos = df.groupby("Plataforma")["Total"].sum().reset_index()
    df_bancos = df_bancos[df_bancos["Total"] > 0]
    
    for _, row in df_bancos.iterrows():
        banco = row["Plataforma"]
        monto = row["Total"]
        clabe_nuda = CUENTAS.get(banco, "PENDIENTE")
        
        st.markdown(f"<p style='margin-bottom:0px; font-weight:600; color:#d4af37;'>{banco}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.2rem; margin-top:0px;'>Total: <b>${monto:,.2f}</b></p>", unsafe_allow_html=True)
        # ÚNICAMENTE LA CLABE ES COPIABLE
        st.code(clabe_nuda, language=None)
        st.markdown("<br>", unsafe_allow_html=True)

with c2:
    st.subheader("Distribución Visual")
    fig = px.pie(df_bancos, values='Total', names='Plataforma', hole=0.7,
                 color_discrete_sequence=['#d4af37', '#ffffff', '#444444', '#888888'])
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#ffffff")
    )
    st.plotly_chart(fig, use_container_width=True)
