import os
import openai
import speech_recognition as sr
from pygame import mixer
import psycopg2
from datetime import datetime

# Clé d'API OpenAI
openai.api_key = 'WRITE_Your_OPENAI_Key'
client = openai.OpenAI(api_key=openai.api_key)

# Informations de connexion à la base de données PostgreSQL
dbname = "Chat-Mascir"
user = "postgres"
password = "SELOHeco1"
host = "localhost"

# Connexion à la base de données PostgreSQL
try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    print("Connexion à la base de données réussie.")
except psycopg2.Error as e:
    print("Erreur lors de la connexion à la base de données:", e)

# Création du recognizer pour la reconnaissance vocale
r = sr.Recognizer()

# Langue pour la reconnaissance vocale
language = "fr-FR"

# Classe pour gérer la reconnaissance vocale et la synthèse vocale
class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.language = "fr-FR"
    
    def asr(self):
        with sr.Microphone() as source:
            print("Veuillez parler maintenant.")
            audio = self.recognizer.listen(source)

        try:
            user_input = self.recognizer.recognize_google(audio, language=self.language)
            print("Vous avez dit: " + user_input)
            return user_input
        except sr.UnknownValueError:
            print("La reconnaissance vocale n'a pas pu comprendre l'audio.")
            return None
        except sr.RequestError as e:
            print(f"Erreur lors de la requête à Google Speech Recognition service: {e}")
            return None
    
    def tts(self, output):
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=output,
        )
        name_file = "output.mp3"
        response.stream_to_file(name_file)

        mixer.init()
        mixer.music.load(name_file)
        mixer.music.play()

        while mixer.music.get_busy():
            pass

        mixer.music.stop()
        mixer.music.unload()
        mixer.quit()

        os.remove(name_file)

# Classe pour gérer les interactions avec la base de données
class DatabaseManager:
    def __init__(self, connection):
        self.conn = connection
    
    def check_user_in_db(self, first_name, last_name):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM ElderlyUsers WHERE first_name = %s AND last_name = %s", (first_name, last_name))
            users = cur.fetchall()
            cur.close()
            return users
        except psycopg2.Error as e:
            print("Erreur lors de la vérification de l'utilisateur dans la base de données:", e)
            return None
    
    def check_room_number(self, first_name, last_name, room_number):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM ElderlyUsers WHERE first_name = %s AND last_name = %s AND room_number = %s", (first_name, last_name, room_number))
            user = cur.fetchone()
            cur.close()
            return user
        except psycopg2.Error as e:
            print("Erreur lors de la vérification du numéro de chambre:", e)
            return None
    
    def insert_health_info(self, first_name, last_name, physical_state, mental_state, last_meal_time, meal_content):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO HealthInfo (first_name, last_name, physical_state, mental_state, last_meal_time, meal_content)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, physical_state, mental_state, last_meal_time, meal_content))
            self.conn.commit()
            cur.close()
            print("Informations de santé enregistrées avec succès.")
            return True
        except psycopg2.Error as e:
            print("Erreur lors de l'enregistrement des informations de santé:", e)
            return False
    
    def insert_user_info(self, first_name, last_name, age, gender, room_number, medical_conditions, allergies, caregiver_contact, emergency_contact_name, emergency_contact_number):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO ElderlyUsers (first_name, last_name, age, gender, room_number, medical_conditions, allergies, caregiver_contact, emergency_contact_name, emergency_contact_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, age, gender, room_number, medical_conditions, allergies, caregiver_contact, emergency_contact_name, emergency_contact_number))
            self.conn.commit()
            cur.close()
            print("Informations utilisateur enregistrées avec succès.")
            return True
        except psycopg2.Error as e:
            print("Erreur lors de l'enregistrement des informations utilisateur:", e)
            return False
    
    def insert_medication_info(self, first_name, last_name, medication_name, dose_taken, medication_time):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO MedicationInfo (first_name, last_name, medication_name, dose_taken, medication_time)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, medication_name, dose_taken, medication_time))
            self.conn.commit()
            cur.close()
            print("Informations sur la prise de médicaments enregistrées avec succès.")
            return True
        except psycopg2.Error as e:
            print("Erreur lors de l'enregistrement des informations sur la prise de médicaments:", e)
            return False

    def check_medication_timing(self, first_name, last_name, medication_name, expected_time_range):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT medication_time FROM MedicationInfo 
                WHERE first_name = %s AND last_name = %s AND medication_name = %s
                ORDER BY medication_time DESC LIMIT 1
            """, (first_name, last_name, medication_name))
            result = cur.fetchone()
            cur.close()
            if result:
                last_medication_time = result[0]
                return expected_time_range[0] <= last_medication_time.time() <= expected_time_range[1]
            return False
        except psycopg2.Error as e:
            print("Erreur lors de la vérification du timing de la médication:", e)
            return False

# Classe pour gérer les questions et les interactions avec l'utilisateur
class InteractionManager:
    def __init__(self, voice_assistant, database_manager):
        self.voice_assistant = voice_assistant
        self.database_manager = database_manager
    
    def get_user_input(self, mode):
        if mode == '1':  # Saisie manuelle
            return input("Vous: ").strip()
        elif mode == '2':  # Saisie vocale
            return self.voice_assistant.asr()
        else:
            print("Mode invalide. Utilisez 1 pour saisie manuelle ou 2 pour saisie vocale.")
            return None
    
    def ask_question(self, question, mode):
        print(f"Bot: {question}")
        self.voice_assistant.tts(question)
        user_response = self.get_user_input(mode)
        if user_response is None:
            print("Bot: Je n'ai pas compris. Pouvez-vous répéter, s'il vous plaît ?")
            self.voice_assistant.tts("Je n'ai pas compris. Pouvez-vous répéter, s'il vous plaît ?")
        return user_response
    
    def collect_health_info(self, first_name, last_name, mode):
        print("Bot: Commençons par recueillir quelques informations sur votre état de santé.")
        self.voice_assistant.tts("Commençons par recueillir quelques informations sur votre état de santé.")
        
        physical_state = self.ask_question("Comment vous sentez-vous physiquement aujourd'hui?", mode)
        mental_state = self.ask_question("Comment vous sentez-vous mentalement aujourd'hui?", mode)
        last_meal_time = self.ask_question("À quelle heure avez-vous pris votre dernier repas?", mode)
        meal_content = self.ask_question("Qu'avez-vous mangé lors de votre dernier repas?", mode)
        
        if self.database_manager.insert_health_info(first_name, last_name, physical_state, mental_state, last_meal_time, meal_content):
            self.voice_assistant.tts("Informations de santé enregistrées avec succès.")
        else:
            self.voice_assistant.tts("Erreur lors de l'enregistrement des informations de santé.")
    
    def collect_user_info(self, mode):
        print("Bot: Veuillez entrer vos informations.")
        self.voice_assistant.tts("Veuillez entrer vos informations.")
        
        first_name = self.ask_question("Quel est votre prénom?", mode)
        last_name = self.ask_question("Quel est votre nom de famille?", mode)
        age = self.ask_question("Quel est votre âge?", mode)
        gender = self.ask_question("Quel est votre genre? (H/F)", mode)
        room_number = self.ask_question("Quel est votre numéro de chambre?", mode)
        medical_conditions = self.ask_question("Avez-vous des conditions médicales particulières? Si oui, veuillez les indiquer.", mode)
        allergies = self.ask_question("Avez-vous des allergies? Si oui, veuillez les indiquer.", mode)
        caregiver_contact = self.ask_question("Quel est le numéro de contact de votre soignant?", mode)
        emergency_contact_name = self.ask_question("Quel est le nom de votre contact d'urgence?", mode)
        emergency_contact_number = self.ask_question("Quel est le numéro de contact de votre contact d'urgence?", mode)
        
        if self.database_manager.insert_user_info(first_name, last_name, age, gender, room_number, medical_conditions, allergies, caregiver_contact, emergency_contact_name, emergency_contact_number):
            self.voice_assistant.tts("Informations utilisateur enregistrées avec succès.")
        else:
            self.voice_assistant.tts("Erreur lors de l'enregistrement des informations utilisateur.")
        
        return first_name, last_name
    
    def collect_medication_info(self, first_name, last_name, mode):
        print("Bot: Passons maintenant à la vérification de la prise de vos médicaments.")
        self.voice_assistant.tts("Passons maintenant à la vérification de la prise de vos médicaments.")
        
        medication_name = self.ask_question("Quel est le nom du médicament que vous avez pris aujourd'hui?", mode)
        dose_taken = self.ask_question("Avez-vous pris votre dose quotidienne de ce médicament aujourd'hui? Répondez par oui ou non.", mode).lower() == 'oui'
        
        # Collect the current time when the medication was taken
        medication_time = datetime.now()

        confirmation = self.ask_question("Confirmez-vous que vous avez pris votre dose quotidienne de ce médicament? Répondez par oui ou non.", mode).lower() == 'oui'
        
        if confirmation:
            if self.database_manager.insert_medication_info(first_name, last_name, medication_name, dose_taken, medication_time):
                self.voice_assistant.tts("Informations sur la prise de médicaments enregistrées avec succès.")
            else:
                self.voice_assistant.tts("Erreur lors de l'enregistrement des informations sur la prise de médicaments.")
        else:
            self.voice_assistant.tts("Informations sur la prise de médicaments non enregistrées.")
    
    def check_medication_timing(self, first_name, last_name, medication_name, expected_time_range):
        if self.database_manager.check_medication_timing(first_name, last_name, medication_name, expected_time_range):
            self.voice_assistant.tts("La prise de médicament est dans la plage horaire correcte.")
        else:
            self.voice_assistant.tts("La prise de médicament n'est pas dans la plage horaire correcte.")
    
# Fonction principale du chatbot
def chatbot():
    voice_assistant = VoiceAssistant()
    database_manager = DatabaseManager(conn)
    interaction_manager = InteractionManager(voice_assistant, database_manager)
    
    print("Mode de saisie: (1) Saisie manuelle, (2) Saisie vocale")
    mode = input("Choisissez le mode de saisie: ")

    first_name = interaction_manager.ask_question("Quel est votre prénom?", mode)
    last_name = interaction_manager.ask_question("Quel est votre nom de famille?", mode)

    if database_manager.check_user_in_db(first_name, last_name):
        room_number = interaction_manager.ask_question("Quel est votre numéro de chambre?", mode)
        if database_manager.check_room_number(first_name, last_name, room_number):
            interaction_manager.collect_health_info(first_name, last_name, mode)
            interaction_manager.collect_medication_info(first_name, last_name, mode)
            
            # Example expected time range for medication, can be customized as needed
            expected_time_range = (datetime.strptime("08:00", "%H:%M").time(), datetime.strptime("20:00", "%H:%M").time())
            interaction_manager.check_medication_timing(first_name, last_name, "medication_name_example", expected_time_range)
            
            messages = []

            while True:
                user_input = interaction_manager.ask_question("Comment puis-je vous aider aujourd'hui?", mode)
                if user_input.lower() in ["quitter", "exit", "stop"]:
                    print("Bot: Merci d'avoir utilisé notre service. À bientôt!")
                    voice_assistant.tts("Merci d'avoir utilisé notre service. À bientôt!")
                    break

                messages.append({"role": "user", "content": user_input})
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages
                )
                bot_response = response['choices'][0]['message']['content']
                messages.append({"role": "assistant", "content": bot_response})

                print(f"Bot: {bot_response}")
                voice_assistant.tts(bot_response)
        else:
            print("Bot: Numéro de chambre incorrect.")
            voice_assistant.tts("Numéro de chambre incorrect.")
    else:
        print("Bot: Utilisateur non trouvé. Veuillez entrer vos informations.")
        voice_assistant.tts("Utilisateur non trouvé. Veuillez entrer vos informations.")
        first_name, last_name = interaction_manager.collect_user_info(mode)
        if first_name and last_name:
            interaction_manager.collect_health_info(first_name, last_name, mode)
            interaction_manager.collect_medication_info(first_name, last_name, mode)
            
            # Example expected time range for medication, can be customized as needed
            expected_time_range = (datetime.strptime("08:00", "%H:%M").time(), datetime.strptime("20:00", "%H:%M").time())
            interaction_manager.check_medication_timing(first_name, last_name, "medication_name_example", expected_time_range)
            
            messages = []

            while True:
                user_input = interaction_manager.ask_question("Comment puis-je vous aider aujourd'hui?", mode)
                if user_input.lower() in ["quitter", "exit", "stop"]:
                    print("Bot: Merci d'avoir utilisé notre service. À bientôt!")
                    voice_assistant.tts("Merci d'avoir utilisé notre service. À bientôt!")
                    break

                messages.append({"role": "user", "content": user_input})
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages
                )
                bot_response = response['choices'][0]['message']['content']
                messages.append({"role": "assistant", "content": bot_response})

                print(f"Bot: {bot_response}")
                voice_assistant.tts(bot_response)

# Lancer le chatbot
chatbot()
