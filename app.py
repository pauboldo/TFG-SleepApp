import streamlit as st
from datetime import time
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import tempfile, os


 # CONFIGURACIÓ DE LA PÀGINA

st.set_page_config(page_title="DeepShift - TFG", layout="wide")

st.title("DeepShift: Anàlisi i Simulació de la Fragmentació del Son 🌙☀️")
st.markdown("##### DeepShift és una aplicació que neix a partir d'un projecte de Fi de Grau en Enginyeria Biomèdica, amb l'objectiu d'ajudar als treballadors a torns a comprendre i gestionar millor la seva qualitat de son. Aquesta eina ofereix una anàlisi detallada del son, permet simular diferents escenaris de fragmentació del son i proporciona recomanacions personalitzades per millorar la salut del son.")

tab1, tab2, tab3 = st.tabs(["📊 Calcula el teu SCORE", "🧪 Simulador de son", "💡 Recomanacions generals"])

# ..................................

# FUNCIONS

def carregar_hipnograma(file_obj):
    """Llegeix un fitxer EDF d'hipnograma i retorna les anotacions MNE."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".edf") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name
    annotations = mne.read_annotations(tmp_path)
    os.unlink(tmp_path)
    return annotations

def anotacions_a_aasm(annotations):
    """Converteix anotacions MNE a llista d'èpoques en format AASM."""
    raw_stages = []
    for ann in annotations:
        num_epochs = int(ann['duration']) // 30
        label = ann['description'].replace('Sleep stage ', '')
        raw_stages.extend([label] * num_epochs)

    def to_aasm(stage):
        if stage in ['3', '4']: return 'N3'
        mapping = {'1': 'N1', '2': 'N2', 'R': 'R', 'W': 'W'}
        return mapping.get(stage, 'W')

    return [to_aasm(s) for s in raw_stages]

def trim_sleep(stages, margin_epochs=10):
    not_wake_idx = [i for i, s in enumerate(stages) if s != 'W']
    if not not_wake_idx: return stages
    start = max(0, not_wake_idx[0] - margin_epochs)
    end = min(len(stages), not_wake_idx[-1] + margin_epochs)
    return stages[start:end]

def calcular_durada(stages, descomptar_finals=0):
    """Retorna (hours, minutes, durada_hores) descomptant marges i W finals."""
    sleep_epochs = len(stages) - 10 - descomptar_finals
    sleep_epochs = max(0, sleep_epochs)
    durada_hores = (sleep_epochs * 30) / 3600
    hours = int(durada_hores)
    minutes = int((durada_hores - hours) * 60)
    return hours, minutes, durada_hores

# ..................................

# PESTANYA 1: Anàlisi de la qualitat del son

with tab1:
    st.header("Anàlisi de la qualitat del son")

    if 'stages_per_score' not in st.session_state:
        # No hi ha dades encara: oferim els dos camins
        st.markdown("### Escull el teu camí d'entrada per calcular els indicadors de la teva sessió de son:")
        
        col_cami1, col_cami2 = st.columns(2)
        
        with col_cami1:
            with st.container(border=True):
                st.markdown("#### 📂 Camí 1: Puja el teu hipnograma")
                st.markdown("""Tens un fitxer .edf d'una polisomnografia que vulguis analitzar? Puja'l aquí per veure els indicadors del teu son.
                Si no tens cap fitxer a mà, pots descarregar un fitxer de la base de dades Sleep-EDF de PhysioNet, que conté polisomnografies nocturnes reals.
                """)
                st.link_button("📥 Descarrega't un hipnograma en format EDF (PhysioNet)", "https://physionet.org/content/sleep-edfx/1.0.0/sleep-cassette/#files-panel")
                file_score = st.file_uploader("Quan el tinguis llest, puja'l aquí ⬇️", type=["edf"], key="score_uploader")

            if file_score is not None:
                annotations = carregar_hipnograma(file_score)
                aasm_full = anotacions_a_aasm(annotations)
                stages = trim_sleep(aasm_full)
                st.session_state['stages_per_score'] = stages
                st.session_state['origen'] = 'directe'
                st.rerun()

        with col_cami2:
            with st.container(border=True):
                st.markdown("#### 🧪 Camí 2: Usa el Simulador")
                st.markdown("Si no tens cap polisomnografia nocturna real per analitzar, però vols veure com seria una sessió de son diürn fragmentat, pots utilitzar el nostre simulador.")
                st.info('Ves a la pestanya "**🧪 Simulador de son**", puja un fitxer .edf, ajusta els paràmetres i fes clic a **➡️ Enviar a Càlcul de Score**.')

    else:
        # Tenim dades: processem independentment del camí d'entrada
        stages = st.session_state['stages_per_score']
        descomptar = 5 if st.session_state.get('origen') == 'simulat' else 0

        # Botó per reiniciar i canviar de camí
        if st.button("🔄 Analitzar una altra sessió"):
            del st.session_state['stages_per_score']
            del st.session_state['origen']
            st.rerun()

        # Càlcul de durada
        hours, minutes, durada_hores = calcular_durada(stages, descomptar_finals=descomptar)

        # Càlcul de percentatges de fases
        counts = pd.Series(stages).value_counts()
        total = len(stages)
        pct_rem = round(counts.get('R', 0) / total * 100, 1)
        pct_n3  = round(counts.get('N3', 0) / total * 100, 1)

        # Càlcul de despertars (excloent els marges de 5 èpoques per banda)
        stages_core = stages[5:-5]
        transicions_w = sum(
            1 for i in range(1, len(stages_core))
            if stages_core[i] == 'W' and stages_core[i-1] != 'W'
        )

        # Etiqueta d'origen
        if st.session_state.get('origen') == 'simulat':
            st.info("📊 Analitzant hipnograma **simulat** provinent del Simulador (son diürn fragmentat).")
        else:
            st.info("📊 Analitzant hipnograma **real** pujat directament.")

        # Visualització dels indicadors
        st.divider()
        st.subheader("📊 Indicadors de la sessió de son")
        st.caption("Els llindars utilitzats s'indiquen per a cada indicador. Cap d'ells és un llindar validat específicament per a treballadors a torns, ja que aquest estudi no existeix a la literatura actual.")

        col1, col2, col3 = st.columns(3)

        # Indicador 1: Durada
        with col1:

            ref_durada = 6.0
            if durada_hores >= 6:
                color_durada = "✅"
                label_durada = "dins de la referència"
            elif durada_hores >= 4:
                color_durada = "⚠️"
                label_durada = "per sota del mínim recomanat"
            else:
                color_durada = "🔴"
                label_durada = "molt per sota, recuperació compromesa"

            delta_durada = durada_hores - ref_durada
            hores_delta = int(abs(delta_durada))
            minuts_delta = int((abs(delta_durada) - hores_delta) * 60)
            signe = "+" if delta_durada >= 0 else "-"

            st.metric(
                label=f"{color_durada} Durada del son",
                value=f"{hours}h {minutes}min",
                delta=f"{signe}{hores_delta}h {minuts_delta}min respecte el mínim (6h)",
                delta_color="normal"
            )
            st.caption("Referència: ≥6h per son diürn post-torn. El son diürn és més curt que el nocturn (aproximadament 2-4 hores més curt) ja que la temperatura corporal és més alta, els cicles hormonals promouen la vigília durant el dia i els factors ambientals com la llum i el soroll dificulten el descans. Tot i això, menys de 6h s'associa amb un augment de somnolència i risc per a la salut.")
        
        # Indicador 2: Despertars i WASO
        with col2:
            # Càlcul de WASO
            stages_core = stages[5:-5]
            primer_son = next((i for i, s in enumerate(stages_core) if s != 'W'), None)
            if primer_son is not None:
                waso_epochs = sum(1 for s in stages_core[primer_son:] if s == 'W')
                waso_minuts = (waso_epochs * 30) // 60
            else:
                waso_minuts = 0

            # Càlcul de NAW
            transicions_w = sum(
                1 for i in range(1, len(stages_core))
                if stages_core[i] == 'W' and stages_core[i-1] != 'W'
            )

            if waso_minuts < 30:
                color_waso = "✅"
                label_waso = "dins de la referència clínica"
            elif waso_minuts < 45:
                color_waso = "⚠️"
                label_waso = "lleugerament elevat"
            else:
                color_waso = "🔴"
                label_waso = "clínicament significatiu"

            st.metric(
                label=f"{color_waso} WASO",
                value=f"{waso_minuts} min",
                delta=label_waso,
                delta_color="off"
            )
        
            st.caption("WASO normal: <30 min. Lleugerament elevat: 30–45 min. Clínicament significatiu: >45 min. El son diürn tendeix a ser més fragmentat, ja que els factors ambientals (sorolls, llum) són més freqüents que de nit. Un WASO elevat s'associa amb una qualitat de son subjectiva més baixa i més somnolència diürna.")
        
        # Indicador 3: REM
        with col3:
            if pct_rem >= 20 and pct_rem <= 25:
                color_rem = "✅"
                label_rem = "dins de la referència clínica"
            elif pct_rem >= 15:
                color_rem = "⚠️"
                label_rem = "lleugerament per sota"
            elif pct_rem > 25:
                color_rem = "ℹ️"
                label_rem = "per sobre de la referència"
            else:
                color_rem = "🔴"
                label_rem = "molt baix, recuperació cognitiva compromesa"
            
            delta_rem = pct_rem - 20

            st.metric(
                label=f"{color_rem} Son REM",
                value=f"{pct_rem}%",
                delta=f"{delta_rem:+.1f}% respecte referència (20-25%)",
                delta_color="normal"
            )
            st.caption("La fase REM és la fase del son on es produeix la major part de la recuperació cognitiva i emocional, necessària per a la consolidació de la memòria i el tractament emocional. Els estudis demostren que és el predictor més fort de qualitat subjectiva del son, de manera que un REM baix s'associa amb una sensació de no haver descansat, encara que la durada total del son sigui adequada. En son diürn, el rellotge biològic tendeix a suprimir el REM, però valors molt baixos (<15%) poden indicar un son de mala qualitat.")

        # Recomanacions personalitzades basades en els indicadors
        st.divider()
        st.subheader("💡 Recomanacions basades en els teus resultats")

        recomanacions_actives = False

        if durada_hores < 4:
            recomanacions_actives = True
            st.error(f"**Durada crítica ({hours}h {minutes}min).** Has dormit menys de 4 hores, un temps insuficient per a qualsevol tipus de recuperació física o cognitiva. Amb aquesta durada, el teu cos no ha tingut temps ni de completar els cicles de son bàsics. És probable que sentis una fatiga intensa, reflexos lents i dificultat per concentrar-te durant el dia. Si encara no has anat a treballar avui, tingues molt present que no estàs al 100% i estàs molt propens a tenir errors. En cas de tenir temps de marge entre ara i anar a treballar, és recomanable fer una migdiada. Si aquesta situació es repeteix, el risc d'errors i accidents laborals augmenta significativament. Prioritza el son per sobre de qualsevol altra activitat i considera parlar amb el teu metge si el problema és recurrent.")

        elif durada_hores < 6:
            recomanacions_actives = True
            st.warning(f"**Durada insuficient ({hours}h {minutes}min).** Has dormit menys de les 6 hores mínimes recomanades per a son diürn post-torn. És possible que sentis somnolència durant el dia i que la teva recuperació sigui incompleta. Intenta ajustar la teva rutina per prioritzar el son, com anar a dormir més aviat, evitar fer migdiades llargues per tal de no interferir amb el son nocturn i crear un entorn de son òptim (fosc, silenciós i fresc).")
    
        if transicions_w > 45:
            recomanacions_actives = True
            st.error(f"**Son molt fragmentat** ({transicions_w} despertars, {waso_minuts} minuts despert dins del son). El teu son ha estat interromput de forma severa. Quan el son es fragmenta tant, el cos no pot completar els cicles de son correctament i la recuperació és molt limitada, fins i tot si la durada total sembla acceptable. Els microdespertars són molt comuns en son diürn i les causes principals són l'excés de llum a l'habitació o sorolls ambientals. Tants microdespertars indiquen que el teu entorn de son no és òptim: potser vius enmig de la ciutat i sents tot el trànsit, o bé convius amb molta gent a casa, o t'entra un raig de llum directe a l'habitació. Considera instal·lar cortines opaques o blackout, usar tapons per les orelles o una màquina de soroll blanc, i parlar amb les persones amb qui convius perquè evitin fer soroll durant les hores en què dorms. Sembla que vius en un entorn molt sorollós: una màscara de son i uns taps de qualitat poden marcar la diferència.")

        elif transicions_w > 30:
            recomanacions_actives = True
            st.warning(f"**Son fragmentat** ({transicions_w} despertars, {waso_minuts} minuts despert dins del son). Despertar-se durant pocs segons enmig d'una sessió de son és molt comú quan es dorm pel matí després d'un torn de nit. Tens molts estímuls i pertorbacions al voltant: lumíniques, com rajos de llum que entren a l'habitació; o sonores, com el clàxon d'un cotxe, cops de porta de veïns o el soroll d'obres del carrer. Per combatre aquestes petites fragmentacions del son, prova de dormir amb antifaç i taps per reduir estímuls ambientals, i procura que el dormitori sigui el més fosc i silenciós possible.")
    
        if pct_rem < 20:
            recomanacions_actives = True
            st.warning(f"**Son REM baix ({pct_rem}%).** El son REM és clau per a la recuperació cognitiva i emocional, així que és possible que els teus nivells d'alerta siguin baixos. El son consta un seguit de fases que formen un cicle, i la fase REM es fa cada cop més llarga a mesura que transcorre la nit. En son diürn, el ritme circadiari talla el son prematurament i no deixa gaudir de les últimes hores de son riques en REM. Intenta no tallar el son amb l'alarma si pots evitar-ho i allargar la durada del son el màxim possible, no subestimis la important relació entre la salut i el dormir.")
            
        if not recomanacions_actives:
            st.success("**Bona sessió de son.** Has assolit els tres indicadors dins de les referències disponibles. Recorda que el son diürn sempre serà més curt i fràgil que el nocturn; has tret el màxim dins les teves circumstàncies.")
        
        st.info("Consulta les recomanacions específiques per al teu torn a la pestanya **💡 Recomanacions generals** per veure estratègies adaptades a les teves necessitats.")
        st.divider()
        st.caption("""⚠️ **Recorda:** els llindars mostrats representen el millor que es pot assolir en les teves circumstàncies com a treballador a torns, 
        no un son òptim en termes absoluts. Per la naturalesa del son diürn, el teu rellotge biològic treballa en contra teva: 
        6 hores de son diürn equivalen fisiològicament a menys descans que 6 hores de son nocturn. 
        Un indicador en verd vol dir que has tret el que és el mínim correcte dins les teves possibilitats, no que el teu son sigui equivalent al d'una persona amb horari convencional.""")

# .................................

# PESTANYA 2: Simulador de fragmentació del son diürn
with tab2:
    st.header("Simulador de fragmentació")
    st.write("Si no acostumes a dormir de nit però ets curiós, pots simular l'efecte de la fragmentació del son diürn a partir d'una polisomnografia nocturna. Puja el teu fitxer .edf per començar.")
    st.markdown("**Nota:** Si no tens un fitxer .edf a mà, pots descarregar un fitxer de prova de la base de dades Sleep-EDF de PhysioNet, que conté polisomnografies nocturnes reals. Aquestes polisomnografies han estat anotades manualment per experts i són perfectes per veure com el nostre simulador transforma un son nocturn real en una versió més fragmentada i curta, típica del son diürn.")
    st.link_button("📥 Descarrega't un hipnograma en format EDF (PhysioNet)", "https://physionet.org/content/sleep-edfx/1.0.0/sleep-cassette/#files-panel")
    file_sim = st.file_uploader("Aquí ⬇️", type=["edf"], key="sim_uploader")

    if file_sim is not None:
        st.success(f"S'ha llegit el fitxer: **{file_sim.name}.** Processant... (Pot trigar uns segons)")

        # A partir d'aquí es realitza el mateix procés que s'ha testejat i validat a Google Colab. Per veure anotacions, conversió a èpoques AASM, trimming i degradació, consulta el notebook de Google Colab associat a aquesta pestanya.
        
        # Llegim les anotacions del fitxer EDF
        annotations = carregar_hipnograma(file_sim)

        # Conversió de les anotacions a èpoques de 30 segons
        aasm_stages_full = anotacions_a_aasm(annotations)

        # Trimming
        aasm_stages = trim_sleep(aasm_stages_full)

        hours, minutes, _ = calcular_durada(aasm_stages)
        st.info(f"⏱️ Durada del son original: **{hours}h {minutes}min**")

        # Paràmetres de simulació
        st.divider()
        st.subheader("⚙️ Paràmetres de simulació")
        st.caption("Ajusta els paràmetres per controlar la intensitat de la degradació del son diürn.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            prob_wake = st.slider(
                "Probabilitat de microdespertars (%)",
                min_value=0.0, max_value=0.15,
                value=0.05, step=0.01,
                help="Percentatge de probabilitat que cada època de 30 segons es converteixi en un microdespertar, comú en el son diürn i causat per factors ambientals (un raig de llum, un soroll de porta d'un veí...). Valors recomanats: 0.03–0.08. Valors superiors a 0.10 es consideren d'ús únicament experimental."
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
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True)
        fig.patch.set_facecolor('#0e1117')
        max_epochs = max(len(aasm_stages), len(shifted_stages))

        for ax in [ax1, ax2]:
            ax.set_facecolor('#0e1117')
            ax.tick_params(colors='white')
            ax.yaxis.label.set_color('white')
            ax.xaxis.label.set_color('white')
            ax.title.set_color('white')
            ax.set_xlim(0, max_epochs)
            for spine in ax.spines.values():
                spine.set_edgecolor('#444')

        ax1.step(range(len(aasm_stages)), [mapping[s] for s in aasm_stages], color='#4da6ff', linewidth=1)
        ax1.set_title('Hipnograma Original (Son Nocturn)')
        ax1.set_yticks(range(5))
        ax1.set_yticklabels(['W', 'REM', 'N1', 'N2', 'N3'], color='white')
        ax1.grid(True, alpha=0.2)
        ax1.set_xlabel('Èpoques (30 segons)', color='white')

        ax2.step(range(len(shifted_stages)), [mapping[s] for s in shifted_stages], color='#ff6b6b', linewidth=1)
        ax2.set_title('Hipnograma Simulat (Son Diürn)')
        ax2.set_yticks(range(5))
        ax2.set_yticklabels(['W', 'REM', 'N1', 'N2', 'N3'], color='white')
        ax2.grid(True, alpha=0.2)
        ax2.set_xlabel('Èpoques (30 segons)', color='white')

        plt.tight_layout()
        st.pyplot(fig)
        st.info(f"⏱️ Durada del son simulat: **{hours_deg}h {minutes_deg}min**")

        # Sempre que hi ha shifted_stages calculades, les guardem en una clau temporal
        st.session_state['_shifted_temp'] = shifted_stages

        st.divider()
        if st.button("➡️ Enviar a Càlcul de Score"):
            st.session_state['stages_per_score'] = st.session_state['_shifted_temp']
            st.session_state['origen'] = 'simulat'
            st.rerun()  # <- aquesta és la clau
        
        if st.session_state.get('origen') == 'simulat' and 'stages_per_score' in st.session_state:
            st.success("✅ Son simulat enviat correctament. Fes clic a **📊 Calcula el teu SCORE** per veure els indicadors.")
# ...................................

# PESTANYA 3: Recomanacions generals per a treballadors a torns
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
        elif 13 <= h_central < 21:
            torn_detectat = "🌆 TARDA"
        else:
            torn_detectat = "🌃 NIT"

        st.info(f"**Torn detectat: {torn_detectat}**.")

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