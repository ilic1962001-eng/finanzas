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
st.sidebar.caption("Prioridad 1 a 7. Si bajas una meta, el dinero 'sube' para cubrir las de arriba.")

meta_renta = st.sidebar.number_input("1. Renta (Meta: 3500/mes)", value=875.0, step=25.0)
meta_transporte = st.sidebar.number_input("2. Transporte", value=300.0, step=25.0)
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

# Cálculos de Objetivo (Fórmulas MATLAB originales para la Auditoría)
obj_renta = (fijo_neto * 0.75) * 0.45
obj_novia = (fijo_neto * 0.75) * 0.20
obj_viajes = (fijo_neto * 0.75) * 0.13
obj_transp = (fijo_neto * 0.75) - (obj_renta + obj_novia + obj_viajes)
obj_deuda = fijo_neto * 0.10
obj_emerg = (fijo_neto * 0.10) * 0.25
obj_colchon = (fijo_neto * 0.10) * 0.50

# ==========================================
# EJECUCIÓN DE LA CASCADA (FIJO)
# ==========================================
fijo_aux = fijo_neto
# Fondos asignados desde el Ingreso FIJO
f_renta = min(fijo_aux, meta_renta); fijo_aux -= f_renta
f_transp = min(fijo_aux, meta_transporte); fijo_aux -= f_transp
f_novia = min(fijo_aux, meta_novia); fijo_aux -= f_novia
f_viajes = min(fijo_aux, meta_viajes); fijo_aux -= f_viajes
f_deuda = min(fijo_aux, meta_deuda); fijo_aux -= f_deuda
f_emerg = min(fijo_aux, meta_emergencias); fijo_aux -= f_emerg
f_colchon = min(fijo_aux, meta_colchon); fijo_aux -= f_colchon
f_retiro = fijo_aux # Todo lo que sobre del fijo va a retiro

# ==========================================
# RESCATE Y MANEJO DEL VARIABLE
# ==========================================
meta_inamovibles = meta_renta + meta_transporte + meta_novia + meta_viajes
logrado_fijo_inamov = f_renta + f_transp + f_novia + f_viajes
faltante_inamov = max(0, meta_inamovibles - logrado_fijo_inamov)

v_rescate = 0
v_deuda = v_emerg = v_colchon = v_retiro = v_reinversion = 0

st.subheader("💡 Diagnóstico de Flujo")
if faltante_inamov > 0:
    st.warning(f"⚠️ El ingreso fijo no cubre los Inamovibles. Faltan **${faltante_inamov:,.2f}**.")
    if var_neto > 0:
        if st.checkbox("🔄 Aplicar rescate con Ingreso Variable"):
            v_rescate = min(faltante_inamov, var_neto)
            var_disponible = var_neto - v_rescate
            st.success(f"✅ Se rescataron ${v_rescate:,.2f} para cubrir gastos.")
        else:
            var_disponible = var_neto
    else:
        var_disponible = 0
else:
    if ingreso_fijo_bruto > 0:
        st.success("✅ Ingreso Fijo suficiente para cubrir metas básicas.")
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
# AUDITORÍA DE DIFERENCIAS
# ==========================================
st.markdown("---")
st.subheader("⚖️ Auditoría: ¿Cómo el ahorro de abajo ayuda arriba?")

df_auditoria = pd.DataFrame({
    "Categoría": ["Renta", "Transporte", "Novia", "Viajes", "Deuda", "Emergencia", "Colchón"],
    "Ideal (MATLAB)": [obj_renta, obj_transp, obj_novia, obj_viajes, obj_deuda, obj_emerg, obj_colchon],
    "Meta Cascada": [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
})
df_auditoria["Ahorro Generado"] = df_auditoria["Ideal (MATLAB)"] - df_auditoria["Meta Cascada"]

def color_diff(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}; font-weight: bold'

# AQUÍ ESTÁ LA CORRECCIÓN DEL ERROR DE PANDAS
formato_columnas = {"Ideal (MATLAB)": "${:,.2f}", "Meta Cascada": "${:,.2f}", "Ahorro Generado": "${:,.2f}"}
st.dataframe(df_auditoria.style.format(formato_columnas).map(color_diff, subset=['Ahorro Generado']), use_container_width=True)

ahorro_total = df_auditoria["Ahorro Generado"].sum()
if ahorro_total > 0 and ingreso_fijo_bruto > 0:
    st.info(f"✨ Al reducir metas en cubetas bajas o ser más eficiente, liberaste **${ahorro_total:,.2f}** que fluyen a tus prioridades o inversiones.")

# ==========================================
# TRANSFERENCIAS FINALES (DESGLOSADAS)
# ==========================================
st.markdown("---")
st.subheader("💳 Plan de Transferencias Final (Desglosado)")

# Cálculo de montos por plataforma y origen
# NU: Renta + Transp + Novia + Colchones
nu_fijo = f_renta + f_transp + f_novia + f_colchon + (v_rescate if v_rescate > 0 else 0)
nu_var = v_colchon
nu_total = nu_fijo + nu_var

# CETES: Emergencias
cetes_fijo = f_emerg
cetes_var = v_emerg
cetes_total = cetes_fijo + cetes_var

# GBM: Retiro + Reinversión
gbm_fijo = f_retiro
gbm_var = v_retiro + v_reinversion
gbm_total = gbm_fijo + gbm_var

# SPIN: Viajes
spin_fijo = f_viajes
spin_total = spin_fijo

df_final = pd.DataFrame({
    "Plataforma": ["NU (Gastos/Colchón)", "CETES", "GBM+", "SPIN", "Deuda"],
    "Monto Total": [nu_total, cetes_total, gbm_total, spin_total, f_deuda + v_deuda],
    "Desde Fijo": [nu_fijo, cetes_fijo, gbm_fijo, spin_fijo, f_deuda],
    "Desde Variable": [nu_var, cetes_var, gbm_var, 0, v_deuda],
    "CLABE / App": ["638180000126660124", "App Cetes", "601180400073884389", "728969000033664690", "N/A"]
})

# Formato específico para la tabla final
formato_final = {"Monto Total": "${:,.2f}", "Desde Fijo": "${:,.2f}", "Desde Variable": "${:,.2f}"}
st.table(df_final.style.format(formato_final))

# ==========================================
# VISUALIZACIÓN
# ==========================================
st.markdown("---")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.write("**💧 Llenado de Cascada**")
    df_bar = pd.DataFrame({
        'Cubeta': ['Renta', 'Transp', 'Novia', 'Viajes', 'Deuda', 'Emerg', 'Colchón'],
        'Nivel Real': [f_renta + v_rescate, f_transp, f_novia, f_viajes, f_deuda, f_emerg, f_colchon],
        'Meta': [meta_renta, meta_transporte, meta_novia, meta_viajes, meta_deuda, meta_emergencias, meta_colchon]
    })
    
    fig = px.bar(df_bar, x='Cubeta', y=['Meta', 'Nivel Real'], barmode='overlay', color_discrete_sequence=['#e5e5e5', '#00CC96'])
    st.plotly_chart(fig, use_container_width=True)

with col_g2:
    st.write("**📈 Composición del Ahorro Total**")
    df_pie = pd.DataFrame({
        'Origen': ['Fondo Emergencia', 'Inversión GBM', 'Colchón NU'],
        'Monto': [cetes_total, gbm_total, f_colchon + v_colchon]
    })
    if cetes_total + gbm_total + f_colchon + v_colchon > 0:
        st.plotly_chart(px.pie(df_pie, values='Monto', names='Origen', hole=0.4), use_container_width=True)
    else:
        st.info("Ingresa montos para visualizar tu ahorro.")
