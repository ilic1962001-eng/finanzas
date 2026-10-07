import streamlit as st
import pandas as pd

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Mi vida con Mirssa ✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CONSTANTES FINANCIERAS (SOBRES)
# =========================================================

# Base semanal
BASE_SEMANAL = 8500.0

# 1. Diezmo
DIEZMO_PCT = 0.10

# 2. Prioridades estrictas (Cantidades exactas por semana)
GASTOS_FIJOS_SEMANALES = 2100.0
SGMM_SEMANAL = 800.0
PPR_SEMANAL = 900.0

# 3. Secundarios
IMPUESTO_QA_SEMANAL = 500.0
DEUDA_SEMANAL = 500.0
EMERGENCIA_SEMANAL = 256.0
DISPONIBLE_MINIMO = 1000.0
SP500_SEMANAL = 500.0
OCIO_SEMANAL = 243.0

# 4. Efecto gatillo (Porcentajes para el excedente arriba de $8,500)
GATILLO_CRECIMIENTO = 0.50
GATILLO_SP500 = 0.25
GATILLO_DEUDA = 0.15
GATILLO_DISPONIBLE = 0.10

# =========================================================
# CUENTAS BANCARIAS
# =========================================================

BANCOS = [
    {
        "nombre": "Revolut",
        "clabe": "646990404064534378",
        "descripcion": "Diezmo, Emergencias y Crecimiento"
    },
    {
        "nombre": "Nu",
        "clabe": "638180000126660124",
        "descripcion": "Gastos Fijos y SGMM"
    },
    {
        "nombre": "GBM",
        "clabe": "601180400073884389",
        "descripcion": "S&P 500"
    },
    {
        "nombre": "Santander LikeU",
        "clabe": "014180140158246414",
        "descripcion": "Deuda y Ocio"
    },
    {
        "nombre": "Hey Banco",
        "clabe": "APARTADO INTERNO",
        "descripcion": "PPR e Impuestos QA"
    },
    {
        "nombre": "Spin by Oxxo",
        "clabe": "728969000033664690",
        "descripcion": "Dinero Disponible"
    }
]

# =========================================================
# SESSION STATE
# =========================================================

if "fijo_val" not in st.session_state:
    st.session_state.fijo_val = 3462.0
if "deduc_val" not in st.session_state:
    st.session_state.deduc_val = 0.0
if "var_val" not in st.session_state:
    st.session_state.var_val = 5000.0
if "exito_trigger" not in st.session_state:
    st.session_state.exito_trigger = False

for i in range(6):
    key = f"chk_banco_{i}"
    if key not in st.session_state:
        st.session_state[key] = False

# =========================================================
# FUNCIÓN CONFIRMAR
# =========================================================

def confirmar_deposito():
    st.session_state.exito_trigger = True
    st.session_state.fijo_val = 0.0
    st.session_state.deduc_val = 0.0
    st.session_state.var_val = 0.0
    for i in range(6):
        st.session_state[f"chk_banco_{i}"] = False

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.titulo {
    font-size: 3rem; font-weight: 800; text-align: center;
    margin-bottom: 0.2rem; background: linear-gradient(90deg, #ff4b91, #8b5cf6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitulo { text-align: center; color: #888; margin-bottom: 2rem; }
.metric-card {
    padding: 1.2rem; border-radius: 18px; border: 1px solid rgba(128,128,128,0.20);
    text-align: center; background: rgba(128,128,128,0.05);
}
.bank-card {
    padding: 1rem; border-radius: 16px; border: 1px solid rgba(128,128,128,0.20);
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# ENCABEZADO
# =========================================================

st.markdown('<div class="titulo">Mi vida con Mirssa ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Tu dinero trabajando para tu futuro ❤️</div>', unsafe_allow_html=True)

# =========================================================
# INPUTS
# =========================================================

col1, col2, col3 = st.columns(3)
with col1:
    ingreso_fijo = st.number_input("💵 Tu Sueldo Fijo ($)", min_value=0.0, step=100.0, key="fijo_val")
with col2:
    deducciones = st.number_input("✂️ ¿Te quitaron algo? ($)", min_value=0.0, step=100.0, key="deduc_val")
with col3:
    ingreso_variable = st.number_input("📈 Tus Extras (Variable) ($)", min_value=0.0, step=100.0, key="var_val")

omitir_fijos = st.checkbox("✨ Ya pagué los gastos fijos esta semana (Omitir Fijo)")

# =========================================================
# SISTEMA DE SOBRES (CASCADA ESTRICTA)
# =========================================================

fijo_neto = max(0.0, ingreso_fijo - deducciones)
ingreso_total = fijo_neto + ingreso_variable
dinero_restante = ingreso_total

# 1. DIEZMO (Siempre el 10% del total, innegociable)
diezmo = ingreso_total * DIEZMO_PCT
dinero_restante = max(0.0, dinero_restante - diezmo)

# 2. GASTOS FIJOS ($2,100)
gastos_fijos = 0.0
if not omitir_fijos:
    gastos_fijos = min(GASTOS_FIJOS_SEMANALES, dinero_restante)
    dinero_restante = max(0.0, dinero_restante - gastos_fijos)

# 3. SGMM ($800)
sgmm = min(SGMM_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - sgmm)

# 4. PPR ($900)
ppr = min(PPR_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - ppr)

# 5. TODO LO DEMÁS (En orden de importancia)
impuesto_qa = min(min(ingreso_variable, IMPUESTO_QA_SEMANAL), dinero_restante)
dinero_restante = max(0.0, dinero_restante - impuesto_qa)

deuda_base = min(DEUDA_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - deuda_base)

emergencia = min(EMERGENCIA_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - emergencia)

disponible_base = min(DISPONIBLE_MINIMO, dinero_restante)
dinero_restante = max(0.0, dinero_restante - disponible_base)

sp500_base = min(SP500_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - sp500_base)

ocio = min(OCIO_SEMANAL, dinero_restante)
dinero_restante = max(0.0, dinero_restante - ocio)

# =========================================================
# CÁLCULO DE CRECIMIENTO Y GATILLO
# =========================================================

# El Excedente existe si ganaste más de la base de $8,500
excedente = max(0.0, ingreso_total - BASE_SEMANAL)

# El crecimiento base es todo el sobrante ANTES de tocar el excedente
if excedente > 0:
    crecimiento_base = max(0.0, dinero_restante - excedente)
else:
    crecimiento_base = dinero_restante

# Si hay excedente (gatillo), lo repartimos:
gatillo_crecimiento = excedente * GATILLO_CRECIMIENTO
gatillo_sp500 = excedente * GATILLO_SP500
gatillo_deuda = excedente * GATILLO_DEUDA
gatillo_disponible = excedente * GATILLO_DISPONIBLE

# Totales finales (Base + Gatillo)
crecimiento = crecimiento_base + gatillo_crecimiento
sp500_total = sp500_base + gatillo_sp500
deuda_total = deuda_base + gatillo_deuda
disponible = disponible_base + gatillo_disponible

# =========================================================
# MÉTRICAS Y TABLAS
# =========================================================

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("💵 Dinero en Mano", f"${disponible:,.0f}")
with col2: st.metric("🚀 Crecimiento", f"${crecimiento:,.0f}")
with col3: st.metric("📈 S&P 500", f"${sp500_total:,.0f}")
with col4: st.metric("💎 Inversión PPR", f"${ppr:,.0f}")

if excedente > 0:
    st.success(f"⚡ EFECTO GATILLO ACTIVADO: Ganaste ${excedente:,.0f} arriba de tu base de $8,500.")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🚀 Crecimiento", f"+${gatillo_crecimiento:,.0f}")
    with c2: st.metric("📈 S&P 500", f"+${gatillo_sp500:,.0f}")
    with c3: st.metric("💳 Deuda", f"+${gatillo_deuda:,.0f}")
    with c4: st.metric("💵 Disponible", f"+${gatillo_disponible:,.0f}")
else:
    st.info("💡 Estás trabajando dentro de tu presupuesto base de $8,500.")

datos = [
    ["1. Diezmo", diezmo],
    ["2. Gastos Fijos", gastos_fijos],
    ["3. SGMM", sgmm],
    ["4. PPR", ppr],
    ["5. Impuestos QA", impuesto_qa],
    ["6. Deuda", deuda_total],
    ["7. Emergencias", emergencia],
    ["8. Disponible", disponible],
    ["9. S&P 500", sp500_total],
    ["10. Ocio", ocio],
    ["11. Crecimiento", crecimiento]
]
df = pd.DataFrame(datos, columns=["Sobre / Categoría", "Cantidad"])
df["Cantidad"] = df["Cantidad"].round(2)
st.subheader("📊 Distribución de Sobres (Cascada)")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("💰 Resumen financiero")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<div class="metric-card"><h3>Presupuesto Base</h3><h2>${BASE_SEMANAL:,.0f}</h2><p>Tu estilo de vida se organiza alrededor de esta cantidad.</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><h3>Dinero Libre</h3><h2>${disponible:,.0f}</h2><p>Dinero que puedes utilizar sin tocar tus objetivos.</p></div>', unsafe_allow_html=True)

# =========================================================
# CUENTAS BANCARIAS
# =========================================================

st.subheader("🏦 ¿A dónde mandar el dinero?")

montos_bancos = [
    diezmo + emergencia + crecimiento,  # Revolut
    gastos_fijos + sgmm,                # Nu
    sp500_total,                        # GBM
    deuda_total + ocio,                 # Santander LikeU
    ppr + impuesto_qa,                  # Hey Banco
    disponible                          # Spin by Oxxo
]

for i, banco in enumerate(BANCOS):
    monto = montos_bancos[i]
    st.markdown(
        f"""
        <div class="bank-card">
            <h4>{banco["nombre"]}</h4>
            <p>{banco["descripcion"]}</p>
            <p><b>CLABE:</b> {banco["clabe"]}</p>
            <h3>${monto:,.2f}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.checkbox("✅ Listo.", key=f"chk_banco_{i}")

# =========================================================
# BOTÓN FINAL Y CONFIRMACIÓN
# =========================================================

st.markdown("---")
st.button("LISTO BB, DINERO GUARDADO ✨", on_click=confirmar_deposito, use_container_width=True)

if st.session_state.exito_trigger:
    st.balloons()
    st.success("✨ ¡Listo BB! Tu dinero ya tiene trabajo. Ahora deja que tu yo del futuro te lo agradezca. ❤️")
    st.audio("https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg")
