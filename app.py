import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

st.title("📊 Control Financiero: Cascada y Compensación Dinámica")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Metas de la Cascada")
st.sidebar.caption("Si reduces una meta, generas un ahorro que sube a compensar los déficits de arriba.")

meta_renta = st.sidebar.number_input("1. Renta (Meta fija)", value=875.0, step=25.0)
meta_transporte = st.sidebar.number_input("2. Transporte (Meta fija)", value=450.0, step=25.0)
meta_novia = st.sidebar.number_input("3. Novia", value=500.0, step=25.0)
meta_viajes = st.sidebar.number_input("4. Viajes/Visitas", value=300.0, step=25.0)
meta_deuda = st.sidebar.number_input("5. Deuda", value=400.0, step=25.0)
meta_emergencias = st.sidebar.number_input("6. Emergencias (CETES)", value=250.0, step=25.0)
meta_colchon = st.sidebar.number_input("7. Colchón", value=250.0, step=25.0)

diezmo_pct = 0.10

# ==========================================
# PROCESAMIENTO DE FONDOS
# ==========================================
fijo_neto = ingreso_fijo_bruto * (1 - diezmo_pct) if ingreso_fijo_bruto > 0 else 0
var_neto = ingreso_var_bruto * (1 - diezmo_pct) if ingreso_var_bruto > 0 else 0

# Ideales MATLAB: Renta y Transporte ahora son inamovibles (fijos a 875 y 450)
obj_renta = 875.0
obj_transp = 450.0
# El resto sigue respetando tu distribución base del ingreso fijo
obj_novia = (fijo_neto * 0.75) * 0.20
obj_viajes = (fijo_neto * 0.75) * 0.13
obj_deuda = fijo_neto * 0.10
obj_emerg = (fijo_neto * 0.10) * 0.25
obj_colchon = (fijo_neto * 0.10) * 0.50

# ==========================================
# EJECUCIÓN DE LA CASCADA (FIJO)
# ==========================================
fijo_aux = fijo_neto
f_renta = min(fijo_aux, meta_renta); fijo_aux -= f_renta
f_transp = min(fijo_aux, meta_transporte); fijo_aux -= f_transp
f_novia = min(fijo_aux, meta_novia); fijo_aux -= f_novia
f_viajes = min(fijo_aux, meta_viajes); fijo_aux -= f_viajes
f_deuda = min(fijo_aux, meta_deuda); fijo_aux -= f_deuda
f_emerg = min(fijo_aux, meta_emergencias); fijo_aux -= f_emerg
f_colchon = min(fijo_aux, meta_colchon); fijo_aux -= f_colchon
f_retiro = max(0, fijo_aux) # Todo lo que sobre del fijo va a retiro

# ==========================================
# RESCATE Y MANEJO DEL VARIABLE
# ==========================================
meta_inamovibles = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_fijo_inamov = f_renta + f_transp + f_novia + f_viajes
faltante_inamov = max(0, meta_inamovibles - logrado_fijo_inamov)

v_rescate = v_deuda = v_emerg = v_colchon = v_retiro = v_reinversion = 0

if faltante_inamov > 0 and var_neto > 0:
    st.info(f"💡 El ingreso fijo no cubre los Inamovibles (Faltan ${faltante_inamov:,.2f}). Tienes variable disponible.")
    if st.checkbox("🔄 Aplicar rescate con Ingreso Variable para cubrir Inamovibles"):
        v_rescate = min(faltante_inamov, var_neto)
        var_disponible = var_neto - v_rescate
        st.success(f"✅ Se inyectaron ${v_rescate:,.2f} al operativo.")
    else:
        var_disponible = var_neto
else:
    var_disponible = var_neto

# Repartición del Variable sobrante (50/30/20)
if var_disponible > 0:
    v_ahorro_bolsa = var_disponible * 0.50
    v_deuda = var_disponible * 0.30
    v_reinversion = var_disponible * 0.20
    
    v_emerg = v_ahorro_bolsa * 0.50
    v_retiro = v_ahorro_bolsa * 0.25
    v_colchon = v_ahorro_bolsa * 0.25

# ==========================================
# AUDITORÍA DE DIFERENCIAS (EFECTO COMPENSACIÓN VISUAL)
# ==========================================
st.subheader("⚖️ Auditoría: Compensación Dinámica de Saldos")
st.markdown("Si bajas una meta manual, generas un ahorro que sube automáticamente a cancelar los déficits de las metas superiores.")

df_auditoria = pd.DataFrame({
    "Categoría": ["Renta", "Transporte", "Novia", "Viajes", "Deuda", "Emergencia", "Colchón"],
    "Ideal (MATLAB)": [obj_renta, obj_transp, obj_novia, obj_viajes, obj_deuda, obj_emerg, obj_colchon],
    "Meta Cascada": [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
})

# Diferencia Inicial (Positivo = Ahorro, Negativo = Déficit)
df_auditoria["Diferencia Bruta"] = df_auditoria["Ideal (MATLAB)"] - df_auditoria["Meta Cascada"]

# Lógica de Compensación: Los ahorros cubren los déficits
ahorro_total_disponible = df_auditoria[df_auditoria["Diferencia Bruta"] > 0]["Diferencia Bruta"].sum()
balance_neto_lista = []

for diff in df_auditoria["Diferencia Bruta"]:
    if diff < 0: # Es un déficit
        necesidad = abs(diff)
        if ahorro_total_disponible >= necesidad:
            balance_neto_lista.append(0.0) # Déficit cubierto
            ahorro_total_disponible -= necesidad
        else:
            balance_neto_lista.append(diff + ahorro_total_disponible) # Cubierto parcialmente
            ahorro_total_disponible = 0
    elif diff > 0:
        balance_neto_lista.append(diff) # Se queda como ahorro inicial (visual), la bolsa maneja el global
    else:
        balance_neto_lista.append(0.0)

df_auditoria["Déficit Restante (Post-Rescate Interno)"] = [min(0, val) for val in balance_neto_lista]

def color_diff(val):
    color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
    return f'color: {color}; font-weight: bold'

formato_columnas = {
    "Ideal (MATLAB)": "${:,.2f}", "Meta Cascada": "${:,.2f}", 
    "Diferencia Bruta": "${:,.2f}", "Déficit Restante (Post-Rescate Interno)": "${:,.2f}"
}
st.dataframe(df_auditoria.style.format(formato_columnas)\
             .map(color_diff, subset=['Diferencia Bruta', 'Déficit Restante (Post-Rescate Interno)']), 
             use_container_width=True)

# Gráfico de Cascada de Compensación (Waterfall)
fig_waterfall = go.Figure(go.Waterfall(
    name = "Compensación", orientation = "v",
    measure = ["relative"] * 7 + ["total"],
    x = ["Renta", "Transp", "Novia", "Viajes", "Deuda", "Emerg", "Colchón", "BALANCE FINAL"],
    textposition = "outside",
    text = [f"${v:,.0f}" for v in df_auditoria["Diferencia Bruta"]] + [f"${df_auditoria['Diferencia Bruta'].sum():,.0f}"],
    y = list(df_auditoria["Diferencia Bruta"]) + [df_auditoria["Diferencia Bruta"].sum()],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    increasing = {"marker":{"color":"#2ca02c"}},
    decreasing = {"marker":{"color":"#d62728"}},
    totals = {"marker":{"color":"#1f77b4"}}
))
fig_waterfall.update_layout(title="Impacto Visual: Ahorros cancelando Déficits", showlegend=False)
st.plotly_chart(fig_waterfall, use_container_width=True)

# ==========================================
# TRANSFERENCIAS FINALES (DESGLOSADAS)
# ==========================================
st.markdown("---")
st.subheader("💳 Plan de Transferencias Final (Desglosado)")

nu_fijo = f_renta + f_transp + f_novia + f_colchon + v_rescate
nu_total = nu_fijo + v_colchon
cetes_total = f_emerg + v_emerg
gbm_total = f_retiro + v_retiro + v_reinversion
spin_total = f_viajes

df_final = pd.DataFrame({
    "Plataforma": ["NU (Gastos/Colchón)", "CETES", "GBM+", "SPIN", "Deuda"],
    "Monto Total": [nu_total, cetes_total, gbm_total, spin_total, f_deuda + v_deuda],
    "Desde Fijo": [nu_fijo, f_emerg, f_retiro, f_viajes, f_deuda],
    "Desde Variable": [v_colchon, v_emerg, v_retiro + v_reinversion, 0, v_deuda],
    "CLABE": ["638180000126660124", "App Cetes", "601180400073884389", "728969000033664690", "N/A"]
})

st.table(df_final.style.format({"Monto Total": "${:,.2f}", "Desde Fijo": "${:,.2f}", "Desde Variable": "${:,.2f}"}))

# ==========================================
# VISUALIZACIÓN DE LA CASCADA REAL
# ==========================================
st.markdown("---")
st.write("**💧 Dinero Real Llenando las Cubetas (Fijo + Rescate Variable)**")

df_bar = pd.DataFrame({
    'Cubeta': ['Renta', 'Transp', 'Novia', 'Viajes', 'Deuda', 'Emerg', 'Colchón'],
    # Para la gráfica, el rescate inyectado asume llenar desde arriba hacia abajo:
    'Nivel Real': [min(meta_renta, f_renta + v_rescate), 
                   min(meta_transporte, f_transp + max(0, v_rescate - (meta_renta - f_renta))), 
                   f_novia, f_viajes, f_deuda, f_emerg, f_colchon],
    'Meta': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
})

fig = px.bar(df_bar, x='Cubeta', y=['Meta', 'Nivel Real'], barmode='overlay', color_discrete_sequence=['#e5e5e5', '#00CC96'])
st.plotly_chart(fig, use_container_width=True)
