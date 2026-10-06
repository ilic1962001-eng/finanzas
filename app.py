import streamlit as st
import pandas as pd

# ==========================================
# INICIALIZACIÓN DE MEMORIA
# ==========================================
if 'fijo_val' not in st.session_state:
    st.session_state.fijo_val = 2329.0
if 'deduc_val' not in st.session_state:
    st.session_state.deduc_val = 0.0
if 'var_val' not in st.session_state:
    st.session_state.var_val = 1000.0
if 'exito_trigger' not in st.session_state:
    st.session_state.exito_trigger = False

for i in range(6):
    if f'chk_banco_{i}' not in st.session_state:
        st.session_state[f'chk_banco_{i}'] = False


def confirmar_deposito():
    st.session_state.exito_trigger = True

    st.session_state.fijo_val = 0.0
    st.session_state.deduc_val = 0.0
    st.session_state.var_val = 0.0

    for i in range(6):
        st.session_state[f'chk_banco_{i}'] = False


# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==========================================
st.set_page_config(
    page_title="Mi vida con Mirssa ✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    audio {
        display: none !important;
    }

    .stApp {
        background-color: #fafbfc;
        color: #333333;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .titulo-pro {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        padding-top: 10px;
    }

    .subtitulo {
        text-align: center;
        color: #764ba2;
        font-size: 1.3rem;
        font-weight: 500;
        letter-spacing: 2px;
        margin-bottom: 30px;
    }

    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
        border-left: 5px solid #667eea;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.08);
    }

    div[data-testid="metric-container"] label {
        color: #888888 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #333333 !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 15px 0;
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 8px 16px rgba(118, 75, 162, 0.4);
        color: #ffffff;
    }

    .link-banco {
        display: inline-block;
        padding: 8px 15px;
        background-color: #f1f3f5;
        color: #764ba2 !important;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: background 0.3s;
    }

    .link-banco:hover {
        background-color: #764ba2;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# NUEVO CEREBRO FINANCIERO
# ==========================================

# ------------------------------------------
# PRIORIDADES
# ------------------------------------------

# Diezmo
DIEZMO_PCT = 0.10

# Reserva fiscal provisional SOLAMENTE sobre QA.
# Se podrá cambiar cuando el contador determine
# la obligación real.
IMPUESTO_QA_PCT = 0.10

# SGMM: fondo independiente
SGMM_SEMANAL = 800.0

# PPR: $4,000 mensuales
PPR_MENSUAL = 4000.0

# ------------------------------------------
# GASTOS FIJOS MENSUALES
# ------------------------------------------

RENTA_MENSUAL = 1500.0
UNIVERSIDAD_MENSUAL = 2500.0
MAMA_MENSUAL = 4000.0
CONTADOR_MENSUAL = 1500.0

GASTOS_FIJOS_MENSUALES = (
    RENTA_MENSUAL +
    UNIVERSIDAD_MENSUAL +
    MAMA_MENSUAL +
    CONTADOR_MENSUAL
)

# Conversión mensual → semanal usando 52 semanas
GASTOS_FIJOS_SEMANALES = (
    GASTOS_FIJOS_MENSUALES * 12 / 52
)

# ------------------------------------------
# REPARTO DEL DINERO DISPONIBLE
# ------------------------------------------

DEUDA_PCT = 0.10
EMERGENCIA_PCT = 0.08
CRECIMIENTO_PCT = 0.08
OCIO_PCT = 0.076


# ==========================================
# HEADER E INPUTS
# ==========================================

st.markdown(
    "<div class='titulo-pro'>¿Cuánto ganaste bb?</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitulo'>Mi vida con Mirssa ✨</div>",
    unsafe_allow_html=True
)

with st.container():

    c_in1, c_in2, c_in3 = st.columns(3)

    with c_in1:
        ingreso_fijo_bruto = st.number_input(
            "💵 Tu Sueldo Fijo ($)",
            min_value=0.0,
            step=100.0,
            key="fijo_val"
        )

    with c_in2:
        deducciones = st.number_input(
            "✂️ ¿Te quitaron algo? ($)",
            min_value=0.0,
            step=10.0,
            key="deduc_val"
        )

    with c_in3:
        ingreso_var_bruto = st.number_input(
            "📈 Tus Extras (Variable) ($)",
            min_value=0.0,
            step=100.0,
            key="var_val"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    omitir_fijo = st.checkbox(
        "✨ Ya pagué los gastos fijos esta semana (Omitir Fijo)",
        value=False
    )

st.markdown("---")


# ==========================================
# 1. INGRESOS
# ==========================================

fijo_disponible = max(
    0.0,
    ingreso_fijo_bruto - deducciones
)

total_ingreso_real = (
    fijo_disponible +
    ingreso_var_bruto
)


# ==========================================
# 2. RESERVA FISCAL DE QA
# ==========================================

# El sueldo fijo de DoorDash no entra aquí.
# La reserva fiscal se calcula solamente sobre QA.

impuesto_qa = (
    ingreso_var_bruto * IMPUESTO_QA_PCT
)


qa_despues_impuestos = (
    ingreso_var_bruto - impuesto_qa
)


# ==========================================
# 3. DIEZMO
# ==========================================

# El diezmo se calcula sobre el dinero recibido
# después de las deducciones indicadas.

base_diezmo = (
    fijo_disponible +
    ingreso_var_bruto
)

diezmo_total = (
    base_diezmo * DIEZMO_PCT
)


# Para continuar con el reparto,
# descontamos el diezmo del ingreso total.

dinero_despues_diezmo = (
    total_ingreso_real -
    diezmo_total
)


# ==========================================
# 4. SGMM
# ==========================================

# El SGMM se maneja como fondo independiente.

sgmm = SGMM_SEMANAL


# ==========================================
# 5. PPR
# ==========================================

# $4,000 mensuales ≈ $923.08 por semana

ppr_semanal = (
    PPR_MENSUAL * 12 / 52
)


# ==========================================
# 6. GASTOS FIJOS
# ==========================================

if omitir_fijo:
    gastos_fijos_semana = 0.0
else:
    gastos_fijos_semana = GASTOS_FIJOS_SEMANALES


# ==========================================
# 7. DINERO DESPUÉS DE OBLIGACIONES
# ==========================================

dinero_comprometido = (
    impuesto_qa +
    diezmo_total +
    sgmm +
    ppr_semanal +
    gastos_fijos_semana
)

dinero_despues_obligaciones = max(
    0.0,
    total_ingreso_real - dinero_comprometido
)


# ==========================================
# 8. FONDOS FLEXIBLES
# ==========================================

t_deuda = (
    dinero_despues_obligaciones *
    DEUDA_PCT
)

t_emerg = (
    dinero_despues_obligaciones *
    EMERGENCIA_PCT
)

t_crecimiento = (
    dinero_despues_obligaciones *
    CRECIMIENTO_PCT
)

t_ocio = (
    dinero_despues_obligaciones *
    OCIO_PCT
)


# ==========================================
# 9. DINERO RESTANTE
# ==========================================

porcentaje_flexible_usado = (
    DEUDA_PCT +
    EMERGENCIA_PCT +
    CRECIMIENTO_PCT +
    OCIO_PCT
)

t_disponible = max(
    0.0,
    dinero_despues_obligaciones *
    (1 - porcentaje_flexible_usado)
)


# ==========================================
# 10. TOTALES
# ==========================================

t_diezmo = diezmo_total
t_impuestos = impuesto_qa
t_sgmm = sgmm
t_ppr = ppr_semanal
t_fijos = gastos_fijos_semana

t_fijo_total = (
    t_fijos +
    t_sgmm +
    t_ppr
)

t_fondo_financiero = (
    t_deuda +
    t_emerg +
    t_crecimiento
)

t_ahorro_inversion = (
    t_ppr +
    t_sgmm +
    t_emerg +
    t_crecimiento
)


# ==========================================
# 11. PROYECCIÓN PPR
# ==========================================

# Aproximación al 7% anual durante 30 años

proyeccion = (
    t_ppr *
    (
        ((1 + (0.07 / 52)) ** (30 * 52) - 1)
        / (0.07 / 52)
    )
    if t_ppr > 0
    else 0.0
)


# ==========================================
# 12. MÉTRICAS SUPERIORES
# ==========================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "💰 Dinero en Mano",
        f"${total_ingreso_real:,.2f}"
    )

with c2:
    st.metric(
        "🌱 Para Nuestro Futuro",
        f"${t_ahorro_inversion:,.2f}"
    )

with c3:
    st.metric(
        "🏰 Proyección (30 Años)",
        f"${proyeccion:,.2f}"
    )

with c4:

    if omitir_fijo:
        st.metric(
            "📌 Fijos de la Semana",
            "CUBIERTOS ✅"
        )

    elif total_ingreso_real >= dinero_comprometido:
        st.metric(
            "📌 Fijos de la Semana",
            "CUBIERTOS ✅"
        )

    else:
        faltante = dinero_comprometido - total_ingreso_real

        st.metric(
            "⚠️ Nos Falta",
            f"-${faltante:,.2f}"
        )


st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# TABLA DE SOBRES
# ==========================================

st.markdown(
    "<h3 style='color: #667eea;'>📊 Tus Sobres de la Semana</h3>",
    unsafe_allow_html=True
)

df_data = [

    {
        "Sobre": "🧾 Impuestos QA",
        "Target": "10% QA",
        "Fijo": "$0.00",
        "Variable": f"${t_impuestos:,.2f}",
        "Total": f"${t_impuestos:,.2f}",
        "Status": "🛡️ Reservado"
    },

    {
        "Sobre": "⛪ Diezmo",
        "Target": "10%",
        "Fijo": f"${fijo_disponible * DIEZMO_PCT:,.2f}",
        "Variable": f"${ingreso_var_bruto * DIEZMO_PCT:,.2f}",
        "Total": f"${t_diezmo:,.2f}",
        "Status": "⚪ Listo"
    },

    {
        "Sobre": "🏠 Gastos Fijos",
        "Target": f"${GASTOS_FIJOS_MENSUALES:,.0f}/mes",
        "Fijo": f"${t_fijos:,.2f}",
        "Variable": "$0.00",
        "Total": f"${t_fijos:,.2f}",
        "Status": "🔒 Obligatorio"
    },

    {
        "Sobre": "🏥 SGMM",
        "Target": "$800/sem.",
        "Fijo": "$0.00",
        "Variable": f"${t_sgmm:,.2f}",
        "Total": f"${t_sgmm:,.2f}",
        "Status": "🛡️ Fondo anual"
    },

    {
        "Sobre": "🏦 PPR",
        "Target": "$4,000/mes",
        "Fijo": "$0.00",
        "Variable": f"${t_ppr:,.2f}",
        "Total": f"${t_ppr:,.2f}",
        "Status": "🚀 Invirtiendo"
    },

    {
        "Sobre": "💳 Deuda (10%)",
        "Target": "10%",
        "Fijo": "$0.00",
        "Variable": f"${t_deuda:,.2f}",
        "Total": f"${t_deuda:,.2f}",
        "Status": "🔥 Pagando"
    },

    {
        "Sobre": "🚨 Emergencias (8%)",
        "Target": "8%",
        "Fijo": "$0.00",
        "Variable": f"${t_emerg:,.2f}",
        "Total": f"${t_emerg:,.2f}",
        "Status": "🛡️ Creciendo"
    },

    {
        "Sobre": "📈 Crecimiento (8%)",
        "Target": "8%",
        "Fijo": "$0.00",
        "Variable": f"${t_crecimiento:,.2f}",
        "Total": f"${t_crecimiento:,.2f}",
        "Status": "🚀 A invertir"
    },

    {
        "Sobre": "🍿 Ocio (7.6%)",
        "Target": "7.6%",
        "Fijo": "$0.00",
        "Variable": f"${t_ocio:,.2f}",
        "Total": f"${t_ocio:,.2f}",
        "Status": "🎮 ¡Disfruta!"
    },

    {
        "Sobre": "💰 Disponible",
        "Target": "Sin asignar",
        "Fijo": "$0.00",
        "Variable": f"${t_disponible:,.2f}",
        "Total": f"${t_disponible:,.2f}",
        "Status": "💎 Disponible"
    }
]

st.dataframe(
    pd.DataFrame(df_data),
    use_container_width=True,
    hide_index=True
)


st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# GUÍA DE DEPÓSITOS
# ==========================================

st.markdown(
    "<h3 style='color: #667eea;'>🏦 ¿A dónde transfiero, bb?</h3>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align: center; margin-bottom: 25px;'>"
    "<a href='https://banco.hey.inc/' target='_blank' "
    "class='link-banco'>🚀 Abrir Hey Banco (Tu Central)</a>"
    "</div>",
    unsafe_allow_html=True
)


# ==========================================
# DISTRIBUCIÓN A LAS MISMAS CUENTAS
# ==========================================

# Revolut:
# Diezmo + Emergencias + Crecimiento

t_revolut_rendimiento = (
    t_diezmo +
    t_emerg +
    t_crecimiento
)


# Nu:
# Gastos operativos + SGMM

t_nu_operativo = (
    t_fijos +
    t_sgmm
)


# Santander:
# Deuda + Ocio

t_santander = (
    t_deuda +
    t_ocio
)


# GBM:
# PPR

t_hey = t_ppr

t_spin = 0.0


destinos = [

    {
        "Nombre": "⚫ Revolut (Diezmo, Emergencias, Crecimiento)",
        "Monto": t_revolut_rendimiento,
        "CLABE": "646990404064534378"
    },

    {
        "Nombre": "🟣 Nu (Gastos Fijos, SGMM)",
        "Monto": t_nu_operativo,
        "CLABE": "638180000126660124"
    },

    {
        "Nombre": "📈 GBM (PPR / Retiro)",
        "Monto": t_hey,
        "CLABE": "601180400073884389"
    },

    {
        "Nombre": "🔴 Santander LikeU (Deuda, Ocio)",
        "Monto": t_santander,
        "CLABE": "014180140158246414"
    },

    {
        "Nombre": "🔵 Hey Banco (Novia)",
        "Monto": 0.0,
        "CLABE": "APARTADO INTERNO"
    },

    {
        "Nombre": "🏪 Spin by Oxxo (Opcional / Vacía)",
        "Monto": t_spin,
        "CLABE": "728969000033664690"
    }
]


# ==========================================
# CHECKBOXES
# ==========================================

for i, d in enumerate(destinos):

    with st.container():

        col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

        col1.markdown(
            f"<div style='font-size: 1.1rem; font-weight: 600; "
            f"color: #333333; margin-top: 10px;'>"
            f"{d['Nombre']}</div>",
            unsafe_allow_html=True
        )

        col2.markdown(
            f"<div style='font-size: 1.4rem; font-weight: 800; "
            f"color: #764ba2; margin-top: 5px;'>"
            f"${d['Monto']:,.2f}</div>",
            unsafe_allow_html=True
        )

        with col3:

            if d['CLABE'] != "APARTADO INTERNO":

                st.code(
                    d['CLABE'],
                    language="text"
                )

            else:

                st.markdown(
                    "<div style='margin-top: 10px; "
                    "color: #888888; font-style: italic;'>"
                    "Sin CLABE (Traspaso interno)</div>",
                    unsafe_allow_html=True
                )

        with col4:

            st.markdown(
                "<div style='margin-top: 5px;'></div>",
                unsafe_allow_html=True
            )

            st.checkbox(
                "✅ Listo",
                key=f"chk_banco_{i}"
            )

    st.markdown(
        "<hr style='margin: 0.5em 0; "
        "border: 0.5px solid #e9ecef;'>",
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# BOTÓN FINAL
# ==========================================

col_espacio1, col_boton, col_espacio2 = st.columns([1, 2, 1])

with col_boton:

    st.button(
        "LISTO BB, DINERO GUARDADO ✨",
        on_click=confirmar_deposito
    )


# ==========================================
# ANIMACIÓN Y SONIDO
# ==========================================

if st.session_state.exito_trigger:

    st.balloons()

    st.toast(
        '¡Transferencias completadas, gran trabajo esta semana! 🎉',
        icon='✨'
    )

    st.audio(
        "https://actions.google.com/sounds/v1/foley/cash_register_kaching.ogg",
        format="audio/ogg",
        autoplay=True
    )

    st.markdown(
        '<audio src="https://actions.google.com/sounds/v1/foley/'
        'cash_register_kaching.ogg" autoplay></audio>',
        unsafe_allow_html=True
    )

    st.session_state.exito_trigger = False
