import math
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIG PAGE
# ============================================================

st.set_page_config(
    page_title="FleetPartner Rescue 24/7",
    page_icon="🛞",
    layout="wide"
)


# ============================================================
# HEADER AVEC LOGO
# ============================================================

LOGO_FILE = Path("assets") / "fleetpartner_logo.png"

col_logo, col_title = st.columns([1, 4])

with col_logo:
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), width=220)
    else:
        st.warning("Logo non trouvé")

with col_title:
    st.title("FleetPartner Rescue 24/7")
    st.caption("Plateforme intelligente de dépannage poids lourds")


# ============================================================
# FICHIERS DATA
# ============================================================

DATA_DIR = Path("data")

# Sécurité : si "data" existe par erreur comme fichier, on le supprime
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
            "longitude", "type_panne", "lieu", "dimension", "statut",
            "depanneur_assigne", "distance_km", "mode_paiement",
            "commentaire", "date_cloture"
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

        commentaire = st.text_area(
            "Commentaire",
            "Véhicule immobilisé. Demande urgente."
        )

    if st.button("🚨 Demander un dépannage", type="primary"):
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
            "statut": "Recherche dépanneur",
            "depanneur_assigne": "",
            "distance_km": "",
            "mode_paiement": mode_paiement,
            "commentaire": commentaire,
            "date_cloture": "",
        }

        candidats = trouver_depanneurs(demande, depanneurs)

        if candidats.empty:
            demande["statut"] = "A traiter manuellement"
            st.error("Aucun dépanneur éligible trouvé. Bascule en traitement manuel.")
        else:
            creer_tentatives(demande_id, candidats)
            st.success(f"Demande créée : {demande_id}. Alerte envoyée au dépanneur le plus proche.")
            st.dataframe(
                candidats[["nom", "reseau", "ville", "distance_km", "telephone", "stock", "score"]],
                use_container_width=True,
                hide_index=True
            )

        save_csv(
            pd.concat([demandes, pd.DataFrame([demande])], ignore_index=True),
            DEMANDES_FILE
        )


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
