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
# CONSTANTES FINANCIERAS
# =========================================================

# Base semanal
BASE_SEMANAL = 8500.0
DISPONIBLE_MINIMO = 1000.0

# Porcentajes
DIEZMO_PCT = 0.10

# Reservas / objetivos semanales
IMPUESTO_QA_SEMANAL = 500.0
SGMM_SEMANAL = 800.0
PPR_SEMANAL = 4000.0 * 12 / 52

GASTOS_FIJOS_MENSUALES = (
    1500.0 +   # Renta / hermano
    2500.0 +   # Universidad
    4000.0 +   # Mamá
    1500.0     # Contador
)

GASTOS_FIJOS_SEMANALES = GASTOS_FIJOS_MENSUALES * 12 / 52

# Inversiones / objetivos
SP500_SEMANAL = 500.0
DEUDA_SEMANAL = 500.0
EMERGENCIA_SEMANAL = 256.0
OCIO_SEMANAL = 243.0

# Efecto gatillo
GATILLO_CRECIMIENTO = 0.50
GATILLO_SP500 = 0.25
GATILLO_DEUDA = 0.15
GATILLO_DISPONIBLE = 0.10

# =========================================================
# CUENTAS BANCARIAS
# NO MODIFICAR
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
        "descripcion": "Novia"
    },
    {
        "nombre": "Spin by Oxxo",
        "clabe": "728969000033664690",
        "descripcion": "Opcional"
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

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.titulo {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.2rem;
    background: linear-gradient(90deg, #ff4b91, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitulo {
    text-align: center;
    color: #888;
    margin-bottom: 2rem;
}

.metric-card {
    padding: 1.2rem;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.20);
    text-align: center;
    background: rgba(128,128,128,0.05);
}

.bank-card {
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.20);
    margin-bottom: 1rem;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# ENCABEZADO
# =========================================================

st.markdown(
    '<div class="titulo">Mi vida con Mirssa ✨</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">Tu dinero trabajando para tu futuro ❤️</div>',
    unsafe_allow_html=True
)


# =========================================================
# INPUTS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    ingreso_fijo = st.number_input(
        "💵 Tu Sueldo Fijo ($)",
        min_value=0.0,
        step=100.0,
        key="fijo_val"
    )

with col2:
    deducciones = st.number_input(
        "✂️ ¿Te quitaron algo? ($)",
        min_value=0.0,
        step=100.0,
        key="deduc_val"
    )

with col3:
    ingreso_variable = st.number_input(
        "📈 Tus Extras (Variable) ($)",
        min_value=0.0,
        step=100.0,
        key="var_val"
    )


omitir_fijos = st.checkbox(
    "✨ Ya pagué los gastos fijos esta semana (Omitir Fijo)"
)


# =========================================================
# INGRESOS
# =========================================================

fijo_neto = max(0.0, ingreso_fijo - deducciones)

ingreso_total = fijo_neto + ingreso_variable

# =========================================================
# DIEZMO
# =========================================================

diezmo = ingreso_total * DIEZMO_PCT


# =========================================================
# IMPUESTOS QA
# =========================================================

# Reserva presupuestaria.
# El porcentaje/cálculo real debe ser definido por el contador.

impuesto_qa = min(
    ingreso_variable,
    IMPUESTO_QA_SEMANAL
)


# =========================================================
# GASTOS OBLIGATORIOS
# =========================================================

gastos_fijos = 0.0 if omitir_fijos else GASTOS_FIJOS_SEMANALES

sgmm = SGMM_SEMANAL

ppr = PPR_SEMANAL


# =========================================================
# CATEGORÍAS BASE
# =========================================================

deuda = min(
    DEUDA_SEMANAL,
    max(0.0, ingreso_total)
)

emergencia = min(
    EMERGENCIA_SEMANAL,
    max(0.0, ingreso_total)
)

ocio = min(
    OCIO_SEMANAL,
    max(0.0, ingreso_total)
)

sp500 = min(
    SP500_SEMANAL,
    max(0.0, ingreso_total)
)


# =========================================================
# CALCULAR CRECIMIENTO
# =========================================================

comprometido_base = (
    impuesto_qa
    + diezmo
    + gastos_fijos
    + sgmm
    + ppr
    + deuda
    + emergencia
    + ocio
    + sp500
)

# Dinero restante dentro del presupuesto de $8,500
crecimiento_base = max(
    0.0,
    BASE_SEMANAL - comprometido_base - DISPONIBLE_MINIMO
)


# =========================================================
# EFECTO GATILLO
# =========================================================

excedente = max(
    0.0,
    ingreso_total - BASE_SEMANAL
)

gatillo_crecimiento = excedente * GATILLO_CRECIMIENTO
gatillo_sp500 = excedente * GATILLO_SP500
gatillo_deuda = excedente * GATILLO_DEUDA
gatillo_disponible = excedente * GATILLO_DISPONIBLE


# =========================================================
# TOTALES FINALES
# =========================================================

crecimiento = crecimiento_base + gatillo_crecimiento

sp500_total = sp500 + gatillo_sp500

deuda_total = deuda + gatillo_deuda

disponible = DISPONIBLE_MINIMO + gatillo_disponible


# =========================================================
# AJUSTE DE SEGURIDAD
# =========================================================

# Nunca permitir que el algoritmo asigne más dinero
# del que realmente existe.

total_asignado = (
    impuesto_qa
    + diezmo
    + gastos_fijos
    + sgmm
    + ppr
    + crecimiento
    + sp500_total
    + deuda_total
    + emergencia
    + ocio
    + disponible
)

diferencia = ingreso_total - total_asignado

# Si existe una pequeña diferencia por redondeos,
# se agrega a disponible.

if diferencia > 0:
    disponible += diferencia

elif diferencia < 0:
    # Reducimos primero crecimiento.
    ajuste = min(
        crecimiento,
        abs(diferencia)
    )
    crecimiento -= ajuste


# =========================================================
# MÉTRICAS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💵 Dinero en Mano",
        f"${disponible:,.0f}"
    )

with col2:
    st.metric(
        "🚀 Crecimiento",
        f"${crecimiento:,.0f}"
    )

with col3:
    st.metric(
        "📈 S&P 500",
        f"${sp500_total:,.0f}"
    )

with col4:
    st.metric(
        "💎 Inversión PPR",
        f"${ppr:,.0f}"
    )


# =========================================================
# EFECTO GATILLO
# =========================================================

if excedente > 0:

    st.success(
        f"⚡ EFECTO GATILLO ACTIVADO: "
        f"Ganaste ${excedente:,.0f} arriba de tu base de $8,500."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🚀 Crecimiento",
            f"+${gatillo_crecimiento:,.0f}"
        )

    with c2:
        st.metric(
            "📈 S&P 500",
            f"+${gatillo_sp500:,.0f}"
        )

    with c3:
        st.metric(
            "💳 Deuda",
            f"+${gatillo_deuda:,.0f}"
        )

    with c4:
        st.metric(
            "💵 Disponible",
            f"+${gatillo_disponible:,.0f}"
        )

else:

    st.info(
        "💡 Estás trabajando dentro de tu presupuesto base de $8,500."
    )


# =========================================================
# TABLA DE DISTRIBUCIÓN
# =========================================================

datos = [
    ["Impuestos QA", impuesto_qa],
    ["Diezmo", diezmo],
    ["Gastos Fijos", gastos_fijos],
    ["SGMM", sgmm],
    ["PPR", ppr],
    ["S&P 500", sp500_total],
    ["Deuda", deuda_total],
    ["Emergencias", emergencia],
    ["Crecimiento", crecimiento],
    ["Ocio", ocio],
    ["Disponible", disponible],
]

df = pd.DataFrame(
    datos,
    columns=["Categoría", "Cantidad"]
)

df["Cantidad"] = df["Cantidad"].round(2)

st.subheader("📊 Distribución de esta semana")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# RESUMEN
# =========================================================

st.subheader("💰 Resumen financiero")

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Presupuesto Base</h3>
            <h2>${BASE_SEMANAL:,.0f}</h2>
            <p>Tu estilo de vida se organiza alrededor de esta cantidad.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Dinero Libre</h3>
            <h2>${disponible:,.0f}</h2>
            <p>Dinero que puedes utilizar sin tocar tus objetivos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# CUENTAS BANCARIAS
# =========================================================

st.subheader("🏦 ¿A dónde mandar el dinero?")

montos_bancos = [
    diezmo + emergencia + crecimiento,
    gastos_fijos + sgmm,
    sp500_total,
    deuda_total + ocio,
    0.0,
    0.0
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

    st.checkbox(
        "✅ Listo.",
        key=f"chk_banco_{i}"
    )


# =========================================================
# BOTÓN FINAL
# =========================================================

st.markdown("---")

st.button(
    "LISTO BB, DINERO GUARDADO ✨",
    on_click=confirmar_deposito,
    use_container_width=True
)


# =========================================================
# CONFIRMACIÓN
# =========================================================

if st.session_state.exito_trigger:

    st.balloons()

    st.success(
        "✨ ¡Listo BB! Tu dinero ya tiene trabajo. "
        "Ahora deja que tu yo del futuro te lo agradezca. ❤️"
    )

    st.audio(
        "https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg"
    )
