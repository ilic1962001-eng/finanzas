import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

st.title("📊 Control Financiero: Cascada y Origen de Fondos")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo_bruto = st.sidebar.number_input("Ingreso FIJO Semanal ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_var_bruto = st.sidebar.number_input("Ingreso VARIABLE Semanal ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Metas de la Cascada")
st.sidebar.caption("Gastos inamovibles. El ingreso fijo llena estas cubetas en este orden.")

# Valores fijos (ya no son inputs editables)
meta_renta = 875.0
meta_transporte = 430.0
meta_novia = 500.0
meta_viajes = 300.0
meta_deuda = 400.0
meta_emergencias = 250.0
meta_colchon = 250.0
diezmo_pct = 0.10

# Mostrar los valores fijos en la UI como solo lectura
st.sidebar.text(f"1. Renta: ${meta_renta:,.2f}")
st.sidebar.text(f"2. Transporte: ${meta_transporte:,.2f}")
st.sidebar.text(f"3. Novia: ${meta_novia:,.2f}")
st.sidebar.text(f"4. Viajes/Visitas: ${meta_viajes:,.2f}")
st.sidebar.text(f"5. Deuda: ${meta_deuda:,.2f}")
st.sidebar.text(f"6. Emergencias: ${meta_emergencias:,.2f}")
st.sidebar.text(f"7. Colchón: ${meta_colchon:,.2f}")

# ==========================================
# PROCESAMIENTO DE FONDOS Y DIEZMO
# ==========================================
# Cálculo del diezmo inicial
diezmo_fijo = ingreso_fijo_bruto * diezmo_pct if ingreso_fijo_bruto > 0 else 0
diezmo_var = ingreso_var_bruto * diezmo_pct if ingreso_var_bruto > 0 else 0

fijo_neto = ingreso_fijo_bruto - diezmo_fijo
var_neto = ingreso_var_bruto - diezmo_var

# ==========================================
# EJECUCIÓN DE LA CASCADA (SÓLO INGRESO FIJO)
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
# LÓGICA DE RESCATE (INGRESO VARIABLE)
# ==========================================
# Evaluamos cuánto faltó de los 4 inamovibles principales
meta_inamovibles = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_fijo = f_renta + f_transp + f_novia + f_viajes
faltante_inamov = max(0, meta_inamovibles - logrado_fijo)

v_rescate = 0
var_disponible = var_neto

if faltante_inamov > 0:
    st.warning(f"⚠️ DÉFICIT DETECTADO: Faltan **${faltante_inamov:,.2f}** para cubrir los gastos inamovibles base.")
    
    if var_neto > 0:
        # Rescate automático si hay fondos variables
        v_rescate = min(faltante_inamov, var_neto)
        var_disponible = var_neto - v_rescate
        st.success(f"✅ Se han tomado **${v_rescate:,.2f}** del ingreso variable para completar los inamovibles.")
    else:
        st.error("❌ ALERTA: No hay suficiente ingreso (Fijo + Variable) para cubrir los gastos básicos.")
else:
    if ingreso_fijo_bruto > 0:
        st.success("✅ Ingreso Fijo suficiente para cubrir metas básicas.")

# REPARTO OBJETIVO DEL VARIABLE (50/30/20)
v_deuda = v_emerg = v_colchon = v_retiro = v_reinversion = 0
if var_disponible > 0:
    v_ahorro_bolsa = var_disponible * 0.50
    v_deuda_extra = var_disponible * 0.30
    v_reinversion = var_disponible * 0.20
    
    v_emerg = v_ahorro_bolsa * 0.50
    v_retiro = v_ahorro_bolsa * 0.25
    v_colchon = v_ahorro_bolsa * 0.25
    v_deuda = v_deuda_extra

# ==========================================
# CONSTRUCCIÓN DEL DETALLE GRANULAR
# ==========================================
# Distribuimos el rescate en orden (Renta -> Transp -> Novia -> Viajes)
rescate_aux = v_rescate
r_renta = min(meta_renta - f_renta, rescate_aux); rescate_aux -= r_renta
r_transp = min(meta_transporte - f_transp, rescate_aux); rescate_aux -= r_transp
r_novia = min(meta_novia - f_novia, rescate_aux); rescate_aux -= r_novia
r_viajes = min(meta_viajes - f_viajes, rescate_aux); rescate_aux -= r_viajes

detalles = [
    {"Concepto": "Diezmo (10%)", "Plataforma": "Cuenta Diezmo", "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Fijo": f_renta, "Variable": r_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Fijo": f_transp, "Variable": r_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Fijo": f_novia, "Variable": r_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Fijo": f_viajes, "Variable": r_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Fijo": f_retiro, "Variable": v_retiro + v_reinversion},
]

df_detalles = pd.DataFrame(detalles)
df_detalles["Total"] = df_detalles["Fijo"] + df_detalles["Variable"]

# ==========================================
# VISUALIZACIÓN DASHBOARD
# ==========================================
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Ingreso Total Bruto", f"${(ingreso_fijo_bruto + ingreso_var_bruto):,.2f}")
col_m2.metric("Total Inversión/Ahorro", f"${df_detalles[df_detalles['Concepto'].isin(['Emergencias', 'Colchón', 'Retiro/Bolsa'])]['Total'].sum():,.2f}")
col_m3.metric("Total Deuda", f"${df_detalles[df_detalles['Concepto'] == 'Deuda']['Total'].sum():,.2f}")

st.markdown("---")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.write("**💧 Llenado de Cascada (Real)**")
    df_bar = pd.DataFrame({
        'Cubeta': df_detalles['Concepto'][1:], # Excluimos Diezmo
        'Nivel Real': df_detalles['Total'][1:],
        'Meta': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon, 0]
    }).iloc[:-1] # Excluimos retiro para la gráfica de metas
    
    fig = px.bar(df_bar, x='Cubeta', y=['Meta', 'Nivel Real'], barmode='overlay', color_discrete_sequence=['#e5e5e5', '#00CC96'])
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    st.write("**📈 Composición del Ahorro Total**")
    df_pie = df_detalles[df_detalles['Concepto'].isin(['Emergencias', 'Colchón', 'Retiro/Bolsa'])]
    if df_pie["Total"].sum() > 0:
        st.plotly_chart(px.pie(df_pie, values='Total', names='Concepto', hole=0.4), use_container_width=True)

# ==========================================
# TABLAS DE TRANSFERENCIA (EL DETALLE HASTA ABAJO)
# ==========================================
st.markdown("---")
st.subheader("💳 Resumen de Transferencias por Banco")

df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
clabes = {
    "NU (Cajita)": "638180000126660124", 
    "NU (Gasto)": "638180000126660124", 
    "CETES": "App Cetes", 
    "GBM+": "601180400073884389", 
    "SPIN": "728969000033664690", 
    "Pago Deuda": "N/A",
    "Cuenta Diezmo": "N/A (Apartar en tu cuenta)"
}
df_bancos["Identificador / CLABE"] = df_bancos["Plataforma"].map(clabes)

st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

st.markdown("---")
st.subheader("📝 Detalle Granular de Movimientos")
st.caption("Uso del dinero desglosado por origen (Fijo vs Variable) y concepto.")

formato_moneda = {"Fijo": "${:,.2f}", "Variable": "${:,.2f}", "Total": "${:,.2f}"}
st.dataframe(df_detalles.style.format(formato_moneda), use_container_width=True)

# ==========================================
# AUDITORÍA DE MATLAB
# ==========================================
with st.expander("⚖️ Auditoría: Comparativa vs Plan MATLAB"):
    f_neto = fijo_neto
    
    # Referencia inicial fija (Los mínimos inamovibles)
    obj_renta = meta_renta
    obj_transp = meta_transporte
    obj_novia = meta_novia
    
    # Todo lo demás se reparte
    obj_viajes = (f_neto * 0.75) * 0.13 if f_neto > 0 else 0
    obj_deuda_matlab = f_neto * 0.10 if f_neto > 0 else 0
    obj_ahorro_matlab = f_neto * 0.10 if f_neto > 0 else 0
    obj_emerg_matlab = obj_ahorro_matlab * 0.25
    obj_colchon_matlab = obj_ahorro_matlab * 0.50
    
    df_auditoria = pd.DataFrame({
        "Categoría": ["Renta", "Transporte", "Novia", "Viajes", "Deuda", "Emergencias", "Colchón"],
        "Plan MATLAB (Fijo)": [obj_renta, obj_transp, obj_novia, obj_viajes, obj_deuda_matlab, obj_emerg_matlab, obj_colchon_matlab],
        "Cascada Real (Fijo)": [f_renta, f_transp, f_novia, f_viajes, f_deuda, f_emerg, f_colchon]
    })
    
    # Diferencia: Positivo = Ahorro / Eficiencia ; Negativo = Déficit
    df_auditoria["Diferencia"] = df_auditoria["Plan MATLAB (Fijo)"] - df_auditoria["Cascada Real (Fijo)"]
    
    # Función de color
    def color_diferencia(val):
        color = '#d62728' if val > 0 else '#2ca02c' if val < 0 else 'gray'
        return f'color: {color}; font-weight: bold'
    
    formato_auditoria = {"Plan MATLAB (Fijo)": "${:,.2f}", "Cascada Real (Fijo)": "${:,.2f}", "Diferencia": "${:,.2f}"}
    
    st.dataframe(df_auditoria.style.format(formato_auditoria).map(color_diferencia, subset=['Diferencia']), use_container_width=True)
