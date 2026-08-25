from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Monitor Pressione", page_icon="❤️", layout="centered"
)

# Stile personalizzato per mantenere il tema blu scuro
st.markdown("""
    <style>
    .stApp {
        background-color: #1e293b;
        color: white;
    }
    h1, h2, h3, label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)


# Database
def inizializza_db():
  conn = sqlite3.connect("pressione_battiti.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS misurazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            massima INTEGER,
            minima INTEGER,
            battiti INTEGER
        )
    """)
  conn.commit()
  conn.close()


inizializza_db()

st.title("❤️ Monitor Pressione e Battiti")

# --- SEZIONE INSERIMENTO DATI ---
st.subheader("Nuova Misurazione")

with st.form("form_misurazione", clear_on_submit=True):
  max_val = st.number_input(
      "Massima (Sistolica)", min_value=50, max_value=250, value=120
  )
  min_val = st.number_input(
      "Minima (Diastolica)", min_value=30, max_value=150, value=80
  )
  bpm_val = st.number_input("Battiti (BPM)", min_value=30, max_value=200, value=70)

  submitted = st.form_submit_button("Salva Misurazione")

  if submitted:
    data_ora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("pressione_battiti.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO misurazioni (data, massima, minima, battiti) VALUES (?, ?,"
        " ?, ?)",
        (data_ora, max_val, min_val, bpm_val),
    )
    conn.commit()
    conn.close()
    st.success("Misurazione salvata con successo!")

# --- VISUALIZZAZIONE STORICO ---
st.subheader("Storico Misurazioni")
conn = sqlite3.connect("pressione_battiti.db")
df = pd.read_sql(
    "SELECT data, massima, minima, battiti FROM misurazioni ORDER BY id DESC",
    conn,
)
conn.close()

if not df.empty:
  st.dataframe(df, use_container_width=True)
else:
  st.info("Nessuna misurazione presente.")

# --- ESPORTAZIONE PER IL MEDICO ---
st.subheader("Esportazione per il Medico")
col1, col2 = st.columns(2)
with col1:
  data_inizio = st.date_input("Dal", value=pd.to_datetime("2026-08-01"))
with col2:
  data_fine = st.date_input("Al", value=pd.to_datetime("2026-08-25"))

if st.button("Genera Report per Email"):
  d_i = data_inizio.strftime("%Y-%m-%d 00:00:00")
  d_f = data_fine.strftime("%Y-%m-%d 23:59:59")

  conn = sqlite3.connect("pressione_battiti.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT data, massima, minima, battiti FROM misurazioni WHERE data BETWEEN"
      " ? AND ? ORDER BY data ASC",
      (d_i, d_f),
  )
  risultati = cursor.fetchall()
  conn.close()

  if risultati:
    report_testo = (
        f"Report Pressione dal {data_inizio} al {data_fine}\n\n"
        + "Data/Ora | Max | Min | BPM\n"
        + "-" * 35
        + "\n"
    )
    for r in risultati:
      report_testo += f"{r[0]} | {r[1]} | {r[2]} | {r[3]}\n"

    st.text_area("Copia il testo per l'email:", report_testo, height=150)
  else:
    st.warning("Nessun dato trovato in questo intervallo.")