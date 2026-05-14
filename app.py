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

# Parámetros de distribución fija (Tus porcentajes de presupuesto)
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65   # Cubre Renta, Novia, Viajes, Transporte
DEUDA_PCT = 0.10   
AHORRO_PCT = 0.10  
INVERSION_PCT = 0.15 

# Metas mínimas (Inamovibles)
meta_renta = 875.0
meta_transporte = 430.0
meta_novia = 500.0
meta_viajes = 300.0
meta_inamovibles_total = meta_renta + meta_transporte + meta_novia + meta_viajes

# ==========================================
# PROCESAMIENTO INICIAL
# ==========================================
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo

diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

# Inicialización de variables
f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

# ==========================================
# 1. ALERTAS DE UMBRAL (BANNER DE ENTRADA)
# ==========================================
total_disponible_para_gastos = (fijo_neto * GASTO_PCT) + var_neto

if total_disponible_para_gastos < meta_inamovibles_total and (ingreso_fijo_bruto + ingreso_var_bruto) > 0:
    faltante = meta_inamovibles_total - total_disponible_para_gastos
    st.error(f"❌ **ALERTA DE DÉFICIT:** Te faltan **${faltante:,.2f}** para cubrir tus gastos inamovibles mínimos.")
elif ingreso_fijo_bruto > 0:
    st.success(f"✅ **SISTEMA SALUDABLE:** Cubriendo mínimos y distribuyendo excedentes.")

# ==========================================
# 2. LÓGICA DE DISTRIBUCIÓN
# ==========================================
capacidad_gasto_fijo = fijo_neto * GASTO_PCT

if capacidad_gasto_fijo >= meta_inamovibles_total:
    # ESCENARIO: DISTRIBUCIÓN PORCENTUAL (EL "DESBLOQUEO")
    # Gastos
    f_renta = capacidad_gasto_fijo * (meta_renta / meta_inamovibles_total)
    f_transp = capacidad_gasto_fijo * (meta_transporte / meta_inamovibles_total)
    f_novia = capacidad_gasto_fijo * (meta_novia / meta_inamovibles_total)
    f_viajes = capacidad_gasto_fijo * (meta_viajes / meta_inamovibles_total)
    # Resto
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.50
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.50
    f_retiro = fijo_neto * INVERSION_PCT
else:
    # ESCENARIO: CASCADA (RELLENO DE HUECOS)
    f_aux = fijo_neto
    f_renta = min(f_aux, meta_renta); f_aux -= f_renta
    f_transp = min(f_aux, meta_transporte); f_aux -= f_transp
    f_novia = min(f_aux, meta_novia); f_aux -= f_novia
    f_viajes = min(f_aux, meta_viajes); f_aux -= f_viajes
    # El resto del fijo a los otros rubros
    f_deuda = min(f_aux, 400); f_aux -= f_deuda
    f_emerg = min(f_aux, 250); f_aux -= f_emerg
    f_colchon = min(f_aux, 250); f_aux -= f_colchon
    f_retiro = f_aux

# ==========================================
# 3. USO DEL INGRESO VARIABLE (RESCATE O EXCESO)
# ==========================================
faltante_tras_fijo_renta = meta_renta - f_renta
faltante_tras_fijo_transp = meta_transporte - f_transp
faltante_tras_fijo_novia = meta_novia - f_novia
faltante_tras_fijo_viajes = meta_viajes - f_viajes

v_aux = var_neto

# Primero rescatamos inamovibles si el fijo no llegó
v_renta = min(v_aux, faltante_tras_fijo_renta); v_aux -= v_renta
v_transp = min(v_aux, faltante_tras_fijo_transp); v_aux -= v_transp
v_novia = min(v_aux, faltante_tras_fijo_novia); v_aux -= v_novia
v_viajes = min(v_aux, faltante_tras_fijo_viajes); v_aux -= v_viajes

# Si sobra variable, se va a la regla 50/30/20 para acelerar metas
if v_aux > 0:
    v_ahorro_bolsa = v_aux * 0.50
    v_deuda = v_aux * 0.30
    v_retiro_extra = v_aux * 0.20
    
    v_emerg = v_ahorro_bolsa * 0.50
    v_colchon = v_ahorro_bolsa * 0.50
    v_retiro = v_retiro_extra

# ==========================================
# CONSTRUCCIÓN DE TABLAS Y UI
# ==========================================
detalles = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Fijo": f_retiro, "Variable": v_retiro},
]

df_detalles = pd.DataFrame(detalles)
df_detalles["Total"] = df_detalles["Fijo"] + df_detalles["Variable"]

col1, col2, col3 = st.columns(3)
col1.metric("Ingreso Fijo Neto (Post-Diezmo)", f"${fijo_neto:,.2f}")
col2.metric("Gasto Total (Operativo)", f"${(df_detalles[df_detalles['Concepto'].isin(['Renta','Transporte','Novia','Viajes/Visitas'])]['Total'].sum()):,.2f}")
col3.metric("Ahorro e Inversión", f"${(df_detalles[df_detalles['Concepto'].isin(['Emergencias','Colchón','Retiro/Bolsa'])]['Total'].sum()):,.2f}")

st.markdown("---")
st.subheader("💳 Resumen de Transferencias por Banco")
df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

with st.expander("📝 Ver desglose granular (Fijo vs Variable)"):
    st.dataframe(df_detalles.style.format({"Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}"}), use_container_width=True)

# Gráfico de Cubetas
st.subheader("💧 Nivel de Llenado vs Metas")
df_bar = pd.DataFrame({
    'Cubeta': df_detalles['Concepto'][1:8],
    'Nivel Real': df_detalles['Total'][1:8],
    'Meta Mínima': [meta_renta, meta_transporte, meta_novia, meta_viajes, 400, 250, 250]
})
fig = px.bar(df_bar, x='Cubeta', y=['Meta Mínima', 'Nivel Real'], barmode='group', color_discrete_sequence=['#E2E8F0', '#3182CE'])
st.plotly_chart(fig, use_container_width=True)
