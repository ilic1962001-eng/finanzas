import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Inteligente", layout="wide", page_icon="💧")

st.title("📊 Dashboard Financiero: Cascada Inteligente")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("💸 Ingresos de la Semana")
ingreso_fijo = st.sidebar.number_input("Ingreso FIJO ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_variable = st.sidebar.number_input("Ingreso VARIABLE ($)", min_value=0.0, value=0.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Metas de la Cascada (Ajustables)")
st.sidebar.caption("Si bajas una meta aquí, el dinero 'sube' para cubrir las de arriba.")

meta_renta = st.sidebar.number_input("1. Renta", value=875.0, step=50.0)
meta_transporte = st.sidebar.number_input("2. Transporte", value=300.0, step=50.0)
meta_novia = st.sidebar.number_input("3. Novia", value=500.0, step=50.0)
meta_viajes = st.sidebar.number_input("4. Viajes/Ocio", value=300.0, step=50.0)
meta_deuda = st.sidebar.number_input("5. Deuda", value=400.0, step=50.0)
meta_emergencias = st.sidebar.number_input("6. Emergencias (CETES)", value=250.0, step=50.0)
meta_colchon = st.sidebar.number_input("7. Colchón", value=250.0, step=50.0)

diezmo_pct = 0.10

# ==========================================
# LÓGICA DE FONDOS DISPONIBLES
# ==========================================
fijo_despues_dios = ingreso_fijo * (1 - diezmo_pct) if ingreso_fijo > 0 else 0
var_despues_dios = ingreso_variable * (1 - diezmo_pct) if ingreso_variable > 0 else 0

# ==========================================
# DISTRIBUCIÓN OBJETIVO (FÓRMULA ORIGINAL)
# ==========================================
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
# ALGORITMO DE CASCADA DINÁMICA
# ==========================================
fijo_operativo = fijo_despues_dios
r_renta = r_transp = r_novia = r_viajes = r_deuda = r_emerg = r_colchon = r_retiro = 0

# Llenado secuencial
r_renta = min(fijo_operativo, meta_renta); fijo_operativo -= r_renta
r_transp = min(fijo_operativo, meta_transporte); fijo_operativo -= r_transp
r_novia = min(fijo_operativo, meta_novia); fijo_operativo -= r_novia
r_viajes = min(fijo_operativo, meta_viajes); fijo_operativo -= r_viajes
r_deuda = min(fijo_operativo, meta_deuda); fijo_operativo -= r_deuda
r_emerg = min(fijo_operativo, meta_emergencias); fijo_operativo -= r_emerg
r_colchon = min(fijo_operativo, meta_colchon); fijo_operativo -= r_colchon
r_retiro = fijo_operativo 

# ==========================================
# DIAGNÓSTICO E INYECCIÓN DE VARIABLE
# ==========================================
meta_total_operativa = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_operativo = r_renta + r_transp + r_novia + r_viajes
faltante_total = max(0, meta_total_operativa - logrado_operativo)

st.subheader("💡 Diagnóstico de Flujo y Rescate")
if faltante_total > 0:
    col_diag1, col_diag2 = st.columns([2,1])
    with col_diag1:
        st.warning(f"⚠️ Te faltan **${faltante_total:,.2f}** para cubrir tus 4 gastos inamovibles.")
    
    with col_diag2:
        if var_despues_dios > 0:
            aplicar_rescate = st.checkbox("🔄 Usar Ingreso Variable para rescate")
            if aplicar_rescate:
                rescate = min(faltante_total, var_despues_dios)
                var_despues_dios -= rescate
                
                # RE-EJECUTAR CASCADA CON INYECCIÓN
                fijo_operativo = fijo_despues_dios + rescate
                r_renta = min(fijo_operativo, meta_renta); fijo_operativo -= r_renta
                r_transp = min(fijo_operativo, meta_transporte); fijo_operativo -= r_transp
                r_novia = min(fijo_operativo, meta_novia); fijo_operativo -= r_novia
                r_viajes = min(fijo_operativo, meta_viajes); fijo_operativo -= r_viajes
                r_deuda = min(fijo_operativo, meta_deuda); fijo_operativo -= r_deuda
                r_emerg = min(fijo_operativo, meta_emergencias); fijo_operativo -= r_emerg
                r_colchon = min(fijo_operativo, meta_colchon); fijo_operativo -= r_colchon
                r_retiro = fijo_operativo
                st.success(f"Rescate de ${rescate:,.2f} aplicado con éxito.")
else:
    if ingreso_fijo > 0:
        st.success("✅ Todas tus metas prioritarias están cubiertas por el Ingreso Fijo.")

# ==========================================
# DISTRIBUCIÓN DEL VARIABLE RESTANTE
# ==========================================
ahorro_var = var_despues_dios * 0.50
deuda_var = var_despues_dios * 0.30
reinversion_var = var_despues_dios * 0.20

emergencia_total = r_emerg + (ahorro_var * 0.50)
colchon_total = r_colchon + (ahorro_var * 0.25)
retiro_total = r_retiro + (ahorro_var * 0.25) + reinversion_var
deuda_total = r_deuda + deuda_var

# ==========================================
# INTERFAZ DE USUARIO (DASHBOARD)
# ==========================================
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingreso Bruto Total", f"${(ingreso_fijo + ingreso_variable):,.2f}")
c2.metric("🏠 Gasto Operativo", f"${(r_renta + r_transp + r_novia + r_viajes):,.2f}")
c3.metric("💳 Total Deuda", f"${deuda_total:,.2f}")
c4.metric("📈 Total Ahorro/Inversión", f"${(emergencia_total + colchon_total + retiro_total):,.2f}")

st.markdown("---")

# ==========================================
# LA TABLA DE AUDITORÍA (RESTAURADA)
# ==========================================
st.subheader("⚖️ Auditoría: Cascada (Manual) vs. Objetivo (Fórmula Original)")
st.markdown("Compara las metas manuales que pusiste a la izquierda contra lo que dice tu regla de porcentajes.")

if ingreso_fijo > 0:
    df_comparativa = pd.DataFrame({
        "Categoría": ["Renta", "Transporte", "Novia", "Viajes/Ocio", "Deuda", "Emergencias", "Colchón"],
        "Objetivo (Fórmula)": [obj_renta, obj_transp, obj_novia, obj_visitas, obj_deuda, obj_emerg, obj_colchon],
        "Cascada (Manual)": [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon],
    })
    
    df_comparativa["Diferencia"] = df_comparativa["Objetivo (Fórmula)"] - df_comparativa["Cascada (Manual)"]
    
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
        st.success(f"🌟 **Balance de Eficiencia:** Estás pidiendo **${ahorro_total_cascada:,.2f}** menos de lo que dicta tu fórmula. ¡Excelente, ese dinero recicla hacia arriba o se va directo a inversión!")
    elif ahorro_total_cascada < 0:
        st.error(f"📉 **Sobrecosto:** Tus metas manuales son **${abs(ahorro_total_cascada):,.2f}** más caras de lo que tu porcentaje base permite. Considera ajustar algunas cubetas a la baja.")
else:
    st.info("Ingresa tu ingreso fijo para ver la auditoría.")

st.markdown("---")

# ==========================================
# GRÁFICOS
# ==========================================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("💧 Estado de la Cascada")
    df_plot = pd.DataFrame({
        'Cubeta': ['Renta', 'Transp', 'Novia', 'Viajes', 'Deuda', 'Emerg', 'Colchón'],
        'Nivel Real ($)': [r_renta, r_transp, r_novia, r_viajes, r_deuda, r_emerg, r_colchon],
        'Meta Requerida': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
    })
    fig = px.bar(df_plot, x='Cubeta', y=['Meta Requerida', 'Nivel Real ($)'], barmode='overlay', 
                 color_discrete_sequence=['#e5e5e5', '#00CC96'])
    st.plotly_chart(fig, use_container_width=True)

with col_graf2:
    st.subheader("🏠 Gasto Operativo Real")
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
        st.info("Sin fondos operativos esta semana.")

st.markdown("---")

# ==========================================
# TABLA DE TRANSFERENCIAS FINALES
# ==========================================
st.subheader("📋 Plan de Transferencias Final")
df_final = pd.DataFrame({
    "Destino": ["NU (Gastos)", "NU (Colchón)", "CETES (Emergencias)", "GBM+ (Inversión/Retiro)", "SPIN (Ocio/Viajes)", "Deuda"],
    "Monto a Transferir": [
        f"${(r_renta + r_transp + r_novia):,.2f}",
        f"${colchon_total:,.2f}",
        f"${emergencia_total:,.2f}",
        f"${retiro_total:,.2f}",
        f"${r_viajes:,.2f}",
        f"${deuda_total:,.2f}"
    ],
    "CLABE / App": ["638180000126660124", "638180000126660124", "N/A (App Cetes)", "601180400073884389", "728969000033664690", "N/A"]
})
st.table(df_final)
