# Pièces Méthanisation Pro

Plateforme professionnelle B2B pour l'achat et la vente d'équipements de méthanisation et biogaz en France et en Europe.

## 🚀 Fonctionnalités

### Pour les vendeurs
- **Wizard de publication en 5 étapes** : Création guidée d'annonces avec sauvegarde automatique
- **Paiement par Stripe** : Paiement sécurisé de 49€ par annonce publiée
- **Tableau de bord** : Gestion des annonces (brouillons, publiées, vendues) et suivi des demandes
- **Demandes de contact** : Réception et suivi des demandes d'acheteurs

### Pour les acheteurs
- **Recherche et filtres** : Filtres en temps réel (catégorie, état, localisation, recherche)
- **Détails complets** : Informations techniques détaillées avec photos
- **Contact direct** : Formulaire de demande de contact intégré
- **Annonces similaires** : Suggestions d'équipements comparables

## 📦 Technologies

- **Backend** : FastAPI (Python)
- **Base de données** : Supabase (PostgreSQL)
- **Paiement** : Stripe Checkout
- **Templates** : Jinja2
- **Frontend** : HTML5, CSS3 moderne (variables CSS, Grid, Flexbox), JavaScript vanilla
- **Serveur** : Uvicorn (ASGI)

## 🛠️ Installation locale

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Compte Supabase (gratuit) - optionnel pour le développement
- Compte Stripe (mode test gratuit) - optionnel pour le développement

### Étapes d'installation

1. **Cloner le dépôt** :
```bash
git clone https://github.com/jeanlura92-alt/pieces-methanisation.git
cd pieces-methanisation
```

2. **Créer un environnement virtuel** (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement** :
```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos propres valeurs. Pour le développement local, vous pouvez laisser les variables Supabase et Stripe vides - l'application fonctionnera en mode "mock" sans base de données ni paiement réel.

5. **Lancer l'application** :
```bash
uvicorn app.main:app --reload
```

6. **Ouvrir dans le navigateur** :
```
http://localhost:8000
```

## ⚙️ Configuration

### Mode Mock (Développement sans DB/Stripe)

Si vous ne configurez pas Supabase et Stripe, l'application fonctionne en mode "mock" :
- Les annonces ne sont pas sauvegardées en base de données
- Le paiement est simulé et les annonces sont publiées immédiatement
- Les demandes de contact sont simulées

### Configuration Supabase

1. Créez un compte gratuit sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Exécutez le script SQL fourni dans `DATABASE_SCHEMA.md` via l'éditeur SQL Supabase
4. **Configurez le stockage de fichiers** :
   - Allez dans Storage dans le dashboard Supabase
   - Créez un nouveau bucket public nommé `listing-photos`
   - Configurez les politiques d'accès :
     - Lecture publique (public read) pour permettre l'affichage des images
     - Écriture authentifiée ou désactivez RLS pour le développement
5. Récupérez votre URL de projet et votre clé anonyme dans Settings > API
6. Ajoutez-les dans votre fichier `.env` :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-cle-anonyme
SUPABASE_STORAGE_BUCKET=listing-photos
```

### Configuration Stripe

1. Créez un compte sur [stripe.com](https://stripe.com)
2. Activez le mode test
3. Récupérez vos clés API de test dans Developers > API keys
4. Créez un produit "Publication d'annonce" à 49.00 EUR
5. Ajoutez les clés dans votre fichier `.env` :

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Configuration du webhook Stripe

Pour recevoir les confirmations de paiement :

1. **En développement local** :
   - Installez Stripe CLI : https://stripe.com/docs/stripe-cli
   - Lancez le forward : `stripe listen --forward-to localhost:8000/webhook/stripe`
   - Copiez le webhook secret affiché et ajoutez-le dans `.env` :
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

2. **En production** :
   - Allez dans Stripe Dashboard > Developers > Webhooks
   - Ajoutez un endpoint : `https://votre-domaine.com/webhook/stripe`
   - Sélectionnez l'événement : `checkout.session.completed`
   - Copiez le webhook secret et ajoutez-le dans vos variables d'environnement

## 🌐 Routes disponibles

### Pages publiques
- `/` - Page d'accueil avec annonces en vedette
- `/annonces` - Liste de toutes les annonces publiées
- `/annonces/{id}` - Détail d'une annonce avec formulaire de contact
- `/contact` - Page de contact

### Flux vendeur
- `/deposer` - Redirection vers le wizard
- `/deposer/step1` - Étape 1 : Type & Catégorie
- `/deposer/step2` - Étape 2 : Détails techniques
- `/deposer/step3` - Étape 3 : Photos & Documents
- `/deposer/step4` - Étape 4 : Prix & Localisation
- `/deposer/step5` - Étape 5 : Contact & Récapitulatif
- `/dashboard` - Tableau de bord vendeur

### Paiement
- `/payment/success` - Page de confirmation après paiement
- `/payment/cancel` - Page d'annulation de paiement

### API/Webhooks
- `POST /annonces/{id}/inquiry` - Soumettre une demande de contact
- `POST /webhook/stripe` - Webhook Stripe pour confirmation de paiement

## 📁 Structure du projet

```
pieces-methanisation/
├── app/
│   ├── main.py              # Application FastAPI avec tous les endpoints
│   ├── db.py                # Couche d'accès à la base de données Supabase
│   ├── config.py            # Configuration et variables d'environnement
│   ├── data.py              # Données d'exemple (legacy)
│   ├── templates/           # Templates Jinja2
│   │   ├── base.html        # Template de base avec navigation
│   │   ├── index.html       # Page d'accueil
│   │   ├── listing.html     # Liste des annonces
│   │   ├── detail.html      # Détail d'une annonce
│   │   ├── contact.html     # Page de contact
│   │   ├── dashboard.html   # Tableau de bord vendeur
│   │   ├── wizard_base.html # Template de base pour le wizard
│   │   ├── wizard_step*.html # Étapes du wizard de publication
│   │   ├── payment_success.html
│   │   └── payment_cancel.html
│   └── static/              # Fichiers statiques
│       ├── css/
│       │   └── styles.css   # Styles CSS modernes
│       └── js/
│           └── app.js       # JavaScript (filtres)
├── .env.example             # Template de configuration
├── .env                     # Configuration locale (git-ignoré)
├── DATABASE_SCHEMA.md       # Documentation du schéma de base de données
├── requirements.txt         # Dépendances Python
├── render.yaml             # Configuration Render
└── README.md               # Documentation
```

## 🎨 Design & UX

- **Design moderne** : Palette de couleurs professionnelles (bleu primaire, vert secondaire)
- **Wizard intuitif** : Processus de publication guidé en 5 étapes avec indicateur de progression
- **Responsive** : Compatible mobile, tablette et desktop
- **Accessibilité** : Contraste élevé, navigation claire
- **Performance** : CSS optimisé, JavaScript vanilla léger

## 🔐 Sécurité

- **Paiement sécurisé** : Intégration Stripe Checkout (PCI-DSS compliant)
- **Base de données** : Supabase avec Row Level Security (RLS) disponible
- **Variables d'environnement** : Toutes les clés sensibles sont dans `.env` (git-ignoré)
- **Webhook signature** : Vérification des signatures Stripe pour les webhooks

## 💰 Modèle de monétisation

- **Pay-per-listing** : 49 € par annonce publiée
- **Paiement unique** : Pas d'abonnement, pas de frais cachés
- **Couverture** : Europe (devise EUR)

## 🔧 Développement

### Modifications du CSS

Les styles sont centralisés dans `app/static/css/styles.css` avec des variables CSS pour faciliter la personnalisation :

```css
:root {
  --primary-color: #1e40af;
  --secondary-color: #10b981;
  --text-dark: #1f2937;
  /* ... */
}
```

### Flux de publication d'une annonce

1. Vendeur remplit le wizard (5 étapes)
2. À chaque étape, les données sont sauvegardées en brouillon dans la DB
3. Étape 5 : création d'une session Stripe Checkout
4. Redirection vers Stripe pour le paiement
5. Après paiement réussi :
   - Stripe envoie un webhook `checkout.session.completed`
   - L'application met à jour le statut de paiement
   - L'annonce passe de "draft" à "published"
   - Le vendeur est redirigé vers la page de succès
6. L'annonce est maintenant visible sur la plateforme

### Flux de demande de contact

1. Acheteur remplit le formulaire sur la page de détail
2. Demande sauvegardée dans la table `inquiries`
3. Statut "new" par défaut
4. Visible dans le dashboard du vendeur avec compteur
5. Email de notification envoyé au vendeur (à implémenter)

## 🚀 Déploiement

### Sur Render

L'application est configurée pour être déployée sur Render via le fichier `render.yaml`.

1. Connecter le dépôt GitHub à Render
2. Render détectera automatiquement `render.yaml`
3. Configurer les variables d'environnement dans le dashboard Render
4. Déploiement automatique

### Variables d'environnement requises en production

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-cle-anonyme
STRIPE_SECRET_KEY=sk_live_...  # Clé LIVE, pas test
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
APP_URL=https://votre-domaine.com
LISTING_PRICE_AMOUNT=4900  # 49.00 EUR en centimes
```

## 📝 Prochaines étapes

Pour une version de production complète, considérez d'ajouter :

- **Authentification utilisateur** : OAuth, email/password avec tokens JWT
- **Upload de documents PDF** : Extension du stockage Supabase pour documents techniques
- **Envoi d'emails** : Notifications automatiques (SendGrid, AWS SES)
- **Modération** : Workflow de validation des annonces
- **Analytics** : Suivi des performances des annonces
- **Messagerie** : Chat en temps réel entre acheteurs et vendeurs
- **Filtres avancés** : Prix, année, fabricant, etc.
- **Favoris** : Sauvegarde d'annonces pour les acheteurs
- **Notifications push** : Alertes pour nouvelles annonces
- **SEO** : Optimisation pour les moteurs de recherche
- **Multi-langue** : Support FR/EN/DE

## 📄 Licence

Ce projet est un prototype de démonstration.

## 🤝 Contact

Pour toute question : contact@pieces-methanisation.fr

## 🔗 Liens utiles

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Supabase](https://supabase.com/docs)
- [Documentation Stripe](https://stripe.com/docs)
- [Stripe CLI](https://stripe.com/docs/stripe-cli)
