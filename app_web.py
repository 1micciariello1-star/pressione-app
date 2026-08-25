import datetime
import pandas as pd
import streamlit as st

st.title("❤️ Monitor Pressione e Battiti")

# --- SEZIONE NUOVA MISURAZIONE CON DATA/ORA MANUALI ---
st.subheader("Nuova Misurazione")

# Otteniamo la data e l'ora attuali come valori predefiniti
oggi = datetime.date.today()
ora_adesso = datetime.datetime.now().time()

# Campi per inserire data e ora a mano (modificabili se ci si è dimenticati prima)
data_inserita = st.date_input("Data della misurazione", value=oggi)
ora_inserita = st.time_input("Ora della misurazione", value=ora_adesso)

# Campi numerici per pressione e battiti
massima = st.number_input("Massima (Sistolica)", min_value=50, max_value=250, value=120)
minima = st.number_input("Minima (Diastolica)", min_value=30, max_value=150, value=80)
battiti = st.number_input("Battiti (BPM)", min_value=30, max_value=200, value=70)

# Uniamo data e ora scelte a mano in un'unica variabile temporale formattata
data_ora_completa = datetime.datetime.combine(data_inserita, ora_inserita).strftime(
    "%Y-%m-%d %H:%M:%S"
)

# --- GESTIONE DEI PULSANTI (Salva e Cancella) ---
col1, col2 = st.columns(2)

with col1:
  if st.button("💾 Salva Misurazione"):
    # Qui inserisci la logica con cui salvi nel database o nel file Excel/CSV
    # Esempio: salviamo data_ora_completa, massima, minima, battiti
    st.success(f"Misurazione salvata per il {data_ora_completa}!")

with col2:
  if st.button("🗑️ Cancella ultima immissione"):
    # Qui inserisci la logica per eliminare l'ultima riga salvata
    st.warning("Ultima misurazione eliminata con successo.")

# --- TASTO ESCI ---
st.markdown("---")
if st.button("🚪 Esci dall'applicazione"):
  st.info(
      "Sei uscito dall'applicazione. Puoi semplicemente chiudere questa scheda"
      " del browser."
  )
  st.stop()