import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Mi Dashboard Financiero", layout="wide", page_icon="💰")

st.title("📊 Dashboard Financiero Semanal")
st.markdown("---")

# ==========================================
# ENTRADA DE DATOS (Barra lateral)
# ==========================================
st.sidebar.header("Ingresos de la Semana")
ingreso_fijo = st.sidebar.number_input("Ingreso FIJO ($)", min_value=0.0, value=0.0, step=100.0)
ingreso_variable = st.sidebar.number_input("Ingreso VARIABLE ($)", min_value=0.0, value=0.0, step=100.0)

diezmo_pct = 0.10

# ==========================================
# LÓGICA MATEMÁTICA Y PROCESAMIENTO
# ==========================================
# Inicializar
renta_guardadito = novia = visitas = transporte = 0
colchon_fijo = emergencia_fijo = ahorro_libre_fijo = 0
ahorro_fijo = deuda_fijo = ocio_fijo = 0
fijo_despues_dios = 0

ahorro_var = deuda_var = reinversion = 0
emergencia_var = retiro_var = colchon_var = 0
var_despues_dios = 0

# FIJO
if ingreso_fijo > 0:
    fijo_despues_dios = ingreso_fijo * (1 - diezmo_pct)
    gasto_fijo = fijo_despues_dios * 0.75
    ahorro_fijo = fijo_despues_dios * 0.10
    deuda_fijo = fijo_despues_dios * 0.10
    ocio_fijo = fijo_despues_dios * 0.05

    renta_guardadito = gasto_fijo * 0.45
    novia = gasto_fijo * 0.20
    visitas = gasto_fijo * 0.13
    transporte = gasto_fijo - (renta_guardadito + novia + visitas)

    colchon_fijo = ahorro_fijo * 0.50
    emergencia_fijo = ahorro_fijo * 0.25
    ahorro_libre_fijo = ahorro_fijo * 0.25

# VARIABLE
if ingreso_variable > 0:
    var_despues_dios = ingreso_variable * (1 - diezmo_pct)
    ahorro_var = var_despues_dios * 0.50
    deuda_var = var_despues_dios * 0.30
    reinversion = var_despues_dios * 0.20

    emergencia_var = ahorro_var * 0.50
    retiro_var = ahorro_var * 0.25
    colchon_var = ahorro_var * 0.25

# ==========================================
# METAS Y ANÁLISIS DE COBERTURA
# ==========================================
meta_renta_mensual = 3500.0
meta_renta_semanal = meta_renta_mensual / 4
meta_novia_semanal = 500.0

factor_renta = (1 - diezmo_pct) * 0.75 * 0.45
factor_novia = (1 - diezmo_pct) * 0.75 * 0.20

ingreso_necesario_renta = meta_renta_semanal / factor_renta
ingreso_necesario_novia = meta_novia_semanal / factor_novia

ingreso_bruto_ideal = max(ingreso_necesario_renta, ingreso_necesario_novia)
ingreso_neto_ideal = ingreso_bruto_ideal * (1 - diezmo_pct)

cobertura_pct = (ingreso_fijo / ingreso_bruto_ideal * 100) if ingreso_bruto_ideal > 0 else 100.0
faltante_neto = max(0, ingreso_neto_ideal - fijo_despues_dios)

# ==========================================
# RESCATE TEMPORAL
# ==========================================
renta_final, novia_final, visitas_final, transporte_final = renta_guardadito, novia, visitas, transporte
gasto_fijo_final = gasto_fijo if ingreso_fijo > 0 else 0
rescate_aplicado = 0

if faltante_neto > 0 and var_despues_dios > 0:
    rescate_aplicado = min(faltante_neto, var_despues_dios)
    fijo_rescatado = fijo_despues_dios + rescate_aplicado
    
    gasto_fijo_final = fijo_rescatado * 0.75
    renta_final = gasto_fijo_final * 0.45
    novia_final = gasto_fijo_final * 0.20
    visitas_final = gasto_fijo_final * 0.13
    transporte_final = gasto_fijo_final - (renta_final + novia_final + visitas_final)

# CONSOLIDADOS
ingreso_total = ingreso_fijo + ingreso_variable
colchon_total = colchon_fijo + colchon_var
emergencia_total = emergencia_fijo + emergencia_var
retiro_total = retiro_var
inversion_gbm_total = retiro_total + reinversion
ocio_total = ocio_fijo

# ==========================================
# INTERFAZ DE USUARIO (DASHBOARD)
# ==========================================

# 1. KPIs Rápidos
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingreso Total Bruto", f"${ingreso_total:,.2f}")
col2.metric("Cobertura de Metas", f"{cobertura_pct:.1f}%")
col3.metric("Rescate Aplicado", f"${rescate_aplicado:,.2f}")
col4.metric("Total a Invertir/Ahorrar", f"${(emergencia_total + inversion_gbm_total + colchon_total):,.2f}")

st.markdown("---")

# 2. Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🏠 Distribución Gasto (NU)")
    if gasto_fijo_final > 0:
        df_pie = pd.DataFrame({
            'Categoría': ['Renta', 'Novia', 'Visitas', 'Transporte'],
            'Monto': [renta_final, novia_final, visitas_final, transporte_final]
        })
        fig_pie = px.pie(df_pie, values='Monto', names='Categoría', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Ingresa un monto para ver la distribución.")

with col_graf2:
    st.subheader("🎯 Termómetro de Metas")
    df_bar = pd.DataFrame({
        'Categoría': ['Renta', 'Renta', 'Novia', 'Novia'],
        'Tipo': ['Logrado', 'Meta', 'Logrado', 'Meta'],
        'Monto': [renta_final, meta_renta_semanal, novia_final, meta_novia_semanal]
    })
    fig_bar = px.bar(df_bar, x='Categoría', y='Monto', color='Tipo', barmode='group',
                     color_discrete_map={'Logrado': '#2ca02c', 'Meta': '#d62728'})
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 3. Tabla de Transferencias y CLABEs
st.subheader("💳 Destino de Fondos (Transferencias)")
df_transferencias = pd.DataFrame({
    "Plataforma": ["NU (Gastos y Colchón)", "CETES Directo (Emergencias)", "GBM+ (Retiro/Inversión)", "SPIN (Ocio)"],
    "Monto ($)": [
        f"${(gasto_fijo_final + colchon_total):,.2f}", 
        f"${emergencia_total:,.2f}", 
        f"${inversion_gbm_total:,.2f}", 
        f"${ocio_total:,.2f}"
    ],
    "CLABE / App": ["638180000126660124", "N/A (Desde App)", "601180400073884389", "728969000033664690"],
    "Detalles": [
        f"Renta: ${renta_final:,.2f} | Novia: ${novia_final:,.2f} | Colchón: ${colchon_total:,.2f} | Visitas: ${visitas_final:,.2f} | Transp: ${transporte_final:,.2f}",
        "Seguridad y liquidez a corto plazo",
        "Estrategia a largo plazo (Bolsa de Valores)",
        "Salidas y gustos personales"
    ]
})

st.table(df_transferencias)

# 4. Proyecciones
with st.expander("Ver Proyecciones Financieras a Futuro 🚀"):
    st.markdown("**🛡️ Fondo de Emergencias (CETES ~11% anual)**")
    semanas = 52
    tasa_cetes = 0.11 / semanas
    fv_cetes = emergencia_total * (((1 + tasa_cetes)**semanas - 1) / tasa_cetes) if emergencia_total > 0 else 0
    st.write(f"Si mantienes esta aportación semanal, en 1 año tendrás: **${fv_cetes:,.2f}**")

    st.markdown("**📈 Retiro / Inversión (GBM ~10% anual)**")
    tasa_gbm = 0.10 / semanas
    fv_gbm10 = inversion_gbm_total * (((1 + tasa_gbm)**(10*semanas) - 1) / tasa_gbm) if inversion_gbm_total > 0 else 0
    fv_gbm30 = inversion_gbm_total * (((1 + tasa_gbm)**(30*semanas) - 1) / tasa_gbm) if inversion_gbm_total > 0 else 0
    st.write(f"Proyección a 10 años: **${fv_gbm10:,.2f}**")
    st.write(f"Proyección a 30 años: **${fv_gbm30:,.2f}**")
