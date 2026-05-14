import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Inteligente", layout="wide", page_icon="💧")

st.title("📊 Dashboard Financiero: Cascada con Recirculación")
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
# LÓGICA DE FONDOS Y DISTRIBUCIÓN OBJETIVO
# ==========================================
fijo_despues_dios = ingreso_fijo * (1 - diezmo_pct) if ingreso_fijo > 0 else 0
var_despues_dios = ingreso_variable * (1 - diezmo_pct) if ingreso_variable > 0 else 0

# Distribución Ideal (MATLAB) para comparativa
obj_gasto = fijo_despues_dios * 0.75
obj_deuda = fijo_despues_dios * 0.10
obj_ahorro = fijo_despues_dios * 0.10
obj_ocio = fijo_despues_dios * 0.05

# ==========================================
# ALGORITMO DE CASCADA DINÁMICA
# ==========================================
# El dinero fluye 1->2->3... pero visualizamos la recirculación
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
# ANÁLISIS DE RECIRCULACIÓN (Ahorro de cubetas bajas)
# ==========================================
# Calculamos si las cubetas bajas están "cediendo" dinero a las altas
ahorro_en_bajas = 0
if r_deuda < obj_deuda: ahorro_en_bajas += (obj_deuda - r_deuda)
if r_emerg < (obj_ahorro * 0.25): ahorro_en_bajas += ((obj_ahorro * 0.25) - r_emerg)
if r_colchon < (obj_ahorro * 0.50): ahorro_en_bajas += ((obj_ahorro * 0.50) - r_colchon)

# ==========================================
# DIAGNÓSTICO E INYECCIÓN DE VARIABLE
# ==========================================
meta_total_operativa = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_operativo = r_renta + r_transp + r_novia + r_viajes
faltante_total = max(0, meta_total_operativa - logrado_operativo)

st.subheader("💡 Diagnóstico de Flujo")
if faltante_total > 0:
    col_diag1, col_diag2 = st.columns([2,1])
    with col_diag1:
        st.warning(f"⚠️ Te faltan **${faltante_total:,.2f}** para cubrir tus metas prioritarias.")
        st.info(f"🔄 **Recirculación:** Actualmente, tus cubetas de ahorro/deuda están aportando **${ahorro_en_bajas:,.2f}** para intentar cubrir el hueco de arriba.")
    
    with col_diag2:
        if var_despues_dios > 0:
            st.write("¿Usar ingreso variable?")
            aplicar_rescate = st.checkbox("🔄 Aplicar Rescate Variable")
            if aplicar_rescate:
                # Inyectar variable a la cascada
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
                st.success(f"Rescate de ${rescate:,.2f} aplicado.")
else:
    st.success("✅ Todas tus metas prioritarias están cubiertas por el Ingreso Fijo.")

# ==========================================
# DISTRIBUCIÓN DEL VARIABLE (Si sobró algo)
# ==========================================
ahorro_var = var_despues_dios * 0.50
deuda_var = var_despues_dios * 0.30
reinversion_var = var_despues_dios * 0.20

emergencia_total = r_emerg + (ahorro_var * 0.50)
colchon_total = r_colchon + (ahorro_var * 0.25)
retiro_total = r_retiro + (ahorro_var * 0.25) + reinversion_var
deuda_total = r_deuda + deuda_var

# ==========================================
# VISUALIZACIÓN (DASHBOARD)
# ==========================================
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingreso Bruto", f"${(ingreso_fijo + ingreso_variable):,.2f}")
c2.metric("🏠 Gasto Operativo", f"${(r_renta + r_transp + r_novia + r_viajes):,.2f}")
c3.metric("💳 Total Deuda", f"${deuda_total:,.2f}")
c4.metric("📈 Total Ahorro", f"${(emergencia_total + colchon_total + retiro_total):,.2f}")

st.markdown("---")
# Gráfico de Llenado con línea de meta
df_plot = pd.DataFrame({
    'Cubeta': ['Renta', 'Transporte', 'Novia', 'Viajes', 'Deuda', 'Emerg', 'Colchón'],
    'Real': [r_renta, r_transp, r_novia, r_viajes, r_deuda, r_emerg, r_colchon],
    'Meta': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
})

fig = px.bar(df_plot, x='Cubeta', y=['Meta', 'Real'], barmode='overlay', 
             title="Estado de Llenado de la Cascada",
             color_discrete_sequence=['#e5e5e5', '#00CC96'])
st.plotly_chart(fig, use_container_width=True)

# Tabla de Transferencias
st.subheader("📋 Plan de Transferencias Final")
df_final = pd.DataFrame({
    "Destino": ["NU (Gastos)", "NU (Colchón)", "CETES", "GBM (Inversión)", "SPIN", "Deuda"],
    "Monto": [
        f"${(r_renta + r_transp + r_novia):,.2f}",
        f"${colchon_total:,.2f}",
        f"${emergencia_total:,.2f}",
        f"${retiro_total:,.2f}",
        f"${r_viajes:,.2f}",
        f"${deuda_total:,.2f}"
    ],
    "Nota": ["Inamovibles", "Ahorro Líquido", "Fondo de Emergencia", "Crecimiento Largo Plazo", "Ocio/Viajes", "Pagos Pendientes"]
})
st.table(df_final)
