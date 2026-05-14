# ==========================================
# TABLA FINAL Y RESUMEN
# ==========================================
# Agregamos la llave "Meta" a los conceptos inamovibles para poder calcular el profit
detalles = [
    {"Concepto": "Diezmo", "Plataforma": "Cuenta Diezmo", "Meta": 0.0, "Fijo": diezmo_fijo, "Variable": diezmo_var},
    {"Concepto": "Renta", "Plataforma": "NU (Cajita)", "Meta": meta_renta, "Fijo": f_renta, "Variable": v_renta},
    {"Concepto": "Transporte", "Plataforma": "NU (Gasto)", "Meta": meta_transporte, "Fijo": f_transp, "Variable": v_transp},
    {"Concepto": "Novia", "Plataforma": "NU (Gasto)", "Meta": meta_novia, "Fijo": f_novia, "Variable": v_novia},
    {"Concepto": "Viajes/Visitas", "Plataforma": "SPIN", "Meta": meta_viajes, "Fijo": f_viajes, "Variable": v_viajes},
    {"Concepto": "Deuda", "Plataforma": "Pago Deuda", "Meta": 0.0, "Fijo": f_deuda, "Variable": v_deuda},
    {"Concepto": "Emergencias", "Plataforma": "CETES", "Meta": 0.0, "Fijo": f_emerg, "Variable": v_emerg},
    {"Concepto": "Colchón", "Plataforma": "NU (Cajita)", "Meta": 0.0, "Fijo": f_colchon, "Variable": v_colchon},
    {"Concepto": "Retiro/Bolsa", "Plataforma": "GBM+", "Meta": 0.0, "Fijo": f_retiro, "Variable": v_retiro},
]

df_detalles = pd.DataFrame(detalles)
df_detalles["Total"] = df_detalles["Fijo"] + df_detalles["Variable"]

# --- CÁLCULO DE PROFIT (EXCEDENTE) ---
# Extraemos el profit solo de las categorías con meta definida
def calcular_profit(row):
    if row["Meta"] > 0:
        return max(0.0, row["Total"] - row["Meta"])
    return 0.0

df_detalles["Profit (Excedente)"] = df_detalles.apply(calcular_profit, axis=1)

# ==========================================
# VISUALIZACIÓN EN INTERFAZ
# ==========================================
st.subheader("💳 Transferencias Requeridas")

# Resumen Bancario
df_bancos = df_detalles.groupby("Plataforma")["Total"].sum().reset_index()
st.table(df_bancos.style.format({"Total": "${:,.2f}"}))

# Métrica Rápida de Excedente
total_profit = df_detalles["Profit (Excedente)"].sum()
if total_profit > 0:
    st.info(f"📈 **Profit Total Generado en Sobres:** ${total_profit:,.2f} (Dinero extra inyectado por encima de tus metas mínimas)")

# Visualización Granular
with st.expander("🔍 Ver desglose Fijo, Variable y Profit"):
    # Reordenamos columnas para que sea fácil de leer
    columnas_mostrar = ["Concepto", "Plataforma", "Meta", "Fijo", "Variable", "Total", "Profit (Excedente)"]
    
    st.dataframe(
        df_detalles[columnas_mostrar].style.format({
            "Meta": "${:,.2f}", 
            "Fijo": "${:,.2f}", 
            "Variable": "${:,.2f}", 
            "Total": "${:,.2f}",
            "Profit (Excedente)": "${:,.2f}"
        }),
        use_container_width=True
    )
