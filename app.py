import streamlit as st
import pandas as pd
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import DEFAULT_BODY, DEFAULT_EMAIL_TOPIC

# Configuration de la page
st.set_page_config(page_title="Email Bulk Sender", page_icon="📧")

st.title("📧 Envoi d'emails en masse")
st.markdown("Chargez un fichier Excel, rédigez votre message et envoyez-le à tous vos contacts.")

# --- BARRE LATÉRALE : CONFIGURATION SMTP ---
with st.sidebar:
    st.header("⚙️ Configuration SMTP")
    st.info("Utilisez un mot de passe d'application si vous utilisez Gmail.")
    smtp_server = st.text_input("Serveur SMTP", value="smtp.gmail.com")
    smtp_port = st.number_input("Port SMTP", value=587)
    sender_email = st.text_input("Votre Email (Expéditeur)")
    sender_password = st.text_input("Votre Mot de passe", type="password")
    
    st.divider()
    st.caption("Note : Vos identifiants ne sont pas stockés.")

# --- ÉTAPE 1 : CHARGEMENT DU FICHIER ---
st.subheader("1. Importation des contacts")
uploaded_file = st.file_uploader("Choisissez un fichier Excel (.xlsx)", type="xlsx")

emails_list = []
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Aperçu des données :")
    st.dataframe(df.head())
    
    col_options = df.columns.tolist()
    email_column = st.selectbox("Sélectionnez la colonne contenant les emails", col_options)
    first_name_column = st.selectbox("Sélectionnez la colonne contenant les prénoms", col_options)
    family_name_column = st.selectbox("Sélectionnez la colonne contenant les noms de famille", col_options)
    emails_list = df[email_column].dropna().unique().tolist()
    first_name_list = df.loc[df[email_column].isin(emails_list), first_name_column].to_list()
    family_name_list = df.loc[df[email_column].isin(emails_list), family_name_column].to_list()
    
    st.success(f"✅ {len(emails_list)} adresses emails trouvées.")

# --- ÉTAPE 2 : RÉDACTION DE L'EMAIL ---
st.subheader("2. Rédaction du Template")
email_subject = st.text_input("Objet de l'email", value=DEFAULT_EMAIL_TOPIC, placeholder=DEFAULT_EMAIL_TOPIC)
email_body = st.text_area("Corps du message", height=200, value=DEFAULT_BODY, placeholder=DEFAULT_BODY)


# --- ÉTAPE 3 : ENVOI ---
st.subheader("3. Expédition")

if st.button("🚀 Envoyer les emails"):
    if not emails_list:
        st.error("Veuillez charger un fichier avec des adresses valides.")
    elif not sender_email or not sender_password:
        st.error("Veuillez configurer vos identifiants SMTP dans la barre latérale.")
    elif not email_subject or not email_body:
        st.error("L'objet ou le corps de l'email est vide.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        success_count = 0
        error_count = 0

        try:
            # Connexion au serveur
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)

            for i, recipient in enumerate(emails_list):
                try:
                    # Création du message
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient
                    msg['Subject'] = email_subject
                    email_body=email_body.replace("<FIRST_NAME>", first_name_list[i])
                    email_body=email_body.replace("<FAMILY_NAME>", family_name_list[i])
                    msg.attach(MIMEText(email_body, 'plain'))

                    # Envoi
                    server.send_message(msg)
                    success_count += 1
                    
                    
                    time.sleep(0.1)    # Pause 0.1 seconds
                    
                except Exception as e:
                    st.error(f"Erreur pour {recipient}: {e}")
                    error_count += 1
                
                # Mise à jour de la progression
                progress = (i + 1) / len(emails_list)
                progress_bar.progress(progress)
                status_text.text(f"Envoi à {recipient} ({i+1}/{len(emails_list)})")

            server.quit()
            st.balloons()
            st.success(f"Terminé ! {success_count} emails envoyés avec succès, {error_count} échecs.")

        except Exception as e:
            st.error(f"Erreur de connexion au serveur SMTP : {e}")