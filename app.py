import streamlit as st

st.set_page_config(page_title="SleepShift Analyzer", layout="wide")

st.title("🌙 SleepShift: Optimització del son")

# Creem les pestanyes
tab1, tab2, tab3 = st.tabs(["📊 Panell de Control", "🧪 Simulador", "💡 Recomanacions"])

with tab1:
    st.header("Anàlisi del son real")
    st.info("Puja el teu fitxer .edf per començar.")

with tab2:
    st.header("Laboratori de fragmentació")
    st.write("Aquí posarem els sliders per trinxar l'hipnograma.")

with tab3:
    st.header("Guia de salut")
    st.success("Consell del dia: Evita la llum blava 2 hores abans de dormir.")