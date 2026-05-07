import streamlit as st
from datetime import time
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import tempfile, os

st.set_page_config(page_title="Sleep App - TFG", layout="wide")

st.title("DeepShift: Anàlisi i Simulació de la Fragmentació del Son 🌙☀️")
st.markdown("##### DeepShift és una aplicació que neix a partir d'un projecte de Fi de Grau en Enginyeria Biomèdica, amb l'objectiu d'ajudar als treballadors a torns a comprendre i gestionar millor la seva qualitat de son. Aquesta eina ofereix una anàlisi detallada del son real, permet simular diferents escenaris de fragmentació del son i proporciona recomanacions personalitzades per millorar la salut del son.")

tab1, tab2, tab3 = st.tabs(["📊 Calcula el teu SCORE", "🧪 Simulador de son", "💡 Recomanacions generals"])

with tab1:
    st.header("Anàlisi de la qualitat del son")

    # PER ACABAR: afegir via 2 del EDF

    if 'stages_per_score' not in st.session_state:
        st.info("Puja el teu fitxer .edf o utilitza el Simulador per calcular el teu score.")
    
    else:
        stages = st.session_state['stages_per_score']

        total_epochs = len(stages)
        sleep_epochs = total_epochs - 10
        total_seconds = sleep_epochs * 30
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        counts = pd.Series(stages).value_counts()
        total = len(stages)

        pct_rem = round(counts.get('R', 0) / total * 100, 1)
        pct_n3  = round(counts.get('N3', 0) / total * 100, 1)
        pct_w   = round(counts.get('W', 0) / total * 100, 1)

        stages_core = stages[5:-5]
        transicions_w = sum(
            1 for i in range(1, len(stages_core))
            if stages_core[i] == 'W' and stages_core[i-1] != 'W'
        )

        durada_hores = (sleep_epochs * 30) / 3600

        rem_score  = max(0, min(100, (pct_rem / 22.5) * 100))
        frag_score = max(0, min(100, (1 - transicions_w / 30) * 100))

        if durada_hores >= 6:
            dur_score = 100
        elif durada_hores >= 4:
            dur_score = ((durada_hores - 4) / 2) * 100
        else:
            dur_score = 0

        score_final = round(rem_score * 0.40 + frag_score * 0.35 + dur_score * 0.25)

        st.divider()
        st.subheader("📊 Resultats")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Durada", f"{hours}h {minutes}min")
        col2.metric("💤 REM", f"{pct_rem}%")
        col3.metric("🌊 N3", f"{pct_n3}%")
        col4.metric("⚡ Despertars", f"{transicions_w}")

        st.divider()
        st.subheader("🏆 Score de qualitat del son")

        color = "green" if score_final >= 70 else "orange" if score_final >= 50 else "red"
        st.markdown(f"## :{color}[{score_final} / 100]")

        with st.expander("🔍 Descomposició del score"):
            st.write(f"- **REM** ({pct_rem}% → {round(rem_score,1)} pts) × 0.40 = **{round(rem_score*0.40,1)}**")
            st.write(f"- **Fragmentació** ({transicions_w} despertars → {round(frag_score,1)} pts) × 0.35 = **{round(frag_score*0.35,1)}**")
            st.write(f"- **Durada** ({durada_hores:.1f}h → {round(dur_score,1)} pts) × 0.25 = **{round(dur_score*0.25,1)}**")
            st.write(f"**Total: {score_final}/100**")

        # PER ACABAR: afegir hipnograma del son simulat
        # PER ACABAR: afegir recomanacions personalitzades basades en el score

with tab2:
    st.header("Simulador de fragmentació")
    st.write("Si no acostumes a dormir de nit però ets curiós, pots simular l'efecte de la fragmentació del son diürn a partir d'una polisomnografia nocturna. Puja el teu fitxer .edf per començar.")
    file_sim = st.file_uploader("Aquí ⬇️", type=["edf"], key="sim_uploader")

    if file_sim is not None:
        st.success(f"S'ha llegit el fitxer: **{file_sim.name}.** Processant... (Pot trigar uns segons)")

        # A partir d'aquí es realitza el mateix procés que s'ha testejat i validat a Google Colab. Per veure anotacions, conversió a èpoques AASM, trimming i degradació, consulta el notebook de Google Colab associat a aquesta pestanya.
        
        # Llegim les anotacions del fitxer EDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as tmp:
            tmp.write(file_sim.read())
            tmp_path = tmp.name

        annotations = mne.read_annotations(tmp_path)
        os.unlink(tmp_path)

        # Conversió de les anotacions a èpoques de 30 segons
        raw_stages = []
        for ann in annotations:
            num_epochs = int(ann['duration']) // 30
            label = ann['description'].replace('Sleep stage ', '')
            raw_stages.extend([label] * num_epochs)

        # Conversió R&K a AASM
        def to_aasm(stage):
            if stage in ['3', '4']: return 'N3'
            mapping = {'1': 'N1', '2': 'N2', 'R': 'R', 'W': 'W'}
            return mapping.get(stage, 'W')

        aasm_stages_full = [to_aasm(s) for s in raw_stages]

        # Trimming
        def trim_sleep(stages, margin_epochs=10):
            not_wake_idx = [i for i, s in enumerate(stages) if s != 'W']
            if not not_wake_idx: return stages
            start = max(0, not_wake_idx[0] - margin_epochs)
            end = min(len(stages), not_wake_idx[-1] + margin_epochs)
            return stages[start:end]

        aasm_stages = trim_sleep(aasm_stages_full)

        sleep_epochs = len(aasm_stages) - 10
        hours = (sleep_epochs * 30) // 3600
        minutes = ((sleep_epochs * 30) % 3600) // 60
        st.info(f"⏱️ Durada del son original: **{hours}h {minutes}min**")

        # Paràmetres de simulació
        st.divider()
        st.subheader("⚙️ Paràmetres de simulació")
        st.caption("Ajusta els paràmetres per controlar la intensitat de la degradació del son diürn.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            prob_wake = st.slider(
                "Probabilitat de microdespertars (%)",
                min_value=0.0, max_value=0.20,
                value=0.05, step=0.01,
                help="Percentatge de probabilitat que un individu es desperti per pocs segons durant el son, comú en el son diürn i causat per factors ambientals (un raig de llum, un soroll de porta d'un veí...). Valors recomanats: 0.03–0.08"
            )
        with col_p2:
            reduccio_hores = st.slider(
                "Reducció de durada del son (en hores)",
                min_value=0.0, max_value=4.0,
                value=2.5, step=0.5,
                help="Nombre d'hores que es retallen del son original per simular la reducció de durada típica del son diürn. Segons la literatura, el son diürn presenta una reducció de 2-4 hores respecte al son nocturn. Valors recomanats: 2.0–3.5 hores."
            )

        # Amb els paràmetres seleccionats, passem a simular la degradació del son diürn.
        def degrade_sleep_diurn(stages, prob_wake=0.05, reduccio_hores=2.5):
            degraded = list(stages)
            for i in range(len(degraded)):
                if degraded[i] not in ['W', 'N3']:
                    if random.random() < prob_wake:
                        degraded[i] = 'W'
            epoques_a_retallar = int((reduccio_hores * 3600) / 30)
            epoques_a_retallar = min(epoques_a_retallar, len(degraded) // 2)
            degraded = degraded[:len(degraded) - epoques_a_retallar]
            if reduccio_hores > 0:
                degraded = degraded + ['W'] * 5
            return degraded

        shifted_stages = degrade_sleep_diurn(aasm_stages, prob_wake, reduccio_hores)

        if reduccio_hores > 0:
            sleep_epochs_deg = max(0, len(shifted_stages) - 10 - 5)
        else:
            sleep_epochs_deg = max(0, len(shifted_stages) - 10)
        hours_deg = (sleep_epochs_deg * 30) // 3600
        minutes_deg = ((sleep_epochs_deg * 30) % 3600) // 60

        # Estadístiques de distribució de fases
        st.divider()
        st.subheader("📊 Distribució de fases")

        def get_stats(stages):
            return (pd.Series(stages).value_counts(normalize=True) * 100).round(2)

        phase_order = ['W', 'N1', 'N2', 'N3', 'R']
        stats_df = pd.DataFrame({
            'Original (%)': get_stats(aasm_stages),
            'Simulat (%)': get_stats(shifted_stages)
        }).fillna(0).reindex(phase_order)

        st.dataframe(stats_df, use_container_width=True)
        st.caption("Distribució percentual de les diferents fases del son en l'hipnograma original i el simulat. Observa com el son diürn tendeix a presentar més fases de vigília (W, degut als microdespertars) i menys fases N2 i REM (a causa de la influència del ritme circadiari i la reducció de durada del son).")

        # Gràfics d'hipnogrames
        st.divider()
        st.subheader("📈 Comparació d'hipnogrames")

        mapping = {'W': 0, 'R': 1, 'N1': 2, 'N2': 3, 'N3': 4}
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=False)
        fig.patch.set_facecolor('#0e1117')

        for ax in [ax1, ax2]:
            ax.set_facecolor('#0e1117')
            ax.tick_params(colors='white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')

        ax1.step(range(len(aasm_stages)), [mapping[s] for s in aasm_stages], color='#4da6ff', linewidth=1)
        ax1.set_title('Hipnograma Original (Son Nocturn Real)')
        ax1.set_yticks(range(5))
        ax1.set_yticklabels(['W', 'REM', 'N1', 'N2', 'N3'], color='white')
        ax1.grid(True, alpha=0.15)
        ax1.set_xlabel('Èpoques (30 segons)', color='white')

        ax2.step(range(len(shifted_stages)), [mapping[s] for s in shifted_stages], color='#ff6b6b', linewidth=1)
        ax2.set_title('Hipnograma Simulat (Son Diürn Fragmentat)')
        ax2.set_yticks(range(5))
        ax2.set_yticklabels(['W', 'REM', 'N1', 'N2', 'N3'], color='white')
        ax2.grid(True, alpha=0.15)
        ax2.set_xlabel('Èpoques (30 segons)', color='white')

        plt.tight_layout()
        st.pyplot(fig)
        st.info(f"⏱️ Durada del son simulat: **{hours_deg}h {minutes_deg}min**")

        # --- DESCÀRREGA ---
        st.divider()
        if st.button("➡️ Enviar a Càlcul de Score"):
            st.session_state['stages_per_score'] = shifted_stages
            st.session_state['origen'] = 'simulat'
            st.success("✅ Son simulat enviat a la pestanya de Score!")
        

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