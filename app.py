import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# CONFIGURACIÓN PREMIUM Y ESTILOS
# ==========================================
st.set_page_config(page_title="Dashboard Cascada Pro", layout="wide", page_icon="💧")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');

    .stApp { background-color: #000000; color: #ffffff; font-family: 'Montserrat', sans-serif; }
    p, span, label, div, li { color: #ffffff !important; }

    h2, h3, h4, h5, h6 {
        color: #d4af37 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .titulo-personalizado {
        color: #FF0000 !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding-bottom: 20px;
    }
    
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #d4af3733; }
    [data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 2.2rem !important; font-weight: 600 !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 0.9rem !important; text-transform: uppercase; letter-spacing: 1px; }
    
    div[data-testid="metric-container"] {
        background-color: #111111;
        border: 1px solid #d4af3744;
        padding: 20px;
        border-radius: 4px;
    }
    
    div.stCodeBlock { background-color: #111111 !important; border: 1px solid #d4af37 !important; border-radius: 0px !important; }
    code { color: #d4af37 !important; font-size: 1.1rem !important; }
    .stDataFrame [data-testid="stTable"] { background-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="titulo-personalizado">¿CUÁNTO TE PAGARON ILICH?</h1>', unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# CONSTANTES Y CLABES
# ==========================================
DIEZMO_PCT = 0.10; GASTO_PCT = 0.65; DEUDA_PCT = 0.10; AHORRO_PCT = 0.10; INVERSION_PCT = 0.15
META_RENTA = 875.0; META_TRANSPORTE = 430.0; META_NOVIA = 500.0; META_VIAJES = 300.0
meta_inamovibles_total = META_RENTA + META_TRANSPORTE + META_NOVIA + META_VIAJES

CUENTAS = {
    "NU (Cajita)": "638180000126660124", "NU (Gasto)": "638180000126660124",
    "GBM+": "601180400073884389", "SPIN": "728969000033664690",
    "Cuenta Diezmo": "PENDIENTE", "Pago Deuda": "PENDIENTE", "CETES": "PENDIENTE"
}

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#d4af37;'>Ingresos de la Semana</h3>", unsafe_allow_html=True)
    ingreso_fijo_bruto = st.number_input("FIJO ($)", min_value=0.0, value=0.0, step=100.0)
    ingreso_var_bruto = st.number_input("VARIABLE ($)", min_value=0.0, value=0.0, step=100.0)

# ==========================================
# LÓGICA (BACKEND)
# ==========================================
diezmo_fijo = ingreso_fijo_bruto * DIEZMO_PCT; fijo_neto = ingreso_fijo_bruto - diezmo_fijo
diezmo_var = ingreso_var_bruto * DIEZMO_PCT; var_neto = ingreso_var_bruto - diezmo_var

f_renta = f_transp = f_novia = f_viajes = f_deuda = f_emerg = f_colchon = f_retiro = 0
v_renta = v_transp = v_novia = v_viajes = v_deuda = v_emerg = v_colchon = v_retiro = 0

capacidad_gasto_fijo = fijo_neto * GASTO_PCT
if capacidad_gasto_fijo >= meta_inamovibles_total:
    p_renta, p_transp = META_RENTA/meta_inamovibles_total, META_TRANSPORTE/meta_inamovibles_total
    p_novia, p_viajes = META_NOVIA/meta_inamovibles_total, META_VIAJES/meta_inamovibles_total
    f_renta, f_transp = capacidad_gasto_fijo*p_renta, capacidad_gasto_fijo*p_transp
    f_novia, f_viajes = capacidad_gasto_fijo*p_novia, capacidad_gasto_fijo*p_viajes
    f_deuda, f_retiro = fijo_neto*DEUDA_PCT, fijo_neto*INVERSION_PCT
    f_emerg, f_colchon = (fijo_neto*AHORRO_PCT)*0.5, (fijo_neto*AHORRO_PCT)*0.5
else:
    f_aux = fijo_neto
    f_renta = min(f_aux, META_RENTA); f_aux -= f_renta
    f_transp = min(f_aux, META_TRANSPORTE); f_aux -= f_transp
    f_novia = min(f_aux, META_NOVIA); f_aux -= f_novia
    f_viajes = min(f_aux, META_VIAJES); f_aux -= f_viajes
    f_deuda = min(f_aux, 400.0); f_aux -= f_deuda
    f_emerg = min(f_aux, 250.0); f_aux -= f_emerg
    f_colchon = min(f_aux, 250.0); f_aux -= f_colchon
    f_retiro = f_aux

v_aux = var_neto
v_renta = min(v_aux, max(0, META_RENTA - f_renta)); v_aux -= v_renta
v_transp = min(v_aux, max(0, META_TRANSPORTE - f_transp)); v_aux -= v_transp
v_novia = min(v_aux, max(0, META_NOVIA - f_novia)); v_aux -= v_novia
v_viajes = min(v_aux, max(0, META_VIAJES - f_viajes)); v_aux -= v_viajes

if v_aux > 0:
    v_ahorro_t = v_aux * 0.50
    v_deuda, v_retiro = v_aux * 0.30, v_aux * 0.20
    v_emerg, v_colchon = v_ahorro_t * 0.50, v_ahorro_t * 0.50

# Cálculos de Déficit y Rescate
rescate_total = v_renta + v_transp + v_novia + v_viajes
if var_neto > 0 and rescate_total > 0:
    pct_rescate = (rescate_total / var_neto) * 100
    texto_rescate = f"{pct_rescate:.1f}%"
else:
    texto_rescate = "Nada"

asignado_basicos = f_renta + v_renta + f_transp + v_transp + f_novia + v_novia + f_viajes + v_viajes
deficit_basico = meta_inamovibles_total - asignado_basicos

# Creación de DataFrame
data = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Meta": 0, "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Meta": META_RENTA, "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Meta": META_TRANSPORTE, "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Meta": META_NOVIA, "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Meta": META_VIAJES, "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Meta": 0, "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Meta": 0, "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Meta": 0, "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Meta": 0, "Fijo": f_retiro, "Variable": v_retiro},
]
df = pd.DataFrame(data)
df["Total"] = df["Fijo"] + df["Variable"]
df["Profit"] = df.apply(lambda x: max(0, x["Total"] - x["Meta"]) if x["Meta"] > 0 else 0, axis=1)

# ==========================================
# CÁLCULOS SUPERIORES (S&P 500)
# ==========================================
ingreso_total_bruto = ingreso_fijo_bruto + ingreso_var_bruto
ahorro_semanal_generado = f_emerg + v_emerg + f_colchon + v_colchon
retiro_total_semanal = f_retiro + v_retiro

# Cálculo Interés Compuesto S&P 500 (10% anual a 30 años)
r_semanal = 0.10 / 52
semanas_30_anios = 30 * 52
proyeccion_sp500 = retiro_total_semanal * (((1 + r_semanal)**semanas_30_anios) - 1) / r_semanal

# ==========================================
# FRONTEND
# ==========================================
# Fila 1: Resumen General
st.markdown("<h4 style='color:#ffffff; text-align:center;'>RESUMEN GENERAL</h4>", unsafe_allow_html=True)
r1, r2, r3 = st.columns(3)
with r1: st.metric("INGRESO TOTAL BRUTO", f"${ingreso_total_bruto:,.2f}")
with r2: st.metric("AHORRO GENERADO (EMERG. + COLCHÓN)", f"${ahorro_semanal_generado:,.2f}")
with r3: 
    st.markdown(f"""
        <div data-testid='metric-container'>
            <label data-testid='stMetricLabel'>PROYECCIÓN S&P 500 (30 AÑOS)</label>
            <div data-testid='stMetricValue' style='color: #00E676 !important;'>${proyeccion_sp500:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Fila 2: Estatus del Sistema
st.markdown("<h4 style='color:#ffffff; text-align:center;'>MÉTRICAS DEL SISTEMA</h4>", unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
with m1: st.metric("NETO SEMANAL", f"${(fijo_neto + var_neto):,.2f}")
with m2: st.metric("% VAR. USADO EN RESCATE", texto_rescate)
with m3: 
    total_profit = df['Profit'].sum()
    if deficit_basico > 0.01:
        st.markdown(f"""
            <div data-testid='metric-container' style='border-color: #FF000044;'>
                <label data-testid='stMetricLabel' style='color: #FF0000 !important;'>DÉFICIT (FALTANTE MÍNIMOS)</label>
                <div data-testid='stMetricValue' style='color: #FF0000 !important;'>-${deficit_basico:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        color_profit = "#00E676" if total_profit > 0 else "#d4af37"
        st.markdown(f"""
            <div data-testid='metric-container'>
                <label data-testid='stMetricLabel'>PROFIT GENERADO (EXCEDENTE)</label>
                <div data-testid='stMetricValue' style='color: {color_profit} !important;'>${total_profit:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- TABLA CON ESTILOS BLINDADOS A PRUEBA DE FALLOS ---
st.subheader("Desglose de Capital")

def apply_styles(x):
    # Creamos un dataframe vacío con la misma estructura para inyectar CSS puro
    styles = pd.DataFrame('', index=x.index, columns=x.columns)
    for col in x.columns:
        if col == 'Profit':
            styles[col] = ['color: #00E676 !important; font-weight: 800 !important;' if v > 0 else 'color: #ffffff !important;' for v in x[col]]
        elif col in ['Meta', 'Fijo', 'Variable', 'Total']:
            styles[col] = ['color: #d4af37 !important;' if isinstance(v, (int, float)) and v > 0 else 'color: #ffffff !important;' for v in x[col]]
        else:
            styles[col] = 'color: #ffffff !important;'
    return styles

styled_df = df.style.apply(apply_styles, axis=None)\
    .format({
        "Meta": "${:,.2f}", "Fijo": "${:,.2f}", "Variable": "${:,.2f}", 
        "Total": "${:,.2f}", "Profit": "${:,.2f}"
    })\
    .set_properties(**{'background-color': '#000000', 'border-color': '#d4af3722'})

st.dataframe(styled_df, use_container_width=True, hide_index=True)

st.markdown("---")

# --- TRANSFERENCIAS ---
c1, c_esp, c2 = st.columns([1, 0.1, 1.2])

with c1:
    st.subheader("🏦 CLABEs (Copiables)")
    df_bancos = df.groupby("Plataforma")["Total"].sum().reset_index()
    df_bancos = df_bancos[df_bancos["Total"] > 0]
    
    for _, row in df_bancos.iterrows():
        banco = row["Plataforma"]; monto = row["Total"]; clabe_nuda = CUENTAS.get(banco, "PENDIENTE")
        
        st.markdown(f"<p style='margin-bottom:0px; font-weight:600; color:#d4af37;'>{banco}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:1.2rem; margin-top:0px;'>Total: <b style='color:#00E676;'>${monto:,.2f}</b></p>", unsafe_allow_html=True)
        st.code(clabe_nuda, language=None)
        st.markdown("<br>", unsafe_allow_html=True)

with c2:
    st.subheader("Distribución Visual")
    fig = px.pie(df_bancos, values='Total', names='Plataforma', hole=0.7,
                 color_discrete_sequence=['#d4af37', '#ffffff', '#444444', '#888888', '#00E676'])
    fig.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(family="Montserrat", color="#ffffff")
    )
    st.plotly_chart(fig, use_container_width=True)
