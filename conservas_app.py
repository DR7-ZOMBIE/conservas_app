# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import numpy_financial as npf   # <-- nuevo


# ╔══════════════════════════════════════════════════════════╗
# ║  1 · PARÁMETROS TRAÍDOS DIRECTO DESDE TU HOJA  EXCEL     ║
# ╚══════════════════════════════════════════════════════════╝
inflation = 0.05          # 5 %
demand_g  = 0.06          # 6 %
tax_rate  = 0.35

# Demanda y precio unitario por año (Año 0 es 0 para alinear tabla)
units   = np.array([0, 22_000, 23_320, 24_719, 26_202, 27_774], dtype=float)
prices  = np.array([0, 15_000, 15_750, 16_538, 17_364, 18_233], dtype=float)

# Costos variables unitarios
unit_cost_jar     = 1_000                              # constante
unit_cost_fruit   = np.array([8_000 * (1 + inflation)**i for i in range(5)])
unit_cost_energy  = np.array([1_100 * (1 + inflation)**i for i in range(5)])

# Costos fijos y SG&A
fixed_costs  = np.array([20_000_000 * (1 + inflation + 0.01)**i for i in range(5)])
sga_costs    = np.array([30_000_000 * (1 + inflation + 0.02)**i for i in range(5)])

# CapEx y depreciaciones
capex = {
    "land"     : 50_000_000,
    "office"   : 20_000_000,
    "vehicles" : 30_000_000,
    "machinery": 10_000_000
}
depr = {
    "office"   : 2_000_000,  # 20 M / 10 a
    "vehicles" : 6_000_000,  # 30 M / 5 a
    "machinery": 1_000_000   # 10 M / 10 a
}
depr_total = sum(depr.values())

# Working‑capital (Δ WC) y recuperación
wc_vector = np.array([-4_166_667, -275_000, -293_250, -312_718, -333_484], dtype=float)
wc_recovery = -wc_vector.sum()          # recuperación en Año 5

# Salvamento final
salvage = 60_000_000 + 10_000_000 + 15_000_000 + 5_000_000   # = 90 M

# ╔══════════════════════════════════════════════════════════╗
# ║  2 · CÓMPUTO DEL FLUJO  DE  CAJA  LIBRE                  ║
# ╚══════════════════════════════════════════════════════════╝
years = np.arange(6)                           # 0‑5
revenues      = units * prices
c_var_total   = units[1:] * (unit_cost_jar + unit_cost_fruit + unit_cost_energy)
c_var_total   = np.insert(c_var_total, 0, 0)

ebit = revenues - c_var_total \
       - np.insert(fixed_costs, 0, 0)          \
       - np.insert(sga_costs,   0, 0)          \
       - np.insert(np.full(5, depr_total), 0, 0)

taxes = np.where(ebit > 0, ebit * tax_rate, 0)
uodi  = ebit - taxes
fc_oper = uodi + np.insert(np.full(5, depr_total), 0, 0)

# CapEx columna
capex_col = np.zeros(6)
capex_col[0] = -sum(capex.values())

# ΔWC columna (incluye recuperación en año 5)
wc_change = np.append(wc_vector, wc_recovery)

# Salvamento columna
salv_col = np.zeros(6); salv_col[-1] = salvage

# Flujo de Caja Libre final
fcl = fc_oper + capex_col + wc_change + salv_col

# ╔══════════════════════════════════════════════════════════╗
# ║  3 · TABLA RESULTADO                                    ║
# ╚══════════════════════════════════════════════════════════╝
tabla = pd.DataFrame({
    "Año"              : years,
    "Ingresos"         : revenues,
    "Costo variable"   : c_var_total,
    "Costos fijos"     : np.insert(fixed_costs, 0, 0),
    "Gastos Adm+Ventas": np.insert(sga_costs,   0, 0),
    "Depreciación"     : np.insert(np.full(5, depr_total), 0, 0),
    "EBIT"             : ebit,
    "Impuesto"         : taxes,
    "UODI"             : uodi,
    "FCL Operación"    : fc_oper,
    "CapEx"            : capex_col,
    "Δ WC"             : wc_change,
    "Salvamento"       : salv_col,
    "FCL"              : fcl
})
tabla["FCL acumulado"] = tabla["FCL"].cumsum()

# ╔══════════════════════════════════════════════════════════╗
# ║  4 ·  STREAMLIT – PRESENTACIÓN                          ║
# ╚══════════════════════════════════════════════════════════╝
st.set_page_config(page_title="Conservas de la Abuela – FCL",
                   layout="centered")
st.title("Conservas de la Abuela – Flujo de Caja Libre")

st.subheader("Tabla consolidada")
st.dataframe(tabla.style.format("{:,.0f}"))

# --------  GRÁFICOS  --------
## 1. FCL anual
st.subheader("Flujo de Caja Libre anual")
st.bar_chart(tabla.set_index("Año")["FCL"])

## 2. Ingresos vs. estructura de costos
st.subheader("Ingresos y estructura de costos (stack)")
fig_cost = go.Figure()
fig_cost.add_bar(x=tabla["Año"], y=tabla["Ingresos"], name="Ingresos")
fig_cost.add_bar(x=tabla["Año"], y=tabla["Costo variable"], name="Costo variable")
fig_cost.add_bar(x=tabla["Año"],
                 y=tabla["Costos fijos"] + tabla["Gastos Adm+Ventas"],
                 name="Costos fijos + SG&A")
fig_cost.update_layout(barmode="stack", template="plotly_white",
                       xaxis_title="Año", yaxis_title="$ COP")
st.plotly_chart(fig_cost, use_container_width=True)

## 3. Márgenes EBITDA y Neto
st.subheader("Márgenes EBITDA y Neto")
tabla["Margen EBITDA"] = np.where(tabla["Ingresos"]>0,
                                  tabla["FCL Operación"]/tabla["Ingresos"], np.nan)
tabla["Margen Neto"]   = np.where(tabla["Ingresos"]>0,
                                  tabla["FCL"]/tabla["Ingresos"], np.nan)
fig_m = go.Figure()
fig_m.add_scatter(x=tabla["Año"], y=tabla["Margen EBITDA"],
                  mode="lines+markers", name="Margen EBITDA")
fig_m.add_scatter(x=tabla["Año"], y=tabla["Margen Neto"],
                  mode="lines+markers", name="Margen Neto")
fig_m.update_layout(yaxis_tickformat="%", template="plotly_white",
                    xaxis_title="Año", yaxis_title="Margen")
st.plotly_chart(fig_m, use_container_width=True)

## 4. FCL acumulado + Pay‑back
st.subheader("FCL acumulado y Pay‑back")
fig_cum = go.Figure()
fig_cum.add_scatter(x=tabla["Año"], y=tabla["FCL acumulado"],
                    mode="lines+markers", name="Acumulado")
try:
    pb_year = tabla.loc[tabla["FCL acumulado"] >= 0, "Año"].iloc[0]
    fig_cum.add_vline(x=pb_year, line_dash="dash",
                      annotation_text=f"Pay‑back Año {int(pb_year)}",
                      annotation_position="top right")
except IndexError:
    pass
fig_cum.update_layout(template="plotly_white",
                      xaxis_title="Año", yaxis_title="$ COP")
st.plotly_chart(fig_cum, use_container_width=True)

# ════════════════════════════════════════════════════
# 5 · Waterfall FCL – Año 1
# ════════════════════════════════════════════════════
st.subheader("Puente de FCL – Año 1")
components_y1 = {
    "Ingresos": revenues[1],
    "− Costo variable": -c_var_total[1],
    "− Costos fijos": -fixed_costs[0],
    "− SG&A": -sga_costs[0],
    "− Depreciación": -depr_total,
    "EBIT": 0,                 # placeholder para salto
    "− Impuestos": -taxes[1],
    "UODI": 0,
    "+ Depreciación": depr_total,
    "FCL Operación": 0,
    "CapEx inicial": capex_col[0],          # cero en Y1
    "Δ WC": wc_change[1],
    "FCL Año 1": fcl[1]
}
fig_wf = go.Figure(go.Waterfall(
    x=list(components_y1.keys()),
    y=list(components_y1.values()),
    measure=["relative"] * (len(components_y1)-1) + ["total"],
    connector={"line":{"color":"rgba(63,63,63,0.7)"}},
))
fig_wf.update_layout(template="plotly_white", showlegend=False,
                     yaxis_title="$ COP", xaxis_title="")
st.plotly_chart(fig_wf, use_container_width=True)

# ════════════════════════════════════════════════════
# 6 · Stacked area: operación vs inversiones + WC
# ════════════════════════════════════════════════════
st.subheader("Origen y uso de caja a lo largo del proyecto")
fig_stack = go.Figure()
fig_stack.add_scatter(x=tabla["Año"], y=fc_oper,
                      stackgroup="one", name="FCL Operación",
                      mode="none")  # relleno
fig_stack.add_scatter(x=tabla["Año"], y=capex_col,
                      stackgroup="one", name="CapEx",
                      mode="none")
fig_stack.add_scatter(x=tabla["Año"], y=wc_change,
                      stackgroup="one", name="Δ WC",
                      mode="none")
fig_stack.update_layout(template="plotly_white",
                        xaxis_title="Año", yaxis_title="$ COP acumulado")
st.plotly_chart(fig_stack, use_container_width=True)

# ════════════════════════════════════════════════════
# 7 · Contribución de costos variables por insumo
# ════════════════════════════════════════════════════
st.subheader("Evolución de costos variables por insumo")
insumos = ["Frasco", "Fruta", "Energía"]
cv_matrix = np.vstack([
    units[1:] * unit_cost_jar,
    units[1:] * unit_cost_fruit,
    units[1:] * unit_cost_energy
])
fig_cv = go.Figure()
for i, ins in enumerate(insumos):
    fig_cv.add_scatter(x=years[1:], y=cv_matrix[i],
                       stackgroup="var", mode="none", name=ins)
fig_cv.update_layout(template="plotly_white",
                     xaxis_title="Año", yaxis_title="$ COP")
st.plotly_chart(fig_cv, use_container_width=True)

# ════════════════════════════════════════════════════
# 8 · Margen de contribución unitario
# ════════════════════════════════════════════════════
st.subheader("Margen de contribución unitario")
cm_unit = prices[1:] - (unit_cost_jar + unit_cost_fruit + unit_cost_energy)
fig_cm = go.Figure()
fig_cm.add_scatter(x=years[1:], y=cm_unit, mode="lines+markers",
                   name="Margen contribución/u")
fig_cm.update_layout(template="plotly_white",
                     xaxis_title="Año",
                     yaxis_title="$ COP por unidad")
st.plotly_chart(fig_cm, use_container_width=True)

# ════════════════════════════════════════════════════
# 9 · Indicadores de creación de valor (estilo pro)
# ════════════════════════════════════════════════════
st.markdown("## 📈 Indicadores de creación de valor")
st.markdown("---")

cash_flows = fcl
wacc       = 0.14                                  # 14 %
irr        = npf.irr(cash_flows)
npv        = npf.npv(wacc, cash_flows)

# ---- 1. Tarjetas KPI con color/delta ---------------------------------
kpi1, kpi2, spacer = st.columns([1,1,0.1])
with kpi1:
    st.metric(label="VPN (WACC 14 %)",
              value=f"${npv:,.0f}",
              delta=f"{'POSITIVO ✅' if npv>0 else 'NEGATIVO ❌'}")
with kpi2:
    st.metric(label="TIR",
              value=f"{irr*100:,.2f} %",
              delta=f"{'>' if irr>wacc else '<'} WACC")

st.markdown("")

# ---- 2. Gauge TIR vs WACC -------------------------------------------
fig_irr = go.Figure()

# Anillo externo: WACC
fig_irr.add_trace(go.Indicator(
    mode="gauge",
    value=wacc*100,
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={
        "shape": "bullet",
        "axis": {"range": [0, max(irr*100*1.5, 25)],
                 "visible": False},
        "bar": {"color": "rgba(0,0,0,0)"},
        "threshold": {
            "line": {"color": "red", "width": 4},
            "thickness": 1.0,
            "value": wacc*100}
    },
    title={"text": " "}  # truco: deja espacio para centrar
))

# Anillo interno: TIR
fig_irr.add_trace(go.Indicator(
    mode="gauge+number",
    value=irr*100,
    number={"suffix": " %"},
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={
        "axis": {"range": [0, max(irr*100*1.5, 25)]},
        "bar":  {"color": "limegreen" if irr>wacc else "orangered"},
        "steps": [
            {"range": [0, wacc*100], "color": "rgba(255,0,0,0.1)"},
            {"range": [wacc*100, max(irr*100*1.5, 25)],
             "color": "rgba(0,128,0,0.1)"}
        ],
    },
    title={"text": "TIR vs WACC"}
))

fig_irr.update_layout(
    template="plotly_white",
    height=300,
    margin=dict(l=30, r=30, t=20, b=10)
)
st.plotly_chart(fig_irr, use_container_width=True)

st.markdown("---")
