import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")
st.title("📊 Control Financiero: Distribución Dinámica")

# ==========================================
# ENTRADA DE DATOS
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

# Parámetros del Sistema
DIEZMO_PCT = 0.10
GASTO_PCT = 0.65   # Renta, Novia, Viajes, Transporte
DEUDA_PCT = 0.10   
AHORRO_PCT = 0.10  
INVERSION_PCT = 0.15 

# Metas Mínimas Inamovibles
meta_renta = 875.0
meta_transporte = 430.0
meta_novia = 500.0
meta_viajes = 300.0
meta_inamovibles_total = meta_renta + meta_transporte + meta_novia + meta_viajes

# ==========================================
# CÁLCULOS BASE
# ==========================================
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo

diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

# Inicialización
f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

# ==========================================
# LÓGICA DE DISTRIBUCIÓN (FIJO)
# ==========================================
capacidad_gasto_fijo = fijo_neto * GASTO_PCT

# DETERMINAR SI HAY DÉFICIT ANTES DE EMPEZAR
if capacidad_gasto_fijo + var_neto < meta_inamovibles_total and (ingreso_fijo_bruto + ingreso_var_bruto) > 0:
    faltante = meta_inamovibles_total - (capacidad_gasto_fijo + var_neto)
    st.error(f"❌ **DÉFICIT DETECTADO:** Faltan **${faltante:,.2f}** para cubrir los mínimos.")

if capacidad_gasto_fijo >= meta_inamovibles_total:
    # --- MODO DESBLOQUEADO (CRECIMIENTO PROPORCIONAL) ---
    # Calculamos cuánto pesa cada meta en el total de gastos para mantener la proporción
    p_renta = meta_renta / meta_inamovibles_total
    p_transp = meta_transporte / meta_inamovibles_total
    p_novia = meta_novia / meta_inamovibles_total
    p_viajes = meta_viajes / meta_inamovibles_total

    f_renta = capacidad_gasto_fijo * p_renta
    f_transp = capacidad_gasto_fijo * p_transp
    f_novia = capacidad_gasto_fijo * p_novia
    f_viajes = capacidad_gasto_fijo * p_viajes
    
    # Distribución del resto del fijo
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.50
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.50
    f_retiro = fijo_neto * INVERSION_PCT
    
    st.success("🚀 **Distribución Proporcional Activa:** Los sobres de gasto están creciendo.")
else:
    # --- MODO CASCADA (RELLENO DE HUECOS) ---
    st.warning("⚠️ **Modo Cascada:** Priorizando el llenado de inamovibles.")
    f_aux = fijo_neto
    f_renta = min(f_aux, meta_renta); f_aux -= f_renta
    f_transp = min(f_aux, meta_transporte); f_aux -= f_transp
    f_novia = min(f_aux, meta_novia); f_aux -= f_novia
    f_viajes = min(f_aux, meta_viajes); f_aux -= f_viajes
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux

# ==========================================
# LÓGICA VARIABLE (RESCATE)
# ==========================================
# Solo rescatamos si el FIJO no llegó a las metas mínimas
v_aux = var_neto
v_renta = min(v_aux, max(0, meta_renta - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0, meta_transporte - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0, meta_novia - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0, meta_viajes - f_viajes)); v_aux -= v_viajes

# El resto del variable se distribuye 50/30/20 para acelerar
if v_aux > 0:
    v_ahorro = v_aux * 0.50
    v_deuda = v_aux * 0.30
    v_retiro = v_aux * 0.20
    v_emerg = v_ahorro * 0.50
    v_colchon = v_ahorro * 0.50

# ==========================================
# TABLA FINAL Y RESUMEN
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

# Resumen Bancario (Aquí es donde verás los cambios en NU Gasto y SPIN)
st.subheader("💳 Transferencias Requeridas")
df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

# Visualización Granular
with st.expander("🔍 Ver desglose Fijo vs Variable"):
    st.dataframe(df_detalles.style.format({"Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}"}))
