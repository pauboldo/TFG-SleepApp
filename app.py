import streamlit as st
from datetime import time

st.set_page_config(page_title="Sleep App - TFG", layout="wide")

st.title("DeepShift: Anàlisi i Simulació de la Fragmentació del Son 🌙☀️")
st.markdown("##### DeepShift és una aplicació que neix a partir d'un projecte de Fi de Grau en Enginyeria Biomèdica, amb l'objectiu d'ajudar als treballadors a torns a comprendre i gestionar millor la seva qualitat de son. Aquesta eina ofereix una anàlisi detallada del son real, permet simular diferents escenaris de fragmentació del son i proporciona recomanacions personalitzades per millorar la salut del son.")

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
        st.warning("☕ **Cafè:** Evita la cafeïna 6 hores abans d'anar a dormir per no interferir amb la qualitat del son.")
    with c2:
        st.success("💊 **Melatonina:** Si preveus que et costarà adormir-te, pren melatonina 60-90 minuts abans del llit.")
    with c3:
        st.error("📱 **Pantalles:** Redueix la llum blava de les pantalles (mòbil, ordinador, televisió) 30-60 minuts abans d'anar a dormir. Aquesta llum pot inhibir la producció de melatonina, fent més difícil adormir-se.")

    st.divider()

    st.subheader("Cada torn de treball presenta desafiaments únics per a la qualitat del son. Aquí tens algunes recomanacions específiques per a cada torn:")
   
    col1, col2 = st.columns(2)
    with col1:
        t_inici = st.time_input("Hora d'inici del torn", value=time(6, 0), key="t_inici")
    with col2:
        t_fi = st.time_input("Hora de finalització del torn", value=time(14, 0), key="t_fi")

    if t_inici and t_fi:
        minuts_inici = t_inici.hour * 60 + t_inici.minute
        minuts_fi = t_fi.hour * 60 + t_fi.minute

        if minuts_fi <= minuts_inici:
            minuts_fi_ajustat = minuts_fi + 24 * 60
        else:
            minuts_fi_ajustat = minuts_fi

        durada_torn = minuts_fi_ajustat - minuts_inici

    # Validació de durada màxima
        if durada_torn > 14 * 60:
            st.error("⚠️ La durada del torn introduïda no sembla correcta. Comprova les hores d'inici i fi.")
            st.stop()

    # Hora central del torn
        minuts_central = (minuts_inici + minuts_fi_ajustat) // 2
        h_central = (minuts_central // 60) % 24

        if 5 <= h_central < 13:
            torn_detectat = "🌅 MATÍ"
            missatge = "Has d'enfocar-te en la higiene vespertina i llum natural en despertar."
        elif 13 <= h_central < 21:
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
        
        ---
        
        **Consell 1:** Evita les migdiades llargues a la tarda, ja que podria interferir amb la capacitat d'adormir-te aviat: si en fas una, que no superi els 20 minuts.
        
        **Consell 2:** Els dies abans de començar el torn, intenta replicar l'horari de son que tindràs durant el torn (anar a dormir i despertar-te més aviat) per ajudar al teu cos a adaptar-se gradualment.
        """)

    with st.expander("🌆 Recomanacions per al Torn de Tarda"):
        st.write("""
        **El repte:** El retard en l'hora d'anar a dormir i la sensació de pèrdua de vida social/familiar.

        Treballar a la tarda son provocar que l'horari de son es desplaci naturalment cap a la matinada. Això pot fer que entris en un bucle de "despertar-dinar-treballar-dormir" que afecta el benestar mental i la regulació circadiària. Aquí tens estratègies per mantenir l'equilibri:
        *   **A l'inici del dia**: Intenta exposar-te a 20-30 minuts de llum solar poc després de llevar-te. Això ajuda a ancorar el teu ritme intern i evita que el teu rellotge biològic derivi cap a horaris cada cop més tardans.
        *   **Al tornar a casa**: Procura mantenir les llums tènues. Utilitza el "mode nit" en els teus dispositius electrònics per reduir l'exposició a llum blava.
        
        ---
        
        **Consell 1:** No vagis directe al llit en arribar. Dedica 30-60 minuts a una activitat relaxant per baixar les revolucions del sistema nerviós després de l'activitat laboral.
        
        **Consell 2:** Evita aixecar-te molt tard. Mantenir una hora de despertar constant i aprofitar el matí per fer activitat física o vida social t'ajudarà a sentir que tens temps personal i evitarà l'esgotament psicològic de sentir que el torn de tarda "roba" la teva vida.
        """)

    with st.expander("🌃 Recomanacions per al Torn de Nit"):
        st.write("""
        **El repte:** Viure a contrarellotge. Estàs obligant a estar en màxima alerta quan la teva biologia et demana dormir, i intentes descansar quan el sol i el teu rellotge intern et diuen que és hora d'estar actiu.

         Aquest torn és el més difícil de gestionar, ja que estàs lluitant contra anys d'evolució que t'han programat per dormir de nit i estar despert de dia, però et proposem eines per guanyar aquesta batalla:
        * **Activació a l'inici del torn:** Cerca llum brillant tan bon punt comencis el torn. Si pots, utilitza llums LED potents o pantalles brillants durant les primeres hores per "enganyar" al teu cervell i augmentar el teu estat d'alerta.
        * **Preparació per al final del torn:** Si la teva feina ho permet, intenta reduir la intensitat de la llum i l'ús de pantalles 1-2 hores abans de sortir. Hem de començar a avisar al cos que la teva "nit" particular s'acosta.

        ---

        **Consell 1: Ulleres de sol al tornar a casa.** Aquesta és l'eina secreta: posa't ulleres de sol ben fosques en sortir de la feina. La llum intensa del matí és el principal senyal que el teu cervell utilitza per reajustar el rellotge intern; si la bloqueges, evitaràs que aquest es ressetegi abans d'hora.
        
        **Consell 2: La migdiada de rescat.** La tarda abans de començar el torn de nit, intenta fer una migdiada d'uns 90 minuts. Imagina que el cansament és un **tanc d'aigua**, que es va omplint poc a poc mentre estàs despert i es buida quan dorms. Fer una migdiada abans del torn és com obrir la vàlvula de buidatge: treus volum al tanc perquè tinguis prou espai lliure per aguantar la nit sense que l'aigua vessi abans d'arribar a casa.
        
        **Consell 3: Crea un entorn de son òptim.** El teu dormitori ha de ser totalment fosc. Utilitza cortines opaques o una màscara de son, i considera l'ús de tapons per les orelles: qualsevol raig de llum o soroll de veïns pot fragmentar el teu son diürn i reduir la seva qualitat.
        
        &nbsp;

        **I recorda:** El son diürn és més fràgil que el nocturn, i ja de per sí tendeix a ser de menys qualitat. No t'obsessionis amb aconseguir les 8 hores de son cada dia, la biologia mateixa t'ho posa difícil. El son serà més curt (2-4 hores menys) degut al procés circadiari, però no vol dir que no puguis tenir un son reparador. Prioritza la qualitat del descans per sobre de la qualitat.
        
        """)