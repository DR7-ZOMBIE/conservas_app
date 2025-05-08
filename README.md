# Conservas de la Abuela – Análisis Financiero del Proyecto

Este proyecto nace del amor por una tradición familiar: las conservas artesanales que prepara la abuela. En un ejercicio de planeación financiera y emprendimiento, se desarrolló una herramienta interactiva en **Streamlit** que permite visualizar y analizar la viabilidad del negocio proyectado a 5 años.

## 📘 Historia

La abuela siempre fue conocida en el pueblo por sus deliciosas conservas de frutas. Tras muchos años de regalar frascos a familiares y vecinos, sus nietos decidieron convertir su legado en un proyecto empresarial.

Con una inversión inicial destinada a terrenos, oficinas, maquinaria y vehículos, y con estimaciones realistas de costos, precios y demanda creciente, se modeló el flujo de caja libre del proyecto para evaluar su rentabilidad y sostenibilidad.

---

## 💡 Objetivo

Desarrollar una **aplicación financiera interactiva** que permita:

- Simular ingresos y costos anuales.
- Calcular el Flujo de Caja Libre (FCL).
- Visualizar márgenes, estructura de costos y recuperación de inversión.
- Analizar indicadores clave como VPN y TIR.
- Tomar decisiones basadas en visualizaciones dinámicas y métricas claras.

---

## 🛠️ Tecnologías utilizadas

- **Python**
- **Streamlit**: Para la interfaz interactiva.
- **Pandas** y **NumPy**: Para cálculos y manipulación de datos.
- **Plotly**: Para visualizaciones gráficas avanzadas.
- **numpy_financial**: Para indicadores como VPN y TIR.

---

## 📊 Contenidos de la app

### Parámetros base

- Crecimiento de la demanda y precios
- Costos variables y fijos
- Inversión inicial (CapEx)
- Depreciación y recuperación de capital de trabajo
- Salvamento de activos al final del proyecto

### Salidas y visualizaciones

- **Tabla consolidada** del flujo de caja libre.
- **Barras apiladas** de ingresos y estructura de costos.
- **Evolución de márgenes** (EBITDA y neto).
- **Flujo acumulado** con año de pay-back.
- **Waterfall** explicando el FCL del Año 1.
- **Distribución por insumos** del costo variable.
- **Margen de contribución por unidad.**
- **Indicadores de creación de valor**: VPN y TIR comparados con WACC.

---

## 📈 Resultados

- **Valor presente neto (VPN)**: Se calcula usando un WACC del 14 %.
- **Tasa interna de retorno (TIR)**: Comparada visualmente contra el WACC.
- **Pay-back** estimado en los primeros años.
- Evaluación clara sobre si el proyecto genera valor económico.

---

## 🚀 Cómo usar

1. Instala las dependencias necesarias:
   ```bash
   pip install streamlit pandas numpy plotly numpy-financial
