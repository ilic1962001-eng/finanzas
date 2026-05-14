import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro V2", layout="wide", page_icon="💧")

st.title("📊 Control Financiero: Cascada Dinámica 60/40")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

# Parámetros de distribución 
DIEZMO_PCT = 0.10
GASTO_PCT = 0.60   
DEUDA_PCT = 0.10   
AHORRO_PCT = 0.10  
INVERSION_PCT = 0.20 

# Metas mínimas (Inamovibles + Ocio)
meta_renta = 875.0
meta_transporte = 430.0
meta_novia = 500.0
meta_viajes = 300.0
meta_ocio = 200.0  
meta_inamovibles_total = meta_renta + meta_transporte + meta_novia + meta_viajes + meta_ocio

st.sidebar.markdown("---")
umbral = meta_inamovibles_total / GASTO_PCT
st.sidebar.info(f"**Umbral de Desbloqueo (60%):** Requiere un ingreso fijo neto de **${umbral:,.2f}**")

# ==========================================
# LÓGICA DE DISTRIBUCIÓN FIJA
# ==========================================
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT
fijo_neto = ingreso_fijo_bruto - diezmo_fijo

f_renta = f_transp = f_novia = f_viajes = f_ocio = f_deuda = f_emerg = f_colchon = f_retiro = 0
capacidad_gasto_real = fijo_neto * GASTO_PCT

if capacidad_gasto_real >= meta_inamovibles_total and ingreso_fijo_bruto > 0:
    st.success("🚀 **Modo Abundancia:** El 60% del fijo cubre y supera los mínimos.")
    
    f_renta = capacidad_gasto_real * (meta_renta / meta_inamovibles_total)
    f_transp = capacidad_gasto_real * (meta_transporte / meta_inamovibles_total)
    f_novia = capacidad_gasto_real * (meta_novia / meta_inamovibles_total)
    f_viajes = capacidad_gasto_real * (meta_viajes / meta_inamovibles_total)
    f_ocio = capacidad_gasto_real * (meta_ocio / meta_inamovibles_total)
    
    f_deuda = fijo_neto * DEUDA_PCT
    f_emerg = (fijo_neto * AHORRO_PCT) * 0.5
    f_colchon = (fijo_neto * AHORRO_PCT) * 0.5
    f_retiro = fijo_neto * INVERSION_PCT

else:
    if ingreso_fijo_bruto > 0:
        st.warning("⚠️ **Modo Cascada:** Cubriendo huecos por orden de prioridad.")
    
    f_aux = fijo_neto
    f_renta = min(f_aux, meta_renta); f_aux -= f_renta
    f_transp = min(f_aux, meta_transporte); f_aux -= f_transp
    f_novia = min(f_aux, meta_novia); f_aux -= f_novia
    f_viajes = min(f_aux, meta_viajes); f_aux -= f_viajes
    f_ocio = min(f_aux, meta_ocio); f_aux -= f_ocio
    
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux

# ==========================================
# LÓGICA DE INGRESO VARIABLE
# ==========================================
diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

faltante_inamov = max(0, meta_inamovibles_total - (f_renta + f_transp + f_novia + f_viajes + f_ocio))
v_rescate = min(faltante_inamov, var_neto)
var_disponible = var_neto - v_rescate

if v_rescate > 0:
    st.info(f"🆘 **Rescate Variable:** ${v_rescate:,.2f} usados para completar mínimos.")

v_emerg = v_colchon = v_deuda = v_retiro = 0
if var_disponible > 0:
    v_emerg = (var_disponible * 0.50) * 0.50
    v_colchon = (var_disponible * 0.50) * 0.50
    v_deuda = var_disponible * 0.30
    v_retiro = var_disponible * 0.20

r_aux = v_rescate
v_renta = min(meta_renta - f_renta, r_aux); r_aux -= v_renta
v_transp = min(meta_transporte - f_transp, r_aux); r_aux -= v_transp
v_novia = min(meta_novia - f_novia, r_aux); r_aux -= v_novia
v_viajes = min(meta_viajes - f_viajes, r_aux); r_aux -= v_viajes
v_ocio = min(meta_ocio - f_ocio, r_aux); r_aux -= v_ocio

# ==========================================
# ASIGNACIÓN PARA TABLA DE DETALLES
# ==========================================
detalles = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Ocio", "Plataforma": "Efectivo/Gasto", "Fijo": f_ocio, "Variable": v_ocio},
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
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fijo Neto", f"${fijo_neto:,.2f}")
c2.metric("Var. Neto", f"${var_neto:,.2f}")
c3.metric("Gasto Total", f"${df_detalles.iloc[1:6]['Total'].sum():,.2f}")
c4.metric("Inversión/Ahorro", f"${df_detalles.iloc[7:10]['Total'].sum():,.2f}")

st.markdown("---")

# ==========================================
# DIAGRAMA DE FLUJO (SANKEY)
# ==========================================
st.subheader("🌊 Flujo de Efectivo (Sankey)")

# 1. Definir los nodos del diagrama
labels = ["Ingreso Fijo", "Ingreso Variable", "Fijo Neto", "Var Neto", "Diezmo",
          "Renta", "Transporte", "Novia", "Viajes", "Ocio",
          "Deuda", "Emergencias", "Colchón", "Retiro/Bolsa"]

# Diccionario para mapear nombres a índices fácilmente
label_dict = {label: i for i, label in enumerate(labels)}

source = []
target = []
value = []

# Función auxiliar para agregar enlaces al gráfico
def add_link(src, tgt, val):
    if val > 0:
        source.append(label_dict[src])
        target.append(label_dict[tgt])
        value.append(val)

# 2. Conectar Ingresos Brutos a Netos y Diezmo
add_link("Ingreso Fijo", "Diezmo", diezmo_fijo)
add_link("Ingreso Fijo", "Fijo Neto", fijo_neto)
add_link("Ingreso Variable", "Diezmo", diezmo_var)
add_link("Ingreso Variable", "Var Neto", var_neto)

# 3. Conectar Fijo Neto a las Cubetas
add_link("Fijo Neto", "Renta", f_renta)
add_link("Fijo Neto", "Transporte", f_transp)
add_link("Fijo Neto", "Novia", f_novia)
add_link("Fijo Neto", "Viajes", f_viajes)
add_link("Fijo Neto", "Ocio", f_ocio)
add_link("Fijo Neto", "Deuda", f_deuda)
add_link("Fijo Neto", "Emergencias", f_emerg)
add_link("Fijo Neto", "Colchón", f_colchon)
add_link("Fijo Neto", "Retiro/Bolsa", f_retiro)

# 4. Conectar Variable Neto a las Cubetas
add_link("Var Neto", "Renta", v_renta)
add_link("Var Neto", "Transporte", v_transp)
add_link("Var Neto", "Novia", v_novia)
add_link("Var Neto", "Viajes", v_viajes)
add_link("Var Neto", "Ocio", v_ocio)
add_link("Var Neto", "Deuda", v_deuda)
add_link("Var Neto", "Emergencias", v_emerg)
add_link("Var Neto", "Colchón", v_colchon)
add_link("Var Neto", "Retiro/Bolsa", v_retiro)

# 5. Dibujar el Sankey
if sum(value) > 0:  # Solo dibujarlo si hay dinero ingresado
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="rgba(49, 130, 206, 0.8)"
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color="rgba(203, 213, 224, 0.6)"
        )
    )])
    fig_sankey.update_layout(height=500, font_size=12)
    st.plotly_chart(fig_sankey, use_container_width=True)
else:
    st.info("Ingresa montos en la barra lateral para visualizar el flujo de efectivo.")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💳 Resumen por Banco")
    df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
    st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

with col_right:
    st.subheader("💧 Nivel de Cubetas")
    df_bar = pd.DataFrame({
        'Cubeta': df_detalles['Concepto'][1:7].tolist(),
        'Nivel Real': df_detalles['Total'][1:7].tolist(),
        'Meta Mínima': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_ocio, 400.0] 
    })
    fig_bar = px.bar(df_bar, x='Cubeta', y=['Meta Mínima', 'Nivel Real'], barmode='group', 
                 color_discrete_sequence=['#E2E8F0', '#0078FF'])
    fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
    st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("📝 Granulado de Movimientos (Fijo vs Variable)"):
    st.dataframe(df_detalles.style.format({"Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}"}), use_container_width=True)
