# Epic Events CRM

Epic Events CRM est une application de gestion de la relation client réalisé en ligne de commande
et développée en Python pour l'entreprise Epic Events,
spécialisée dans l'organisation d'événements.

## Fonctionnalités

- **Authentification sécurisée** avec gestion des sessions utilisateur
- **Gestion des utilisateurs** avec trois rôles distincts :
  - **Commercial** : Démarchage et suivi des clients
  - **Support** : Organisation et gestion des événements
  - **Gestion** : Administration complète du système


- **Gestion des clients** :
  - Création et mise à jour des profils clients
  - Suivi des contacts et historique
  - Association avec les commerciaux


- **Gestion des contrats** :
  - Création et modification des contrats
  - Suivi des montants et des paiements
  - Gestion des signatures


- **Gestion des événements** :
  - Planification des événements
  - Attribution des équipes support
  - Suivi des détails


- **Système de filtrage** avancé pour tous les modules
- **Journalisation** complète avec Sentry pour le monitoring des erreurs
- **Sécurité** renforcée avec prévention des injections SQL et principe du moindre privilège


## Prérequis

- Python 3.9+
- PostgreSQL
- Pip

## Installation

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone https://github.com/Hedi-Slm/Python_SQLAlchemy_backend.git
   ```

2. Créez un environnement virtuel :
   ```bash
   python -m venv env
   ```

3. Activez l'environnement virtuel :
   - Windows : `env\Scripts\activate`
   - macOS/Linux : `source env/bin/activate`


4. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

5. Configurez les variables d'environnement :

   Modifiez le fichier `.env` avec vos paramètres :
   ```
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=crm_db
    DB_USER=crm_user
    DB_PASSWORD=crm_password
   ```

6. Créez la base de données :
   ```bash
   python create_db.py
   ```

7. Créez l'utilisateur gestion :
   ```bash
   python create_user.py
   ```
   utilisateur initial :
   - Nom : "Gestion"
   - Email : "gestion@mail.com"
   - Role : "GESTION"
   - Mot de passe : "gestion"


8. Lancez l'application :
   ```bash
   python main.py
   ```

## Utilisation

### Connexion
Au démarrage, l'application vous demande vos identifiants :
- Email
- Mot de passe

### Menu principal
Après connexion, vous accédez au menu principal avec les options suivantes :
1. **Gestion des clients** - Visualiser, créer et modifier les clients
2. **Gestion des contrats** - Visualiser, créer et modifier les contrats
3. **Gestion des événements** - Visualiser, créer et modifier les événements
4. **Gestion des utilisateurs** - Administration des utilisateurs (Gestion uniquement)


### Permissions par rôle

#### Commercial
- ✅ Voir tous les clients, contrats et événements
- ✅ Créer des clients (automatiquement associés)
- ✅ Modifier ses propres clients
- ✅ Modifier les contrats de ses clients
- ✅ Créer des événements pour ses contrats signés
- ✅ Filtrer les contrats

#### Support
- ✅ Voir tous les clients, contrats et événements
- ✅ Modifier les événements qui leur sont assignés
- ✅ Filtrer les événements

#### Gestion
- ✅ Voir tous les utilisateurs, clients, contrats et événements
- ✅ Créer, modifier et supprimer des utilisateurs
- ✅ Créer et modifier tous les contrats
- ✅ Assigner des équipes support aux événements
- ✅ Filtrer tous les éléments selon divers critères


## Sécurité

- **Authentification** : Système de connexion sécurisé avec hachage des mots de passe
- **Autorisation** : Contrôle d'accès basé sur les rôles
- **Principe du moindre privilège** : Chaque utilisateur n'a accès qu'aux données nécessaires
- **Prévention des injections SQL** : Utilisation d'ORM avec requêtes paramétrées
- **Journalisation** : Suivi des erreurs et des actions importantes avec Sentry

## Monitoring et logs

L'application utilise Sentry pour le monitoring des erreurs et la journalisation. Les événements suivants sont trackés :
- Erreurs et exceptions
- Créations, modifications et suppressions d'entités

