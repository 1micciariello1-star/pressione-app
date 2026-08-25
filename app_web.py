import datetime
import pandas as pd
import streamlit as st

# Nome del file in cui salviamo le misurazioni in locale/sul cloud temporaneo
DB_FILE = "pressione_battiti.csv"


# Funzione per caricare i dati salvati
def carica_dati():
  try:
    return pd.read_csv(DB_FILE)
  except FileNotFoundError:
    # Se il file non esiste ancora, creiamo una tabella vuota
    return pd.DataFrame(
        columns=["Data e Ora", "Massima", "Minima", "Battiti (BPM)"]
    )


# Funzione per salvare i dati
def salva_dati(df):
  df.to_csv(DB_FILE, index=False)


st.title("❤️ Monitor Pressione e Battiti")

# Carichiamo i dati attuali
df_storico = carica_dati()

# --- SEZIONE NUOVA MISURAZIONE ---
st.subheader("📝 Nuova Misurazione")

oggi = datetime.date.today()
ora_adesso = datetime.datetime.now().time()

# Campi modificabili a mano per rimediare a eventuali dimenticanze
data_inserita = st.date_input("Data della misurazione", value=oggi)
ora_inserita = st.time_input("Ora della misurazione", value=ora_adesso)

massima = st.number_input(
    "Massima (Sistolica)", min_value=50, max_value=250, value=120
)
minima = st.number_input(
    "Minima (Diastolica)", min_value=30, max_value=150, value=80
)
battiti = st.number_input("Battiti (BPM)", min_value=30, max_value=200, value=70)

data_ora_completa = datetime.datetime.combine(data_inserita, ora_inserita).strftime(
    "%Y-%m-%d %H:%M:%S"
)

col1, col2 = st.columns(2)

with col1:
  if st.button("💾 Salva Misurazione"):
    nuova_riga = pd.DataFrame([{
        "Data e Ora": data_ora_completa,
        "Massima": int(massima),
        "Minima": int(minima),
        "Battiti (BPM)": int(battiti),
    }])
    df_storico = pd.concat([df_storico, nuova_riga], ignore_index=True)
    # Ordiniamo per data/ora (dalla più recente)
    df_storico = df_storico.sort_values(by="Data e Ora", ascending=False)
    salva_dati(df_storico)
    st.success("Misurazione salvata con successo!")
    st.rerun()

with col2:
  if st.button("🗑️ Cancella ultima immissione"):
    if not df_storico.empty:
      df_storico = df_storico.iloc[1:]  # Rimuove la prima riga
      salva_dati(df_storico)
      st.warning("Ultima misurazione eliminata.")
      st.rerun()
    else:
      st.info("Non ci sono misurazioni da cancellare.")

# --- SEZIONE STORICO MISURAZIONI (Per vedere i dati e darli al medico) ---
st.markdown("---")
st.subheader("📊 Storico Misurazioni")

if not df_storico.empty:
  # Mostriamo la tabella interattiva
  st.dataframe(df_storico, use_container_width=True)

  # --- INOLTRO AL MEDICO VIA EMAIL ---
  st.markdown("---")
  st.subheader("✉️ Invia Report al Medico")

  email_medico = st.text_input(
      "Inserisci l'indirizzo email del medico:", "medico@esempio.it"
  )

  # Prepariamo il testo delle misurazioni formattato per l'email
  testo_report = "Buongiorno dottore, le invio il mio report di pressione e battiti:\n\n"
  for index, row in df_storico.iterrows():
    testo_report += (
        f"- {row['Data e Ora']} | Max: {row['Massima']} | Min:"
        f" {row['Minima']} | BPM: {row['Battiti (BPM)']}\n"
    )

  import urllib.parse

  subject = urllib.parse.quote("Report Pressione e Battiti - Luciano")
  body = urllib.parse.quote(testo_report)
  mailto_link = f"mailto:{email_medico}?subject={subject}&body={body}"

  # Pulsante link per aprire il programma di posta con i dati già dentro
  st.markdown(
      f'<a href="{mailto_link}" target="_blank"><button'
      ' style="background-color:#FF4B4B; color:white; border:none; padding:10px'
      ' 20px; border-radius:5px; cursor:pointer; font-size:16px;">📧 Apri'
      ' Email con Report per il Medico</button></a>',
      unsafe_allow_html=True,
  )

else:
  st.info(
      "Nessuna misurazione salvata al momento. Inserisci la prima qui sopra!"
  )

# --- TASTO ESCI ---
st.markdown("---")
if st.button("🚪 Esci dall'applicazione"):
  st.info(
      "Sei uscito dall'applicazione. Puoi semplicemente chiudere questa scheda"
      " del browser."
  )
  st.stop()