import streamlit as st
from groq import Groq

# Configurazione grafica
st.set_page_config(page_title="MyTranscriber Web", page_icon="🎙️", layout="centered")
st.title("🎙️ MyTranscribe: Trascrizione & Chat")
st.markdown("Carica il file per iniziare.")

# Inizializzazione della memoria della chat se non esiste
if "full_text" not in st.session_state:
    st.session_state.full_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Barra laterale per la chiave
api_key = st.sidebar.text_input("Inserisci Groq API Key", type="password")

if not api_key:
    st.info("⚠️ Inserisci la tua API Key di Groq per attivare l'AI.")
else:
    client = Groq(api_key=api_key)

    # Caricamento file (accetta quasi tutto)
    uploaded_file = st.file_uploader("Seleziona audio dal Timoom", type=['mp3', 'wav', 'm4a', 'flac', 'ogg'])

    if uploaded_file:
        st.audio(uploaded_file)
        
        # Bottone per la prima analisi
        if st.button("🚀 Elabora Registrazione"):
            try:
                with st.spinner("Trascrizione in corso..."):
                    file_bytes = uploaded_file.read()
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, file_bytes),
                        model="whisper-large-v3",
                        language="it"
                    )
                    st.session_state.full_text = transcription.text
                
                with st.spinner("Creazione verbale..."):
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Sei un assistente esperto. Crea un verbale con: Riassunto, Punti chiave e Action items."},
                            {"role": "user", "content": f"Testo: {st.session_state.full_text}"}
                        ]
                    )
                    st.session_state.summary = completion.choices[0].message.content
                st.success("Analisi completata!")
            except Exception as e:
                st.error(f"Errore: {e}. Se il file è troppo grande, prova a caricarne uno più breve.")

    # Se abbiamo un testo, mostriamo i risultati e la CHAT
    if st.session_state.full_text:
        tab1, tab2 = st.tabs(["📋 Verbale", "📝 Testo Completo"])
        
        with tab1:
            st.markdown(st.session_state.summary)
        with tab2:
            st.write(st.session_state.full_text)

        # FUNZIONALITÀ CHAT (Chiedi alla trascrizione)
        st.divider()
        st.subheader("💬 Chiedi all'AI sulla registrazione")
        user_query = st.text_input("Fai una domanda specifica (es: 'Quali compiti sono stati assegnati?')")
        
        if user_query:
            with st.spinner("L'AI sta cercando nel testo..."):
                chat_res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"Rispondi basandoti esclusivamente su questo testo: {st.session_state.full_text}"},
                        {"role": "user", "content": user_query}
                    ]
                )
                st.info(chat_res.choices[0].message.content)

# Bottone per resettare tutto
if st.sidebar.button("Cancella tutto"):
    st.session_state.full_text = ""
    st.session_state.summary = ""
    st.rerun()