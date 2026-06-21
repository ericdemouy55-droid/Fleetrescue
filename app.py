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


def get_sms_target_number(depanneur=None):
    """
    En mode démo, on force l'envoi vers DEMO_PHONE_NUMBER.
    En mode réel, si USE_DEMO_PHONE_NUMBER = false dans secrets.toml,
    le SMS part vers le téléphone du dépanneur sélectionné.
    """
    use_demo = st.secrets.get("USE_DEMO_PHONE_NUMBER", True)

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

    body = (
        f"Orane Assistance : votre demande {demande_id} est enregistrée. "
        f"Client : {client}. Véhicule : {immatriculation}. Panne : {type_panne}. "
        f"Un dépanneur est en cours de sollicitation."
    )

    message = client_twilio.messages.create(
        body=body,
        from_=st.secrets["TWILIO_FROM_NUMBER"],
        to=telephone
    )

    return message.sid


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

    if not DEMANDES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "date_creation", "client", "chauffeur",
            "telephone_chauffeur", "immatriculation", "latitude",
            "longitude", "type_panne", "lieu", "dimension", "urgence",
            "statut", "depanneur_assigne", "distance_km", "mode_paiement",
            "commentaire", "photo_1", "photo_2", "date_cloture"
        ]).to_csv(DEMANDES_FILE, index=False)

    if not TENTATIVES_FILE.exists():
        pd.DataFrame(columns=[
            "id", "demande_id", "rang", "depanneur_id",
            "depanneur_nom", "distance_km", "canal",
            "statut", "date_tentative"
        ]).to_csv(TENTATIVES_FILE, index=False)


# ============================================================
# OUTILS CSV
# ============================================================

def load_csv(path):
    return pd.read_csv(path)


def save_csv(df, path):
    df.to_csv(path, index=False)


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


def trouver_depanneurs(demande, depanneurs):
    rows = []

    for _, d in depanneurs.iterrows():
        if not bool(d["disponible"]) or not bool(d["pl"]):
            continue

        if demande["lieu"] == "Autoroute" and not bool(d["autoroute"]):
            continue

        if demande["lieu"] == "Route" and not bool(d["route"]):
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
            rows.append(row)

    return pd.DataFrame(
        sorted(rows, key=lambda x: (x["distance_km"], -float(x["score"])))
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
            Stock : {d["stock"]}
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
            "canal": "Appel + SMS + Email",
            "statut": "En attente" if rang == 1 else "En file",
            "date_tentative": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
    demandes.loc[d_idx, "statut"] = "Accepté par dépanneur"
    demandes.loc[d_idx, "depanneur_assigne"] = nom
    demandes.loc[d_idx, "distance_km"] = dist

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


# ============================================================
# LANCEMENT APP
# ============================================================

init_data()

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

tab1, tab2, tab3, tab4 = st.tabs([
    "🚨 Demande chauffeur",
    "🧭 Superviseur",
    "🛠️ Dépanneurs",
    "📊 Reporting"
])


# ============================================================
# ONGLET 1 — DEMANDE CHAUFFEUR
# ============================================================

with tab1:
    st.subheader("Créer une demande de dépannage")

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
        }

        candidats = trouver_depanneurs(demande, depanneurs)

        if candidats.empty:
            demande["statut"] = "A traiter manuellement"
            st.error("Aucun dépanneur éligible trouvé. Bascule en traitement manuel.")
        else:
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

            st.success(f"Demande créée : {demande_id}. Dépanneur le plus proche sollicité.")

            st.dataframe(
                candidats[["nom", "reseau", "ville", "distance_km", "telephone", "stock", "score"]],
                use_container_width=True,
                hide_index=True
            )

        save_csv(
            pd.concat([demandes, pd.DataFrame([demande])], ignore_index=True),
            DEMANDES_FILE
        )

        ok_twilio, missing_key = twilio_is_configured()

        if ok_twilio:
            try:
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

                driver_sms_sid = send_driver_confirmation_sms(
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
                st.success(f"SMS chauffeur envoyé. SID : {driver_sms_sid}")
                st.success(f"Appel Twilio déclenché. SID : {call_sid}")

            except Exception as e:
                st.error(f"Demande créée, mais erreur Twilio : {e}")
        else:
            st.warning(f"Demande créée, mais SMS/appel non envoyés. Secret manquant : {missing_key}")


# ============================================================
# ONGLET 2 — SUPERVISEUR
# ============================================================

with tab2:
    st.subheader("Tableau superviseur")

    demandes = load_csv(DEMANDES_FILE)
    tentatives = load_csv(TENTATIVES_FILE)

    if demandes.empty:
        st.info("Aucune demande pour le moment.")
    else:
        st.dataframe(
            demandes.sort_values("date_creation", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        selected_id = st.selectbox(
            "Sélectionner une demande",
            demandes["id"].tolist()
        )

        st.markdown("### Cascade")

        current = tentatives[tentatives.demande_id == selected_id].sort_values("rang")

        st.dataframe(
            current,
            use_container_width=True,
            hide_index=True
        )

        active = current[current.statut == "En attente"]

        if len(active):
            row = active.iloc[0]
            st.warning(
                f"Sollicitation en cours : {row.depanneur_nom} — {row.distance_km} km — {row.canal}"
            )

        c1, c2, c3 = st.columns(3)

        if c1.button("✅ Simuler acceptation", type="primary"):
            accepter_tentative(selected_id)
            st.rerun()

        if c2.button("⏱️ Pas de réponse → suivant"):
            passer_au_suivant(selected_id)
            st.rerun()

        if c3.button("🏁 Clôturer intervention"):
            cloturer(selected_id)
            st.rerun()


# ============================================================
# ONGLET 3 — DÉPANNEURS
# ============================================================

with tab3:
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


# ============================================================
# ONGLET 4 — REPORTING
# ============================================================

with tab4:
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
