import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

st.title("📊 Control Financiero: Cascada y Desglose de Transferencias")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Metas de la Cascada")
st.sidebar.caption("Prioridad de llenado: 1 -> 7. El ahorro abajo compensa el déficit arriba.")

meta_renta = st.sidebar.number_input("1. Renta (875 ideal)", value=875.0, step=25.0)
meta_transporte = st.sidebar.number_input("2. Transporte (450 ideal)", value=450.0, step=25.0)
meta_novia = st.sidebar.number_input("3. Novia", value=500.0, step=25.0)
meta_viajes = st.sidebar.number_input("4. Viajes/Visitas", value=300.0, step=25.0)
meta_deuda = st.sidebar.number_input("5. Deuda", value=400.0, step=25.0)
meta_emergencias = st.sidebar.number_input("6. Emergencias (CETES)", value=250.0, step=25.0)
meta_colchon = st.sidebar.number_input("7. Colchón (NU)", value=250.0, step=25.0)

diezmo_pct = 0.10

# ==========================================
# PROCESAMIENTO DE FONDOS
# ==========================================
fijo_neto = ingreso_fijo_bruto * (1 - diezmo_pct) if ingreso_fijo_bruto > 0 else 0
var_neto = ingreso_var_bruto * (1 - diezmo_pct) if ingreso_var_bruto > 0 else 0

# Ideales MATLAB Fijos
obj_renta, obj_transp = 875.0, 450.0
obj_novia = (fijo_neto * 0.75) * 0.20
obj_viajes = (fijo_neto * 0.75) * 0.13
obj_deuda = fijo_neto * 0.10
obj_ahorro = fijo_neto * 0.10
obj_emerg = obj_ahorro * 0.25
obj_colchon = obj_ahorro * 0.50

# ==========================================
# EJECUCIÓN DE LA CASCADA (FIJO)
# ==========================================
f_aux = fijo_neto
f_renta = min(f_aux, meta_renta); f_aux -= f_renta
f_transp = min(f_aux, meta_transporte); f_aux -= f_transp
f_novia = min(f_aux, meta_novia); f_aux -= f_novia
f_viajes = min(f_aux, meta_viajes); f_aux -= f_viajes
f_deuda = min(f_aux, meta_deuda); f_aux -= f_deuda
f_emerg = min(f_aux, meta_emergencias); f_aux -= f_emerg
f_colchon = min(f_aux, meta_colchon); f_aux -= f_colchon
f_retiro = max(0, f_aux) 

# ==========================================
# RESCATE Y MANEJO DEL VARIABLE
# ==========================================
meta_inamov = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_fijo = f_renta + f_transp + f_novia + f_viajes
faltante_inamov = max(0, meta_inamov - logrado_fijo)

v_rescate = 0
if faltante_inamov > 0 and var_neto > 0:
    st.warning(f"⚠️ Faltan ${faltante_inamov:,.2f} para cubrir Inamovibles.")
    if st.checkbox("🔄 Aplicar rescate con Ingreso Variable"):
        v_rescate = min(faltante_inamov, var_neto)
        var_disponible = var_neto - v_rescate
    else: var_disponible = var_neto
else: var_disponible = var_neto

# Repartición Variable (50/30/20)
v_deuda = v_emerg = v_colchon = v_retiro = v_reinversion = 0
if var_disponible > 0:
    v_ahorro = var_disponible * 0.50
    v_deuda = var_disponible * 0.30
    v_reinversion = var_disponible * 0.20
    v_emerg = v_ahorro * 0.50
    v_retiro = v_ahorro * 0.25
    v_colchon = v_ahorro * 0.25

# ==========================================
# AUDITORÍA DE COMPENSACIÓN
# ==========================================
st.subheader("⚖️ Auditoría y Compensación de Saldos")
df_auditoria = pd.DataFrame({
    "Categoría": ["Renta", "Transporte", "Novia", "Viajes", "Deuda", "Emergencia", "Colchón"],
    "Ideal (MATLAB)": [obj_renta, obj_transp, obj_novia, obj_viajes, obj_deuda, obj_emerg, obj_colchon],
    "Meta Cascada": [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
})
df_auditoria["Diferencia"] = df_auditoria["Ideal (MATLAB)"] - df_auditoria["Meta Cascada"]

formato = {"Ideal (MATLAB)": "${:,.2f}", "Meta Cascada": "${:,.2f}", "Diferencia": "${:,.2f}"}
def color_diff(val):
    return f'color: {"green" if val > 0 else "red"}; font-weight: bold'
st.dataframe(df_auditoria.style.format(formato).map(color_diff, subset=['Diferencia']), use_container_width=True)

# ==========================================
# DESGLOSE DETALLADO POR CONCEPTO (NUEVO)
# ==========================================
st.markdown("---")
st.subheader("📝 Desglose Específico por Concepto")

# Creamos una lista de diccionarios para armar la tabla detallada
desglose_data = [
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Fijo": f_renta, "Variable (Rescate)": min(v_rescate, max(0, meta_renta - f_renta)), "Total": 0},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Fijo": f_transp, "Variable (Rescate)": min(max(0, v_rescate - (meta_renta - f_renta)), meta_transporte - f_transp), "Total": 0},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Fijo": f_novia, "Variable (Rescate)": 0, "Total": 0}, # El rescate se asume para Renta/Transp primero
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Fijo": f_viajes, "Variable (Rescate)": 0, "Total": 0},
    {"Concepto": "Deuda", "Plataforma": "N/A", "Fijo": f_deuda, "Variable (Rescate)": v_deuda, "Total": 0},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Fijo": f_emerg, "Variable (Rescate)": v_emerg, "Total": 0},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Fijo": f_colchon, "Variable (Rescate)": v_colchon, "Total": 0},
    {"Concepto": "Retiro/Reinversión", "Plataforma": "GBM+", "Fijo": f_retiro, "Variable (Rescate)": v_retiro + v_reinversion, "Total": 0}
]

for item in desglose_data:
    item["Total"] = item["Fijo"] + item["Variable (Rescate)"]

df_desglose = pd.DataFrame(desglose_data)
st.table(df_desglose.style.format({"Fijo": "${:,.2f}", "Variable (Rescate)": "${:,.2f}", "Total": "${:,.2f}"}))

# ==========================================
# PLAN DE TRANSFERENCIAS POR BANCO
# ==========================================
st.markdown("---")
st.subheader("💳 Resumen de Transferencia por Banco")

nu_total = df_desglose[df_desglose["Plataforma"].str.contains("NU")]["Total"].sum()
gbm_total = df_desglose[df_desglose["Plataforma"] == "GBM+"]["Total"].sum()
cetes_total = df_desglose[df_desglose["Plataforma"] == "CETES"]["Total"].sum()
spin_total = df_desglose[df_desglose["Plataforma"] == "SPIN"]["Total"].sum()

df_bancos = pd.DataFrame({
    "Banco": ["NU", "GBM+", "CETES", "SPIN"],
    "Monto a Depositar": [nu_total, gbm_total, cetes_total, spin_total],
    "CLABE": ["638180000126660124", "601180400073884389", "App Cetes", "728969000033664690"]
})
st.table(df_bancos.style.format({"Monto a Depositar": "${:,.2f}"}))

# ==========================================
# GRÁFICOS
# ==========================================
st.markdown("---")
c_g1, c_g2 = st.columns(2)
with c_g1:
    st.write("**💧 Llenado de Cascada**")
    df_bar = pd.DataFrame({
        'Cubeta': ['Renta', 'Transp', 'Novia', 'Viajes', 'Deuda', 'Emerg', 'Colchón'],
        'Real': [f_renta + min(v_rescate, max(0, meta_renta - f_renta)), f_transp + min(max(0, v_rescate - (meta_renta - f_renta)), meta_transporte - f_transp), f_novia, f_viajes, f_deuda + v_deuda, f_emerg + v_emerg, f_colchon + v_colchon],
        'Meta': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
    })
    st.plotly_chart(px.bar(df_bar, x='Cubeta', y=['Meta', 'Real'], barmode='overlay', color_discrete_sequence=['#e5e5e5', '#00CC96']), use_container_width=True)

with c_g2:
    st.write("**📈 Composición del Ahorro**")
    df_pie = pd.DataFrame({'Concepto': ['Emergencias', 'Inversión', 'Colchón'], 'Monto': [cetes_total, gbm_total, f_colchon + v_colchon]})
    if df_pie["Monto"].sum() > 0:
        st.plotly_chart(px.pie(df_pie, values='Monto', names='Concepto', hole=0.4), use_container_width=True)
