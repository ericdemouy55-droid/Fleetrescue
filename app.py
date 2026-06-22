try:
    from twilio.rest import Client
except Exception:
    Client = None
import math
import uuid
from datetime import datetime
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from ai_tire_analysis import analyser_pneu
except Exception:
    def analyser_pneu(photo_flanc, photo_avarie):
        return {
            "photo_flanc": {
                "marque": "module IA non chargé",
                "dimension": "non déterminé",
                "profil": "non déterminé",
                "DOT": "non visible",
            },
            "photo_avarie": {
                "description": "analyse indisponible",
                "localisation": "non déterminé",
                "gravité": "non déterminé",
                "réparabilité": "non déterminé",
            },
        }


# ============================================================
# CONFIG PAGE
# ============================================================

st.set_page_config(
    page_title="Orane Roadside Assistance",
    page_icon="🚛",
    layout="wide",
)


# ============================================================
# STYLE CSS
# ============================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 18% 12%, rgba(37,99,235,0.25), transparent 30%),
        radial-gradient(circle at 85% 5%, rgba(6,182,212,0.16), transparent 32%),
        linear-gradient(135deg, #050b16 0%, #07111f 44%, #0b1220 100%) !important;
    color: #e5eefb;
}
.block-container { padding-top: 1.1rem !important; max-width: 1420px !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
h1, h2, h3, h4, h5, h6, .stMarkdown, label, p { color: #e5eefb !important; }
.stCaptionContainer, .stCaptionContainer p { color: #94a3b8 !important; }

.main-header {
    background:
        linear-gradient(135deg, rgba(15,23,42,0.92), rgba(7,17,31,0.82)),
        radial-gradient(circle at 20% 20%, rgba(37,99,235,0.36), transparent 42%) !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    box-shadow: 0 24px 80px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(18px);
    padding: 25px;
    border-radius: 24px;
    margin-bottom: 22px;
}
.main-title { color: white; font-size: 46px; font-weight: 950; letter-spacing: -0.055em; margin-bottom: 6px; }
.main-subtitle { color: #9fb0c8; font-size: 17px; }

.kpi-card, .fr-card, .mobile-card, .fr-responder-card {
    background: linear-gradient(180deg, rgba(15,23,42,0.88), rgba(15,23,42,0.60)) !important;
    color: #e5eefb !important;
    border: 1px solid rgba(148,163,184,0.16) !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.30) !important;
    backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 18px;
    margin-bottom: 14px;
}
.kpi-card { min-height: 115px; position: relative; overflow: hidden; }
.kpi-card:before {
    content: ""; position: absolute; inset: -60px -40px auto auto; width: 140px; height: 140px;
    background: radial-gradient(circle, rgba(56,189,248,.22), transparent 68%);
}
.kpi-title { color: #8aa0bd !important; text-transform: uppercase; letter-spacing: .08em; font-size: 12px; font-weight: 800; }
.kpi-value { color: #f8fbff !important; font-size: 34px; font-weight: 950; letter-spacing: -.05em; margin-top: 8px; }

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(15,23,42,0.62);
    padding: 9px;
    border-radius: 22px;
    border: 1px solid rgba(148,163,184,0.14);
}
.stTabs [data-baseweb="tab"] {
    height: 48px;
    border-radius: 16px !important;
    color: #9fb0c8 !important;
    padding: 0 16px !important;
    font-weight: 850;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb, #06b6d4) !important;
    color: white !important;
    box-shadow: 0 12px 30px rgba(37,99,235,0.28);
}

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: rgba(15,23,42,0.78) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(148,163,184,0.2) !important;
    border-radius: 16px !important;
}
.stSelectbox div[data-baseweb="select"] > div, .stRadio > div {
    background: rgba(15,23,42,0.58) !important;
    border-radius: 16px !important;
}
.stFileUploader section {
    background: rgba(15,23,42,0.58) !important;
    border: 1px dashed rgba(56,189,248,0.34) !important;
    border-radius: 20px !important;
}
.stAlert {
    background: rgba(15,23,42,0.72) !important;
    border: 1px solid rgba(148,163,184,0.18) !important;
    color: #e5eefb !important;
    border-radius: 16px !important;
}
.stButton>button, .stDownloadButton>button, .stLinkButton>a {
    background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 16px !important;
    font-weight: 900 !important;
    min-height: 48px;
    box-shadow: 0 14px 34px rgba(37,99,235,0.28) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover, .stLinkButton>a:hover {
    transform: translateY(-1px);
    filter: brightness(1.08);
}

.mobile-card-title { font-size: 24px; font-weight: 950; color: #f8fafc; margin-bottom: 8px; }
.mobile-status { display: inline-flex; padding: 7px 11px; border-radius: 999px; background: rgba(245,158,11,.14); color: #fcd34d; border: 1px solid rgba(245,158,11,.28); font-size: 14px; font-weight: 900; }
.fr-section-title { font-size: 20px; font-weight: 900; color: #f8fafc; margin: 8px 0 12px 0; }
.fr-muted { color: #94a3b8; }
.fr-empty { background: rgba(251,146,60,.12); border: 1px dashed rgba(251,146,60,.45); color: #fed7aa; border-radius: 20px; padding: 22px; font-weight: 800; }
.fr-badge { display:inline-flex; border-radius:999px; padding:6px 10px; font-weight:900; font-size:12px; margin: 2px; }
.fr-badge-blue { background:#dbeafe; color:#1d4ed8; }
.fr-badge-green { background:#dcfce7; color:#15803d; }
.fr-badge-orange { background:#ffedd5; color:#c2410c; }
.fr-badge-red { background:#fee2e2; color:#b91c1c; }
.fr-info-row { display:flex; justify-content:space-between; gap:16px; border-bottom:1px solid rgba(148,163,184,.12); padding:9px 0; font-size:14px; }
.fr-info-row:last-child { border-bottom:0; }
.fr-info-label { color:#94a3b8; font-weight:750; }
.fr-info-value { color:#f8fafc; font-weight:900; text-align:right; }
.fr-responder-card { padding: 14px; border-radius: 18px; }
.fr-responder-name { font-size:16px; font-weight:950; color:#f8fafc; }
.fr-score { background: linear-gradient(135deg, #2563eb, #06b6d4); color: white; border-radius:14px; padding:7px 10px; font-weight:950; min-width:58px; text-align:center; }
.fr-responder-top { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:8px; }
.fr-timeline { display:flex; gap:7px; flex-wrap:wrap; margin:10px 0 14px; }
.fr-step { border-radius:999px; padding:7px 10px; font-size:12px; font-weight:900; background:rgba(148,163,184,.12); color:#94a3b8; border:1px solid rgba(148,163,184,.16); }
.fr-step-active { background:#dbeafe; color:#1d4ed8; }
.fr-step-done { background:#dcfce7; color:#15803d; }

@media (max-width: 768px) {
    .main-title { font-size: 30px; }
    .main-subtitle { font-size: 14px; }
    .kpi-value { font-size: 25px; }
    .stButton>button { width:100%; min-height:56px; font-size:18px; }
    div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; }
    .fr-info-row { display:block; }
    .fr-info-value { text-align:left; margin-top:3px; }
}
</style>
""",
    unsafe_allow_html=True,
)


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

DEMANDES_COLUMNS = [
    "id", "date_creation", "client", "chauffeur", "telephone_chauffeur",
    "immatriculation", "latitude", "longitude", "type_panne", "lieu", "dimension",
    "urgence", "statut", "depanneur_assigne", "distance_km", "mode_paiement",
    "commentaire", "photo_1", "photo_2", "date_cloture", "depanneur_nom",
    "depanneur_telephone", "depanneur_latitude", "depanneur_longitude", "eta_minutes",
    "tracking_url", "date_prise_en_charge", "stock_disponible", "stock_quantite",
    "stock_marque", "stock_profil", "score_ia", "decision_ia", "date_mise_a_jour_statut",
]

TENTATIVES_COLUMNS = [
    "id", "demande_id", "rang", "depanneur_id", "depanneur_nom", "distance_km",
    "canal", "statut", "date_tentative", "depanneur_telephone", "depanneur_latitude",
    "depanneur_longitude", "stock_disponible", "stock_quantite", "stock_marque",
    "stock_profil", "score_ia", "decision_ia",
]


# ============================================================
# OUTILS CSV ET DONNÉES
# ============================================================

def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        if path == DEMANDES_FILE:
            return pd.DataFrame(columns=DEMANDES_COLUMNS)
        if path == TENTATIVES_FILE:
            return pd.DataFrame(columns=TENTATIVES_COLUMNS)
        return pd.DataFrame()


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
            "id", "nom", "reseau", "ville", "latitude", "longitude", "telephone",
            "email", "zone_km", "route", "autoroute", "pl", "disponible", "stock", "score",
        ]).to_csv(DEPANNEURS_FILE, index=False)

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
        ], columns=["depanneur_id", "dimension", "marque", "profil", "quantite", "last_update"]).to_csv(STOCKS_FILE, index=False)

    if not DEMANDES_FILE.exists():
        pd.DataFrame(columns=DEMANDES_COLUMNS).to_csv(DEMANDES_FILE, index=False)

    if not TENTATIVES_FILE.exists():
        pd.DataFrame(columns=TENTATIVES_COLUMNS).to_csv(TENTATIVES_FILE, index=False)


def ensure_data_schema():
    ensure_columns(DEMANDES_FILE, {column: "" for column in DEMANDES_COLUMNS})
    ensure_columns(TENTATIVES_FILE, {column: "" for column in TENTATIVES_COLUMNS})
    ensure_columns(STOCKS_FILE, {"last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


# ============================================================
# OUTILS MÉTIER
# ============================================================

def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in ["true", "1", "yes", "oui", "vrai"]


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


def normalize_dimension(value):
    return str(value).upper().replace(" ", "")


def distance_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def generate_google_maps_link(latitude, longitude):
    return f"https://www.google.com/maps?q={latitude},{longitude}"


def generate_google_maps_directions_link(origin_lat, origin_lon, dest_lat, dest_lon):
    return f"https://www.google.com/maps/dir/{origin_lat},{origin_lon}/{dest_lat},{dest_lon}"


def estimate_eta_minutes(distance_km_value, average_speed_kmh=60):
    try:
        distance = float(distance_km_value)
        if distance <= 0:
            return 5
        return max(5, int(round((distance / average_speed_kmh) * 60)))
    except Exception:
        return ""


def get_stock_for_depanneur(depanneur_id, dimension):
    stocks = load_csv(STOCKS_FILE)
    if stocks.empty or not dimension or dimension == "Autre / inconnue":
        return {"available": False, "quantity": 0, "brand": "", "profile": "", "last_update": ""}

    dim_norm = normalize_dimension(dimension)
    stocks = stocks.copy()
    stocks["dimension_norm"] = stocks["dimension"].apply(normalize_dimension)
    rows = stocks[(stocks["depanneur_id"] == depanneur_id) & (stocks["dimension_norm"] == dim_norm)]

    if rows.empty:
        return {"available": False, "quantity": 0, "brand": "", "profile": "", "last_update": ""}

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
    score = 100.0
    score -= float(distance_value) * 1.2

    if stock_info["available"]:
        score += 45
        score += min(int(stock_info["quantity"]), 6) * 2
    else:
        score -= 70

    urgence = demande.get("urgence", "")
    if urgence == "Danger immédiat / voie rapide":
        score += 20 if to_bool(depanneur.get("autoroute", False)) else -80
    elif urgence == "Urgent":
        score += 10

    try:
        score += float(depanneur.get("score", 0)) * 8
    except Exception:
        pass

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

        dist = distance_km(demande["latitude"], demande["longitude"], d["latitude"], d["longitude"])
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
            row["decision_ia"] = "Recommandé : stock disponible" if stock_info["available"] else "Dégradé : stock non confirmé"
            rows.append(row)

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(sorted(rows, key=lambda x: (-float(x["score_ia"]), x["distance_km"])))


# ============================================================
# TWILIO
# ============================================================

def twilio_is_configured():
    if Client is None:
        return False, "package twilio non installé dans requirements.txt"

    required_keys = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "DEMO_PHONE_NUMBER"]
    try:
        for key in required_keys:
            if key not in st.secrets:
                return False, key
    except Exception:
        return False, "secrets Streamlit non configurés"

    return True, ""


def get_twilio_client():
    if Client is None:
        raise RuntimeError("Le package twilio n'est pas installé. Ajoute twilio dans requirements.txt ou désactive l'envoi SMS.")
    return Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])


def get_sms_target_number(depanneur=None):
    use_demo = st.secrets.get("USE_DEMO_PHONE_NUMBER", True)
    if isinstance(use_demo, str):
        use_demo = use_demo.strip().lower() in ["true", "1", "yes", "oui"]
    if use_demo or depanneur is None:
        return st.secrets["DEMO_PHONE_NUMBER"]
    return depanneur["telephone"]


def send_assistance_sms(demande_id, demande, depanneur=None):
    client_twilio = get_twilio_client()
    maps_link = generate_google_maps_link(demande["latitude"], demande["longitude"])
    target_number = get_sms_target_number(depanneur)
    depanneur_nom = depanneur["nom"] if depanneur is not None else "Dépanneur démo"
    distance = depanneur.get("distance_km", "N/A") if depanneur is not None else "N/A"

    body = (
        f"🚨 ALERTE DEPANNAGE PL\n"
        f"ID : {demande_id}\n"
        f"Dépanneur IA sollicité : {depanneur_nom}\n"
        f"Distance : {distance} km\n"
        f"Client : {demande['client']}\n"
        f"Chauffeur : {demande['chauffeur']}\n"
        f"Tel chauffeur : {demande['telephone_chauffeur']}\n"
        f"Véhicule : {demande['immatriculation']}\n"
        f"Panne : {demande['type_panne']}\n"
        f"Dimension : {demande['dimension']}\n"
        f"Lieu : {demande['lieu']}\n"
        f"Urgence : {demande['urgence']}\n"
        f"GPS : {demande['latitude']},{demande['longitude']}\n"
        f"Itinéraire : {maps_link}\n"
        f"Répondre depuis l'app dépanneur : accepter ou refuser."
    )
    message = client_twilio.messages.create(body=body, from_=st.secrets["TWILIO_FROM_NUMBER"], to=target_number)
    return message.sid, target_number


def send_driver_confirmation_sms(demande_id, demande):
    client_twilio = get_twilio_client()
    use_demo = st.secrets.get("USE_DEMO_PHONE_NUMBER", True)
    if isinstance(use_demo, str):
        use_demo = use_demo.strip().lower() in ["true", "1", "yes", "oui"]
    target_number = st.secrets["DEMO_PHONE_NUMBER"] if use_demo else demande["telephone_chauffeur"]
    body = (
        f"Orane Assistance : votre demande {demande_id} est enregistrée. "
        f"Un dépanneur sélectionné par IA est en cours de sollicitation. "
        f"Vous recevrez la confirmation après son acceptation."
    )
    message = client_twilio.messages.create(body=body, from_=st.secrets["TWILIO_FROM_NUMBER"], to=target_number)
    return message.sid, target_number


def make_assistance_call(demande_id, demande):
    client_twilio = get_twilio_client()
    twiml = f"""
    <Response>
        <Say language="fr-FR" voice="alice">
            Bonjour. Nouvelle demande de dépannage. Référence {demande_id}.
            Client {demande['client']}. Chauffeur {demande['chauffeur']}.
            Véhicule {demande['immatriculation']}. Panne {demande['type_panne']}.
            Merci de répondre depuis l'application dépanneur.
        </Say>
    </Response>
    """
    call = client_twilio.calls.create(twiml=twiml, from_=st.secrets["TWILIO_FROM_NUMBER"], to=st.secrets["DEMO_PHONE_NUMBER"])
    return call.sid


# ============================================================
# CASCADE ET STATUTS
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
    save_csv(pd.concat([tentatives, pd.DataFrame(new_rows)], ignore_index=True), TENTATIVES_FILE)


def update_demande_from_active_tentative(demande_id):
    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)
    idx = demandes[demandes.id == demande_id].index
    if len(idx) == 0:
        return

    active = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En attente")].sort_values("rang")
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
            demandes.loc[idx[0], col] = row.get(col, "")
    demandes.loc[idx[0], "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_csv(demandes, DEMANDES_FILE)


def accepter_tentative(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    demandes = load_csv(DEMANDES_FILE)
    idxs = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En attente")].sort_values("rang").index
    if len(idxs) == 0:
        return

    idx = idxs[0]
    tentatives.loc[idx, "statut"] = "Accepté"
    tentatives.loc[(tentatives.demande_id == demande_id) & (tentatives.statut == "En file"), "statut"] = "Annulé"

    d_idx = demandes[demandes.id == demande_id].index
    if len(d_idx) == 0:
        save_csv(tentatives, TENTATIVES_FILE)
        return

    dep_lat = tentatives.loc[idx, "depanneur_latitude"]
    dep_lon = tentatives.loc[idx, "depanneur_longitude"]
    dist = tentatives.loc[idx, "distance_km"]

    demandes.loc[d_idx[0], "statut"] = "Accepté par dépanneur"
    demandes.loc[d_idx[0], "depanneur_assigne"] = tentatives.loc[idx, "depanneur_nom"]
    demandes.loc[d_idx[0], "depanneur_nom"] = tentatives.loc[idx, "depanneur_nom"]
    demandes.loc[d_idx[0], "depanneur_telephone"] = tentatives.loc[idx, "depanneur_telephone"]
    demandes.loc[d_idx[0], "depanneur_latitude"] = dep_lat
    demandes.loc[d_idx[0], "depanneur_longitude"] = dep_lon
    demandes.loc[d_idx[0], "distance_km"] = dist
    demandes.loc[d_idx[0], "eta_minutes"] = estimate_eta_minutes(dist)
    demandes.loc[d_idx[0], "date_prise_en_charge"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    demandes.loc[d_idx[0], "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for col in ["stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]:
        demandes.loc[d_idx[0], col] = tentatives.loc[idx, col]

    demandes.loc[d_idx[0], "tracking_url"] = generate_google_maps_directions_link(
        dep_lat,
        dep_lon,
        demandes.loc[d_idx[0], "latitude"],
        demandes.loc[d_idx[0], "longitude"],
    )

    save_csv(tentatives, TENTATIVES_FILE)
    save_csv(demandes, DEMANDES_FILE)


def passer_au_suivant(demande_id):
    tentatives = load_csv(TENTATIVES_FILE)
    active = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En attente")].index
    if len(active):
        tentatives.loc[active[0], "statut"] = "Expiré / pas de réponse"

    queued = tentatives[(tentatives.demande_id == demande_id) & (tentatives.statut == "En file")].sort_values("rang")
    if len(queued):
        tentatives.loc[queued.index[0], "statut"] = "En attente"
    save_csv(tentatives, TENTATIVES_FILE)
    update_demande_from_active_tentative(demande_id)


def depanneur_refuse_mission(demande_id):
    passer_au_suivant(demande_id)


def update_demande_status(demande_id, statut):
    demandes = load_csv(DEMANDES_FILE)
    idx = demandes[demandes.id == demande_id].index
    if len(idx):
        demandes.loc[idx[0], "statut"] = statut
        demandes.loc[idx[0], "date_mise_a_jour_statut"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if statut == "Clôturé":
            demandes.loc[idx[0], "date_cloture"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_csv(demandes, DEMANDES_FILE)


def cloturer(demande_id):
    update_demande_status(demande_id, "Clôturé")


# ============================================================
# CARTES ET UI HELPERS
# ============================================================

def afficher_carte_depanneurs(latitude, longitude, candidats, client, chauffeur, immatriculation, type_panne, dimension, urgence):
    if candidats.empty:
        return
    m = folium.Map(location=[latitude, longitude], zoom_start=8, tiles="OpenStreetMap")
    folium.Marker(
        location=[latitude, longitude],
        tooltip="Camion en panne",
        popup=f"<b>🚛 Camion en panne</b><br>Client : {client}<br>Chauffeur : {chauffeur}<br>Immatriculation : {immatriculation}<br>Panne : {type_panne}<br>Dimension : {dimension}<br>Urgence : {urgence}",
        icon=folium.Icon(color="red", icon="truck", prefix="fa"),
    ).add_to(m)
    folium.CircleMarker(location=[latitude, longitude], radius=14, color="red", fill=True, fill_color="red", fill_opacity=0.35).add_to(m)

    for _, d in candidats.iterrows():
        folium.Marker(
            location=[d["latitude"], d["longitude"]],
            tooltip=f'{d["nom"]} - {d["distance_km"]} km',
            popup=f"<b>🛠️ {d['nom']}</b><br>Ville : {d['ville']}<br>Distance : {d['distance_km']} km<br>Stock : {'✅ Oui' if d.get('stock_disponible', False) else '⚠️ Non confirmé'}<br>Score IA : {d.get('score_ia', '')}",
            icon=folium.Icon(color="green", icon="wrench", prefix="fa"),
        ).add_to(m)
        folium.PolyLine([[latitude, longitude], [d["latitude"], d["longitude"]]], color="orange", weight=2, opacity=0.7).add_to(m)
    components.html(m._repr_html_(), height=520)


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
        popup=f"<b>🚛 Camion en panne</b><br>ID : {ui_safe(demande.get('id', ''))}<br>Client : {ui_safe(demande.get('client', ''))}<br>Véhicule : {ui_safe(demande.get('immatriculation', ''))}",
        icon=folium.Icon(color="red", icon="truck", prefix="fa"),
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
                popup=f"<b>🛠️ {ui_safe(d.get('depanneur_nom', ''))}</b><br>Rang : {ui_safe(d.get('rang', ''))}<br>Statut : {statut}<br>Score IA : {ui_safe(d.get('score_ia', ''))}",
                icon=folium.Icon(color=color, icon="wrench", prefix="fa"),
            ).add_to(m)
            folium.PolyLine([[lat, lon], [dep_lat, dep_lon]], color="#2563eb", weight=2, opacity=0.45).add_to(m)
    components.html(m._repr_html_(), height=520)


def ui_status_class(statut):
    statut = ui_safe(statut, "").lower()
    if "danger" in statut or "manuel" in statut or "annul" in statut:
        return "fr-badge-red"
    if "clôturé" in statut or "cloture" in statut or "accepté" in statut or "accepte" in statut:
        return "fr-badge-green"
    if "route" in statut or "place" in statut or "propos" in statut or "recherche" in statut:
        return "fr-badge-orange"
    return "fr-badge-blue"


def ui_stock_badge(value):
    return "fr-badge-green" if to_bool(value) else "fr-badge-orange"


def render_timeline(statut):
    steps = ["Créée", "Recherche", "Proposée", "Acceptée", "En route", "Sur place", "Clôturée"]
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
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def statut_confirme_cote_chauffeur(statut):
    return str(statut).strip() in ["Accepté par dépanneur", "Dépanneur en route", "Dépanneur sur place", "Clôturé"]


def calculer_taux_acceptation_moins_5_min(demandes):
    """
    KPI métier : part des demandes acceptées par un dépanneur en moins de 5 minutes.

    Numérateur : demandes avec date_prise_en_charge renseignée et délai <= 5 minutes
    Dénominateur : demandes créées, hors demandes annulées
    """
    if demandes is None or demandes.empty:
        return "—"

    df = demandes.copy()

    if "statut" in df.columns:
        df = df[~df["statut"].astype(str).str.contains("Annulé|Annule", case=False, na=False)]

    if df.empty or "date_creation" not in df.columns or "date_prise_en_charge" not in df.columns:
        return "—"

    df["date_creation_calc"] = pd.to_datetime(df["date_creation"], errors="coerce")
    df["date_acceptation_calc"] = pd.to_datetime(df["date_prise_en_charge"], errors="coerce")

    total_demandes = len(df[df["date_creation_calc"].notna()])
    if total_demandes == 0:
        return "—"

    df_accept = df[df["date_creation_calc"].notna() & df["date_acceptation_calc"].notna()].copy()
    if df_accept.empty:
        return "0%"

    delai_minutes = (df_accept["date_acceptation_calc"] - df_accept["date_creation_calc"]).dt.total_seconds() / 60
    acceptees_moins_5 = int((delai_minutes <= 5).sum())

    return f"{round((acceptees_moins_5 / total_demandes) * 100)}%"


# ============================================================
# VUES
# ============================================================

def render_header():
    logo_file = Path("assets") / "fleetpartner_logo.png"
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if logo_file.exists():
            st.image(str(logo_file), width=180)
    with col_title:
        st.markdown(
            """
            <div class="main-header">
                <div class="main-title">Orane Roadside Assistance</div>
                <div class="main-subtitle">Assistance et dépannage poids lourds • Route • Autoroute • 24/7</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_top_kpis():
    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)
    if demandes.empty:
        actifs, eta, connected, taux_acceptation_5min = 0, "—", 128, "—"
    else:
        actifs = len(demandes[~demandes["statut"].astype(str).isin(["Clôturé", "Annulé", "Annule"])] )
        eta_numeric = pd.to_numeric(demandes.get("eta_minutes", pd.Series(dtype=float)), errors="coerce").dropna()
        eta = f"{int(round(eta_numeric.mean()))} min" if len(eta_numeric) else "—"
        connected = 128
        taux_acceptation_5min = calculer_taux_acceptation_moins_5_min(demandes)

    labels = [
        ("Dépannages actifs", actifs),
        ("Temps moyen", eta),
        ("Dépanneurs connectés", connected),
        ("Acceptés < 5 min", taux_acceptation_5min),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, labels):
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)


def render_product_showcase(demandes, tentatives):
    if not demandes.empty:
        d = demandes.sort_values("date_creation", ascending=False).iloc[0].to_dict()
    else:
        d = {
            "id": "REQ-DEMO42", "client": "Transport Demo", "immatriculation": "AB-123-CD",
            "type_panne": "Éclatement", "dimension": "315/80 R22.5", "urgence": "Urgent",
            "statut": "Mission proposée au dépanneur", "depanneur_nom": "BestDrive Compiègne",
            "distance_km": "18.4", "eta_minutes": "18", "stock_quantite": "6",
            "stock_marque": "Continental", "stock_profil": "Conti Hybrid HD3", "score_ia": "148.2",
            "decision_ia": "Recommandé : stock disponible",
        }

    statut = ui_safe(d.get("statut", ""))
    status_badge = ui_status_class(statut)
    st.markdown(
        f"""
        <div class="fr-card">
            <div style="display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap;">
                <div>
                    <div style="font-size:13px;color:#94a3b8;font-weight:900;text-transform:uppercase;letter-spacing:.08em;">Vue produit</div>
                    <div style="font-size:36px;font-weight:950;letter-spacing:-.05em;color:white;">FleetRescue</div>
                    <div class="fr-muted">Driver → IA Dispatch → Responder → Operator supervision</div>
                </div>
                <div><span class="fr-badge {status_badge}">{statut}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.4, 1])
    with c1:
        st.markdown('<div class="fr-section-title">🗺️ Démo opérationnelle</div>', unsafe_allow_html=True)
        if not demandes.empty:
            selected = pd.Series(d)
            current = tentatives[tentatives.demande_id == d["id"]].sort_values("rang") if not tentatives.empty else pd.DataFrame()
            afficher_carte_superviseur(selected, current)
        else:
            st.markdown('<div class="fr-empty">Crée une demande dans l’onglet Chauffeur pour alimenter la carte et le cockpit.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""
            <div class="fr-card">
                <div class="fr-section-title">🚛 Intervention active</div>
                <div class="fr-info-row"><div class="fr-info-label">ID</div><div class="fr-info-value">{ui_safe(d.get('id'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Client</div><div class="fr-info-value">{ui_safe(d.get('client'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Véhicule</div><div class="fr-info-value">{ui_safe(d.get('immatriculation'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Panne</div><div class="fr-info-value">{ui_safe(d.get('type_panne'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Dimension</div><div class="fr-info-value">{ui_safe(d.get('dimension'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Dépanneur IA</div><div class="fr-info-value">{ui_safe(d.get('depanneur_nom'))}</div></div>
                <div class="fr-info-row"><div class="fr-info-label">Score IA</div><div class="fr-info-value">{ui_safe(d.get('score_ia'))}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def afficher_suivi_chauffeur(demande):
    statut = demande.get("statut", "En cours")
    statut_confirme = statut_confirme_cote_chauffeur(statut)
    immatriculation = demande.get("immatriculation", "")
    type_panne = demande.get("type_panne", "")

    if statut_confirme:
        depanneur_nom = demande.get("depanneur_nom", "") or demande.get("depanneur_assigne", "")
        depanneur_tel = demande.get("depanneur_telephone", "")
        distance = demande.get("distance_km", "")
        eta = demande.get("eta_minutes", "")
        tracking_url = demande.get("tracking_url", "")
        depanneur_nom = depanneur_nom if ui_safe(depanneur_nom, "") else "Dépanneur confirmé"
        eta_label = f"{eta} min" if ui_safe(eta, "") else "En cours"
        distance_label = ui_safe(distance)
    else:
        depanneur_nom = "Dépanneur IA sollicité — en attente d’acceptation"
        depanneur_tel = ""
        distance_label = "—"
        eta_label = "En attente"
        tracking_url = ""

    st.markdown(
        f"""
        <div class="mobile-card">
            <div class="mobile-card-title">🚛 Votre dépannage</div>
            <div class="mobile-status">{statut}</div>
            <br><br>
            <b>Véhicule :</b> {immatriculation}<br>
            <b>Panne :</b> {type_panne}<br>
            <b>Agence / dépanneur :</b> {depanneur_nom}<br>
            <b>Téléphone :</b> {depanneur_tel if depanneur_tel else "—"}<br>
            <b>Distance :</b> {distance_label} km
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.metric("Temps estimé d'arrivée", eta_label)

    if not statut_confirme:
        st.info("Votre demande a bien été transmise. Le dépanneur sélectionné par l’IA doit maintenant accepter la mission.")
        return

    if depanneur_tel and str(depanneur_tel).lower() != "nan":
        st.link_button("📞 Appeler le dépanneur", f"tel:{depanneur_tel}", use_container_width=True)
    if tracking_url and str(tracking_url).lower() != "nan":
        st.link_button("🗺️ Suivre / voir l’itinéraire", tracking_url, use_container_width=True)


def afficher_app_chauffeur():
    st.subheader("Créer une demande de dépannage")

    demandes_existantes = load_csv(DEMANDES_FILE)
    statuts_ouverts = ["Recherche dépanneur", "Mission proposée au dépanneur", "Accepté par dépanneur", "Dépanneur en route", "Dépanneur sur place", "A traiter manuellement"]
    demande_session_id = st.session_state.get("chauffeur_demande_id", "")

    if demande_session_id and not demandes_existantes.empty:
        demande_active = demandes_existantes[(demandes_existantes["id"] == demande_session_id) & (demandes_existantes["statut"].isin(statuts_ouverts))]
        if not demande_active.empty:
            afficher_suivi_chauffeur(demande_active.iloc[0])
            c_refresh, c_new = st.columns(2)
            if c_refresh.button("🔄 Rafraîchir le suivi", use_container_width=True):
                st.rerun()
            if c_new.button("➕ Créer une nouvelle demande", use_container_width=True):
                st.session_state["chauffeur_demande_id"] = ""
                st.rerun()
            st.divider()

    ok_twilio, missing_key = twilio_is_configured()
    if not ok_twilio:
        st.warning(f"Twilio n'est pas encore configuré. Secret manquant : {missing_key}. La demande sera créée, mais le SMS et l'appel ne partiront pas.")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client / société", "Transport Demo")
        chauffeur = st.text_input("Nom chauffeur", "Jean Martin")
        telephone = st.text_input("Téléphone chauffeur", "+33612345678")
        immatriculation = st.text_input("Immatriculation", "AB-123-CD")
        type_panne = st.selectbox("Type de panne", ["Crevaison", "Éclatement", "Valve / pression", "Permutation", "Autre"])
        dimension = st.selectbox("Dimension pneu", ["315/80 R22.5", "315/70 R22.5", "385/65 R22.5", "295/80 R22.5", "Autre / inconnue"])
    with col2:
        st.info("Coordonnées GPS préremplies pour la démo. Dans la vraie app, elles viendraient du téléphone.")
        lieu = st.radio("Lieu", ["Route", "Autoroute"], horizontal=True)
        latitude = st.number_input("Latitude panne", value=49.2500, format="%.6f")
        longitude = st.number_input("Longitude panne", value=2.6500, format="%.6f")
        mode_paiement = st.radio("Paiement", ["Client en compte", "CB / Apple Pay"], horizontal=True)
        urgence = st.selectbox("Niveau d'urgence", ["Standard", "Urgent", "Danger immédiat / voie rapide"])
        commentaire = st.text_area("Commentaire", "Véhicule immobilisé. Demande urgente.")
        photo_flanc = st.file_uploader("Photo flanc pneu", type=["jpg", "jpeg", "png"], key="photo_flanc_pneu")
        photo_avarie = st.file_uploader("Photo incident", type=["jpg", "jpeg", "png"], key="photo_incident")

        if photo_flanc and photo_avarie:
            st.markdown("### 🛞 Analyse IA pneumatique")
            c1, c2 = st.columns(2)
            with c1:
                st.image(photo_flanc, caption="Photo flanc pneu", use_container_width=True)
            with c2:
                st.image(photo_avarie, caption="Photo incident", use_container_width=True)
            if st.button("🔍 Analyser les photos avec IA"):
                with st.spinner("Analyse IA en cours..."):
                    resultat = analyser_pneu(photo_flanc, photo_avarie)
                flanc = resultat.get("photo_flanc", {})
                avarie = resultat.get("photo_avarie", {}) or resultat.get("photo_incident", {}) or resultat.get("avarie", {})
                st.success("Analyse terminée")
                st.write(f"**Marque :** {flanc.get('marque', 'non visible')}")
                st.write(f"**Dimension :** {flanc.get('dimension', 'non visible')}")
                st.write(f"**Profil :** {flanc.get('profil', 'non visible')}")
                st.write(f"**DOT :** {flanc.get('DOT', flanc.get('dot', 'non visible'))}")
                st.write(f"**Avarie :** {avarie.get('description', avarie.get('type', 'non visible'))}")
                st.write(f"**Gravité :** {avarie.get('gravité', avarie.get('gravite', 'non visible'))}")

    st.divider()
    if st.button("🚨 DEMANDER UN DÉPANNAGE", type="primary", use_container_width=True):
        depanneurs = load_csv(DEPANNEURS_FILE)
        demandes = load_csv(DEMANDES_FILE)
        demande_id = "REQ-" + str(uuid.uuid4())[:8].upper()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        demande = {
            "id": demande_id,
            "date_creation": now,
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
            "date_mise_a_jour_statut": now,
        }

        candidats = trouver_depanneurs(demande, depanneurs)
        best_depanneur = None
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
            demande["stock_disponible"] = best_depanneur.get("stock_disponible", False)
            demande["stock_quantite"] = best_depanneur.get("stock_quantite", 0)
            demande["stock_marque"] = best_depanneur.get("stock_marque", "")
            demande["stock_profil"] = best_depanneur.get("stock_profil", "")
            demande["score_ia"] = best_depanneur.get("score_ia", 0)
            demande["decision_ia"] = best_depanneur.get("decision_ia", "")

        save_csv(pd.concat([demandes, pd.DataFrame([demande])], ignore_index=True), DEMANDES_FILE)
        if not candidats.empty:
            creer_tentatives(demande_id, candidats)

        st.session_state["chauffeur_demande_id"] = demande_id
        st.success(f"Demande créée : {demande_id}. Le dépanneur sélectionné par l’IA doit maintenant accepter la mission.")

        if not candidats.empty:
            st.markdown("### Candidats IA")
            st.dataframe(candidats[["nom", "reseau", "ville", "distance_km", "telephone", "stock_disponible", "stock_quantite", "stock_marque", "stock_profil", "score_ia", "decision_ia"]], use_container_width=True, hide_index=True)
            afficher_carte_depanneurs(latitude, longitude, candidats, client, chauffeur, immatriculation, type_panne, dimension, urgence)

        if ok_twilio:
            try:
                sms_sid, sms_target = send_assistance_sms(demande_id, demande, best_depanneur)
                driver_sid, driver_target = send_driver_confirmation_sms(demande_id, demande)
                call_sid = make_assistance_call(demande_id, demande)
                st.success(f"SMS dépanneur envoyé vers {sms_target}. SID : {sms_sid}")
                st.success(f"SMS chauffeur envoyé vers {driver_target}. SID : {driver_sid}")
                st.success(f"Appel Twilio déclenché. SID : {call_sid}")
            except Exception as e:
                st.error(f"Erreur Twilio : {e}")


def afficher_app_depanneur():
    st.subheader("📱 App dépanneur")
    st.caption("Simulation de l'application mobile utilisée par le dépanneur : accepter, partir, arriver, terminer.")

    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)
    if demandes.empty:
        st.info("Aucune mission pour le moment.")
        return

    statuts_depanneur = ["Mission proposée au dépanneur", "Accepté par dépanneur", "Dépanneur en route", "Dépanneur sur place"]
    missions = demandes[demandes["statut"].isin(statuts_depanneur)].copy()
    if missions.empty:
        st.success("Aucune mission active côté dépanneur.")
        return

    missions = missions.sort_values("date_creation", ascending=False)
    mission_id = st.selectbox(
        "Mission",
        missions["id"].tolist(),
        format_func=lambda x: f"{x} — {missions[missions['id'] == x].iloc[0]['immatriculation']} — {missions[missions['id'] == x].iloc[0]['statut']}",
    )

    demande = missions[missions["id"] == mission_id].iloc[0]
    current_tentatives = tentatives[tentatives.demande_id == mission_id].sort_values("rang") if not tentatives.empty else pd.DataFrame(columns=TENTATIVES_COLUMNS)
    active = current_tentatives[current_tentatives.statut == "En attente"] if not current_tentatives.empty else pd.DataFrame()

    if demande.get("statut", "") == "Mission proposée au dépanneur" and active.empty:
        st.warning("Cette mission est proposée, mais aucune tentative active n’est disponible.")
        st.dataframe(current_tentatives, use_container_width=True, hide_index=True)
        return

    if not active.empty:
        mission_dep = active.iloc[0]
        depanneur_nom = mission_dep.get("depanneur_nom", demande.get("depanneur_nom", ""))
        depanneur_tel = mission_dep.get("depanneur_telephone", demande.get("depanneur_telephone", ""))
        score_ia = mission_dep.get("score_ia", demande.get("score_ia", ""))
        decision_ia = mission_dep.get("decision_ia", demande.get("decision_ia", ""))
        stock_ok = mission_dep.get("stock_disponible", demande.get("stock_disponible", False))
        stock_qte = mission_dep.get("stock_quantite", demande.get("stock_quantite", 0))
        distance = mission_dep.get("distance_km", demande.get("distance_km", ""))
        eta = estimate_eta_minutes(distance)
    else:
        depanneur_nom = demande.get("depanneur_nom", "")
        depanneur_tel = demande.get("depanneur_telephone", "")
        score_ia = demande.get("score_ia", "")
        decision_ia = demande.get("decision_ia", "")
        stock_ok = demande.get("stock_disponible", False)
        stock_qte = demande.get("stock_quantite", 0)
        distance = demande.get("distance_km", "")
        eta = demande.get("eta_minutes", "")

    stock_label = "✅ disponible" if to_bool(stock_ok) else "⚠️ non confirmé"
    maps_link = generate_google_maps_link(demande.get("latitude", ""), demande.get("longitude", ""))

    st.markdown(
        f"""
        <div class="mobile-card">
            <div class="mobile-card-title">🚨 Mission dépanneur</div>
            <div class="mobile-status">{demande.get('statut', '')}</div>
            <br><br>
            <b>Dépanneur :</b> {depanneur_nom}<br>
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
        unsafe_allow_html=True,
    )

    st.link_button("🗺️ Ouvrir le lieu de panne", maps_link, use_container_width=True)

    if demande.get("statut", "") == "Mission proposée au dépanneur":
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


def render_intervention_card(demande):
    statut = ui_safe(demande.get("statut", ""))
    urgence = ui_safe(demande.get("urgence", ""))
    badge_class = ui_status_class(statut)
    urgency_class = "fr-badge-red" if "Danger" in urgence else "fr-badge-orange" if "Urgent" in urgence else "fr-badge-blue"
    st.markdown(
        f"""
        <div class="fr-card">
            <div style="display:flex; justify-content:space-between; gap:12px; align-items:flex-start; margin-bottom:12px;">
                <div>
                    <div style="font-size:13px; color:#94a3b8; font-weight:900; text-transform:uppercase; letter-spacing:.08em;">Intervention sélectionnée</div>
                    <div style="font-size:30px; font-weight:950; letter-spacing:-.04em; margin-top:4px; color:white;">{ui_safe(demande.get('id', ''))}</div>
                    <div class="fr-muted">{ui_safe(demande.get('client', ''))} • {ui_safe(demande.get('immatriculation', ''))}</div>
                </div>
                <div style="text-align:right;"><span class="fr-badge {badge_class}">{statut}</span><br><span class="fr-badge {urgency_class}">{urgence}</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_timeline(statut)
    st.markdown(
        f"""
        <div class="fr-card">
            <div class="fr-info-row"><div class="fr-info-label">Chauffeur</div><div class="fr-info-value">{ui_safe(demande.get('chauffeur', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Téléphone</div><div class="fr-info-value">{ui_safe(demande.get('telephone_chauffeur', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Panne</div><div class="fr-info-value">{ui_safe(demande.get('type_panne', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Dimension</div><div class="fr-info-value">{ui_safe(demande.get('dimension', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Lieu</div><div class="fr-info-value">{ui_safe(demande.get('lieu', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Commentaire</div><div class="fr-info-value">{ui_safe(demande.get('commentaire', ''))}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_stock_card(demande):
    stock_ok = demande.get("stock_disponible", False)
    stock_class = ui_stock_badge(stock_ok)
    stock_label = "Stock confirmé" if to_bool(stock_ok) else "Stock non confirmé"
    eta = ui_safe(demande.get("eta_minutes", ""))
    eta_label = f"{eta} min" if eta != "—" and "min" not in eta else eta
    st.markdown(
        f"""
        <div class="fr-card">
            <div class="fr-section-title">🧠 Décision IA</div>
            <span class="fr-badge {stock_class}">{stock_label}</span>
            <div class="fr-info-row"><div class="fr-info-label">Score IA</div><div class="fr-info-value">{ui_safe(demande.get('score_ia', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Distance</div><div class="fr-info-value">{ui_safe(demande.get('distance_km', ''))} km</div></div>
            <div class="fr-info-row"><div class="fr-info-label">ETA</div><div class="fr-info-value">{eta_label}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Dépanneur</div><div class="fr-info-value">{ui_safe(demande.get('depanneur_nom', demande.get('depanneur_assigne', '')))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Téléphone</div><div class="fr-info-value">{ui_safe(demande.get('depanneur_telephone', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Stock</div><div class="fr-info-value">Qté {ui_safe(demande.get('stock_quantite', '0'))} — {ui_safe(demande.get('stock_marque', ''))} {ui_safe(demande.get('stock_profil', ''))}</div></div>
            <div class="fr-info-row"><div class="fr-info-label">Raison IA</div><div class="fr-info-value">{ui_safe(demande.get('decision_ia', ''))}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
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
        st.markdown(
            f"""
            <div class="fr-responder-card">
                <div class="fr-responder-top">
                    <div>
                        <div class="fr-responder-name">#{ui_safe(row.get('rang', ''))} — {ui_safe(row.get('depanneur_nom', ''))}</div>
                        <div class="fr-muted">{ui_safe(row.get('distance_km', ''))} km • {ui_safe(row.get('canal', ''))}</div>
                    </div>
                    <div class="fr-score">{ui_safe(row.get('score_ia', ''))}</div>
                </div>
                <span class="fr-badge {badge}">{statut}</span>
                <span class="fr-badge {stock_class}">{stock_label} · Qté {ui_safe(row.get('stock_quantite', '0'))}</span>
                <div class="fr-muted" style="margin-top:8px; font-size:13px;">{ui_safe(row.get('stock_marque', ''))} {ui_safe(row.get('stock_profil', ''))}<br>{ui_safe(row.get('decision_ia', ''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def afficher_cockpit_operateur():
    st.markdown(
        """
        <div class="fr-card">
            <div style="font-size:30px;font-weight:950;letter-spacing:-.04em;color:white;">🎯 Cockpit Opérateur FleetRescue</div>
            <div class="fr-muted">Supervision temps réel • Dispatch IA • Stock simulé Winpro/Inovaxo • Cascade dépanneurs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)
    if demandes.empty:
        st.markdown('<div class="fr-empty">Aucune demande pour le moment. Crée une demande depuis l’onglet Chauffeur.</div>', unsafe_allow_html=True)
        return

    demandes_view = demandes.sort_values("date_creation", ascending=False).copy()
    selected_id = st.selectbox(
        "Sélectionner une demande",
        demandes_view["id"].tolist(),
        format_func=lambda x: f"{x} — {ui_safe(demandes_view[demandes_view['id'] == x].iloc[0].get('immatriculation', ''))} — {ui_safe(demandes_view[demandes_view['id'] == x].iloc[0].get('statut', ''))}",
    )
    demande = demandes_view[demandes_view["id"] == selected_id].iloc[0]
    current = tentatives[tentatives.demande_id == selected_id].sort_values("rang") if not tentatives.empty else pd.DataFrame(columns=TENTATIVES_COLUMNS)

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown('<div class="fr-section-title">🗺️ Carte opérationnelle</div>', unsafe_allow_html=True)
        afficher_carte_superviseur(demande, current)
        with st.expander("Afficher les tables techniques"):
            st.markdown("Demandes")
            st.dataframe(demandes_view, use_container_width=True, hide_index=True)
            st.markdown("Cascade")
            st.dataframe(current, use_container_width=True, hide_index=True)
    with right:
        render_intervention_card(demande)
        render_ai_stock_card(demande)
        st.markdown('<div class="fr-section-title">⚡ Supervision opérateur</div>', unsafe_allow_html=True)
        st.info("L’opérateur supervise. L’acceptation doit être faite depuis l’onglet App dépanneur.")
        c1, c2 = st.columns(2)
        if c1.button("⏱️ Pas de réponse → proposer au suivant", use_container_width=True):
            passer_au_suivant(selected_id)
            st.rerun()
        if c2.button("🚨 Escalader en traitement manuel", use_container_width=True):
            update_demande_status(selected_id, "A traiter manuellement")
            st.rerun()
        c3, c4 = st.columns(2)
        if c3.button("❌ Annuler la demande", use_container_width=True):
            update_demande_status(selected_id, "Annulé")
            st.rerun()
        if c4.button("🏁 Clôturer admin", use_container_width=True):
            cloturer(selected_id)
            st.rerun()
        render_responder_cards(current)


def afficher_administration():
    st.subheader("Référentiel dépanneurs")
    depanneurs = load_csv(DEPANNEURS_FILE)
    edited = st.data_editor(depanneurs, use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder le référentiel"):
        save_csv(edited, DEPANNEURS_FILE)
        st.success("Référentiel sauvegardé.")

    st.divider()
    st.subheader("Stock simulé PDV / future API Winpro-Innovaxo")
    stocks = load_csv(STOCKS_FILE)
    edited_stocks = st.data_editor(stocks, use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder le stock simulé"):
        save_csv(edited_stocks, STOCKS_FILE)
        st.success("Stock simulé sauvegardé.")


def afficher_kpi():
    st.subheader("Reporting démo")
    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)
    if demandes.empty:
        st.info("Pas encore de données.")
        return

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
    st.download_button("Télécharger demandes CSV", demandes.to_csv(index=False).encode("utf-8"), file_name="demandes_depannage.csv", mime="text/csv")


# ============================================================
# LANCEMENT APP
# ============================================================

init_data()
ensure_data_schema()
render_header()
render_top_kpis()

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✨ Vue produit",
    "🚛 Chauffeur",
    "🛠️ Dépanneur",
    "🎯 Cockpit opérateur",
    "⚙️ Administration",
    "📈 KPI",
])

with tab0:
    render_product_showcase(load_csv(DEMANDES_FILE), load_csv(TENTATIVES_FILE))
with tab1:
    afficher_app_chauffeur()
with tab2:
    afficher_app_depanneur()
with tab3:
    afficher_cockpit_operateur()
with tab4:
    afficher_administration()
with tab5:
    afficher_kpi()
