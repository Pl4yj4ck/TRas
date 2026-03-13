import streamlit as st
from groq import Groq

# Configurazione grafica
st.set_page_config(page_title="MyPlaud - Timoom Edition", page_icon="🎙️")
st.title("🎙️ MyPlaud: Dal Timoom al Verbale")
st.markdown("Carica il file registrato per ottenere trascrizione e riassunto istantaneo.")

# Gestione Chiave API (la trovi su console.groq.com)
# Per ora la inserisci a mano, poi ti spiego come nasconderla
api_key = st.sidebar.text_input("Inserisci Groq API Key", type="password")

if not api_key:
    st.info("⚠️ Inserisci la tua API Key di Groq nella barra laterale per iniziare.")
else:
    client = Groq(api_key=api_key)

    # Caricamento del file dal telefono (via OTG o memoria interna)
    uploaded_file = st.file_uploader("Seleziona il file MP3 del tuo Timoom", type=['mp3', 'wav', 'm4a'])

    if uploaded_file:
        st.audio(uploaded_file)
        
        if st.button("Genera Analisi"):
            try:
                # 1. TRASCRIZIONE VELOCE (Whisper-large-v3)
                with st.spinner("Trascrizione lampo in corso..."):
                    file_content = uploaded_file.read()
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, file_content),
                        model="whisper-large-v3",
                        response_format="verbose_json",
                        language="it" # Forza l'italiano
                    )
                    full_text = transcription.text
                
                # 2. RIASSUNTO INTELLIGENTE (Llama 3.1 70B)
                with st.spinner("Analisi dei punti chiave..."):
                    completion = client.chat.completions.create(
                        model="llama-3.1-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Sei un assistente che redige verbali professionali. Trasforma la trascrizione in un documento strutturato con: 1. Riassunto breve, 2. Punti chiave discussi, 3. Cose da fare (Action Items). Rispondi in Italiano."},
                            {"role": "user", "content": f"Ecco il testo della registrazione: {full_text}"}
                        ],
                        temperature=0.5
                    )
                    summary = completion.choices[0].message.content

                # Visualizzazione risultati
                st.success("✅ Elaborazione completata!")
                
                tab1, tab2 = st.tabs(["📋 Verbale Riassuntivo", "📝 Trascrizione Completa"])
                
                with tab1:
                    st.markdown(summary)
                    st.download_button("Scarica Verbale", summary, file_name="verbale_riunione.md")
                
                with tab2:
                    st.write(full_text)
                    st.download_button("Scarica Trascrizione", full_text, file_name="trascrizione.txt")

            except Exception as e:
                st.error(f"Errore tecnico: {e}")