import streamlit as st

st.set_page_config(page_title="Sleep App - TFG", layout="wide")

st.title("DeepShift: Anàlisi i Simulació de la Fragmentació del Son 🌙☀️")
st.subheader("DeepShift és una aplicació que neix a partir d'un projecte de Fi de Grau en Enginyeria Biomèdica, amb l'objectiu d'ajudar als treballadors a torns a comprendre i gestionar millor la seva qualitat de son. Aquesta eina ofereix una anàlisi detallada del son real, permet simular diferents escenaris de fragmentació del son i proporciona recomanacions personalitzades per millorar la salut del son.")

tab1, tab2, tab3 = st.tabs(["📊 Calcula el teu SCORE", "🧪 Simulador de son", "💡 Recomanacions generals"])

with tab1:
    st.header("Anàlisi de la qualitat del son")
    st.info("Puja el teu fitxer .edf per començar.")
    file_score = st.file_uploader("Aquí ⬇️", type=["edf"], key="score_uploader")

    if file_score is not None:
        st.success(f"Fitxer {file_score.name} carregat amb èxit!")

with tab2:
    st.header("Simulador de fragmentació")
    st.write("Si no acostumes a dormir de nit però ets curiós, pots simular l'efecte de la fragmentació del son diürn a partir d'una polisomnografia nocturna. Puja el teu fitxer .edf per començar.")
    file_sim = st.file_uploader("Aquí ⬇️", type=["edf"], key="sim_uploader")

    if file_sim is not None:
        st.success(f"Fitxer {file_sim.name} preparat per a la simulació!")

with tab3:
    st.header("Guia de salut - Recomanacions per treballadors a torns")
     
    st.markdown("### 🌙 Regles d'Or - Independentment del torn")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.warning("☕ **Cafè:** Evita la cafeïna 6 hores abans d'anar a dormir.")
    with c2:
        st.success("💊 **Melatonina:** Si preveus que et costarà adormir-te, pren melatonina 60-90 minuts abans del llit.")
    with c3:
        st.error("📱 **Pantalles:** Redueix la llum blava de les pantalles (mòbil, ordinador, televisió) 30-60 minuts abans d'anar a dormir. La llum blava de les pantalles pot inhibir la producció de melatonina, fent més difícil adormir-se.")

    st.divider()

    st.subheader("Cada torn de treball presenta desafiaments únics per a la qualitat del son. Aquí tens algunes recomanacions específiques per a cada torn:")
   
    col1, col2 = st.columns(2)
    with col1:
        t_inici = st.time_input("Hora d'inici del torn", key="t_inici")
    with col2:
        t_fi = st.time_input("Hora de finalització del torn", key="t_fi")

    if t_inici and t_fi:
        h = t_inici.hour
        
        if 6 <= h < 14:
            torn_detectat = "🌅 MATÍ"
            missatge = "Has d'enfocar-te en la higiene vespertina i llum natural en despertar."
        elif 14 <= h < 22:
            torn_detectat = "🌆 TARDA"
            missatge = "Prioritza la descompressió en arribar a casa per no retardar el son."
        else:
            torn_detectat = "🌃 NIT"
            missatge = "Compte amb el bloqueig de llum al matí i la pèrdua de REM/N2."

        st.info(f"**Torn detectat: {torn_detectat}**. {missatge}")


    with st.expander("🌅 Recomanacions per al Torn de Matí"):
        st.write("""
        **El repte:** Llevar-se molt d'hora i adaptar-se a un horari de son més aviat.

        Aixecar-se molt aviat (entre 04:00 i 05:00) està fortament associat amb un augment de somnolència durant la resta del dia. Sabem que és difícil despertar-se aviat, així com mantenir 8h de son i obligar el cos a dormir més aviat del que està acostumat. Per això, aquí tens algunes estratègies per ajudar-te a adaptar-te:
        *   **Llum al matí:** Tingues exposició lumínica intensa (preferiblement, llum natural) durant els primers minuts després de despertar-te. Això ajudarà a configurar el teu rellotge intern i a reduir la somnolència diürna.
        *   **Higiene vespertina:** Comença a reduir la intensitat de la llum a casa 2 hores abans de dormir, per entrar en un estat més relaxat i propici per al son.
        *   **Consell:** Evita les migdiades llargues a la tarda; si en fas una, que no superi els 20 minuts.
        """)

    with st.expander("🌆 Recomanacions per al Torn de Tarda"):
        st.write("""
        **El repte:** El retard en l'hora d'anar a dormir i la possible pèrdua de vida social/familiar.
        *   **Descompressió:** En arribar a casa (sovint tard), dedica 30-45 minuts a una activitat relaxant sense pantalles abans d'entrar al llit.
        *   **Consistència:** Intenta no aixecar-te excessivament tard al matí per no desplaçar el teu ritme circadiari cap a la nit.
        """)

    with st.expander("🌃 Recomanacions per al Torn de Nit (Fonamental)"):
        st.info("Aquest torn és el que més afecta l'arquitectura del son (especialment N2 i REM).")
        st.write("""
        **Estratègies post-torn:**
        1.  **Bloqueig de llum:** Fes servir ulleres de sol fosques en sortir de la feina cap a casa per evitar que la llum del sol bloquegi la producció de melatonina.
        2.  **Entorn de son:** L'habitació ha d'estar totalment fosca (cortines opaques o antifaç) i fresca.
        3.  **Nutrició:** No te'n vagis a dormir amb gana, però evita menjars molt pesats abans del son diürn.
        4.  **Pressió Homeostàtica:** Entén que el teu son serà més curt (2-4 hores menys) degut al procés circadiari; no t'estressis si et despertes abans, és la teva biologia intentant sincronitzar-se.
        """)