import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Mi Dashboard Financiero", layout="wide", page_icon="💰")

st.title("📊 Dashboard Financiero: Sistema en Cascada")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo = st.sidebar.number_input("Ingreso FIJO ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_variable = st.sidebar.number_input("Ingreso VARIABLE ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Metas de la Cascada")
st.sidebar.caption("Define cuánto requiere cada cubeta. El sistema las llenará de arriba hacia abajo.")

meta_renta = st.sidebar.number_input("1. Renta", value=875.0, step=50.0)
meta_transporte = st.sidebar.number_input("2. Transporte", value=300.0, step=50.0)
meta_novia = st.sidebar.number_input("3. Novia", value=500.0, step=50.0)
meta_viajes = st.sidebar.number_input("4. Viajes/Ocio (Visitas)", value=300.0, step=50.0)
meta_deuda = st.sidebar.number_input("5. Deuda", value=400.0, step=50.0)
meta_emergencias = st.sidebar.number_input("6. Emergencias (CETES)", value=250.0, step=50.0)
meta_colchon = st.sidebar.number_input("7. Colchón", value=250.0, step=50.0)

diezmo_pct = 0.10

# ==========================================
# LÓGICA DE FONDOS DISPONIBLES
# ==========================================
fijo_despues_dios = ingreso_fijo * (1 - diezmo_pct) if ingreso_fijo > 0 else 0
var_despues_dios = ingreso_variable * (1 - diezmo_pct) if ingreso_variable > 0 else 0

# Los gastos inamovibles son las primeras 4 prioridades
meta_inamovibles = meta_renta + meta_transporte + meta_novia + meta_viajes
faltante_inamovibles = max(0, meta_inamovibles - fijo_despues_dios)

# ==========================================
# DISTRIBUCIÓN OBJETIVO (MATEMÁTICA PURA)
# ==========================================
# ¿Qué dictan tus porcentajes originales si aplicamos la fórmula estricta a tu ingreso?
obj_gasto = fijo_despues_dios * 0.75
obj_renta = obj_gasto * 0.45
obj_novia = obj_gasto * 0.20
obj_visitas = obj_gasto * 0.13
obj_transp = obj_gasto - (obj_renta + obj_novia + obj_visitas)

obj_deuda = fijo_despues_dios * 0.10
obj_ahorro = fijo_despues_dios * 0.10
obj_colchon = obj_ahorro * 0.50
obj_emerg = obj_ahorro * 0.25

# ==========================================
# DIAGNÓSTICO Y RESCATE TEMPORAL
# ==========================================
rescate_aplicado = 0
aplicar_rescate = False

if faltante_inamovibles > 0 and fijo_despues_dios > 0:
    st.warning(f"⚠️ **Diagnóstico:** Tu ingreso fijo neto (${fijo_despues_dios:,.2f}) no cubre tus 4 gastos inamovibles (${meta_inamovibles:,.2f}). Faltan **${faltante_inamovibles:,.2f}**.")
    
    if var_despues_dios > 0:
        st.info(f"💡 **Solución Temporal:** Tienes ${var_despues_dios:,.2f} netos en el Variable. Puedes usar parte para blindar tus metas operativas.")
        aplicar_rescate = st.checkbox("🔄 Utilizar Ingreso Variable como rescate esta semana.")
        
        if aplicar_rescate:
            rescate_aplicado = min(faltante_inamovibles, var_despues_dios)
            st.success(f"✅ Se transfirieron **${rescate_aplicado:,.2f}** del Variable al Fijo.")
    else:
        st.error("❌ No hay Ingreso Variable para un rescate. El dinero llegará hasta donde alcance la cascada.")
elif fijo_despues_dios == 0:
    st.info("Introduce tus ingresos en el menú lateral para ver el diagnóstico.")
else:
    st.success(f"✅ ¡Excelente! Tu Ingreso Fijo cubre tus gastos inamovibles. Tu Ingreso Variable se invertirá íntegramente.")

fijo_operativo = fijo_despues_dios + rescate_aplicado
var_operativo = var_despues_dios - rescate_aplicado

# ==========================================
# ALGORITMO DE CASCADA (LLENADO POR PRIORIDAD)
# ==========================================
r_renta = r_transp = r_novia = r_viajes = r_deuda = r_emerg = r_colchon = r_retiro = 0

r_renta = min(fijo_operativo, meta_renta); fijo_operativo -= r_renta
r_transp = min(fijo_operativo, meta_transporte); fijo_operativo -= r_transp
r_novia = min(fijo_operativo, meta_novia); fijo_operativo -= r_novia
r_viajes = min(fijo_operativo, meta_viajes); fijo_operativo -= r_viajes
r_deuda = min(fijo_operativo, meta_deuda); fijo_operativo -= r_deuda
r_emerg = min(fijo_operativo, meta_emergencias); fijo_operativo -= r_emerg
r_colchon = min(fijo_operativo, meta_colchon); fijo_operativo -= r_colchon
r_retiro = fijo_operativo 

# ==========================================
# PROCESAMIENTO DEL VARIABLE INTOCABLE
# ==========================================
ahorro_var = deuda_var = reinversion_var = 0
emergencia_var = retiro_var = colchon_var = 0

if var_operativo > 0:
    ahorro_var = var_operativo * 0.50
    deuda_var = var_operativo * 0.30
    reinversion_var = var_operativo * 0.20

    emergencia_var = ahorro_var * 0.50
    retiro_var = ahorro_var * 0.25
    colchon_var = ahorro_var * 0.25

emergencia_total = r_emerg + emergencia_var
retiro_total = r_retiro + retiro_var
inversion_gbm_total = retiro_total + reinversion_var
colchon_total = r_colchon + colchon_var
deuda_total = r_deuda + deuda_var

st.markdown("---")

# ==========================================
# INTERFAZ DE USUARIO (DASHBOARD)
# ==========================================

col1, col2, col3 = st.columns(3)
col1.metric("Ingreso Total Bruto", f"${(ingreso_fijo + ingreso_variable):,.2f}")
col2.metric("Total a Deuda", f"${deuda_total:,.2f}")
col3.metric("Total Ahorro/GBM", f"${(emergencia_total + inversion_gbm_total + colchon_total):,.2f}")

st.markdown("---")

# ==========================================
# NUEVO: AUDITORÍA CASCADA VS OBJETIVO
# ==========================================
st.subheader("⚖️ Auditoría: Cascada (Real) vs. Objetivo (Porcentajes)")
st.markdown("Compara cuánto pediste en tu cascada manual vs. lo que la matemática estricta dictaba para tu nivel de ingresos.")

if ingreso_fijo > 0:
    # Calcular diferencias (Positivo = Ahorraste/Pediste menos; Negativo = Gastaste más del porcentaje)
    df_comparativa = pd.DataFrame({
        "Categoría": ["Renta", "Transporte", "Novia", "Viajes/Ocio", "Deuda", "Emergencias", "Colchón"],
        "Objetivo (Fórmula)": [obj_renta, obj_transp, obj_novia, obj_visitas, obj_deuda, obj_emerg, obj_colchon],
        "Cascada (Manual)": [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon],
    })
    
    df_comparativa["Diferencia"] = df_comparativa["Objetivo (Fórmula)"] - df_comparativa["Cascada (Manual)"]
    
    # Formatear la tabla para visualizar colores y signos
    def color_diferencia(val):
        color = '#2ca02c' if val > 0 else '#d62728' if val < 0 else 'gray'
        return f'color: {color}; font-weight: bold'

    df_formateado = df_comparativa.style.format({
        "Objetivo (Fórmula)": "${:,.2f}",
        "Cascada (Manual)": "${:,.2f}",
        "Diferencia": "${:,.2f}"
    }).map(color_diferencia, subset=['Diferencia'])
    
    st.dataframe(df_formateado, use_container_width=True)
    
    ahorro_total_cascada = df_comparativa["Diferencia"].sum()
    if ahorro_total_cascada > 0:
        st.success(f"🌟 **Balance Positivo:** Al ajustar tus metas manualmente en la cascada, estás exigiendo **${ahorro_total_cascada:,.2f}** menos de lo que dictaban tus porcentajes. ¡Ese dinero bajará directo a tus inversiones libres!")
    elif ahorro_total_cascada < 0:
        st.error(f"📉 **Balance Negativo:** Tus metas manuales de la cascada son **${abs(ahorro_total_cascada):,.2f}** más altas de lo que tu ingreso actual puede soportar según tus porcentajes base.")
else:
    st.info("Ingresa tu ingreso fijo para generar la auditoría comparativa.")

st.markdown("---")

# ==========================================
# GRÁFICOS
# ==========================================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("💧 Nivel de Llenado (La Cascada)")
    df_cascada = pd.DataFrame({
        'Prioridad': ['1. Renta', '2. Transp.', '3. Novia', '4. Viajes', '5. Deuda', '6. Emerg.', '7. Colchón'],
        'Asignado ($)': [r_renta, r_transp, r_novia, r_viajes, r_deuda, r_emerg, r_colchon],
        'Meta Requerida': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
    })
    fig_bar = px.bar(df_cascada, x='Prioridad', y=['Meta Requerida', 'Asignado ($)'], 
                     barmode='overlay', opacity=0.8, color_discrete_sequence=['#e5e5e5', '#1f77b4'])
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    st.subheader("🏠 Distribución Gasto Operativo Real")
    total_gasto = r_renta + r_transp + r_novia + r_viajes
    if total_gasto > 0:
        df_pie = pd.DataFrame({
            'Categoría': ['Renta', 'Transporte', 'Novia', 'Viajes'],
            'Monto': [r_renta, r_transp, r_novia, r_viajes]
        })
        fig_pie = px.pie(df_pie, values='Monto', names='Categoría', hole=0.4)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sin fondos en la cascada.")

st.markdown("---")

# ==========================================
# TRANSFERENCIAS FINALES
# ==========================================
st.subheader("💳 Destino de Fondos a Transferir")
df_transferencias = pd.DataFrame({
    "Plataforma": ["NU (Gastos y Colchón)", "CETES Directo (Emergencias)", "GBM+ (Retiro/Inversión)", "SPIN (Ocio/Viajes)"],
    "Monto ($)": [
        f"${(r_renta + r_transp + r_novia + colchon_total):,.2f}", 
        f"${emergencia_total:,.2f}", 
        f"${inversion_gbm_total:,.2f}", 
        f"${r_viajes:,.2f}"
    ],
    "CLABE / App": ["638180000126660124", "N/A (Desde App)", "601180400073884389", "728969000033664690"],
    "Detalle": [
        f"Renta: ${r_renta:,.2f} | Transp: ${r_transp:,.2f} | Novia: ${r_novia:,.2f} | Colchón: ${colchon_total:,.2f}",
        "La cubeta #6 y el 25% del variable",
        f"Todo el dinero libre sobrante (${r_retiro:,.2f}) + Porción variable",
        "La cubeta #4 completa"
    ]
})

st.table(df_transferencias)
