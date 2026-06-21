from twilio.rest import Client
import math
import uuid
from datetime import datetime
from pathlib import Path
from ai_tire_analysis import analyser_pneu

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# CONFIG PAGE
# ============================================================

st.set_page_config(
    page_title="Orane Roadside Assistance",
    page_icon="🚛",
    layout="wide"
)


# ============================================================
# STYLE CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

.main-header {
    background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.15);
}

.main-title {
    color: white;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.main-subtitle {
    color: #d1d5db;
    font-size: 18px;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
    border-left: 6px solid #f97316;
    margin-bottom: 15px;
}

.kpi-title {
    color: #6b7280;
    font-size: 15px;
}

.kpi-value {
    color: #111827;
    font-size: 34px;
    font-weight: 700;
}

.stButton>button {
    background-color: #f97316;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 12px 20px;
    font-weight: 700;
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #ea580c;
    transform: scale(1.02);
}

.stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: 600;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div,
.stTextArea textarea {
    border-radius: 12px !important;
}

.stAlert {
    border-radius: 14px;
}

@media (max-width: 768px) {
    .main-header {
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 16px;
    }

    .main-title {
        font-size: 28px;
        line-height: 1.1;
    }

    .main-subtitle {
        font-size: 14px;
    }

    .kpi-card {
        padding: 14px;
        border-radius: 14px;
    }

    .kpi-value {
        font-size: 24px;
    }

    .stButton>button {
        width: 100%;
        min-height: 56px;
        font-size: 18px;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
}

.mobile-card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 2px 12px rgba(0,0,0,0.08);
    margin-bottom: 16px;
    border-left: 6px solid #f97316;
}

.mobile-card-title {
    font-size: 22px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 8px;
}

.mobile-status {
    font-size: 16px;
    font-weight: 700;
    color: #f97316;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# STYLE UI SAAS FLEETRESCUE — AJOUT V1
# ============================================================

st.markdown("""
<style>
:root {
    --fr-navy: #07111f;
    --fr-navy-2: #0f172a;
    --fr-blue: #2563eb;
    --fr-cyan: #06b6d4;
    --fr-green: #22c55e;
    --fr-orange: #f97316;
    --fr-red: #ef4444;
    --fr-gray: #64748b;
    --fr-light: #f8fafc;
    --fr-card: #ffffff;
    --fr-border: rgba(15, 23, 42, 0.10);
}

.fr-hero {
    background: radial-gradient(circle at top left, rgba(37,99,235,0.35), transparent 35%),
                linear-gradient(135deg, #07111f 0%, #111827 52%, #0f172a 100%);
    color: white;
    border-radius: 24px;
    padding: 24px 28px;
    margin: 4px 0 20px 0;
    box-shadow: 0 18px 50px rgba(15, 23, 42, 0.24);
    border: 1px solid rgba(255,255,255,0.08);
}

.fr-hero-title {
    font-size: 28px;
    line-height: 1.1;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
}

.fr-hero-subtitle {
    color: #cbd5e1;
    font-size: 15px;
}

.fr-section-title {
    font-size: 20px;
    font-weight: 850;
    color: #0f172a;
    margin: 8px 0 12px 0;
    letter-spacing: -0.02em;
}

.fr-card {
    background: rgba(255,255,255,0.96);
    border: 1px solid var(--fr-border);
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
}

.fr-card-dark {
    background: linear-gradient(145deg, #0f172a, #111827);
    color: white;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 18px 50px rgba(15, 23, 42, 0.22);
}

.fr-kpi {
    background: white;
    border-radius: 20px;
    border: 1px solid var(--fr-border);
    padding: 16px 18px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.07);
    min-height: 112px;
    position: relative;
    overflow: hidden;
}

.fr-kpi:after {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 80px;
    height: 80px;
    background: radial-gradient(circle, rgba(37,99,235,0.16), transparent 70%);
}

.fr-kpi-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.fr-kpi-value {
    font-size: 34px;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -0.04em;
    margin-top: 8px;
}

.fr-kpi-foot {
    color: #64748b;
    font-size: 13px;
    margin-top: 4px;
}

.fr-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 6px 10px;
    font-weight: 850;
    font-size: 12px;
    border: 1px solid transparent;
    white-space: nowrap;
}
.fr-badge-blue { background: #dbeafe; color: #1d4ed8; border-color: #bfdbfe; }
.fr-badge-green { background: #dcfce7; color: #15803d; border-color: #bbf7d0; }
.fr-badge-orange { background: #ffedd5; color: #c2410c; border-color: #fed7aa; }
.fr-badge-red { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }
.fr-badge-gray { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }

.fr-muted { color: #64748b; }
.fr-strong { font-weight: 850; color: #0f172a; }
.fr-white-muted { color: #cbd5e1; }

.fr-info-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 1px solid rgba(15,23,42,0.08);
    padding: 9px 0;
    font-size: 14px;
}
.fr-info-row:last-child { border-bottom: 0; }
.fr-info-label { color: #64748b; font-weight: 650; }
.fr-info-value { color: #0f172a; font-weight: 800; text-align: right; }

.fr-responder-card {
    background: white;
    border: 1px solid rgba(15,23,42,0.10);
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
}

.fr-responder-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
}

.fr-responder-name {
    font-size: 16px;
    font-weight: 900;
    color: #0f172a;
}

.fr-score {
    background: linear-gradient(135deg, #2563eb, #06b6d4);
    color: white;
    border-radius: 14px;
    padding: 7px 10px;
    font-weight: 900;
    min-width: 58px;
    text-align: center;
}

.fr-mini-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 10px;
}

.fr-mini {
    background: #f8fafc;
    border-radius: 14px;
    padding: 10px;
    border: 1px solid #e2e8f0;
}
.fr-mini-label { color: #64748b; font-size: 11px; font-weight: 750; text-transform: uppercase; }
.fr-mini-value { color: #0f172a; font-size: 15px; font-weight: 900; margin-top: 2px; }

.fr-timeline {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-top: 10px;
}
.fr-step {
    border-radius: 999px;
    padding: 7px 10px;
    font-size: 12px;
    font-weight: 800;
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
}
.fr-step-active {
    background: #dbeafe;
    color: #1d4ed8;
    border-color: #bfdbfe;
}
.fr-step-done {
    background: #dcfce7;
    color: #15803d;
    border-color: #bbf7d0;
}

.fr-empty {
    background: linear-gradient(135deg, #fff7ed, #ffffff);
    border: 1px dashed #fdba74;
    color: #9a3412;
    border-radius: 20px;
    padding: 22px;
    font-weight: 750;
}

/* Rend les boutons plus SaaS, sans casser Streamlit */
.stButton>button {
    border-radius: 14px !important;
    font-weight: 850 !important;
    min-height: 44px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.10);
}

@media (max-width: 768px) {
    .fr-hero-title { font-size: 22px; }
    .fr-kpi-value { font-size: 26px; }
    .fr-mini-grid { grid-template-columns: 1fr; }
    .fr-info-row { display: block; }
    .fr-info-value { text-align: left; margin-top: 3px; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# TWILIO
# ============================================================

def twilio_is_configured():
    required_keys = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "DEMO_PHONE_NUMBER"
    ]

    for key in required_keys:
        if key not in st.secrets:
            return False, key

    return True, ""


def get_twilio_client():
    return Client(
        st.secrets["TWILIO_ACCOUNT_SID"],
        st.secrets["TWILIO_AUTH_TOKEN"]
    )


def generate_google_maps_link(latitude, longitude):
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def generate_google_maps_directions_link(origin_lat, origin_lon, dest_lat, dest_lon):
    return (
        "https://www.google.com/maps/dir/"
        f"{origin_lat},{origin_lon}/{dest_lat},{dest_lon}"
    )


def estimate_eta_minutes(distance_km_value, average_speed_kmh=60):
    try:
        distance = float(distance_km_value)
        if distance <= 0:
            return 5
        return max(5, int(round((distance / average_speed_kmh) * 60)))
    except Exception:
        return ""


def get_sms_target_number(depanneur=None):
    """
    En mode démo, on force l'envoi vers DEMO_PHONE_NUMBER.
    En mode réel, si USE_DEMO_PHONE_NUMBER = false dans secrets.toml,
    le SMS part vers le téléphone du dépanneur sélectionné.
    """
    use_demo = st.secrets.get("USE_DEMO_PHONE_NUMBER", True)
    if isinstance(use_demo, str):
        use_demo = use_demo.strip().lower() in ["true", "1", "yes", "oui"]

    if use_demo or depanneur is None:
        return st.secrets["DEMO_PHONE_NUMBER"]

    return depanneur["telephone"]


def send_assistance_sms(demande_id, client, chauffeur, telephone, immatriculation, latitude, longitude, type_panne, lieu, dimension, urgence, commentaire, depanneur=None):
    client_twilio = get_twilio_client()
    maps_link = generate_google_maps_link(latitude, longitude)
    target_number = get_sms_target_number(depanneur)

    depanneur_nom = depanneur["nom"] if depanneur is not None else "Dépanneur démo"
    distance = depanneur.get("distance_km", "N/A") if depanneur is not None else "N/A"

    body = (
        f"🚨 ALERTE DEPANNAGE PL\n"
        f"ID : {demande_id}\n"
        f"Dépanneur : {depanneur_nom}\n"
        f"Distance : {distance} km\n"
        f"Client : {client}\n"
        f"Chauffeur : {chauffeur}\n"
        f"Tel chauffeur : {telephone}\n"
        f"Véhicule : {immatriculation}\n"
        f"Panne : {type_panne}\n"
        f"Dimension : {dimension}\n"
        f"Lieu : {lieu}\n"
        f"Urgence : {urgence}\n"
        f"GPS : {latitude},{longitude}\n"
        f"Itinéraire : {maps_link}\n"
        f"Commentaire : {commentaire[:120]}"
    )

    message = client_twilio.messages.create(
        body=body,
        from_=st.secrets["TWILIO_FROM_NUMBER"],
        to=target_number
    )

    return message.sid, target_number


def send_driver_confirmation_sms(demande_id, telephone, client, immatriculation, type_panne):
    client_twilio = get_twilio_client()

    # En mode démo / compte Trial Twilio, on force aussi le SMS chauffeur
    # vers le numéro vérifié DEMO_PHONE_NUMBER.
    use_demo = st.secrets.get("USE_DEMO_PHONE_NUMBER", True)
    if isinstance(use_demo, str):
        use_demo = use_demo.strip().lower() in ["true", "1", "yes", "oui"]

    target_number = st.secrets["DEMO_PHONE_NUMBER"] if use_demo else telephone

    body = (
        f"Orane Assistance : votre demande {demande_id} est enregistrée. "
        f"Client : {client}. Véhicule : {immatriculation}. Panne : {type_panne}. "
        f"Un dépanneur est en cours de sollicitation."
    )

    message = client_twilio.messages.create(
        body=body,
        from_=st.secrets["TWILIO_FROM_NUMBER"],
        to=target_number
    )

    return message.sid, target_number


def make_assistance_call(demande_id, client, chauffeur, immatriculation, type_panne, lieu, urgence):
    client_twilio = get_twilio_client()

    twiml = f"""
    <Response>
        <Say language="fr-FR" voice="alice">
            Bonjour. Nouvelle demande de dépannage.
            Référence {demande_id}.
            Client {client}.
            Chauffeur {chauffeur}.
            Véhicule immatriculé {immatriculation}.
            Type de panne : {type_panne}.
            Lieu : {lieu}.
            Niveau d'urgence : {urgence}.
            Merci de prendre en charge l'intervention.
        </Say>
    </Response>
    """

    call = client_twilio.calls.create(
        twiml=twiml,
        from_=st.secrets["TWILIO_FROM_NUMBER"],
        to=st.secrets["DEMO_PHONE_NUMBER"]
    )

    return call.sid


# ============================================================
# HEADER AVEC LOGO
# ============================================================

LOGO_FILE = Path("assets") / "fleetpartner_logo.png"

col_logo, col_title = st.columns([1, 5])

with col_logo:
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), width=180)
    else:
        st.markdown("")

with col_title:
    st.markdown("""
    <div class="main-header">
        <div class="main-title">Orane Roadside Assistance</div>
        <div class="main-subtitle">
            Assistance et dépannage poids lourds • Route • Autoroute • 24/7
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FICHIERS DATA
# ============================================================

DATA_DIR = Path("data")

if DATA_DIR.exists() and not DATA_DIR.is_dir():
    DATA_DIR.unlink()

DATA_DIR.mkdir(exist_ok=True)

DEPANNEURS_FILE = DATA_DIR / "depanneurs_demo.csv"
DEMANDES_FILE = DATA_DIR / "demandes_demo.csv"
TENTATIVES_FILE = DATA_DIR / "tentatives_demo.csv"
STOCKS_FILE = DATA_DIR / "stocks_demo.csv"


# ============================================================
# INITIALISATION DES DONNÉES
# ============================================================

def init_data():
    if not DEPANNEURS_FILE.exists():
        pd.DataFrame([
            ["D001", "BestDrive Roissy", "BestDrive", "Roissy-en-France", 49.0040, 2.5170, "+33600000001", "roissy@bestdrive-demo.fr", 90, True, True, True, True, "315/80 R22.5;315/70 R22.5;385/65 R22.5", 4.7],
            ["D002", "BestDrive Compiègne", "BestDrive", "Compiègne", 49.4179, 2.8261, "+33600000002", "compiegne@bestdrive-demo.fr", 100, True, True, True, True, "315/80 R22.5;295/80 R22.5", 4.8],
            ["D003", "BestDrive Lille", "BestDrive", "Lille", 50.6292, 3.0573, "+33600000003", "lille@bestdrive-demo.fr", 120, True, True, True, True, "315/70 R22.5;385/65 R22.5", 4.5],
            ["D004", "BestDrive Amiens", "BestDrive", "Amiens", 49.8941, 2.2958, "+33600000004", "amiens@bestdrive-demo.fr", 100, True, True, True, True, "315/80 R22.5;385/65 R22.5", 4.3],
            ["D005", "BestDrive Rouen", "BestDrive", "Rouen", 49.4431, 1.0993, "+33600000005", "rouen@bestdrive-demo.fr", 100, True, True, True, True, "315/80 R22.5;315/70 R22.5", 4.2],
            ["D006", "BestDrive Paris Nord", "BestDrive", "Saint-Denis", 48.9362, 2.3574, "+33600000006", "parisnord@bestdrive-demo.fr", 80, True, True, True, False, "315/70 R22.5", 4.1],
            ["D007", "BestDrive Reims", "BestDrive", "Reims", 49.2583, 4.0317, "+33600000007", "reims@bestdrive-demo.fr", 110, True, True, True, True, "315/80 R22.5;385/65 R22.5", 4.6],
            ["D008", "BestDrive Metz", "BestDrive", "Metz", 49.1193, 6.1757, "+33600000008", "metz@bestdrive-demo.fr", 120, True, True, True, True, "315/80 R22.5;315/60 R22.5", 4.4],
            ["D009", "BestDrive Lyon", "BestDrive", "Lyon", 45.7640, 4.8357, "+33600000009", "lyon@bestdrive-demo.fr", 150, True, True, True, True, "315/80 R22.5;385/65 R22.5", 4.7],
            ["D010", "BestDrive Marseille", "BestDrive", "Marseille", 43.2965, 5.3698, "+33600000010", "marseille@bestdrive-demo.fr", 150, True, True, True, True, "315/80 R22.5;295/80 R22.5", 4.2],
            ["D011", "BestDrive Toulouse", "BestDrive", "Toulouse", 43.6047, 1.4442, "+33600000011", "toulouse@bestdrive-demo.fr", 140, True, True, True, True, "315/70 R22.5;385/65 R22.5", 4.5],
            ["D012", "BestDrive Bordeaux", "BestDrive", "Bordeaux", 44.8378, -0.5792, "+33600000012", "bordeaux@bestdrive-demo.fr", 140, True, True, True, True, "315/80 R22.5;385/55 R22.5", 4.6],
            ["D013", "BestDrive Nantes", "BestDrive", "Nantes", 47.2184, -1.5536, "+33600000013", "nantes@bestdrive-demo.fr", 130, True, True, True, True, "315/80 R22.5;315/70 R22.5", 4.4],
            ["D014", "BestDrive Strasbourg", "BestDrive", "Strasbourg", 48.5734, 7.7521, "+33600000014", "strasbourg@bestdrive-demo.fr", 120, True, True, True, True, "315/80 R22.5;385/65 R22.5", 4.5],
            ["D015", "BestDrive Nice", "BestDrive", "Nice", 43.7102, 7.2620, "+33600000015", "nice@bestdrive-demo.fr", 120, True, True, True, True, "315/70 R22.5;295/80 R22.5", 4.1],
        ], columns=[
            "id", "nom", "reseau", "ville", "latitude", "longitude",
            "telephone", "email", "zone_km", "route", "autoroute",
            "pl", "disponible", "stock", "score"
        ]).to_csv(DEPANNEURS_FILE, index=False)

    # Stock simulé : dans une vraie version, cette table sera remplacée
    # par une API Winpro / Innovaxo. On garde le même format cible.
    if not STOCKS_FILE.exists():
        pd.DataFrame([
            ["D001", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 4, "2026-06-21 08:00:00"],
            ["D001", "315/70 R22.5", "Continental", "Conti EcoPlus HS3", 2, "2026-06-21 08:00:00"],
            ["D001", "385/65 R22.5", "Semperit", "Runner T3", 1, "2026-06-21 08:00:00"],
            ["D002", "315/80 R22.5", "Continental", "Conti Hybrid HD3", 6, "2026-06-21 08:00:00"],
            ["D002", "295/80 R22.5", "Uniroyal", "FH40", 3, "2026-06-21 08:00:00"],
            ["D003", "315/70 R22.5", "Continental", "Conti EcoRegional HS3", 5, "2026-06-21 08:00:00"],
            ["D003", "385/65 R22.5", "Continental", "Conti Hybrid HT3", 2, "2026-06-21 08:00:00"],
            ["D004", "315/80 R22.5", "Barum", "BF200R", 1, "2026-06-21 08:00:00"],
            ["D004", "385/65 R22.5", "Continental", "Conti Hybrid HT3", 0, "2026-06-21 08:00:00"],
            ["D005", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 2, "2026-06-21 08:00:00"],
            ["D006", "315/70 R22.5", "Semperit", "Runner D2", 1, "2026-06-21 08:00:00"],
            ["D007", "315/80 R22.5", "Continental", "Conti Hybrid HD3", 4, "2026-06-21 08:00:00"],
            ["D007", "385/65 R22.5", "Continental", "Conti Hybrid HT3", 2, "2026-06-21 08:00:00"],
            ["D008", "315/80 R22.5", "Continental", "Conti EcoPlus HS3", 2, "2026-06-21 08:00:00"],
            ["D009", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 5, "2026-06-21 08:00:00"],
            ["D009", "385/65 R22.5", "Semperit", "Runner T3", 4, "2026-06-21 08:00:00"],
            ["D010", "295/80 R22.5", "Continental", "Conti Hybrid HD3", 2, "2026-06-21 08:00:00"],
            ["D011", "315/70 R22.5", "Continental", "Conti EcoRegional HD3", 3, "2026-06-21 08:00:00"],
            ["D012", "315/80 R22.5", "Continental", "Conti Hybrid HS3", 3, "2026-06-21 08:00:00"],
            ["D013", "315/80 R22.5", "Semperit", "Runner D2", 2, "2026-06-21 08:00:00"],
            ["D014", "315/80 R22.5", "Continental", "Conti Hybrid HD3", 3, "2026-06-21 08:00:00"],
            ["D015", "315/70 R22.5", "Continental", "Conti Hybrid HS3", 2, "2026-06-21 08:00:00"],
        ], columns=[
            "depanneur_id", "dimension", "marque", "profil", "quantite", "last_update"
        ]).to_csv(STOCKS_FILE, index=False)

    if not DEMANDES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "date_creation", "client", "chauffeur",
            "telephone_chauffeur", "immatriculation", "latitude",
            "longitude", "type_panne", "lieu", "dimension", "urgence",
            "statut", "depanneur_assigne", "distance_km", "mode_paiement",
            "commentaire", "photo_1", "photo_2", "date_cloture",
            "depanneur_nom", "depanneur_telephone", "depanneur_latitude",
            "depanneur_longitude", "eta_minutes", "tracking_url",
            "date_prise_en_charge", "stock_disponible", "stock_quantite",
            "stock_marque", "stock_profil", "score_ia", "decision_ia",
            "date_mise_a_jour_statut"
        ]).to_csv(DEMANDES_FILE, index=False)

    if not TENTATIVES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "demande_id", "rang", "depanneur_id",
            "depanneur_nom", "distance_km", "canal",
            "statut", "date_tentative", "depanneur_telephone",
            "depanneur_latitude", "depanneur_longitude", "stock_disponible",
            "stock_quantite", "stock_marque", "stock_profil", "score_ia",
            "decision_ia"
        ]).to_csv(TENTATIVES_FILE, index=False)


# ============================================================
# OUTILS CSV
# ============================================================

def load_csv(path):
    return pd.read_csv(path)


def save_csv(df, path):
    df.to_csv(path, index=False)


def ensure_columns(path, columns_defaults):
    df = load_csv(path)
    changed = False

    for column, default_value in columns_defaults.items():
        if column not in df.columns:
            df[column] = default_value
            changed = True

    if changed:
        save_csv(df, path)

    return df


def ensure_data_schema():
    ensure_columns(DEMANDES_FILE, {
        "depanneur_nom": "",
        "depanneur_telephone": "",
        "depanneur_latitude": "",
        "depanneur_longitude": "",
        "eta_minutes": "",
        "tracking_url": "",
        "date_prise_en_charge": "",
        "stock_disponible": False,
        "stock_quantite": 0,
        "stock_marque": "",
        "stock_profil": "",
        "score_ia": 0,
        "decision_ia": "",
        "date_mise_a_jour_statut": "",
    })

    ensure_columns(TENTATIVES_FILE, {
        "depanneur_telephone": "",
        "depanneur_latitude": "",
        "depanneur_longitude": "",
        "stock_disponible": False,
        "stock_quantite": 0,
        "stock_marque": "",
        "stock_profil": "",
        "score_ia": 0,
        "decision_ia": "",
    })

    ensure_columns(STOCKS_FILE, {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


# ============================================================
# CALCUL DISTANCE
# ============================================================

def distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    )

    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in ["true", "1", "yes", "oui", "vrai"]


def normalize_dimension(value):
    return str(value).upper().replace(" ", "").replace("/", "/")


def get_stock_for_depanneur(depanneur_id, dimension):
    """
    Simulation API stock Winpro / Innovaxo.
    Aujourd'hui : lecture dans stocks_demo.csv.
    Demain : appel HTTP/API ou connecteur base de données.
    """
    stocks = load_csv(STOCKS_FILE)
    if stocks.empty or not dimension or dimension == "Autre / inconnue":
        return {
            "available": False,
            "quantity": 0,
            "brand": "",
            "profile": "",
            "last_update": "",
        }

    dim_norm = normalize_dimension(dimension)
    stocks = stocks.copy()
    stocks["dimension_norm"] = stocks["dimension"].apply(normalize_dimension)

    rows = stocks[
        (stocks["depanneur_id"] == depanneur_id)
        & (stocks["dimension_norm"] == dim_norm)
    ]

    if rows.empty:
        return {
            "available": False,
            "quantity": 0,
            "brand": "",
            "profile": "",
            "last_update": "",
        }

    row = rows.sort_values("quantite", ascending=False).iloc[0]
    quantity = int(row.get("quantite", 0))

    return {
        "available": quantity > 0,
        "quantity": quantity,
        "brand": row.get("marque", ""),
        "profile": row.get("profil", ""),
        "last_update": row.get("last_update", ""),
    }


def scorer_depanneur(depanneur, demande, distance_value, stock_info):
    """
    Moteur de dispatch automatique.
    L'objectif n'est pas seulement de trouver le plus proche,
    mais celui qui a la meilleure probabilité de résoudre vite.
    """
    score = 100.0

    # Distance : pénalité progressive.
    score -= float(distance_value) * 1.2

    # Stock : énorme facteur de décision.
    if stock_info["available"]:
        score += 45
        score += min(int(stock_info["quantity"]), 6) * 2
    else:
        score -= 70

    # Urgence / autoroute.
    urgence = demande.get("urgence", "")
    if urgence == "Danger immédiat / voie rapide":
        score += 20 if to_bool(depanneur.get("autoroute", False)) else -80
    elif urgence == "Urgent":
        score += 10

    # Qualité / performance historique simulée.
    try:
        score += float(depanneur.get("score", 0)) * 8
    except Exception:
        pass

    # Disponibilité.
    if to_bool(depanneur.get("disponible", False)):
        score += 20
    else:
        score -= 200

    return round(score, 1)


def trouver_depanneurs(demande, depanneurs):
    rows = []

    for _, d in depanneurs.iterrows():
        if not to_bool(d.get("disponible", False)) or not to_bool(d.get("pl", False)):
            continue

        if demande["lieu"] == "Autoroute" and not to_bool(d.get("autoroute", False)):
            continue

        if demande["lieu"] == "Route" and not to_bool(d.get("route", False)):
            continue

        dist = distance_km(
            demande["latitude"],
            demande["longitude"],
            d["latitude"],
            d["longitude"]
        )

        if dist <= float(d["zone_km"]):
            row = d.to_dict()
            row["distance_km"] = round(dist, 1)

            stock_info = get_stock_for_depanneur(row["id"], demande.get("dimension", ""))
            row["stock_disponible"] = stock_info["available"]
            row["stock_quantite"] = stock_info["quantity"]
            row["stock_marque"] = stock_info["brand"]
            row["stock_profil"] = stock_info["profile"]
            row["stock_last_update"] = stock_info["last_update"]

            row["score_ia"] = scorer_depanneur(row, demande, row["distance_km"], stock_info)

            if stock_info["available"]:
                row["decision_ia"] = "Recommandé : stock disponible"
            else:
                row["decision_ia"] = "Dégradé : stock non confirmé"

            rows.append(row)

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(
        sorted(rows, key=lambda x: (-float(x["score_ia"]), x["distance_km"]))
    )


# ============================================================
# CARTE FOLIUM
# ============================================================

def afficher_carte_depanneurs(latitude, longitude, candidats, client, chauffeur, immatriculation, type_panne, dimension, urgence):
    if candidats.empty:
        return

    st.markdown("### 🗺️ Carte des dépanneurs à proximité")

    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=8,
        tiles="OpenStreetMap"
    )

    folium.Marker(
        location=[latitude, longitude],
        tooltip="Camion en panne",
        popup=f"""
        <b>🚛 Camion en panne</b><br>
        Client : {client}<br>
        Chauffeur : {chauffeur}<br>
        Immatriculation : {immatriculation}<br>
        Panne : {type_panne}<br>
        Dimension : {dimension}<br>
        Urgence : {urgence}
        """,
        icon=folium.Icon(
            color="red",
            icon="truck",
            prefix="fa"
        )
    ).add_to(m)

    folium.CircleMarker(
        location=[latitude, longitude],
        radius=14,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.35,
        popup="Zone de panne"
    ).add_to(m)

    for _, d in candidats.iterrows():
        folium.Marker(
            location=[d["latitude"], d["longitude"]],
            tooltip=f'{d["nom"]} - {d["distance_km"]} km',
            popup=f"""
            <b>🛠️ {d["nom"]}</b><br>
            Ville : {d["ville"]}<br>
            Réseau : {d["reseau"]}<br>
            Distance : {d["distance_km"]} km<br>
            Téléphone : {d["telephone"]}<br>
            Stock demandé : {"✅ Oui" if d.get("stock_disponible", False) else "⚠️ Non confirmé"}<br>
            Quantité : {d.get("stock_quantite", 0)}<br>
            Marque/profil : {d.get("stock_marque", "")} {d.get("stock_profil", "")}<br>
            Score IA : {d.get("score_ia", "")}
            """,
            icon=folium.Icon(
                color="green",
                icon="wrench",
                prefix="fa"
            )
        ).add_to(m)

        folium.PolyLine(
            locations=[
                [latitude, longitude],
                [d["latitude"], d["longitude"]]
            ],
            color="orange",
            weight=2,
            opacity=0.7
        ).add_to(m)

    components.html(
        m._repr_html_(),
        height=550
    )


# ============================================================
# SUIVI CHAUFFEUR MOBILE
# ============================================================

def afficher_suivi_chauffeur(demande):
    statut = demande.get("statut", "En cours")
    depanneur_nom = demande.get("depanneur_nom", "") or demande.get("depanneur_assigne", "")
    depanneur_tel = demande.get("depanneur_telephone", "")
    distance = demande.get("distance_km", "")
    eta = demande.get("eta_minutes", "")
    tracking_url = demande.get("tracking_url", "")
    immatriculation = demande.get("immatriculation", "")
    type_panne = demande.get("type_panne", "")

    if not depanneur_nom:
        depanneur_nom = "Dépanneur en cours d’affectation"

    if not eta or str(eta).lower() == "nan":
        eta_label = "En cours"
    else:
        eta_label = f"{eta} min"

    st.markdown(
        f"""
        <div class="mobile-card">
            <div class="mobile-card-title">🚛 Votre dépannage</div>
            <div class="mobile-status">{statut}</div>
            <br>
            <b>Véhicule :</b> {immatriculation}<br>
            <b>Panne :</b> {type_panne}<br>
            <b>Agence / dépanneur :</b> {depanneur_nom}<br>
            <b>Téléphone :</b> {depanneur_tel if depanneur_tel else "—"}<br>
            <b>Distance :</b> {distance if str(distance).lower() != "nan" else "—"} km
        </div>
        """,
        unsafe_allow_html=True
    )

    st.metric("Temps estimé d'arrivée", eta_label)

    if depanneur_tel and str(depanneur_tel).lower() != "nan":
        st.link_button(
            "📞 Appeler le dépanneur",
            f"tel:{depanneur_tel}",
            use_container_width=True
        )

    if tracking_url and str(tracking_url).lower() != "nan":
        st.link_button(
            "🗺️ Suivre / voir l’itinéraire",
            tracking_url,
            use_container_width=True
        )

    st.info("Le suivi temps réel GPS du dépanneur sera ajouté dans une prochaine étape. Pour le MVP, ce bouton ouvre l’itinéraire Google Maps.")


# ============================================================
# CASCADE DE SOLLICITATION
# ============================================================

def creer_tentatives(demande_id, candidats):
    tentatives = load_csv(TENTATIVES_FILE)
    new_rows = []

    for rang, (_, d) in enumerate(candidats.head(5).iterrows(), start=1):
        new_rows.append({
            "id": str(uuid.uuid4())[:8],
            "demande_id": demande_id,
            "rang": rang,
            "depanneur_id": d["id"],
            "depanneur_nom": d["nom"],
            "distance_km": d["distance_km"],
            "canal": "App dépanneur + SMS + Appel",
            "statut": "En attente" if rang == 1 else "En file",
            "date_tentative": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "depanneur_telephone": d.get("telephone", ""),
            "depanneur_latitude": d.get("latitude", ""),
            "depanneur_longitude": d.get("longitude", ""),
            "stock_disponible": d.get("stock_disponible", False),
            "stock_quantite": d.get("stock_quantite", 0),
            "stock_marque": d.get("stock_marque", ""),
            "stock_profil": d.get("stock_profil", ""),
            "score_ia": d.get("score_ia", 0),
            "decision_ia": d.get("decision_ia", ""),
        })

    save_csv(
        pd.concat([tentatives, pd.DataFrame(new_rows)], ignore_index=True),
        TENTATIVES_FILE
    )


def accepter_tentative(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    demandes = load_csv(DEMANDES_FILE)

    idxs = tentatives[
        (tentatives.demande_id == demande_id)
        & (tentatives.statut == "En attente")
    ].index

    if len(idxs) == 0:
        return

    idx = idxs[0]

    nom = tentatives.loc[idx, "depanneur_nom"]
    dist = tentatives.loc[idx, "distance_km"]

    tentatives.loc[idx, "statut"] = "Accepté"
    tentatives.loc[
        (tentatives.demande_id == demande_id)
        & (tentatives.statut == "En file"),
        "statut"
    ] = "Annulé"

    d_idx = demandes[demandes.id == demande_id].index[0]
    dep_tel = tentatives.loc[idx, "depanneur_telephone"] if "depanneur_telephone" in tentatives.columns else ""
    dep_lat = tentatives.loc[idx, "depanneur_latitude"] if "depanneur_latitude" in tentatives.columns else ""
    dep_lon = tentatives.loc[idx, "depanneur_longitude"] if "depanneur_longitude" in tentatives.columns else ""

    demandes.loc[d_idx, "statut"] = "Accepté par dépanneur"
    demandes.loc[d_idx, "depanneur_assigne"] = nom
    demandes.loc[d_idx, "depanneur_nom"] = nom
    demandes.loc[d_idx, "depanneur_telephone"] = dep_tel
    demandes.loc[d_idx, "depanneur_latitude"] = dep_lat
    demandes.loc[d_idx, "depanneur_longitude"] = dep_lon
    demandes.loc[d_idx, "distance_km"] = dist
    demandes.loc[d_idx, "eta_minutes"] = estimate_eta_minutes(dist)
    demandes.loc[d_idx, "date_prise_en_charge"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    demandes.loc[d_idx, "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for col in ["stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]:
        if col in tentatives.columns:
            demandes.loc[d_idx, col] = tentatives.loc[idx, col]

    if dep_lat != "" and dep_lon != "":
        demandes.loc[d_idx, "tracking_url"] = generate_google_maps_directions_link(
            dep_lat,
            dep_lon,
            demandes.loc[d_idx, "latitude"],
            demandes.loc[d_idx, "longitude"]
        )

    save_csv(tentatives, TENTATIVES_FILE)
    save_csv(demandes, DEMANDES_FILE)


def passer_au_suivant(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)

    active = tentatives[
        (tentatives.demande_id == demande_id)
        & (tentatives.statut == "En attente")
    ].index

    if len(active):
        tentatives.loc[active[0], "statut"] = "Expiré / pas de réponse"

    queued = tentatives[
        (tentatives.demande_id == demande_id)
        & (tentatives.statut == "En file")
    ].sort_values("rang")

    if len(queued):
        tentatives.loc[queued.index[0], "statut"] = "En attente"
    else:
        demandes = load_csv(DEMANDES_FILE)
        idx = demandes[demandes.id == demande_id].index

        if len(idx):
            demandes.loc[idx[0], "statut"] = "A traiter manuellement"
            save_csv(demandes, DEMANDES_FILE)

    save_csv(tentatives, TENTATIVES_FILE)


def cloturer(demande_id):
    demandes = load_csv(DEMANDES_FILE)

    idx = demandes[demandes.id == demande_id].index

    if len(idx):
        demandes.loc[idx[0], "statut"] = "Clôturé"
        demandes.loc[idx[0], "date_cloture"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_csv(demandes, DEMANDES_FILE)



def update_demande_status(demande_id, statut):
    demandes = load_csv(DEMANDES_FILE)
    idx = demandes[demandes.id == demande_id].index

    if len(idx):
        demandes.loc[idx[0], "statut"] = statut
        demandes.loc[idx[0], "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if statut == "Clôturé":
            demandes.loc[idx[0], "date_cloture"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_csv(demandes, DEMANDES_FILE)


def depanneur_refuse_mission(demande_id):
    passer_au_suivant(demande_id)
    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)

    active = tentatives[
        (tentatives.demande_id == demande_id)
        & (tentatives.statut == "En attente")
    ]

    idx = demandes[demandes.id == demande_id].index
    if len(idx):
        if active.empty:
            demandes.loc[idx[0], "statut"] = "A traiter manuellement"
        else:
            row = active.iloc[0]
            demandes.loc[idx[0], "statut"] = "Mission proposée au dépanneur"
            demandes.loc[idx[0], "depanneur_nom"] = row.get("depanneur_nom", "")
            demandes.loc[idx[0], "depanneur_telephone"] = row.get("depanneur_telephone", "")
            demandes.loc[idx[0], "depanneur_latitude"] = row.get("depanneur_latitude", "")
            demandes.loc[idx[0], "depanneur_longitude"] = row.get("depanneur_longitude", "")
            demandes.loc[idx[0], "distance_km"] = row.get("distance_km", "")
            demandes.loc[idx[0], "eta_minutes"] = estimate_eta_minutes(row.get("distance_km", ""))
            for col in ["stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]:
                if col in row.index:
                    demandes.loc[idx[0], col] = row.get(col, "")
        demandes.loc[idx[0], "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_csv(demandes, DEMANDES_FILE)


def afficher_app_depanneur():
    st.subheader("📱 App dépanneur")
    st.caption("Simulation de l'application mobile utilisée par le dépanneur : accepter, partir, arriver, terminer.")

    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)

    if demandes.empty:
        st.info("Aucune mission pour le moment.")
        return

    statuts_depanneur = [
        "Mission proposée au dépanneur",
        "Recherche dépanneur",
        "Accepté par dépanneur",
        "Dépanneur en route",
        "Dépanneur sur place",
        "A traiter manuellement",
    ]

    missions = demandes[demandes["statut"].isin(statuts_depanneur)].copy()

    if missions.empty:
        st.success("Aucune mission active côté dépanneur.")
        return

    missions = missions.sort_values("date_creation", ascending=False)
    mission_id = st.selectbox(
        "Mission",
        missions["id"].tolist(),
        format_func=lambda x: f"{x} — {missions[missions['id'] == x].iloc[0]['immatriculation']} — {missions[missions['id'] == x].iloc[0]['statut']}"
    )

    demande = missions[missions["id"] == mission_id].iloc[0]
    current_tentatives = tentatives[tentatives.demande_id == mission_id].sort_values("rang")
    active = current_tentatives[current_tentatives.statut == "En attente"]

    if not active.empty:
        mission_dep = active.iloc[0]
        depanneur_nom = mission_dep.get("depanneur_nom", demande.get("depanneur_nom", ""))
        depanneur_tel = mission_dep.get("depanneur_telephone", demande.get("depanneur_telephone", ""))
        score_ia = mission_dep.get("score_ia", demande.get("score_ia", ""))
        decision_ia = mission_dep.get("decision_ia", demande.get("decision_ia", ""))
        stock_ok = mission_dep.get("stock_disponible", demande.get("stock_disponible", False))
        stock_qte = mission_dep.get("stock_quantite", demande.get("stock_quantite", 0))
        stock_label = "✅ disponible" if to_bool(stock_ok) else "⚠️ non confirmé"
    else:
        depanneur_nom = demande.get("depanneur_nom", "")
        depanneur_tel = demande.get("depanneur_telephone", "")
        score_ia = demande.get("score_ia", "")
        decision_ia = demande.get("decision_ia", "")
        stock_ok = demande.get("stock_disponible", False)
        stock_qte = demande.get("stock_quantite", 0)
        stock_label = "✅ disponible" if to_bool(stock_ok) else "⚠️ non confirmé"

    eta = demande.get("eta_minutes", "")
    distance = demande.get("distance_km", "")
    maps_link = generate_google_maps_link(demande.get("latitude", ""), demande.get("longitude", ""))

    st.markdown(
        f"""
        <div class="mobile-card">
            <div class="mobile-card-title">🚨 Nouvelle mission</div>
            <div class="mobile-status">{demande.get('statut', '')}</div>
            <br>
            <b>Dépanneur proposé :</b> {depanneur_nom}<br>
            <b>Téléphone :</b> {depanneur_tel}<br>
            <b>Client :</b> {demande.get('client', '')}<br>
            <b>Chauffeur :</b> {demande.get('chauffeur', '')}<br>
            <b>Véhicule :</b> {demande.get('immatriculation', '')}<br>
            <b>Panne :</b> {demande.get('type_panne', '')}<br>
            <b>Dimension :</b> {demande.get('dimension', '')}<br>
            <b>Stock :</b> {stock_label} — Qté {stock_qte}<br>
            <b>Distance :</b> {distance} km<br>
            <b>ETA :</b> {eta} min<br>
            <b>Score IA :</b> {score_ia}<br>
            <b>Décision IA :</b> {decision_ia}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.link_button("🗺️ Ouvrir le lieu de panne", maps_link, use_container_width=True)

    if demande.get("statut", "") in ["Mission proposée au dépanneur", "Recherche dépanneur"]:
        c1, c2 = st.columns(2)
        if c1.button("✅ Accepter la mission", type="primary", use_container_width=True):
            accepter_tentative(mission_id)
            st.rerun()
        if c2.button("❌ Refuser / indisponible", use_container_width=True):
            depanneur_refuse_mission(mission_id)
            st.rerun()

    if demande.get("statut", "") == "Accepté par dépanneur":
        if st.button("🚚 Je pars / En route", type="primary", use_container_width=True):
            update_demande_status(mission_id, "Dépanneur en route")
            st.rerun()

    if demande.get("statut", "") == "Dépanneur en route":
        if st.button("📍 Je suis sur place", type="primary", use_container_width=True):
            update_demande_status(mission_id, "Dépanneur sur place")
            st.rerun()

    if demande.get("statut", "") == "Dépanneur sur place":
        if st.button("🏁 Intervention terminée", type="primary", use_container_width=True):
            update_demande_status(mission_id, "Clôturé")
            st.rerun()

    with st.expander("Voir la cascade complète"):
        st.dataframe(current_tentatives, use_container_width=True, hide_index=True)


# ============================================================
# UI COCKPIT OPÉRATEUR — HELPERS V1
# ============================================================

def ui_safe(value, default="—"):
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    value = str(value).strip()
    if value == "" or value.lower() in ["nan", "none", "null"]:
        return default
    return value


def ui_status_class(statut):
    statut = ui_safe(statut, "").lower()
    if "danger" in statut or "manuel" in statut:
        return "fr-badge-red"
    if "clôturé" in statut or "cloture" in statut or "accepté" in statut or "accepte" in statut:
        return "fr-badge-green"
    if "route" in statut or "place" in statut or "propos" in statut or "recherche" in statut:
        return "fr-badge-orange"
    return "fr-badge-blue"


def ui_stock_badge(value):
    return "fr-badge-green" if to_bool(value) else "fr-badge-orange"


def render_operator_hero():
    st.markdown("""
    <div class="fr-hero">
        <div class="fr-hero-title">🎯 Cockpit Opérateur FleetRescue</div>
        <div class="fr-hero-subtitle">
            Supervision temps réel des interventions • Dispatch IA • Stock simulé Winpro/Inovaxo • Cascade dépanneurs
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_operator_kpis(demandes, tentatives):
    if demandes.empty:
        total = actifs = danger = clotures = 0
        avg_eta = "—"
    else:
        total = len(demandes)
        actifs = len(demandes[~demandes["statut"].isin(["Clôturé", "Cloturé", "Annulé", "Annule"])] ) if "statut" in demandes.columns else total
        danger = len(demandes[demandes["urgence"].astype(str).str.contains("Danger", case=False, na=False)]) if "urgence" in demandes.columns else 0
        clotures = len(demandes[demandes["statut"].astype(str).str.contains("Clôturé|Cloturé", case=False, na=False)]) if "statut" in demandes.columns else 0
        if "eta_minutes" in demandes.columns:
            eta_numeric = pd.to_numeric(demandes["eta_minutes"], errors="coerce").dropna()
            avg_eta = f"{int(round(eta_numeric.mean()))} min" if len(eta_numeric) else "—"
        else:
            avg_eta = "—"

    if tentatives.empty or "statut" not in tentatives.columns:
        accept_rate = "—"
    else:
        sent = len(tentatives[tentatives["statut"].isin(["Accepté", "Expiré / pas de réponse", "En attente", "Annulé"])])
        accepted = len(tentatives[tentatives["statut"].astype(str).str.contains("Accepté|Accepte", case=False, na=False)])
        accept_rate = f"{round((accepted / sent) * 100)}%" if sent else "—"

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Interventions", total, "Total demandes"),
        (c2, "Actives", actifs, "À superviser"),
        (c3, "Danger", danger, "Voie rapide / risque"),
        (c4, "ETA moyen", avg_eta, "Sur demandes affectées"),
        (c5, "Acceptation", accept_rate, "Cascade dépanneurs"),
    ]
    for col, label, value, foot in cards:
        with col:
            st.markdown(f"""
            <div class="fr-kpi">
                <div class="fr-kpi-label">{label}</div>
                <div class="fr-kpi-value">{value}</div>
                <div class="fr-kpi-foot">{foot}</div>
            </div>
            """, unsafe_allow_html=True)


def render_timeline(statut):
    steps = [
        "Créée",
        "Recherche",
        "Proposée",
        "Acceptée",
        "En route",
        "Sur place",
        "Clôturée",
    ]
    statut_lower = ui_safe(statut, "").lower()
    active_index = 0
    if "recherche" in statut_lower:
        active_index = 1
    elif "propos" in statut_lower or "mission" in statut_lower:
        active_index = 2
    elif "accept" in statut_lower:
        active_index = 3
    elif "route" in statut_lower:
        active_index = 4
    elif "place" in statut_lower:
        active_index = 5
    elif "clôt" in statut_lower or "clot" in statut_lower:
        active_index = 6
    elif "manuel" in statut_lower:
        active_index = 2

    html = '<div class="fr-timeline">'
    for i, step in enumerate(steps):
        klass = "fr-step-done" if i < active_index else "fr-step-active" if i == active_index else ""
        html += f'<span class="fr-step {klass}">{step}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_intervention_card(demande):
    statut = ui_safe(demande.get("statut", ""))
    badge_class = ui_status_class(statut)
    urgence = ui_safe(demande.get("urgence", ""))
    urgency_class = "fr-badge-red" if "Danger" in urgence else "fr-badge-orange" if "Urgent" in urgence else "fr-badge-blue"

    st.markdown(f"""
    <div class="fr-card-dark">
        <div style="display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:12px;">
            <div>
                <div style="font-size:13px; color:#94a3b8; font-weight:800; text-transform:uppercase; letter-spacing:.08em;">Intervention sélectionnée</div>
                <div style="font-size:30px; font-weight:950; letter-spacing:-.04em; margin-top:4px;">{ui_safe(demande.get('id', ''))}</div>
                <div class="fr-white-muted" style="margin-top:3px;">{ui_safe(demande.get('client', ''))} • {ui_safe(demande.get('immatriculation', ''))}</div>
            </div>
            <div style="text-align:right;">
                <span class="fr-badge {badge_class}">{statut}</span><br><br>
                <span class="fr-badge {urgency_class}">{urgence}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_timeline(statut)

    st.markdown(f"""
    <div class="fr-card">
        <div class="fr-info-row"><div class="fr-info-label">Chauffeur</div><div class="fr-info-value">{ui_safe(demande.get('chauffeur', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Téléphone</div><div class="fr-info-value">{ui_safe(demande.get('telephone_chauffeur', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Panne</div><div class="fr-info-value">{ui_safe(demande.get('type_panne', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Dimension</div><div class="fr-info-value">{ui_safe(demande.get('dimension', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Lieu</div><div class="fr-info-value">{ui_safe(demande.get('lieu', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Création</div><div class="fr-info-value">{ui_safe(demande.get('date_creation', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Commentaire</div><div class="fr-info-value">{ui_safe(demande.get('commentaire', ''))}</div></div>
    </div>
    """, unsafe_allow_html=True)


def render_ai_stock_card(demande):
    stock_ok = demande.get("stock_disponible", False)
    stock_class = ui_stock_badge(stock_ok)
    stock_label = "Stock confirmé" if to_bool(stock_ok) else "Stock non confirmé"
    eta = ui_safe(demande.get("eta_minutes", ""))
    eta_label = f"{eta} min" if eta != "—" and "min" not in eta else eta

    st.markdown(f"""
    <div class="fr-card">
        <div class="fr-section-title">🧠 Décision IA</div>
        <span class="fr-badge {stock_class}">{stock_label}</span>
        <div class="fr-mini-grid">
            <div class="fr-mini"><div class="fr-mini-label">Score IA</div><div class="fr-mini-value">{ui_safe(demande.get('score_ia', ''))}</div></div>
            <div class="fr-mini"><div class="fr-mini-label">Distance</div><div class="fr-mini-value">{ui_safe(demande.get('distance_km', ''))} km</div></div>
            <div class="fr-mini"><div class="fr-mini-label">ETA</div><div class="fr-mini-value">{eta_label}</div></div>
        </div>
        <div class="fr-info-row"><div class="fr-info-label">Dépanneur</div><div class="fr-info-value">{ui_safe(demande.get('depanneur_nom', demande.get('depanneur_assigne', '')))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Téléphone</div><div class="fr-info-value">{ui_safe(demande.get('depanneur_telephone', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Stock</div><div class="fr-info-value">Qté {ui_safe(demande.get('stock_quantite', '0'))} — {ui_safe(demande.get('stock_marque', ''))} {ui_safe(demande.get('stock_profil', ''))}</div></div>
        <div class="fr-info-row"><div class="fr-info-label">Raison IA</div><div class="fr-info-value">{ui_safe(demande.get('decision_ia', ''))}</div></div>
    </div>
    """, unsafe_allow_html=True)

    tracking_url = ui_safe(demande.get("tracking_url", ""), "")
    if tracking_url:
        st.link_button("🗺️ Ouvrir itinéraire Google Maps", tracking_url, use_container_width=True)


def render_responder_cards(current):
    st.markdown('<div class="fr-section-title">🛠 Cascade dépanneurs recommandés</div>', unsafe_allow_html=True)
    if current.empty:
        st.markdown('<div class="fr-empty">Aucune cascade créée pour cette demande.</div>', unsafe_allow_html=True)
        return

    for _, row in current.sort_values("rang").head(5).iterrows():
        statut = ui_safe(row.get("statut", ""))
        badge = ui_status_class(statut)
        stock_class = ui_stock_badge(row.get("stock_disponible", False))
        stock_label = "Stock OK" if to_bool(row.get("stock_disponible", False)) else "Stock ?"
        score = ui_safe(row.get("score_ia", ""))
        st.markdown(f"""
        <div class="fr-responder-card">
            <div class="fr-responder-top">
                <div>
                    <div class="fr-responder-name">#{ui_safe(row.get('rang', ''))} — {ui_safe(row.get('depanneur_nom', ''))}</div>
                    <div class="fr-muted">{ui_safe(row.get('distance_km', ''))} km • {ui_safe(row.get('canal', ''))}</div>
                </div>
                <div class="fr-score">{score}</div>
            </div>
            <span class="fr-badge {badge}">{statut}</span>
            <span class="fr-badge {stock_class}">{stock_label} · Qté {ui_safe(row.get('stock_quantite', '0'))}</span>
            <div class="fr-muted" style="margin-top:8px; font-size:13px;">
                {ui_safe(row.get('stock_marque', ''))} {ui_safe(row.get('stock_profil', ''))}<br>
                {ui_safe(row.get('decision_ia', ''))}
            </div>
        </div>
        """, unsafe_allow_html=True)


def afficher_carte_superviseur(demande, current):
    try:
        lat = float(demande.get("latitude", 49.25))
        lon = float(demande.get("longitude", 2.65))
    except Exception:
        st.warning("Coordonnées GPS invalides pour cette demande.")
        return

    m = folium.Map(location=[lat, lon], zoom_start=8, tiles="CartoDB positron")

    folium.Marker(
        location=[lat, lon],
        tooltip="Camion en panne",
        popup=f"""
        <b>🚛 Camion en panne</b><br>
        ID : {ui_safe(demande.get('id', ''))}<br>
        Client : {ui_safe(demande.get('client', ''))}<br>
        Véhicule : {ui_safe(demande.get('immatriculation', ''))}<br>
        Panne : {ui_safe(demande.get('type_panne', ''))}<br>
        Dimension : {ui_safe(demande.get('dimension', ''))}
        """,
        icon=folium.Icon(color="red", icon="truck", prefix="fa")
    ).add_to(m)

    folium.CircleMarker(
        location=[lat, lon],
        radius=16,
        color="#ef4444",
        fill=True,
        fill_color="#ef4444",
        fill_opacity=0.25,
    ).add_to(m)

    if not current.empty:
        for _, d in current.iterrows():
            dep_lat = ui_safe(d.get("depanneur_latitude", ""), "")
            dep_lon = ui_safe(d.get("depanneur_longitude", ""), "")
            if not dep_lat or not dep_lon:
                continue
            try:
                dep_lat = float(dep_lat)
                dep_lon = float(dep_lon)
            except Exception:
                continue

            statut = ui_safe(d.get("statut", ""))
            color = "green" if "Accept" in statut or "Accepté" in statut else "orange" if "attente" in statut.lower() else "blue"
            folium.Marker(
                location=[dep_lat, dep_lon],
                tooltip=f"{ui_safe(d.get('depanneur_nom', ''))} — {ui_safe(d.get('distance_km', ''))} km",
                popup=f"""
                <b>🛠️ {ui_safe(d.get('depanneur_nom', ''))}</b><br>
                Rang : {ui_safe(d.get('rang', ''))}<br>
                Statut : {statut}<br>
                Distance : {ui_safe(d.get('distance_km', ''))} km<br>
                Stock : {'Oui' if to_bool(d.get('stock_disponible', False)) else 'Non confirmé'}<br>
                Score IA : {ui_safe(d.get('score_ia', ''))}
                """,
                icon=folium.Icon(color=color, icon="wrench", prefix="fa")
            ).add_to(m)
            folium.PolyLine([[lat, lon], [dep_lat, dep_lon]], color="#2563eb", weight=2, opacity=0.45).add_to(m)

    components.html(m._repr_html_(), height=520)


# ============================================================
# LANCEMENT APP
# ============================================================

init_data()
ensure_data_schema()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Dépannages actifs</div>
        <div class="kpi-value">14</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Temps moyen</div>
        <div class="kpi-value">18 min</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Dépanneurs connectés</div>
        <div class="kpi-value">128</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">SLA respecté</div>
        <div class="kpi-value">98%</div>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚛 Chauffeur",
    "🛠️ Dépanneur",
    "🎯 Cockpit opérateur",
    "⚙️ Administration",
    "📈 KPI"
])


# ============================================================
# ONGLET 1 — DEMANDE CHAUFFEUR
# ============================================================

with tab1:
    st.subheader("Créer une demande de dépannage")

    demandes_existantes = load_csv(DEMANDES_FILE)
    statuts_ouverts = [
        "Recherche dépanneur",
        "Mission proposée au dépanneur",
        "Accepté par dépanneur",
        "Dépanneur en route",
        "Dépanneur sur place",
        "A traiter manuellement"
    ]

    # Important : on n'affiche PAS automatiquement une ancienne demande
    # stockée dans le CSV. Sinon, au lancement de l'app, un ancien dépannage
    # peut apparaître comme déjà accepté alors que le chauffeur n'a encore
    # rien demandé dans cette session.
    demande_session_id = st.session_state.get("chauffeur_demande_id", "")

    if demande_session_id and not demandes_existantes.empty:
        demande_active = demandes_existantes[
            (demandes_existantes["id"] == demande_session_id)
            & (demandes_existantes["statut"].isin(statuts_ouverts))
        ]

        if not demande_active.empty:
            afficher_suivi_chauffeur(demande_active.iloc[0])

            if st.button("🔄 Rafraîchir le suivi", use_container_width=True):
                st.rerun()

            if st.button("➕ Créer une nouvelle demande", use_container_width=True):
                st.session_state["chauffeur_demande_id"] = ""
                st.rerun()

            st.divider()

    ok_twilio, missing_key = twilio_is_configured()

    if not ok_twilio:
        st.warning(
            f"Twilio n'est pas encore configuré. Secret manquant : {missing_key}. "
            "La demande sera créée, mais le SMS et l'appel ne partiront pas."
        )

    col1, col2 = st.columns(2)

    with col1:
        client = st.text_input("Client / société", "Transport Demo")
        chauffeur = st.text_input("Nom chauffeur", "Jean Martin")
        telephone = st.text_input("Téléphone chauffeur", "+33612345678")
        immatriculation = st.text_input("Immatriculation", "AB-123-CD")

        type_panne = st.selectbox(
            "Type de panne",
            ["Crevaison", "Éclatement", "Valve / pression", "Permutation", "Autre"]
        )

        dimension = st.selectbox(
            "Dimension pneu",
            ["315/80 R22.5", "315/70 R22.5", "385/65 R22.5", "295/80 R22.5", "Autre / inconnue"]
        )

    with col2:
        st.info("Coordonnées GPS préremplies pour la démo. Dans la vraie app, elles viendraient du téléphone.")

        lieu = st.radio("Lieu", ["Route", "Autoroute"], horizontal=True)

        latitude = st.number_input("Latitude panne", value=49.2500, format="%.6f")
        longitude = st.number_input("Longitude panne", value=2.6500, format="%.6f")

        mode_paiement = st.radio("Paiement", ["Client en compte", "CB / Apple Pay"], horizontal=True)

        urgence = st.selectbox(
            "Niveau d'urgence",
            [
                "Standard",
                "Urgent",
                "Danger immédiat / voie rapide"
            ]
        )

        commentaire = st.text_area(
            "Commentaire",
            "Véhicule immobilisé. Demande urgente."
        )

        photo_flanc = st.file_uploader(
            "Photo flanc pneu",
            type=["jpg", "jpeg", "png"],
            key="photo_flanc_pneu"
        )

        photo_avarie = st.file_uploader(
            "Photo incident",
            type=["jpg", "jpeg", "png"],
            key="photo_incident"
        )

        if photo_flanc and photo_avarie:
            st.markdown("### 🛞 Analyse IA pneumatique")

            c1, c2 = st.columns(2)

            with c1:
                st.image(
                    photo_flanc,
                    caption="Photo flanc pneu",
                    use_column_width=True
                )

            with c2:
                st.image(
                    photo_avarie,
                    caption="Photo incident",
                    use_column_width=True
                )

            if st.button("🔍 Analyser les photos avec IA"):
                with st.spinner("Analyse IA en cours..."):
                    resultat = analyser_pneu(photo_flanc, photo_avarie)

                flanc = resultat.get("photo_flanc", {})
                avarie = (
                    resultat.get("photo_avarie", {})
                    or resultat.get("photo_incident", {})
                    or resultat.get("avarie", {})
                )

                st.success("Analyse terminée")
                st.subheader("Synthèse IA")

                st.write(f"**Marque :** {flanc.get('marque', 'non visible')}")
                st.write(f"**Dimension :** {flanc.get('dimension', 'non visible')}")
                st.write(f"**Profil :** {flanc.get('profil', 'non visible')}")
                st.write(f"**DOT :** {flanc.get('DOT', flanc.get('dot', 'non visible'))}")

                st.write(f"**Avarie :** {avarie.get('description', avarie.get('type', 'non visible'))}")
                st.write(f"**Localisation :** {avarie.get('localisation', avarie.get('zone', 'non visible'))}")
                st.write(f"**Gravité :** {avarie.get('gravité', avarie.get('gravite', 'non visible'))}")
                st.write(f"**Réparation possible :** {avarie.get('réparabilité', avarie.get('reparabilite', 'non déterminé'))}")

    st.divider()

    if st.button(
        "🚨 DEMANDER UN DÉPANNAGE",
        type="primary",
        use_container_width=True
    ):
        depanneurs = load_csv(DEPANNEURS_FILE)
        demandes = load_csv(DEMANDES_FILE)

        demande_id = "REQ-" + str(uuid.uuid4())[:8].upper()

        demande = {
            "id": demande_id,
            "date_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client": client,
            "chauffeur": chauffeur,
            "telephone_chauffeur": telephone,
            "immatriculation": immatriculation,
            "latitude": latitude,
            "longitude": longitude,
            "type_panne": type_panne,
            "lieu": lieu,
            "dimension": dimension,
            "urgence": urgence,
            "statut": "Recherche dépanneur",
            "depanneur_assigne": "",
            "distance_km": "",
            "mode_paiement": mode_paiement,
            "commentaire": commentaire,
            "photo_1": photo_flanc.name if photo_flanc else "",
            "photo_2": photo_avarie.name if photo_avarie else "",
            "date_cloture": "",
            "depanneur_nom": "",
            "depanneur_telephone": "",
            "depanneur_latitude": "",
            "depanneur_longitude": "",
            "eta_minutes": "",
            "tracking_url": "",
            "date_prise_en_charge": "",
            "stock_disponible": False,
            "stock_quantite": 0,
            "stock_marque": "",
            "stock_profil": "",
            "score_ia": 0,
            "decision_ia": "",
            "date_mise_a_jour_statut": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        candidats = trouver_depanneurs(demande, depanneurs)

        if candidats.empty:
            demande["statut"] = "A traiter manuellement"
            st.error("Aucun dépanneur éligible trouvé. Bascule en traitement manuel.")
        else:
            best_depanneur = candidats.iloc[0].to_dict()
            demande["statut"] = "Mission proposée au dépanneur"
            demande["depanneur_nom"] = best_depanneur.get("nom", "")
            demande["depanneur_telephone"] = best_depanneur.get("telephone", "")
            demande["depanneur_latitude"] = best_depanneur.get("latitude", "")
            demande["depanneur_longitude"] = best_depanneur.get("longitude", "")
            demande["distance_km"] = best_depanneur.get("distance_km", "")
            demande["eta_minutes"] = estimate_eta_minutes(best_depanneur.get("distance_km", ""))
            demande["tracking_url"] = generate_google_maps_directions_link(
                best_depanneur.get("latitude", ""),
                best_depanneur.get("longitude", ""),
                latitude,
                longitude
            )
            demande["stock_disponible"] = best_depanneur.get("stock_disponible", False)
            demande["stock_quantite"] = best_depanneur.get("stock_quantite", 0)
            demande["stock_marque"] = best_depanneur.get("stock_marque", "")
            demande["stock_profil"] = best_depanneur.get("stock_profil", "")
            demande["score_ia"] = best_depanneur.get("score_ia", 0)
            demande["decision_ia"] = best_depanneur.get("decision_ia", "")

            afficher_carte_depanneurs(
                latitude=latitude,
                longitude=longitude,
                candidats=candidats,
                client=client,
                chauffeur=chauffeur,
                immatriculation=immatriculation,
                type_panne=type_panne,
                dimension=dimension,
                urgence=urgence
            )

            creer_tentatives(demande_id, candidats)

            st.success(f"Demande créée : {demande_id}. Dispatch IA lancé vers le meilleur dépanneur.")

            st.dataframe(
                candidats[["nom", "reseau", "ville", "distance_km", "telephone", "stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]],
                use_container_width=True,
                hide_index=True
            )

        save_csv(
            pd.concat([demandes, pd.DataFrame([demande])], ignore_index=True),
            DEMANDES_FILE
        )

        # La demande créée devient la seule demande visible côté chauffeur
        # dans cette session. Cela évite d'afficher une ancienne demande
        # au prochain rafraîchissement de la page.
        st.session_state["chauffeur_demande_id"] = demande_id

        ok_twilio, missing_key = twilio_is_configured()

        if ok_twilio:
            try:
                st.write("FROM utilisé :", st.secrets["TWILIO_FROM_NUMBER"])
                st.write("TO démo :", st.secrets["DEMO_PHONE_NUMBER"])

                best_depanneur = None if candidats.empty else candidats.iloc[0].to_dict()

                sms_sid, sms_target = send_assistance_sms(
                    demande_id=demande_id,
                    client=client,
                    chauffeur=chauffeur,
                    telephone=telephone,
                    immatriculation=immatriculation,
                    latitude=latitude,
                    longitude=longitude,
                    type_panne=type_panne,
                    lieu=lieu,
                    dimension=dimension,
                    urgence=urgence,
                    commentaire=commentaire,
                    depanneur=best_depanneur
                )

                driver_sms_sid, driver_sms_target = send_driver_confirmation_sms(
                    demande_id=demande_id,
                    telephone=telephone,
                    client=client,
                    immatriculation=immatriculation,
                    type_panne=type_panne
                )

                call_sid = make_assistance_call(
                    demande_id=demande_id,
                    client=client,
                    chauffeur=chauffeur,
                    immatriculation=immatriculation,
                    type_panne=type_panne,
                    lieu=lieu,
                    urgence=urgence
                )

                st.success(f"SMS dépanneur envoyé vers {sms_target}. SID : {sms_sid}")
                st.success(f"SMS chauffeur envoyé vers {driver_sms_target}. SID : {driver_sms_sid}")
                st.success(f"Appel Twilio déclenché. SID : {call_sid}")

            except Exception as e:
                st.error(f"Erreur Twilio : {e}")
                st.error(f"Type : {type(e)}")

                if hasattr(e, "status"):
                    st.error(f"HTTP status : {e.status}")

                if hasattr(e, "code"):
                    st.error(f"Code Twilio : {e.code}")

                if hasattr(e, "msg"):
                    st.error(f"Message Twilio : {e.msg}")

                st.write("FROM utilisé :", st.secrets["TWILIO_FROM_NUMBER"])
                st.write("TO démo :", st.secrets["DEMO_PHONE_NUMBER"])

        else:
            st.warning(f"Demande créée, mais SMS/appel non envoyés. Secret manquant : {missing_key}")


# ============================================================
# ONGLET 2 — APP DÉPANNEUR
# ============================================================

with tab2:
    afficher_app_depanneur()



# ============================================================
# ONGLET 3 — COCKPIT OPÉRATEUR
# ============================================================

with tab3:
    render_operator_hero()

    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)

    render_operator_kpis(demandes, tentatives)

    if demandes.empty:
        st.markdown("""
        <div class="fr-empty">
            Aucune demande pour le moment. Crée une demande depuis l’onglet Chauffeur pour alimenter le cockpit.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="fr-section-title">📍 Intervention à superviser</div>', unsafe_allow_html=True)

        demandes_view = demandes.sort_values("date_creation", ascending=False).copy()

        def format_demande_option(x):
            row = demandes_view[demandes_view["id"] == x].iloc[0]
            return f"{x} — {ui_safe(row.get('immatriculation', ''))} — {ui_safe(row.get('statut', ''))}"

        selected_id = st.selectbox(
            "Sélectionner une demande",
            demandes_view["id"].tolist(),
            format_func=format_demande_option,
            label_visibility="collapsed"
        )

        demande = demandes_view[demandes_view["id"] == selected_id].iloc[0]
        current = tentatives[tentatives.demande_id == selected_id].sort_values("rang") if not tentatives.empty else pd.DataFrame()

        left, right = st.columns([1.45, 1])

        with left:
            st.markdown('<div class="fr-section-title">🗺️ Carte opérationnelle</div>', unsafe_allow_html=True)
            afficher_carte_superviseur(demande, current)

            st.markdown('<div class="fr-section-title">🧾 Données brutes</div>', unsafe_allow_html=True)
            with st.expander("Afficher / masquer les tables techniques"):
                st.markdown("Demandes")
                st.dataframe(
                    demandes_view,
                    use_container_width=True,
                    hide_index=True
                )
                st.markdown("Cascade")
                st.dataframe(
                    current,
                    use_container_width=True,
                    hide_index=True
                )

        with right:
            render_intervention_card(demande)
            render_ai_stock_card(demande)

            st.markdown('<div class="fr-section-title">⚡ Actions opérateur</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("✅ Accepter", type="primary", use_container_width=True):
                accepter_tentative(selected_id)
                st.rerun()

            if c2.button("⏱️ Suivant", use_container_width=True):
                passer_au_suivant(selected_id)
                st.rerun()

            c3, c4 = st.columns(2)
            if c3.button("🚚 En route", use_container_width=True):
                update_demande_status(selected_id, "Dépanneur en route")
                st.rerun()

            if c4.button("🏁 Clôturer", use_container_width=True):
                cloturer(selected_id)
                st.rerun()

            render_responder_cards(current)


# ============================================================
# ONGLET 4 — RÉFÉRENTIEL DÉPANNEURS
# ============================================================

with tab4:
    st.subheader("Référentiel dépanneurs")

    depanneurs = load_csv(DEPANNEURS_FILE)

    edited = st.data_editor(
        depanneurs,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("💾 Sauvegarder le référentiel"):
        save_csv(edited, DEPANNEURS_FILE)
        st.success("Référentiel sauvegardé.")

    st.divider()
    st.subheader("Stock simulé PDV / future API Winpro-Innovaxo")
    stocks = load_csv(STOCKS_FILE)
    edited_stocks = st.data_editor(
        stocks,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("💾 Sauvegarder le stock simulé"):
        save_csv(edited_stocks, STOCKS_FILE)
        st.success("Stock simulé sauvegardé.")


# ============================================================
# ONGLET 5 — REPORTING
# ============================================================

with tab5:
    st.subheader("Reporting démo")

    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)

    if demandes.empty:
        st.info("Pas encore de données.")
    else:
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Demandes", len(demandes))
        c2.metric("Acceptées", len(demandes[demandes.statut == "Accepté par dépanneur"]))
        c3.metric("Clôturées", len(demandes[demandes.statut == "Clôturé"]))
        c4.metric("Traitement manuel", len(demandes[demandes.statut == "A traiter manuellement"]))

        st.markdown("### Statuts des demandes")
        st.bar_chart(demandes["statut"].value_counts())

        if not tentatives.empty:
            st.markdown("### Statuts des sollicitations")
            st.bar_chart(tentatives["statut"].value_counts())

        st.download_button(
            "Télécharger demandes CSV",
            demandes.to_csv(index=False).encode("utf-8"),
            file_name="demandes_depannage.csv",
            mime="text/csv",
        )
