import streamlit as st
import pandas as pd

# ==========================================
# CONSTANTES (Porcentajes de Crecimiento)
# ==========================================
DIEZMO_PCT = 0.10
DEUDA_PCT = 0.30
INVERSION_PCT = 0.20
AHORRO_PCT = 0.50

# Metas Mínimas Inamovibles (Prioridad #1)
META_RENTA = 1000.0
META_TRANSPORTE = 300.0
META_NOVIA = 300.0
META_VIAJES = 200.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

# ==========================================
# INTERFAZ DE ENTRADA
# ==========================================
st.set_page_config(page_title="Flujo de Capital", layout="wide")
st.markdown("<h2 style='color:#d4af37;'>Flujo de Capital Semanal</h2>", unsafe_allow_html=True)

c_in1, c_in2, c_in3 = st.columns(3)
with c_in1:
    ingreso_fijo_bruto = st.number_input("INGR. FIJO BRUTO ($)", min_value=0.0, step=100.0, value=3500.0)
with c_in2:
    deducciones = st.number_input("DEDUCCIONES EXACTAS ($)", min_value=0.0, step=10.0, value=0.0, help="Pon en pesos lo que te retuvo la empresa")
with c_in3:
    ingreso_var_bruto = st.number_input("INGR. VARIABLE ($)", min_value=0.0, step=100.0, value=1000.0)

omitir_fijo = st.checkbox("OMITIR INGRESO FIJO", value=False, help="Actívalo si ya cubriste las metas mínimas con ahorros pasados.")
st.markdown("---")

# ==========================================
# LÓGICA DE DISTRIBUCIÓN CASCADA ESTRICTA
# ==========================================
fijo_disponible = max(0.0, ingreso_fijo_bruto - deducciones)

diezmo_fijo = fijo_disponible * DIEZMO_PCT if not omitir_fijo else 0.0
fijo_neto = fijo_disponible - diezmo_fijo

diezmo_var = ingreso_var_bruto * DIEZMO_PCT
var_neto = ingreso_var_bruto - diezmo_var

f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0.0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0.0

if omitir_fijo:
    v_aux = var_neto
    if v_aux > 0:
        v_deuda = v_aux * DEUDA_PCT
        v_retiro = v_aux * INVERSION_PCT
        v_ahorro_t = v_aux * AHORRO_PCT
        v_emerg = v_ahorro_t * 0.50
        v_colchon = v_ahorro_t * 0.50
else:
    f_aux = fijo_neto
    f_renta = min(f_aux, META_RENTA); f_aux -= f_renta
    f_transp = min(f_aux, META_TRANSPORTE); f_aux -= f_transp
    f_novia = min(f_aux, META_NOVIA); f_aux -= f_novia
    f_viajes = min(f_aux, META_VIAJES); f_aux -= f_viajes
    
    if f_aux > 0:
        f_deuda = f_aux * DEUDA_PCT
        f_retiro = f_aux * INVERSION_PCT
        f_ahorro_t = f_aux * AHORRO_PCT
        f_emerg = f_ahorro_t * 0.50
        f_colchon = f_ahorro_t * 0.50

v_aux = var_neto
v_renta = min(v_aux, max(0.0, META_RENTA - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0.0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0.0, META_NOVIA - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0.0, META_VIAJES - f_viajes)); v_aux -= v_viajes

if v_aux > 0 and not omitir_fijo:
    v_deuda = v_aux * DEUDA_PCT
    v_retiro = v_aux * INVERSION_PCT
    v_ahorro_t = v_aux * AHORRO_PCT
    v_emerg = v_ahorro_t * 0.50
    v_colchon = v_ahorro_t * 0.50

deficit_total = max(0.0, meta_inamovibles_total - (f_renta + v_renta + f_transp + v_transp + f_novia + v_novia + f_viajes + v_viajes))

retiro_total = f_retiro + v_retiro
tasa_semanal_real = (0.07 / 52)
proyeccion = retiro_total * (((1 + tasa_semanal_real)**(30 * 52)) - 1) / tasa_semanal_real if retiro_total > 0 else 0.0

# ==========================================
# VISUALIZACIÓN DE RESULTADOS (Lo que faltaba)
# ==========================================
st.markdown("### RESUMEN SEMANAL")
c1, c2, c3, c4 = st.columns(4)
with c1: 
    st.metric("INGRESO NETO EVALUADO", f"${(fijo_disponible + var_neto):,.2f}")
with c2: 
    st.metric("AHORRO GENERADO", f"${(f_emerg + v_emerg + f_colchon + v_colchon):,.2f}")
with c3: 
    st.metric("PATRIMONIO 30 AÑOS", f"${proyeccion:,.2f}")
with c4:
    if omitir_fijo:
        st.metric("ESTADO MÍNIMOS", "CUBIERTOS ✅")
    elif deficit_total > 0.01:
        st.metric("DÉFICIT", f"-${deficit_total:,.2f}")
    else:
        st.metric("ESTADO MÍNIMOS", "CUBIERTOS ✅")

st.markdown("### DESGLOSE POR SOBRE")
df_data = [
    {"Sobre": "Diezmo", "Meta": "S/M", "Fijo": f"${diezmo_fijo:,.2f}", "Variable": f"${diezmo_var:,.2f}", "Total": f"${(diezmo_fijo+diezmo_var):,.2f}", "Fit": "⚪ OK"},
    {"Sobre": "Renta", "Meta": f"${META_RENTA:,.2f}", "Fijo": f"${f_renta:,.2f}", "Variable": f"${v_renta:,.2f}", "Total": f"${(f_renta+v_renta):,.2f}", "Fit": "🔵 Cubierto" if omitir_fijo else (f"🟢 OK" if (f_renta+v_renta)>=META_RENTA else f"🔴 -${META_RENTA-(f_renta+v_renta):,.2f}")},
    {"Sobre": "Transporte", "Meta": f"${META_TRANSPORTE:,.2f}", "Fijo": f"${f_transp:,.2f}", "Variable": f"${v_transp:,.2f}", "Total": f"${(f_transp+v_transp):,.2f}", "Fit": "🔵 Cubierto" if omitir_fijo else (f"🟢 OK" if (f_transp+v_transp)>=META_TRANSPORTE else f"🔴 -${META_TRANSPORTE-(f_transp+v_transp):,.2f}")},
    {"Sobre": "Novia", "Meta": f"${META_NOVIA:,.2f}", "Fijo": f"${f_novia:,.2f}", "Variable": f"${v_novia:,.2f}", "Total": f"${(f_novia+v_novia):,.2f}", "Fit": "🔵 Cubierto" if omitir_fijo else (f"🟢 OK" if (f_novia+v_novia)>=META_NOVIA else f"🔴 -${META_NOVIA-(f_novia+v_novia):,.2f}")},
    {"Sobre": "Viajes", "Meta": f"${META_VIAJES:,.2f}", "Fijo": f"${f_viajes:,.2f}", "Variable": f"${v_viajes:,.2f}", "Total": f"${(f_viajes+v_viajes):,.2f}", "Fit": "🔵 Cubierto" if omitir_fijo else (f"🟢 OK" if (f_viajes+v_viajes)>=META_VIAJES else f"🔴 -${META_VIAJES-(f_viajes+v_viajes):,.2f}")},
    {"Sobre": "Deuda", "Meta": "S/M", "Fijo": f"${f_deuda:,.2f}", "Variable": f"${v_deuda:,.2f}", "Total": f"${(f_deuda+v_deuda):,.2f}", "Fit": "⚪ OK"},
    {"Sobre": "Emergencias", "Meta": "S/M", "Fijo": f"${f_emerg:,.2f}", "Variable": f"${v_emerg:,.2f}", "Total": f"${(f_emerg+v_emerg):,.2f}", "Fit": "⚪ OK"},
    {"Sobre": "Colchón", "Meta": "S/M", "Fijo": f"${f_colchon:,.2f}", "Variable": f"${v_colchon:,.2f}", "Total": f"${(f_colchon+v_colchon):,.2f}", "Fit": "⚪ OK"},
    {"Sobre": "Retiro (Inversión)", "Meta": "S/M", "Fijo": f"${f_retiro:,.2f}", "Variable": f"${v_retiro:,.2f}", "Total": f"${(f_retiro+v_retiro):,.2f}", "Fit": "⚪ OK"}
]

st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
