import streamlit as st
import requests
# import plotly.express as px # Commenté car plotly.graph_objects est utilisé pour les graphiques plus complexes.
import pandas as pd # Essentiel pour la manipulation des données (DataFrames).
from auth import login, register, get_token, logout, get_with_auth, post_with_auth # Fonctions d'authentification et d'interaction avec l'API.
from datetime import date # Utilisé pour la sélection de date dans la prédiction.
from streamlit_option_menu import option_menu # Pour la barre de navigation latérale moderne.
import plotly.graph_objects as go # Utilisé pour la création de graphiques interactifs.
import numpy as np # Utilisé pour les opérations numériques, notamment dans la simulation de données si besoin.
import pydeck as pdk # Utilisé pour la visualisation des données géospatiales sur une carte.

# --- Initialisation de st.session_state ---
# Ces variables maintiennent l'état de l'application à travers les différentes exécutions du script.
if "country" not in st.session_state:
    st.session_state["country"] = "France" # Définit le pays par défaut lors du premier chargement de la session.
# La variable 'available_countries' n'est plus utilisée pour la sélection de pays globale
# car la liste des pays est maintenant récupérée dynamiquement depuis l'API pour la page de prédiction.
# if "available_countries" not in st.session_state:
#     st.session_state["available_countries"] = ["France", "Switzerland", "US"]
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français" # Définit la langue par défaut de l'interface.

# --- CONFIGURATION DU THÈME ET DE LA PAGE ---
st.set_page_config(page_title="MSPR IA Pandémies", layout="wide") # Configure le titre de l'onglet du navigateur et le layout large de l'application.

# --- DÉFINITION DES TRADUCTIONS ---
# Dictionnaire imbriqué contenant toutes les chaînes de caractères de l'interface utilisateur,
# traduites pour le Français, l'Anglais, l'Italien et l'Allemand.
# Cela permet une internationalisation (i18n) flexible de l'application.
translations = {
    "Français": {
        "home": "Accueil",
        "login": "Connexion",
        "data": "Données",
        "predict": "Prédiction IA",
        "choose_lang": "🌐 Choisir la langue",
        "main_menu": "Menu principal",
        "welcome": "Bienvenue sur PandemIA",
        "subtitle": "Anticiper aujourd'hui, protéger demain",
        "desc": "Application de suivi et de prédiction de la pandémie Covid-19",
        "realtime": "Suivi en temps réel",
        "realtime_desc": "Visualisez les cas Covid-19 mis à jour quotidiennement.",
        "ai_pred": "Prédictions IA",
        "ai_pred_desc": "Nos modèles prédisent l'évolution des tendances.",
        "support": "Support décisionnel",
        "support_desc": "Des analyses fiables pour les acteurs de la santé.",
        "world_map": "Taux de cas Covid-19 par pays",
        "global_cases": "Cas mondiaux",
        "countries_tracked": "Pays suivis",
        "who": "Qui sommes-nous ?",
        "team_desc": "PandemIA est une équipe passionnée de data scientists et développeurs utilisant l'IA pour comprendre et anticiper les épidémies mondiales.",
        "login_title": "Connexion / Inscription",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "login_btn": "Se connecter",
        "register_tab": "Inscription",
        "register_btn": "Créer un compte",
        "email": "Email",
        "logout": "Se déconnecter",
        "data_title": "Données historiques",
        "connect_warn": "Veuillez vous connecter pour accéder aux données.",
        "entries": "Nombre d'entrées",
        "mean": "Valeur moyenne",
        "max": "Valeur max",
        "value_dist": "Distribution des valeurs",
        "value_by_region": "Valeur par région",
        "table": "Tableau des données",
        "no_data": "Aucune donnée disponible.",
        "predict_title": "Prédiction IA",
        "region": "Région",
        "location": "Localisation",
        "construction": "Type de construction",
        "value": "Valeur",
        "date": "Date",
        "predict_btn": "Lancer la prédiction",
        "result": "Résultat de la prédiction",
        "score": "Score",
        "predict_warn": "Veuillez vous connecter pour accéder à la prédiction.",
        "disconnect": "Déconnecté",
        "login_success": "Connecté !",
        "login_error": "Erreur de connexion",
        "register_success": "Compte créé, connectez-vous !",
        "register_error": "Erreur lors de l'inscription",
        "data_error": "Erreur lors de la récupération des données.",
        "predict_error": "Erreur lors de la prédiction.",
        "connect_button": "Se connecter",
        "country": "Pays",
        "death_rate": "Taux de mortalité",
        "recovery_rate": "Taux de guérison",
        "cases_overview": "Vue d'ensemble des cas",
        "metrics_overview": "Vue d'ensemble des métriques",
        "total_confirmed": "Total confirmés",
        "total_deaths": "Total décès",
        "total_recovered": "Total guéris",
        "confirmed": "Cas confirmés",
        "deaths": "Décès",
        "recovered": "Guéris",
        "new_cases": "Nouveaux cas"
    },
    "Anglais": {
        "home": "Home",
        "login": "Login",
        "data": "Data",
        "predict": "AI Prediction",
        "choose_lang": "🌐 Choose language",
        "main_menu": "Main menu",
        "welcome": "Welcome to PandemIA",
        "subtitle": "Anticipate today, protect tomorrow",
        "desc": "Covid-19 monitoring and prediction application",
        "realtime": "Real-time Tracking",
        "realtime_desc": "Visualize daily updated COVID-19 case numbers.",
        "ai_pred": "AI Predictions",
        "ai_pred_desc": "Our models reliably forecast future case trends.",
        "support": "Decision Support",
        "support_desc": "Accurate analyses to inform health stakeholders.",
        "world_map": "Covid-19 case rate by country",
        "global_cases": "Global cases",
        "countries_tracked": "Countries tracked",
        "who": "Who Are We?",
        "team_desc": "PandemIA is a passionate team of data scientists and developers using AI to understand and forecast global epidemics.",
        "login_title": "Login / Register",
        "username": "Username",
        "password": "Password",
        "login_btn": "Login",
        "register_tab": "Register",
        "register_btn": "Create account",
        "email": "Email",
        "logout": "Logout",
        "data_title": "Historical Data",
        "connect_warn": "Please login to access data.",
        "entries": "Entries",
        "mean": "Mean value",
        "max": "Max value",
        "value_dist": "Value distribution",
        "value_by_region": "Value by region",
        "table": "Data table",
        "no_data": "No data available.",
        "predict_title": "AI Prediction",
        "region": "Region",
        "location": "Location",
        "construction": "Construction type",
        "value": "Value",
        "date": "Date",
        "predict_btn": "Run prediction",
        "result": "Prediction result",
        "score": "Score",
        "predict_warn": "Please login to access prediction.",
        "disconnect": "Logged out",
        "login_success": "Logged in!",
        "login_error": "Login error",
        "register_success": "Account created, please login!",
        "register_error": "Registration error",
        "data_error": "Error fetching data.",
        "predict_error": "Prediction error.",
        "connect_button": "Login",
        "country": "Country",
        "death_rate": "Death rate",
        "recovery_rate": "Recovery rate",
        "cases_overview": "Cases overview",
        "metrics_overview": "Metrics overview",
        "total_confirmed": "Total confirmed",
        "total_deaths": "Total deaths",
        "total_recovered": "Total recovered",
        "confirmed": "Confirmed",
        "deaths": "Deaths",
        "recovered": "Recovered",
        "new_cases": "New cases"
    },
    "Italien": {
        "home": "Home",
        "login": "Accesso",
        "data": "Dati",
        "predict": "Predizione IA",
        "choose_lang": "🌐 Scegli la lingua",
        "main_menu": "Menu principale",
        "welcome": "Benvenuto su PandemIA",
        "subtitle": "Anticipa oggi, proteggi domani",
        "desc": "Applicazione di monitoraggio e previsione Covid-19",
        "realtime": "Monitoraggio in tempo reale",
        "realtime_desc": "Visualizza i casi Covid-19 aggiornati quotidianamente.",
        "ai_pred": "Previsioni IA",
        "ai_pred_desc": "I nostri modelli prevedono l'évolution delle tendenze.",
        "support": "Supporto decisionale",
        "support_desc": "Analisi affidabili per gli operatori sanitari.",
        "world_map": "Tasso di casi Covid-19 par pays",
        "global_cases": "Casi globali",
        "countries_tracked": "Paesi monitorati",
        "who": "Chi siamo?",
        "team_desc": "PandemIA è un team appassionato de data scientist e développatori qui utilizzano l'IA per comprendere e anticipare le epidemie mondiali.",
        "login_title": "Accesso / Registrazione",
        "username": "Nome utente",
        "password": "Password",
        "login_btn": "Accedi",
        "register_tab": "Registrazione",
        "register_btn": "Crea account",
        "email": "Email",
        "logout": "Disconnetti",
        "data_title": "Dati storici",
        "connect_warn": "Accedi per visualizzare i dati.",
        "entries": "Numero di voci",
        "mean": "Valore medio",
        "max": "Valore massimo",
        "value_dist": "Distribuzione dei valori",
        "value_by_region": "Valore per regione",
        "table": "Tabella dati",
        "no_data": "Nessun dato disponibile.",
        "predict_title": "Predizione IA",
        "region": "Regione",
        "location": "Località",
        "construction": "Tipo di costruzione",
        "value": "Valore",
        "date": "Data",
        "predict_btn": "Esegui predizione",
        "result": "Risultato della predizione",
        "score": "Punteggio",
        "predict_warn": "Accedi per eseguire la predizione.",
        "disconnect": "Disconnesso",
        "login_success": "Accesso effettuato!",
        "login_error": "Errore di accesso",
        "register_success": "Account creato, accedi!",
        "register_error": "Errore di registrazione",
        "data_error": "Erreur nel recupero dei dati.",
        "predict_error": "Errore nella predizione.",
        "connect_button": "Accedi",
        "country": "Paese",
        "death_rate": "Tasso di mortalità",
        "recovery_rate": "Tasso di guarigione",
        "cases_overview": "Panoramica dei casi",
        "metrics_overview": "Panoramica delle metriche",
        "total_confirmed": "Totale confermato",
        "total_deaths": "Totale morti",
        "total_recovered": "Totale guariti",
        "confirmed": "Confermato",
        "deaths": "Morti",
        "recovered": "Guariti",
        "new_cases": "Nuovi casi"
    },
    "Allemand": {
        "home": "Startseite",
        "login": "Anmelden",
        "data": "Daten",
        "predict": "KI-Vorhersage",
        "choose_lang": "🌐 Sprache wählen",
        "main_menu": "Hauptmenü",
        "welcome": "Willkommen bei PandemIA",
        "subtitle": "Heute vorausdenken, morgen schützen",
        "desc": "Covid-19 Überwachungs- und Vorhersageanwendung",
        "realtime": "Echtzeit-Tracking",
        "realtime_desc": "Visualisieren Sie täglich aktualisierte COVID-19-Fallzahlen.",
        "ai_pred": "KI-Vorhersagen",
        "ai_pred_desc": "Unsere Modelle prognostizieren zuverlässig zukünftige Falltrends.",
        "support": "Entscheidungsunterstützung",
        "support_desc": "Präzise Analysen für Gesundheitsakteure.",
        "world_map": "Covid-19-Fallrate nach Land",
        "global_cases": "Globale Fälle",
        "countries_tracked": "Verfolgte Länder",
        "who": "Wer sind wir?",
        "team_desc": "PandemIA ist ein leidenschaftliches Team von Datenwissenschaftlern und Entwicklern, die KI nutzen, um globale Epidemien zu verstehen und vorherzusagen.",
        "login_title": "Anmelden / Registrieren",
        "username": "Benutzername",
        "password": "Passwort",
        "login_btn": "Anmelden",
        "register_tab": "Registrieren",
        "register_btn": "Konto erstellen",
        "email": "E-Mail",
        "logout": "Abmelden",
        "data_title": "Historische Daten",
        "connect_warn": "Bitte melden Sie sich an, um auf Daten zuzugreifen.",
        "entries": "Einträge",
        "mean": "Durchschnittswert",
        "max": "Maximalwert",
        "value_dist": "Wertverteilung",
        "value_by_region": "Wert nach Region",
        "table": "Datentabelle",
        "no_data": "Keine Daten verfügbar.",
        "predict_title": "KI-Vorhersage",
        "region": "Region",
        "location": "Standort",
        "construction": "Bautyp",
        "value": "Wert",
        "date": "Datum",
        "predict_btn": "Vorhersage starten",
        "result": "Vorhersageergebnis",
        "score": "Punktzahl",
        "predict_warn": "Bitte melden Sie sich an, um auf die Vorhersage zuzugreifen.",
        "disconnect": "Abgemeldet",
        "login_success": "Angemeldet!",
        "login_error": "Anmeldefehler",
        "register_success": "Konto erstellt, bitte anmelden!",
        "register_error": "Registrierungsfehler",
        "data_error": "Fehler beim Abrufen der Daten.",
        "predict_error": "Vorhersagefehler.",
        "connect_button": "Anmelden",
        "country": "Land",
        "death_rate": "Sterberate",
        "recovery_rate": "Wiedererkrankungsrate",
        "cases_overview": "Fälleübersicht",
        "metrics_overview": "Metrikenübersicht",
        "total_confirmed": "Total bestätigt",
        "total_deaths": "Total verstorben",
        "total_recovered": "Total geheilt",
        "confirmed": "Bestätigt",
        "deaths": "Verstorben",
        "recovered": "Geheilt",
        "new_cases": "Neue Fälle"
    }
}

# Nous déplaçons la logique de session_state ici pour qu'elle soit traitée avant les widgets de la sidebar
user = st.session_state.get("user", None)
# Si un token d'authentification existe et qu'aucun utilisateur n'est encore défini dans la session,
# tente de récupérer les informations de l'utilisateur via l'API pour peupler la session.
if get_token() and not user:
    user_data = get_with_auth("/me")
    if user_data:
        st.session_state["user"] = user_data
        user = st.session_state["user"]

# --- AFFICHAGE DU PROFIL UTILISATEUR EN SIDEBAR ---
# Affiche le nom d'utilisateur et l'email de l'utilisateur connecté dans la barre latérale.
# Cette section n'apparaît que si un utilisateur est connecté.
if user:
    st.sidebar.markdown(
        f"""
        <div style='text-align:center; margin-bottom:1rem;'>
            <img src='https://img.icons8.com/ios-filled/50/1976d2/user-male-circle.png' width='40'/>
            <div style='font-size:1.1rem; color:#1976d2;'><b>{user['username']}</b></div>
            <div style='font-size:0.9rem; color:#888;'>{user['email']}</div>
        </div>
        """, unsafe_allow_html=True
    )

with st.sidebar:
    # --- BARRE LATÉRALE DE NAVIGATION (SIDEBAR) ---
    # Cette section configure l'apparence et le contenu de la barre latérale, y compris le logo et le menu de navigation.
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <img src='logo-pandemia.png' width='100' style='margin:auto;display:block;'/>
        </div>
        """, unsafe_allow_html=True
    )

    # Définit l'objet de traduction (dictionnaire 't') basé sur la langue actuellement sélectionnée dans la session.
    t = translations[st.session_state["lang"]]

    # --- SÉLECTION DU PAYS (RGPD) ---
    # Ce sélecteur permet à l'utilisateur de choisir un pays. Ce choix est crucial car il influence
    # les options de navigation disponibles et les langues proposées, conformément aux règles RGPD.
    country_selected_sidebar = st.selectbox(t["country"],
                                           ["France", "Switzerland", "US"],
                                           index=["France", "Switzerland", "US"].index(st.session_state["country"]) if st.session_state["country"] in ["France", "Switzerland", "US"] else 0,
                                           key="sidebar_country_select")
    st.session_state["country"] = country_selected_sidebar # Met à jour la valeur du pays sélectionné dans st.session_state.

    # --- LOGIQUE DE SÉLECTION DE LA LANGUE BASÉE SUR LE PAYS ---
    # Implémente les règles RGPD pour les langues :
    # - Suisse : Choix entre Français, Italien, Allemand.
    # - France : Langue fixée au Français.
    # - US : Langue fixée à l'Anglais.
    if st.session_state["country"] == "Switzerland":
        lang_options = ["Français", "Italien", "Allemand"]
        current_lang_in_swiss = st.session_state.get("lang", "Français")
        if current_lang_in_swiss not in lang_options:
            current_lang_in_swiss = lang_options[0]

        lang_from_selector = st.selectbox(
            t["choose_lang"], # Utilise le texte traduit pour le sélecteur de langue.
            lang_options,
            index=lang_options.index(current_lang_in_swiss),
            key="language_selector"
        )
        st.session_state["lang"] = lang_from_selector # Met à jour la langue choisie dans st.session_state.
    else:
        # Pour la France, la langue est toujours le Français par défaut.
        if st.session_state["country"] == "France":
            st.session_state["lang"] = "Français"
        # Pour les États-Unis, la langue est toujours l'Anglais par défaut.
        elif st.session_state["country"] == "US":
            st.session_state["lang"] = "Anglais"
    
    # Met à jour l'objet de traduction 't' une dernière fois, après que la langue a été finalisée.
    t = translations[st.session_state["lang"]]

    # --- MENU DE NAVIGATION PRINCIPAL (option_menu) ---
    # Les options de menu affichées sont dynamiques et dépendent du pays sélectionné,
    # respectant ainsi les règles RGPD définies.
    options = [t["home"], t["login"]]
    
    # Logique RGPD spécifique par pays pour l'affichage des onglets de navigation.
    if st.session_state["country"] == "France":
        options.append(t["data"])  # France : accès uniquement à l'onglet "Données".
    elif st.session_state["country"] == "US":
        options.extend([t["data"], t["predict"]])  # US : accès aux onglets "Données" et "Prédiction IA".
    elif st.session_state["country"] == "Switzerland":
        options.append(t["predict"])  # Suisse : accès uniquement à l'onglet "Prédiction IA".

    # Définition des icônes correspondantes pour chaque option de menu.
    icons = ["house", "box-arrow-in-right"]
    if t["data"] in options: icons.append("bar-chart") # Ajoute l'icône pour "Données" si l'option est présente.
    if t["predict"] in options: icons.append("robot") # Ajoute l'icône pour "Prédiction IA" si l'option est présente.

    # Gère la page actuellement sélectionnée dans le menu, en veillant à ce qu'elle soit une option valide.
    current_selected_page = st.session_state.get("selected_page", t["home"])
    if current_selected_page not in options:
        current_selected_page = t["home"]

    # Crée le menu de navigation Streamlit en utilisant `streamlit_option_menu`.
    selected = option_menu(
        menu_title=None, # Pas de titre affiché directement au-dessus du menu principal.
        options=options,
        icons=icons,
        menu_icon="cast",
        default_index=options.index(current_selected_page),
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#23242a"}, # Style du conteneur du menu.
            "icon": {"color": "#1976d2", "font-size": "24px"}, # Style des icônes du menu.
            "nav-link": { # Style des liens de navigation.
                "font-size": "20px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e3f2fd",
            },
            "nav-link-selected": {"background-color": "#1976d2", "color": "white"}, # Style du lien sélectionné.
        }
    )
    st.session_state["selected_page"] = selected # Met à jour la page sélectionnée dans st.session_state.

# --- ROUTAGE DES PAGES EN FONCTION DE LA SÉLECTION DU MENU ---
# Cette section est le cœur de l'application, déterminant quel contenu de page afficher
# en fonction de l'option sélectionnée dans le menu de navigation latéral.
if selected == t["home"]:
    # --- PAGE D'ACCUEIL ---
    # Cette page fournit une introduction à l'application, des métriques globales de la pandémie
    # et une carte interactive affichant les cas par pays.
    st.markdown(f"""
        <div style='text-align:center; margin-top: 30px;'>
            <img src='logo-pandemia.png' width='100'/>
            <h1 style='color:#1976d2; margin-bottom:0; font-size:2.5rem;'>{t['welcome']}</h1>
            <h3 style='color:#388e3c; margin-top:0; font-size:1.7rem;'>{t['subtitle']}</h3>
            <p style='font-size:1.2rem; color:#444;'>{t['desc']}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    # Création de trois colonnes pour présenter les fonctionnalités clés de l'application avec des icônes et des descriptions.
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        st.markdown(f"""
            <div style='background:#e3f2fd;border-radius:16px;padding:2rem 1rem;box-shadow:0 2px 8px #1976d220;'>
                <img src='https://img.icons8.com/ios-filled/100/1976d2/activity-history.png' width='48'/><br>
                <h4 style='color:#1976d2; font-size:1.3rem;'>{t['realtime']}</h4>
                <p style='color:#388e3c; font-size:1.1rem;'>{t['realtime_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    with fcol2:
        st.markdown(f"""
            <div style='background:#e8f5e9;border-radius:16px;padding:2rem 1rem;box-shadow:0 2px 8px #388e3c20;'>
                <img src='https://img.icons8.com/ios-filled/100/1976d2/robot-2.png' width='48'/><br>
                <h4 style='color:#1976d2; font-size:1.3rem;'>{t['ai_pred']}</h4>
                <p style='color:#388e3c; font-size:1.1rem;'>{t['ai_pred_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    with fcol3:
        st.markdown(f"""
            <div style='background:#fff;border-radius:16px;padding:2rem 1rem;box-shadow:0 2px 8px #1976d220;'>
                <img src='https://img.icons8.com/ios-filled/100/1976d2/health-checkup.png' width='48'/><br>
                <h4 style='color:#1976d2; font-size:1.3rem;'>{t['support']}</h4>
                <p style='color:#388e3c; font-size:1.1rem;'>{t['support_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Récupérer toutes les données pour la vue globale depuis le backend via l'API /data.
    global_data = get_with_auth("/data")

    if global_data:
        df_global = pd.DataFrame(global_data) # Convertit les données en DataFrame Pandas.
        df_global["date"] = pd.to_datetime(df_global["date"]) # Convertit la colonne de date au format datetime.

        # Calculer les métriques globales : total des cas confirmés et nombre de pays suivis.
        total_global_cases = int(df_global["confirmed"].sum()) if not df_global.empty else 0
        num_countries = df_global["country"].nunique() if not df_global.empty else 0

        st.markdown(f"<h3 style='text-align:center; color:#1976d2; font-size:1.8rem;'>{t['global_cases']}</h3>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.metric(t["global_cases"], f"{total_global_cases:,}") # Affiche le nombre total de cas mondiaux.
        with col_g2:
            st.metric(t["countries_tracked"], num_countries) # Affiche le nombre de pays suivis.
        st.markdown("---")

        st.markdown(f"<h3 style='text-align:center; color:#1976d2; font-size:1.8rem;'>{t['world_map']} (PyDeck)</h3>", unsafe_allow_html=True)
        
        # Pour la carte du monde, agréger les données par pays à la date la plus récente disponible.
        latest_data_per_country = df_global.loc[df_global.groupby('country')['date'].idxmax()] # Sélectionne la dernière entrée par pays.
        
        # IMPORTANT: Pydeck nécessite des coordonnées de latitude et longitude (lat, lon).
        # Étant donné que le jeu de données actuel ne contient que des noms de pays,
        # nous utilisons ici un dictionnaire de coordonnées approximatives pour une démonstration.
        # Pour une représentation géographique précise et complète, l'intégration d'un fichier GeoJSON
        # de centroïdes de pays ou l'utilisation d'une API de géocodage serait nécessaire.
        country_coords = {
            "France": (46.603354, 1.888334),
            "US": (37.09024, -95.712891),
            "Switzerland": (46.818188, 8.227512),
            "Afghanistan": (33.93911, 67.709953),
            "Albania": (41.153332, 20.168331),
            "Algeria": (28.033886, 1.659626),
            "Andorra": (42.546245, 1.601554),
            "Angola": (-11.202692, 17.873887),
            "Argentina": (-38.416097, -63.616672),
            "Australia": (-25.274398, 133.775136),
            "Austria": (47.516231, 14.550072),
            "Brazil": (-14.235004, -51.92528),
            "Canada": (56.130366, -106.346771),
            "China": (35.86166, 104.195397),
            "India": (20.593684, 78.96288),
            "Russia": (61.52401, 105.318756),
            "Germany": (51.165691, 10.451526),
            "United Kingdom": (55.378051, -3.435973),
            "Italy": (41.87194, 12.56738),
            "Spain": (40.463667, -3.74922),
            "Mexico": (23.634501, -102.552784),
            "South Africa": (-30.559482, 22.937506),
            "Egypt": (26.820553, 30.802498),
            "Nigeria": (9.081999, 8.675277),
            "Japan": (36.204824, 138.252924),
            "South Korea": (35.907757, 127.766922),
            "Indonesia": (-0.789275, 113.921327),
            "Pakistan": (30.37532, 69.345116),
            "Bangladesh": (23.684994, 90.356331),
            "Philippines": (12.879721, 121.774017),
            "Turkey": (38.963745, 35.243322),
            "Iran": (32.427908, 53.688046),
            "Colombia": (4.570868, -74.297333),
            "Peru": (-9.189967, -75.015152),
            "Chile": (-35.675147, -71.542969),
            "Sweden": (60.128161, 18.643501),
            "Norway": (60.472024, 8.468946),
            "Denmark": (56.26392, 9.501785),
            "Finland": (61.92411, 25.748151),
            "Estonia": (58.595272, 25.013607),
            "Latvia": (56.879635, 24.603189),
            "Lithuania": (55.169438, 23.881275),
            "Poland": (51.919438, 19.145136),
            "Czechia": (49.817492, 15.472962),
            "Slovakia": (48.669026, 19.699024),
            "Hungary": (47.162494, 19.503304),
            "Romania": (45.943161, 24.96676),
            "Bulgaria": (42.733883, 25.48583),
            "Croatia": (45.1, 15.2),
            "Serbia": (44.016521, 21.005859),
            "Bosnia and Herzegovina": (43.915886, 17.679076),
            "Montenegro": (42.708677, 19.37439),
            "Kosovo": (42.602636, 20.902977),
            "Albania": (41.153332, 20.168331),
            "North Macedonia": (41.608635, 21.745275),
            "Greece": (39.074208, 21.824312),
            "Turkey": (38.963745, 35.243322),
            "Cyprus": (35.126413, 33.429859),
            "Malta": (35.937496, 14.375416),
            "Luxembourg": (49.815273, 6.129583),
            "Austria": (47.516231, 14.550072),
            "Slovenia": (46.151241, 14.995463),
            "Liechtenstein": (47.166, 9.555),
            "San Marino": (43.94236, 12.457777),
            "Vatican City": (41.902916, 12.453389),
            "Monaco": (43.733333, 7.416667),
            "Andorra": (42.546245, 1.601554),
            "Gibraltar": (36.137741, -5.345374),
            "Faroe Islands": (61.892635, -6.911805),
            "Greenland": (71.706936, -42.604303),
            "Puerto Rico": (18.220833, -66.590149),
            "Guadeloupe": (16.265, -61.551),
            "Martinique": (14.641528, -61.024174),
            "French Guiana": (3.933889, -53.125782),
            "Reunion": (-21.115143, 55.536384),
            "Mayotte": (-12.8275, 45.166244),
            "New Caledonia": (-20.904305, 165.618042),
            "French Polynesia": (-17.6797, -149.4068),
            "Wallis and Futuna": (-13.7687, -177.156),
            "Saint Pierre and Miquelon": (46.8852, -56.3159),
            "Saint Barthélemy": (17.9, -62.83),
            "Saint Martin": (18.07, -63.05),
            "Saint Helena": (-15.965, -5.707),
            "Falkland Islands": (-51.796253, -59.523613),
            "South Georgia and South Sandwich Islands": (-54.4295, -36.5879),
            "Norfolk Island": (-29.0408, 167.9547),
            "Christmas Island": (-10.4475, 105.6904),
            "Cocos (Keeling) Islands": (-12.1642, 96.871),
            "Pitcairn Islands": (-25.0667, -130.1),
            "Turks and Caicos Islands": (21.694, -71.7979),
            "British Virgin Islands": (18.4207, -64.6399),
            "Cayman Islands": (19.3133, -81.2546),
            "Anguilla": (18.2206, -63.0686),
            "Montserrat": (16.7425, -62.1873),
            "Bermuda": (32.3078, -64.7505),
            "Guam": (13.4443, 144.7937),
            "American Samoa": (-14.271, -170.132),
            "Northern Mariana Islands": (15.0979, 145.3855),
            "United States Minor Outlying Islands": (19.2833, 166.6),
            "U.S. Virgin Islands": (17.7333, -64.95),
            "Hong Kong": (22.3193, 114.1694),
            "Macau": (22.1667, 113.55),
            "Taiwan": (23.6978, 120.9605),
            "South Sudan": (6.877, 31.307),
            "Somalia": (10.0275, 49.3138),
            "Eritrea": (15.179384, 39.782334),
            "Djibouti": (11.825138, 42.590275),
            "" : (0,0) # Placeholder for empty/unknown country
        }

        # Filtre les données des pays pour n'inclure que ceux pour lesquels des coordonnées sont définies.
        countries_with_coords = [c for c in latest_data_per_country['country'].unique() if c in country_coords]
        df_map_data = latest_data_per_country[latest_data_per_country['country'].isin(countries_with_coords)].copy()
        
        # Assigne les coordonnées de latitude et longitude au DataFrame pour PyDeck.
        df_map_data['lat'] = df_map_data['country'].apply(lambda x: country_coords.get(x, (0,0))[0])
        df_map_data['lon'] = df_map_data['country'].apply(lambda x: country_coords.get(x, (0,0))[1])
        
        # Adapte la taille du rayon des points sur la carte en fonction du nombre de cas confirmés.
        # Une taille de base est ajoutée pour que même les pays avec peu de cas soient visibles.
        max_confirmed = df_map_data['confirmed'].max()
        if max_confirmed > 0:
            # Échelle le rayon pour une meilleure visibilité, avec un rayon de base.
            df_map_data['radius'] = (df_map_data['confirmed'] / max_confirmed) * 50000 + 5000 
        else:
            df_map_data['radius'] = 5000 # Rayon par défaut si aucun cas n'est enregistré.

        # Crée l'état initial de la vue de la carte PyDeck.
        view_state = pdk.ViewState(
            latitude=0, # Centre la carte sur l'équateur (latitude 0).
            longitude=0,
            zoom=1, # Niveau de zoom initial, montrant une vue globale.
            pitch=0,
        )

        # Définit la couche de points (ScatterplotLayer) pour la carte PyDeck.
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map_data,
            get_position="[lon, lat]", # Spécifie les colonnes pour les positions longitude et latitude.
            get_color="[255, 140, 0, 160]", # Définit la couleur des points (orange avec transparence).
            get_radius="radius", # Utilise la colonne 'radius' calculée pour la taille des points.
            pickable=True, # Rend les points interactifs (infos-bulles au survol/clic).
            auto_highlight=True, # Active le surlignage automatique des points au survol.
        )

        # Affiche la carte PyDeck dans l'application Streamlit avec un thème sombre.
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10", # Utilise un style de carte sombre de Mapbox.
            initial_view_state=view_state,
            layers=[layer],
        ))
    else:
        st.info(t["no_data"]) # Affiche un message si aucune donnée n'est disponible pour la carte.

    st.markdown("""
    <div style='text-align:center; margin-top: 30px;'>
        <h2 style='color:#1976d2; font-size:2rem;'>Qui sommes-nous ?</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write(f"<p style='font-size:1.1rem; text-align:center;'>{t['team_desc']}</p>", unsafe_allow_html=True)

    # Section de présentation de l'équipe (composée de 4 colonnes pour chaque membre).
    col_team1, col_team2, col_team3, col_team4 = st.columns(4)
    with col_team1:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown("<p style='text-align:center;'><b>Anas</b><br/>Développeur IA</p>", unsafe_allow_html=True)
    with col_team2:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown("<p style='text-align:center;'><b>Laura</b><br/>Développeur fullstack & Devops</p>", unsafe_allow_html=True)
    with col_team3:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown("<p style='text-align:center;'><b>Akram</b><br/>Développeur Devops</p>", unsafe_allow_html=True)
    with col_team4:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.markdown("<p style='text-align:center;'><b>Romance</b><br/>Développeur fullstack</p>", unsafe_allow_html=True)

    st.markdown("---")
    # Affichage d'informations spécifiques au pays sélectionné (règles RGPD) en bas de la page d'accueil.
    if st.session_state["country"] == "France":
        st.info("🇫🇷 Les données affichées couvrent l'ensemble du territoire français.")
    elif st.session_state["country"] == "Switzerland":
        st.info("🇨🇭 Les données affichées couvrent l'ensemble du territoire suisse.")
    elif st.session_state["country"] == "US":
        st.info("🇺🇸 Les données affichées couvrent l'ensemble du territoire américain.")

elif selected == t["login"]:
    # --- PAGE DE CONNEXION / INSCRIPTION ---
    # Cette page gère l'authentification des utilisateurs, leur permettant de se connecter
    # à un compte existant ou d'en créer un nouveau.
    st.markdown(f"<h2 style='font-size:2.2rem;'>{t['login_title']}</h2>", unsafe_allow_html=True)
    # Crée deux onglets pour la navigation entre les formulaires de connexion et d'inscription.
    tab1, tab2 = st.tabs([t["login"], t["register_tab"]])
    with tab1:
        # Formulaire de connexion.
        username = st.text_input(t["username"])
        password = st.text_input(t["password"], type="password")
        if st.button(t["login_btn"]):
            # Tente de se connecter en utilisant la fonction `login` du module `auth`.
            if login(username, password): 
                st.session_state["logged_in"] = True # Met à jour l'état de connexion dans st.session_state.
                st.experimental_rerun() # Recharge l'application pour refléter le nouvel état (ex: affichage de nouvelles options de menu).
    with tab2:
        # Formulaire d'inscription.
        username = st.text_input(f"{t['username']} ({t['register_tab']})")
        email = st.text_input(t["email"])
        password = st.text_input(f"{t['password']} ({t['register_tab']})", type="password")
        country_register = st.selectbox(f"{t['country']} ({t['register_tab']})", ["France", "Switzerland", "US"], key="country_register")
        if st.button(t["register_btn"]):
            # Tente d'enregistrer un nouvel utilisateur via la fonction `register` du module `auth`.
            if register(username, email, password, country_register): 
                st.success(t["register_success"]) # Message de succès si l'inscription est réussie.
                st.experimental_rerun()
            else:
                st.error(t["register_error"]) # Message d'erreur en cas d'échec de l'inscription.
    # Affiche un bouton de déconnexion si l'utilisateur est connecté (vérifié par la présence d'un token).
    if get_token():
        if st.button(t["logout"]):
            logout() # Appelle la fonction de déconnexion.
            st.success(t["disconnect"]) # Message de confirmation de déconnexion.
            st.experimental_rerun()

elif selected == t["data"]:
    # --- PAGE DONNÉES HISTORIQUES ---
    # Cette page est dédiée à la visualisation des données historiques de la pandémie COVID-19
    # sous forme de graphiques interactifs pour le pays sélectionné.
    st.markdown(f"<h2 style='font-size:2.2rem;'>{t['data_title']}</h2>", unsafe_allow_html=True)
    token = get_token()
    if not token:
        st.warning(t["connect_warn"]) # Avertit l'utilisateur s'il n'est pas connecté, car l'accès aux données nécessite une authentification.
    else:
        country_selected = st.session_state["country"] # Récupère le pays sélectionné par l'utilisateur dans la sidebar.
        # Récupère les données historiques pour le pays sélectionné via l'API /data.
        data = get_with_auth("/data", params={"country": country_selected}) 
        if data:
            df = pd.DataFrame(data) # Convertit les données JSON reçues en un DataFrame Pandas.
            df["date"] = pd.to_datetime(df["date"]) # Convertit la colonne 'date' au format datetime pour des opérations basées sur le temps.
            
            # ===============================================
            # 1. Cas confirmés vs Taux de mortalité (Graphique en barres et ligne)
            # Ce graphique illustre l'évolution des cas confirmés (barres) et du taux de mortalité (ligne) au fil du temps.
            # Il permet d'identifier visuellement les pics de contamination et leur corrélation avec la mortalité.
            # ===============================================
            st.subheader("📈 " + t["value_dist"]) # Titre du sous-graphique.

            fig1 = go.Figure() # Initialise une nouvelle figure Plotly.

            # Ajoute une trace en barres pour les cas confirmés.
            fig1.add_trace(go.Bar(
                x=df["date"],
                y=df["confirmed"],
                name=t["confirmed"],
                marker=dict(color='cyan'),
                yaxis='y1'
            ))

            # Ajoute une trace en ligne pour le taux de mortalité.
            fig1.add_trace(go.Scatter(
                x=df["date"],
                y=(df["deaths"] / df["confirmed"] * 100).fillna(0), # Calcul du taux de mortalité (décès / cas confirmés * 100). Gère les NaN si confirmed est 0.
                name=t["death_rate"],
                yaxis='y2',
                mode='lines',
                line=dict(color='pink')
            ))

            # Configure le layout du premier graphique : titres des axes, couleurs de fond, et position de la légende.
            fig1.update_layout(
                xaxis=dict(title=t["date"]),
                yaxis=dict(title=t["confirmed"], side='left'),
                yaxis2=dict(title=t["death_rate"] + " (%)", overlaying='y', side='right'),
                bargap=0.1,
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                legend=dict(x=0.01, y=0.99)
            )

            st.plotly_chart(fig1, use_container_width=True) # Affiche le premier graphique dans Streamlit.

            # ===============================================
            # 2. Nouveaux cas vs Taux de guérison (Graphique en barres et ligne)
            # Ce graphique visualise les nouveaux cas quotidiens (barres) et le taux de guérison (ligne).
            # Il est utile pour comprendre la dynamique de propagation de la maladie et l'efficacité des traitements/récupérations.
            # ===============================================
            st.subheader("📈 " + t["new_cases"] + " vs " + t["recovery_rate"])

            fig2 = go.Figure()

            fig2.add_trace(go.Bar(
                x=df["date"],
                y=df["new_cases"],
                name=t["new_cases"],
                marker=dict(color='cyan'),
                yaxis='y1'
            ))

            fig2.add_trace(go.Scatter(
                x=df["date"],
                y=(df["recovered"] / df["confirmed"] * 100).fillna(0),
                name=t["recovery_rate"],
                yaxis='y2',
                mode='lines',
                line=dict(color='pink')
            ))

            fig2.update_layout(
                xaxis=dict(title=t["date"]),
                yaxis=dict(title=t["new_cases"], side='left'),
                yaxis2=dict(title=t["recovery_rate"] + " (%)", overlaying='y', side='right'),
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                legend=dict(x=0.01, y=0.99)
            )

            st.plotly_chart(fig2, use_container_width=True)

            # ===============================================
            # 3. Vue d'ensemble des cas (Mini-graphique de tendance)
            # Un aperçu simple des tendances cumulatives des cas confirmés et des décès au fil du temps.
            # ===============================================
            st.subheader("📉 " + t["cases_overview"])

            fig3 = go.Figure()

            fig3.add_trace(go.Scatter(
                x=df["date"],
                y=df["confirmed"],
                name=t["confirmed"],
                line=dict(color='magenta')
            ))

            fig3.add_trace(go.Scatter(
                x=df["date"],
                y=df["deaths"],
                name=t["deaths"],
                yaxis='y2',
                line=dict(color='pink')
            ))

            fig3.update_layout(
                xaxis=dict(title=t["date"]),
                yaxis=dict(title=t["confirmed"]),
                yaxis2=dict(title=t["deaths"], overlaying='y', side='right'),
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white')
            )

            st.plotly_chart(fig3, use_container_width=True)

            # ===============================================
            # 4. Vue d'ensemble des métriques (Cartes de métriques et mini-graphiques cumulatifs)
            # Affiche les métriques clés (total des cas confirmés, décès, guéris)
            # accompagnées de petits graphiques montrant leur tendance cumulative.
            # ===============================================
            st.subheader("📊 " + t["metrics_overview"])
            col1, col2, col3 = st.columns(3) # Crée trois colonnes pour organiser les métriques.

            with col1:
                total_confirmed = int(df["confirmed"].sum()) # Calcule le total des cas confirmés sur toute la période.
                st.metric(label=t["total_confirmed"], value=f"{total_confirmed:,}") # Affiche la métrique.
                fig4 = go.Figure(go.Scatter(
                    x=df["date"],
                    y=df["confirmed"].cumsum(), # Trace la tendance cumulative des cas confirmés.
                    line=dict(color='lightgreen')
                ))
                fig4.update_layout(
                    height=250,
                    paper_bgcolor='black',
                    plot_bgcolor='black',
                    font=dict(color='white')
                )
                st.plotly_chart(fig4, use_container_width=True)

            with col2:
                total_deaths = int(df["deaths"].sum()) # Calcule le total des décès sur toute la période.
                st.metric(label=t["total_deaths"], value=f"{total_deaths:,}") # Affiche la métrique.
                fig5 = go.Figure(go.Scatter(
                    x=df["date"],
                    y=df["deaths"].cumsum(), # Trace la tendance cumulative des décès.
                    line=dict(color='lightyellow')
                ))
                fig5.update_layout(
                    height=250,
                    paper_bgcolor='black',
                    plot_bgcolor='black',
                    font=dict(color='white')
                )
                st.plotly_chart(fig5, use_container_width=True)

            with col3:
                total_recovered = int(df["recovered"].sum()) # Calcule le total des guéris sur toute la période.
                st.metric(label=t["total_recovered"], value=f"{total_recovered:,}") # Affiche la métrique.
                fig6 = go.Figure(go.Scatter(
                    x=df["date"],
                    y=df["recovered"].cumsum(), # Trace la tendance cumulative des guéris.
                    line=dict(color='lightblue')
                ))
                fig6.update_layout(
                    height=250,
                    paper_bgcolor='black',
                    plot_bgcolor='black',
                    font=dict(color='white')
                )
                st.plotly_chart(fig6, use_container_width=True)

        else:
            st.error(t["data_error"]) # Gère l'erreur si les données ne peuvent pas être récupérées pour le pays sélectionné.
    # Affiche le pays actuellement sélectionné pour la page de données à des fins d'information utilisateur.
    st.markdown(f"<div style='text-align:right; color:#1976d2; font-size:1.1rem;'><b>Pays sélectionné : {st.session_state['country']}</b></div>", unsafe_allow_html=True)
    # Affiche des informations spécifiques au pays concernant la couverture des données (règles RGPD).
    if st.session_state["country"] == "France":
        st.info("🇫🇷 Les données affichées couvrent l'ensemble du territoire français.")
    elif st.session_state["country"] == "Switzerland":
        st.info("🇨🇭 Les données affichées couvrent l'ensemble du territoire suisse.")
    elif st.session_state["country"] == "US":
        st.info("🇺🇸 Les données affichées couvrent l'ensemble du territoire américain.")

elif selected == t["predict"]:
    # --- PAGE PRÉDICTION IA ---
    # Cette page permet aux utilisateurs d'interagir avec le modèle de prédiction IA pour anticiper
    # le nombre de cas confirmés pour un pays et une date future donnés.
    st.markdown(f"<h2 style='font-size:2.2rem;'>{t['predict_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:1.1rem; color:#888;'>{t['ai_pred_desc']}</p>", unsafe_allow_html=True)
    token = get_token()
    if not token:
        st.warning(t["predict_warn"]) # Avertit l'utilisateur si la connexion est requise pour accéder à la prédiction.
    else:
        st.info("Veuillez entrer les paramètres de prédiction pour obtenir le nombre de cas confirmés pour un pays spécifique.")
        
        # Récupérer la liste de tous les pays disponibles pour la prédiction depuis l'API.
        # Cela garantit que le sélecteur de pays contient tous les pays pertinents du jeu de données,
        # et non seulement ceux définis par les règles RGPD en sidebar.
        all_data = get_with_auth("/data")
        if all_data:
            df_all = pd.DataFrame(all_data)
            available_countries = sorted(df_all['country'].unique().tolist()) # Crée une liste unique et triée des pays.
            
            # Le formulaire de prédiction est encapsulé dans un conteneur pour une meilleure présentation et isolation UI.
            with st.container(border=True):
                with st.form("prediction_form"):
                    # Sélecteur de pays pour la prédiction. La liste des options est dynamique.
                    country_predict = st.selectbox(t["country"],
                                                available_countries,
                                                key="predict_country_select")
                    # Sélecteur de date pour la prédiction, avec la date du jour comme valeur par défaut.
                    future_date = st.date_input(t["date"], value=date.today(), key="prediction_date_input")
                    # Bouton de soumission du formulaire pour lancer la prédiction.
                    submitted = st.form_submit_button(t["predict_btn"], use_container_width=True)
                
                # Logique exécutée après la soumission du formulaire de prédiction.
                if submitted:
                    with st.spinner("Prédiction en cours..."): # Affiche un indicateur de chargement pour l'utilisateur.
                        # Construction du payload (corps de la requête) pour l'API de prédiction.
                        prediction_payload = {
                            "country": country_predict,
                            "future_date": str(future_date)
                        }
                        # Envoie la requête POST au backend pour obtenir la prédiction.
                        result = post_with_auth("/predict", prediction_payload) 
                    # Affiche les résultats de la prédiction ou un message d'erreur si la prédiction échoue.
                    if result:
                        st.success("Prédiction terminée !")
                        st.subheader(t["result"])
                        st.write(f"**Pays :** {country_predict}")
                        st.write(f"**Date de prédiction :** {future_date}")
                        st.write(f"**{t['result']} :** {result['prediction']:.2f}")
                        st.write(f"**{t['score']} :** {result['score']:.2f}")
                    else:
                        st.error(t["predict_error"]) # Message d'erreur si la prédiction a échoué.
        else:
            st.error(t["data_error"]) # Gère l'erreur si les données des pays ne peuvent pas être récupérées pour le sélecteur de prédiction.

# --- FIN DU FICHIER APP.PY --- 