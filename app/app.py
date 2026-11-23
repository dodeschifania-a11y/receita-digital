import streamlit as st
import sqlite3, io, qrcode
from pathlib import Path
from datetime import date, datetime
from fpdf import FPDF

DB = Path(__file__).parent / "receitas.db"
st.set_page_config(page_title="Sistema Receita Digital - Doutor ba Farmasia", page_icon="💊", layout="wide")

# ===== LOGIN =====
if "login" not in st.session_state:
    st.session_state.login = None
if st.session_state.login is None:
    st.markdown("<h1 style='text-align:center; color:black !important;'>💊 SISTEMA RECEITA DIGITAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:black !important;'>Doutór ba Farmasia | Dili, Timor-Leste</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        user = st.selectbox("Hili Papel", ["Doutór", "Farmasia"])
    with col2:
        senha = st.text_input("Senha", type="password", placeholder="Doutór: 1234 | Farmasia: 5678")
    if st.button("🔐 Tama Ba Sistema", use_container_width=True):
        if (user=="Doutór" and senha=="1234") or (user=="Farmasia" and senha=="5678"):
            st.session_state.login = user
            st.rerun()
        else:
            st.error("Senha sala! Tenta fali.")
    st.info("Ba teste: Doutór senha 1234, Farmasia senha 5678.")
    st.stop()

# ===== KOLUNA MATAK + ARROW HALOKON ONA =====
st.markdown("""
<style>
html, body, p, h1, h2, h3, h4, label, div, span, input, textarea, select {
    font-family: "Times New Roman", Times, serif !important;
    color: #000000 !important;
}
.stApp { background: #ffffff !important; }
.header-box { background: #0f766e !important; padding: 22px; border-radius: 16px; text-align: center; border: 2px solid #000000; margin-bottom: 15px; }
.header-box h1 { color: white !important; font-size: 30px; margin: 0; }
.header-box p { color: white !important; margin: 5px 0 0 0; font-weight: bold; }
.small-note { background: #fff4d6 !important; padding: 13px; border-left: 6px solid #e0a526; border-radius: 10px; color: #000000 !important; }
.small-note * { color: #000000 !important; }
.notif { background: #d1fae5 !important; padding: 15px; border-left: 6px solid #059669; border-radius: 10px; font-size: 18px; color: #000000 !important; }
.notif * { color: #000000 !important; }
div[data-testid="stForm"] { background: white !important; padding: 20px; border-radius: 16px; border: 1px solid #000000; }
div[data-testid="stForm"] * { color: #000000 !important; }
/* ARROW HALOKON TIHA - LA MOSU ONA */
div[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
div[data-testid="stExpander"] summary svg { display: none !important; }
div[data-testid="stExpander"] summary::marker { display: none !important; }
div[data-testid="stExpander"] { background: white !important; border-radius: 12px !important; border: 1px solid #000000 !important; margin-bottom: 10px; }
div[data-testid="stExpander"] * { color: #000000 !important; }
div[data-testid="stExpander"] summary p { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; word-break: break-word !important; line-height: 1.4 !important; }
div[data-testid="stExpander"] summary { white-space: normal !important; height: auto !important; }
.stButton > button, .stFormSubmitButton > button { background: #0f766e !important; color: white !important; border-radius: 10px !important; font-weight: bold !important; border: 1px solid #000000 !important; }
.stButton > button *, .stFormSubmitButton > button * { color: white !important; }
</style>
""", unsafe_allow_html=True)

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_no TEXT NOT NULL, prescription_date TEXT NOT NULL,
            patient_name TEXT NOT NULL, patient_age TEXT, patient_contact TEXT,
            prescriber_name TEXT NOT NULL, prescriber_license TEXT,
            medicine_name TEXT NOT NULL, strength TEXT, dosage TEXT NOT NULL,
            route TEXT, frequency TEXT, duration TEXT, quantity TEXT,
            instructions TEXT, status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL
        )""")
        # HALOKON DADUS _arrow OTOMATIKU - LA MOSU TAN
        con.execute("DELETE FROM prescriptions WHERE lower(patient_name) LIKE '%arrow%' OR lower(medicine_name) LIKE '%arrow%'")
def save_record(v):
    with connect() as con:
        con.execute("INSERT INTO prescriptions (prescription_no,prescription_date,patient_name,patient_age,patient_contact,prescriber_name,prescriber_license,medicine_name,strength,dosage,route,frequency,duration,quantity,instructions,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", v)
def get_records():
    with connect() as con:
        return con.execute("SELECT * FROM prescriptions ORDER BY id DESC").fetchall()
def update_status(i,s):
    with connect() as con:
        con.execute("UPDATE prescriptions SET status=? WHERE id=?", (s,i))
def delete_record(i):
    with connect() as con:
        con.execute("DELETE FROM prescriptions WHERE id=?", (i,))

def make_qr(text):
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def make_pdf(r):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "RECEITA DIGITAL - DOUTOR BA FARMASIA", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Numeru: {r['prescription_no']} | Data: {r['prescription_date']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 8, "Dadus Pasiente", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, f"Pasiente: {r['patient_name']}\nIdade: {r['patient_age'] or '-' } | Kontaktu: {r['patient_contact'] or '-'}\nDoutor: {r['prescriber_name']} | Lisensa: {r['prescriber_license'] or '-'}")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 8, "Remediu", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7, f"Remediu: {r['medicine_name']} | Forca: {r['strength'] or '-'}\nDose: {r['dosage']} | Via: {r['route']}\nFrequensia: {r['frequency'] or '-'} | Durasaun: {r['duration'] or '-'} | Kuantidadi: {r['quantity'] or '-'}\nInstrusaun: {r['instructions'] or '-'}")
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 6, "Nota: Sistema demonstrasaun deit. Farmaseutiku tenke verifika receita, dose, alergia no regra lokal antes entrega remediu.")
    return bytes(pdf.output())

def make_print_html(r):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Print - {r['prescription_no']}</title>
<style>
body{{font-family:'Times New Roman',serif; padding:30px; max-width:700px; margin:auto; color:#000 !important;}}
.header{{text-align:center; border-bottom:3px solid #000; padding-bottom:10px;}}
.header h1{{color:#000; margin:0; font-size:26px;}}
.box{{border:1px solid #000; padding:15px; margin-top:15px; border-radius:8px; color:#000;}}
.box h3{{margin:0 0 8px 0; color:#000;}}
.row{{display:flex; justify-content:space-between;}}
.sign{{margin-top:40px; display:flex; justify-content:space-between;}}
.sign div{{text-align:center; border-top:1px solid #000; padding-top:5px; width:200px;}}
@media print{{ .no-print{{display:none;}} }}
</style></head>
<body onload="window.print()">
<div class="no-print" style="text-align:center; background:#fff4d6; padding:10px; border-radius:8px; color:#000;"><b>Pagina print loke ona!</b> Se la mosu, klik Ctrl+P / klik Print iha browser.</div>
<div class="header"><h1>RECEITA DIGITAL</h1><p>Doutor ba Farmasia | Dili, Timor-Leste</p></div>
<div class="row"><p><b>Numeru:</b> {r['prescription_no']}</p><p><b>Data:</b> {r['prescription_date']}</p><p><b>Status:</b> {r['status']}</p></div>
<div class="box"><h3>Dadus Pasiente</h3><p><b>Pasiente:</b> {r['patient_name']}</p><p><b>Idade:</b> {r['patient_age'] or '-'} | <b>Kontaktu:</b> {r['patient_contact'] or '-'}</p></div>
<div class="box"><h3>Dadus Doutor</h3><p><b>Doutor:</b> {r['prescriber_name']}</p><p><b>Lisensa:</b> {r['prescriber_license'] or '-'}</p></div>
<div class="box"><h3>Remediu</h3><p><b>Remediu:</b> {r['medicine_name']} | <b>Forca:</b> {r['strength'] or '-'}</p><p><b>Dose:</b> {r['dosage']} | <b>Via:</b> {r['route']}</p><p><b>Frequensia:</b> {r['frequency'] or '-'} | <b>Durasaun:</b> {r['duration'] or '-'} | <b>Kuantidadi:</b> {r['quantity'] or '-'}</p><p><b>Instrusaun:</b> {r['instructions'] or '-'}</p></div>
<div class="sign"><div>Asinatura Doutor<br><br><br>({r['prescriber_name']})</div><div>Asinatura Farmasia<br><br><br>(_________________)</div></div>
<p style="font-size:11px; text-align:center; margin-top:20px;"><i>Nota: Farmaseutiku tenke verifika receita, dose, alergia no regra lokal antes entrega remediu.</i></p>
</body></html>"""

init_db()

col_h1, col_h2 = st.columns([4,1])
with col_h1:
    st.markdown(f'<div class="header-box"><h1>💊 SISTEMA RECEITA DIGITAL</h1><p>Login hanesan: {st.session_state.login} | DOUTÓR BA FARMASIA</p></div>', unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Sai / Logout"):
        st.session_state.login = None
        st.rerun()

all_rec = get_records()
c1,c2,c3 = st.columns(3)
c1.metric("📋 Total Reseita", len(all_rec))
c2.metric("🔔 Reseita Foun", len([r for r in all_rec if r["status"]=="Haruka husi Doutor"]))
c3.metric("✅ Entrega Ona", len([r for r in all_rec if r["status"]=="Dispensed"]))
st.markdown('<div class="small-note"><b>⚠️ Nota:</b> Sistema demonstrasaun deit. Farmaséutiku tenke verifika antes entrega remédiu.</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.login == "Doutór":
    tab_doutor, tab_lista = st.tabs(["👨‍⚕️ DOUTÓR - Haruka Reseita", "📋 Lista no Arkivu"])
    tab_farmacia = None
else:
    tab_farmacia, tab_lista = st.tabs(["🏥 FARMASIA - Simu Reseita", "📋 Lista no Arkivu"])
    tab_doutor = None

if tab_doutor:
    with tab_doutor:
        st.header("👨‍⚕️ Doutór - Haruka Reseita ba Farmasia")
        with st.form("doutor_form", clear_on_submit=False):
            a,b = st.columns(2)
            with a:
                rx_no = st.text_input("Númeru receita *", placeholder="RX-0001")
                rx_date = st.date_input("Data receita", value=date.today())
                patient = st.text_input("Naran pasiente *")
                age = st.text_input("Idade pasiente", placeholder="Ezemplu: 35")
                contact = st.text_input("Kontaktu pasiente / Telefone")
                prescriber = st.text_input("Naran doutór *")
                license_no = st.text_input("Númeru lisensa doutór")
            with b:
                medicine = st.text_input("Naran remédiu *")
                strength = st.text_input("Força", placeholder="Ezemplu: 500 mg")
                dosage = st.text_input("Dose *", placeholder="Ezemplu: 1 tablete")
                route = st.selectbox("Via", ["Oral", "Tópika", "Inalasaun", "Injeksaun", "Seluk"])
                frequency = st.text_input("Frequénsia", placeholder="Ezemplu: 3x1 / loron")
                duration = st.text_input("Durasaun", placeholder="Ezemplu: 3 loron")
                quantity = st.text_input("Kuantidadi")
            instructions = st.text_area("Instrusaun ba pasiente / Farmasia")
            farmacia = st.selectbox("Haruka ba Farmasia ne'ebé?", ["Farmasia Central Dili", "Farmasia Becora", "Farmasia Comoro", "Farmasia Seluk"])
            submitted = st.form_submit_button("📤 HARUKA BA FARMASIA", use_container_width=True)
            if submitted:
                missing = []
                if not rx_no.strip(): missing.append("Númeru receita")
                if not patient.strip(): missing.append("Naran pasiente")
                if not prescriber.strip(): missing.append("Naran doutór")
                if not medicine.strip(): missing.append("Naran remédiu")
                if not dosage.strip(): missing.append("Dose")
                if missing:
                    st.error("Favor kompleta: " + ", ".join(missing))
                else:
                    save_record((rx_no.strip(), rx_date.isoformat(), patient.strip(), age.strip(), contact.strip(), prescriber.strip(), license_no.strip(), medicine.strip(), strength.strip(), dosage.strip(), route, frequency.strip(), duration.strip(), quantity.strip(), f"[Ba: {farmacia}] {instructions.strip()}", "Haruka husi Doutor", datetime.now().isoformat(timespec="seconds")))
                    st.success(f"✅ HARUKA ONA! Reseita {rx_no} haruka ona ba {farmacia}!")
                    st.balloons()

if tab_farmacia:
    with tab_farmacia:
        st.header("🏥 Farmasia - Reseita Foun Husi Doutór")
        records = get_records()
        novos = [r for r in records if r["status"] == "Haruka husi Doutor"]
        if not novos:
            st.info("📭 Seidauk iha reseita foun husi Doutór. Hein lai...")
        else:
            st.markdown(f'<div class="notif">🔔 <b>Iha Reseita Foun {len(novos)} husi Doutór!</b> Favor verifika no simu!</div>', unsafe_allow_html=True)
            for r in novos:
                # SEM EXPANDER, SEM ARROW - KARTA DE'IT
                with st.container(border=True):
                    st.markdown(f"### 🔔 {r['patient_name']} — {r['medicine_name']}")
                    st.write(f'**Numeru RX:** {r["prescription_no"]} | **Data:** {r["prescription_date"]} | **Pasiente:** {r["patient_name"]} | **Idade:** {r["patient_age"] or "-"}')
                    st.write(f'**Doutór:** {r["prescriber_name"]} | **Remédiu:** {r["medicine_name"]} | **Dose:** {r["dosage"]}')
                    st.write(f'**Instrusaun:** {r["instructions"] or "-"}')
                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button("✅ SIMU RESEITA", key=f'simu_{r["id"]}', use_container_width=True):
                            update_status(r["id"], "Pending"); st.success("Simu ona!"); st.rerun()
                    with c2:
                        if st.button("❌ REJEITA", key=f'rej_{r["id"]}', use_container_width=True):
                            update_status(r["id"], "Rejected"); st.success("Rejeita ona!"); st.rerun()

with tab_lista:
    st.header("📋 Lista no Arkivu - Hotu")
    records = get_records()
    search = st.text_input("🔍 Buka tuir númeru, pasiente ka remédiu", placeholder="Ezemplu: RX-0001 / Maria")
    status_filter = st.selectbox("Filtru Status", ["Hotu", "Haruka husi Doutor", "Pending", "Verified", "Dispensed", "Rejected"])
    filtered = [r for r in records if search.lower() in (r["prescription_no"]+" "+r["patient_name"]+" "+r["medicine_name"]).lower()]
    if status_filter != "Hotu":
        filtered = [r for r in filtered if r["status"]==status_filter]
    if not filtered:
        st.info("Seidauk iha receita.")
    for r in filtered:
        emoji = "🟡" if r["status"]=="Haruka husi Doutor" else "🔵" if r["status"]=="Pending" else "🟢" if r["status"] in ["Verified","Dispensed"] else "🔴"
        # SEM EXPANDER, SEM ARROW - KARTA DE'IT, NARAN LA TAHAN ONA
        with st.container(border=True):
            st.markdown(f"### {emoji} {r['patient_name']} — {r['medicine_name']}")
            st.write(f'**Numeru RX:** {r["prescription_no"]} | **Status:** {r["status"]}')
            st.write(f'**Pasiente:** {r["patient_name"]} | **Remediu:** {r["medicine_name"]}')
            st.write(f'**Data:** {r["prescription_date"]} | **Idade:** {r["patient_age"] or "-"}')
            st.write(f'**Doutór:** {r["prescriber_name"]} | **Dose:** {r["dosage"]} | **Frequénsia:** {r["frequency"] or "-"}')
            st.write(f'**Instrusaun:** {r["instructions"] or "-"}')
            col_qr, col_pdf = st.columns([1,2])
            with col_qr:
                qr_data = f"RECEITA:{r['prescription_no']}|PASIENTE:{r['patient_name']}|REMEDIU:{r['medicine_name']}|DOSE:{r['dosage']}|DOUTOR:{r['prescriber_name']}|STATUS:{r['status']}"
                st.image(make_qr(qr_data), width=150, caption=f"QR - {r['prescription_no']}")
            with col_pdf:
                st.download_button("📄 Download PDF Reseita", data=make_pdf(r), file_name=f"{r['prescription_no']}.pdf", mime="application/pdf", key=f"pdf_{r['id']}")
                st.download_button("📷 Download QR Code", data=make_qr(qr_data), file_name=f"QR-{r['prescription_no']}.png", mime="image/png", key=f"qr_{r['id']}")
                st.download_button("🖨️ PRINT RESEITA", data=make_print_html(r), file_name=f"PRINT-{r['prescription_no']}.html", mime="text/html", key=f"print_{r['id']}")
            new_status = st.selectbox("Status", ["Haruka husi Doutor", "Pending", "Verified", "Dispensed", "Rejected"], index=["Haruka husi Doutor","Pending","Verified","Dispensed","Rejected"].index(r["status"]), key=f'status_{r["id"]}')
            c1,c2 = st.columns(2)
            with c1:
                if st.button("Atualiza status", key=f'update_{r["id"]}', use_container_width=True):
                    update_status(r["id"], new_status); st.success("Status atualizadu!"); st.rerun()
            with c2:
                if st.button("🗑️ Hapaga", key=f'del_{r["id"]}', use_container_width=True):
                    delete_record(r["id"]); st.success("Hapaga ona!"); st.rerun()

st.markdown("<br><center><small style='color:black !important;'>© 2026 Sistema Receita Digital - Doutor ba Farmasia | Dili, Timor-Leste</small></center>", unsafe_allow_html=True)