# MASCIR-CHATBOT-

Voici le contenu complet du fichier `README.md` en une seule grille de code :

```markdown
# Chatbot Assistant avec GPT-4 et Reconnaissance Vocale

Ce projet implémente un chatbot assistant utilisant GPT-4 et la reconnaissance vocale pour interagir avec les utilisateurs. Il comprend des fonctionnalités telles que la gestion des informations utilisateur, la collecte de données de santé, et la vérification de la prise de médicaments.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration de la Base de Données](#configuration-de-la-base-de-données)
4. [Configuration de l'Environnement](#configuration-de-lenvironnement)
5. [Installation des Dépendances](#installation-des-dépendances)
6. [Téléchargement et Paramétrage de PostgreSQL](#téléchargement-et-paramétrage-de-postgresql)
7. [Utilisation](#utilisation)
8. [Contribuer](#contribuer)

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :
- [Python](https://www.python.org/downloads/) (version 3.7 ou ultérieure)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [PostgreSQL](https://www.postgresql.org/download/) (voir section Téléchargement et Paramétrage de PostgreSQL)

## Installation

1. **Cloner le Dépôt**

   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-depot.git
   cd nom-du-depot
   ```

## Configuration de la Base de Données

1. **Créer la Base de Données et les Tables**

   Connectez-vous à PostgreSQL et exécutez les commandes SQL suivantes pour créer la base de données et les tables nécessaires.

   ```sql
   -- Créer la base de données
   CREATE DATABASE "Chat-Mascir";

   -- Connexion à la base de données
   \c "Chat-Mascir";

   -- Créer la table des utilisateurs âgés
   CREATE TABLE ElderlyUsers (
       id SERIAL PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50),
       age INTEGER,
       gender VARCHAR(10),
       room_number VARCHAR(10),
       medical_conditions TEXT,
       allergies TEXT,
       caregiver_contact TEXT,
       emergency_contact_name VARCHAR(50),
       emergency_contact_number VARCHAR(20)
   );

   -- Créer la table des informations de médication
   CREATE TABLE MedicationInfo (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES ElderlyUsers(id),
       medication_name VARCHAR(100),
       dosage VARCHAR(50),
       time_taken TIME,
       date_taken DATE
   );

   -- Créer la table des informations de santé
   CREATE TABLE HealthInfo (
       id SERIAL PRIMARY KEY,
       user_id INTEGER REFERENCES ElderlyUsers(id),
       physical_state TEXT,
       mental_state TEXT,
       last_meal_time TIME,
       meal_content TEXT
   );
   ```

## Configuration de l'Environnement

1. **Créer un Environnement Virtuel**

   ```bash
   python -m venv venv
   ```

2. **Activer l'Environnement Virtuel**

   - Sur Windows :
     ```bash
     venv\Scripts\activate
     ```

   - Sur macOS/Linux :
     ```bash
     source venv/bin/activate
     ```

## Installation des Dépendances

1. **Installer les Dépendances avec `pip`**

   Créez un fichier `requirements.txt` avec les dépendances suivantes :

   ```
   openai
   pygame
   SpeechRecognition
   psycopg2-binary
   ```

   Ensuite, installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

## Téléchargement et Paramétrage de PostgreSQL

1. **Télécharger PostgreSQL**

   Téléchargez PostgreSQL depuis [le site officiel](https://www.postgresql.org/download/) et suivez les instructions d'installation pour votre système d'exploitation.

2. **Configurer PostgreSQL**

   - Lors de l'installation, vous devrez définir un mot de passe pour l'utilisateur `postgres`.
   - Ouvrez pgAdmin ou utilisez la ligne de commande pour créer une base de données comme décrit dans la section Configuration de la Base de Données.

## Utilisation

1. **Démarrer le Bot**

   Assurez-vous que votre environnement virtuel est activé et que les dépendances sont installées. Ensuite, exécutez le script principal :

   ```bash
   python votre_script.py
   ```

2. **Interagir avec le Bot**

   Suivez les instructions affichées pour interagir avec le bot. Vous pourrez entrer vos informations et poser des questions au chatbot.

