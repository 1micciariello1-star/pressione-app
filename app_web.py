import datetime
import urllib.parse
import pandas as pd
import streamlit as st

DB_FILE = "pressione_battiti.csv"


def carica_dati():
  try:
    df = pd.read_csv(DB_FILE, sep=";")
    if (
        "Data e Ora" not in df.columns
        or "Massima" not in df.columns
        or len(df.columns) > 4
    ):
      return pd.DataFrame(
          columns=["Data e Ora", "Massima", "Minima", "Battiti (BPM)"]
      )
    return df
  except (FileNotFoundError, pd.errors.EmptyDataError):
    return pd.DataFrame(
        columns=["Data e Ora", "Massima", "Minima", "Battiti (BPM)"]
    )


def salva_dati(df):
  df.to_csv(DB_FILE, index=False, sep=";")


# --- STILE GRAFICO (BLU E BIANCO) ---
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #0056b3;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #004085;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("❤️ Monitor Pressione e Battiti")

df_storico = carica_dati()

# --- SEZIONE NUOVA MISURAZIONE ---
st.subheader("📝 Nuova Misurazione")

oggi = datetime.date.today()
ora_adesso = datetime.datetime.now().time()

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
    df_storico = df_storico.sort_values(by="Data e Ora", ascending=False)
    salva_dati(df_storico)
    st.success("Misurazione salvata con successo!")
    st.rerun()

with col2:
  if st.button("🗑️ Cancella ultima immissione"):
    if not df_storico.empty:
      df_storico = df_storico.iloc[1:]
      salva_dati(df_storico)
      st.warning("Ultima misurazione eliminata.")
      st.rerun()
    else:
      st.info("Non ci sono misurazioni da cancellare.")

# --- SEZIONE STORICO E REPORT PER IL MEDICO ---
st.markdown("---")
st.subheader("📊 Storico Misurazioni e Report Medico")

if not df_storico.empty and "Data e Ora" in df_storico.columns:
  st.dataframe(df_storico, use_container_width=True)

  st.markdown("---")
  st.subheader("✉️ Invia Report al Medico per Periodo (Da - A)")

  df_storico["Data_Solo"] = pd.to_datetime(df_storico["Data e Ora"]).dt.date

  min_data_db = df_storico["Data_Solo"].min()
  max_data_db = df_storico["Data_Solo"].max()

  col_date1, col_date2 = st.columns(2)
  with col_date1:
    data_inizio = st.date_input(
        "Data Inizio (Da)", value=min_data_db, min_value=min_data_db
    )
  with col_date2:
    data_fine = st.date_input(
        "Data Fine (A)", value=max_data_db, max_value=max_data_db
    )

  email_medico = st.text_input(
      "Indirizzo email del medico:", "medico@esempio.it"
  )

  mask = (df_storico["Data_Solo"] >= data_inizio) & (
      df_storico["Data_Solo"] <= data_fine
  )
  df_filtrato = df_storico.loc[mask]

  if not df_filtrato.empty:
    testo_report = (
        f"Buongiorno dottore, le invio il mio report di pressione e battiti dal"
        f" {data_inizio} al {data_fine}:\n\n"
    )
    for index, row in df_filtrato.iterrows():
      testo_report += (
          f"- {row['Data e Ora']} | Max: {row['Massima']} | Min:"
          f" {row['Minima']} | BPM: {row['Battiti (BPM)']}\n"
      )

    subject = urllib.parse.quote(
        f"Report Pressione ({data_inizio} / {data_fine}) - Luciano"
    )
    body = urllib.parse.quote(testo_report)
    mailto_link = f"mailto:{email_medico}?subject={subject}&body={body}"

    st.markdown(
        f'<a href="{mailto_link}" target="_blank"><button'
        ' style="background-color:#0056b3; color:white; border:none;'
        " padding:10px 20px; border-radius:5px; cursor:pointer; font-size:16px;"
        ' font-weight:bold;">📧 Invia Email con Report Selezionato</button></a>',
        unsafe_allow_html=True,
    )
  else:
    st.warning(
        "Nessuna misurazione trovata nell'intervallo di date selezionato."
    )

else:
  st.info("Nessuna misurazione salvata al momento.")

# --- TASTO ESCI ---
st.markdown("---")
if st.button("🚪 Esci dall'applicazione"):
  st.info(
      "Sei uscito dall'applicazione. Puoi semplicemente chiudere questa scheda"
      " del browser."
  )
  st.stop()