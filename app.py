import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

st.title("📊 Control Financiero: Distribución Dinámica")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

# Parámetros de distribución fija
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65   # Renta, Novia, Viajes, Transporte
DEUDA_PCT = 0.10   # Deuda
AHORRO_PCT = 0.10  # Emergencias (50%) y Colchón (50%)
INVERSION_PCT = 0.15 # Retiro / Reinversión

# Metas mínimas (Inamovibles)
meta_renta = 875.0
meta_transporte = 430.0
meta_novia = 500.0
meta_viajes = 300.0
meta_inamovibles_total = meta_renta + meta_transporte + meta_novia + meta_viajes

st.sidebar.markdown("---")
st.sidebar.info(f"**Umbral de Desbloqueo:** Para activar la distribución completa del 65%, necesitas un ingreso fijo neto de **${(meta_inamovibles_total / GASTO_PCT):,.2f}**")

# ==========================================
# LÓGICA DE DISTRIBUCIÓN FIJA
# ==========================================
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo

# Inicialización de variables de salida
f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0

# ¿El 65% del ingreso neto actual alcanza para cubrir las metas mínimas?
capacidad_gasto_real = fijo_neto * GASTO_PCT

if capacidad_gasto_real >= meta_inamovibles_total and ingreso_fijo_bruto > 0:
    # ESCENARIO A: DISTRIBUCIÓN PORCENTUAL (DINERO SOBRANTE)
    # El dinero se reparte según tus porcentajes originales porque ya cubriste el mínimo
    st.success(f"🚀 **Distribución Desbloqueada:** El ingreso fijo cubre las metas. Repartiendo el 65% total en gastos.")
    
    # Reparto proporcional de los gastos (se "engordan" los sobres)
    # Calculamos cuánto le toca a cada uno basado en su peso relativo sobre el total de metas
    f_renta = capacidad_gasto_real * (meta_renta / meta_inamovibles_total)
    f_transp = capacidad_gasto_real * (meta_transporte / meta_inamovibles_total)
    f_novia = capacidad_gasto_real * (meta_novia / meta_inamovibles_total)
    f_viajes = capacidad_gasto_real * (meta_viajes / meta_inamovibles_total)
    
    # Resto de la distribución fija
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.50
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.50
    f_retiro = fijo_neto * INVERSION_PCT

else:
    # ESCENARIO B: CASCADA DE EMERGENCIA (NO ALCANZA EL 65%)
    # Prioridad absoluta a llenar las metas inamovibles una por una
    if ingreso_fijo_bruto > 0:
        st.warning("⚠️ **Modo Cascada:** El ingreso fijo no llega al umbral del 65%. Cubriendo huecos por prioridad.")
    
    f_aux = fijo_neto
    f_renta = min(f_aux, meta_renta); f_aux -= f_renta
    f_transp = min(f_aux, meta_transporte); f_aux -= f_transp
    f_novia = min(f_aux, meta_novia); f_aux -= f_novia
    f_viajes = min(f_aux, meta_viajes); f_aux -= f_viajes
    
    # Lo que sobre (si sobra algo antes de llegar al umbral) se va a deuda y ahorro
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux

# ==========================================
# LÓGICA DE RESCATE (INGRESO VARIABLE)
# ==========================================
# El ingreso variable SOLO actúa si el FIJO no cubrió las metas mínimas
faltante_inamov = max(0, meta_inamovibles_total - (f_renta + f_transp + f_novia + f_viajes))
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

v_rescate = 0
if faltante_inamov > 0 and var_neto > 0:
    v_rescate = min(faltante_inamov, var_neto)
    st.info(f"🆘 **Rescate Variable:** Se usaron ${v_rescate:,.2f} para completar mínimos inamovibles.")

var_disponible = var_neto - v_rescate

# Distribución del resto del variable (50/30/20 como regla general para extras)
v_deuda = v_emerg = v_colchon = v_retiro = 0
if var_disponible > 0:
    v_ahorro_bolsa = var_disponible * 0.50
    v_deuda = var_disponible * 0.30
    v_retiro_extra = var_disponible * 0.20
    
    v_emerg = v_ahorro_bolsa * 0.50
    v_colchon = v_ahorro_bolsa * 0.50
    v_retiro = v_retiro_extra

# ==========================================
# CONSTRUCCIÓN DE DATOS PARA TABLAS
# ==========================================
# Reparto del rescate variable en los huecos de los gastos
rescate_aux = v_rescate
r_renta = min(meta_renta - f_renta, rescate_aux); rescate_aux -= r_renta
r_transp = min(meta_transporte - f_transp, rescate_aux); rescate_aux -= r_transp
r_novia = min(meta_novia - f_novia, rescate_aux); rescate_aux -= r_novia
r_viajes = min(meta_viajes - f_viajes, rescate_aux); rescate_aux -= r_viajes

detalles = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Fijo": f_renta, "Variable": r_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Fijo": f_transp, "Variable": r_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Fijo": f_novia, "Variable": r_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Fijo": f_viajes, "Variable": r_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Fijo": f_retiro, "Variable": v_retiro},
]

df_detalles = pd.DataFrame(detalles)
df_detalles["Total"] = df_detalles["Fijo"] + df_detalles["Variable"]

# ==========================================
# UI: DASHBOARD
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Ingreso Fijo Neto", f"${fijo_neto:,.2f}")
col2.metric("Gasto Operativo (65%)", f"${(f_renta + f_transp + f_novia + f_viajes):,.2f}")
col3.metric("Ahorro/Inv (25%)", f"${(f_emerg + f_colchon + f_retiro):,.2f}")

st.markdown("---")
st.subheader("💳 Resumen de Transferencias")
df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

with st.expander("📝 Detalle de Movimientos (Fijo vs Variable)"):
    st.dataframe(df_detalles.style.format({"Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}"}), use_container_width=True)

# Gráfico de Cubetas
st.subheader("💧 Estado de las Cubetas")
df_bar = pd.DataFrame({
    'Cubeta': df_detalles['Concepto'][1:8],
    'Nivel Real': df_detalles['Total'][1:8],
    'Meta Mínima': [meta_renta, meta_transporte, meta_novia, meta_viajes, 400, 250, 250]
})
fig = px.bar(df_bar, x='Cubeta', y=['Meta Mínima', 'Nivel Real'], barmode='group', color_discrete_sequence=['#CBD5E0', '#3182CE'])
st.plotly_chart(fig, use_container_width=True)
