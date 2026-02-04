# Pièces Méthanisation Pro

Plateforme professionnelle B2B pour l'achat et la vente d'équipements de méthanisation et biogaz en France et en Europe.

## 🚀 Fonctionnalités

- **Page d'accueil** : Hero moderne, statistiques, catégories, dernières annonces, CTA
- **Liste des annonces** : Filtres en temps réel (catégorie, état, localisation, recherche), cartes professionnelles
- **Détail d'annonce** : Informations complètes, contact vendeur, annonces similaires
- **Dépôt d'annonce** : Formulaire complet pour publier une annonce
- **Contact** : Formulaire de contact avec FAQ

## 📦 Technologies

- **Backend** : FastAPI (Python)
- **Templates** : Jinja2
- **Frontend** : HTML5, CSS3 moderne (variables CSS, Grid, Flexbox), JavaScript vanilla
- **Serveur** : Uvicorn (ASGI)

## 🛠️ Installation locale

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner le dépôt :
```bash
git clone https://github.com/jeanlura92-alt/pieces-methanisation.git
cd pieces-methanisation
```

2. Créer un environnement virtuel (recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancer l'application :
```bash
uvicorn app.main:app --reload
```

5. Ouvrir dans le navigateur :
```
http://localhost:8000
```

## 🌐 Routes disponibles

- `/` - Page d'accueil
- `/annonces` - Liste de toutes les annonces
- `/annonces/{id}` - Détail d'une annonce
- `/deposer` - Formulaire de dépôt d'annonce
- `/contact` - Page de contact

## 📁 Structure du projet

```
pieces-methanisation/
├── app/
│   ├── main.py              # Application FastAPI principale
│   ├── data.py              # Données d'exemple (15 annonces)
│   ├── templates/           # Templates Jinja2
│   │   ├── base.html        # Template de base
│   │   ├── index.html       # Page d'accueil
│   │   ├── listing.html     # Liste des annonces
│   │   ├── detail.html      # Détail d'une annonce
│   │   ├── create.html      # Formulaire de dépôt
│   │   └── contact.html     # Page de contact
│   └── static/              # Fichiers statiques
│       ├── css/
│       │   └── styles.css   # Styles CSS modernes
│       └── js/
│           └── app.js       # JavaScript (filtres)
├── requirements.txt         # Dépendances Python
├── render.yaml             # Configuration Render
└── README.md               # Documentation
```

## 🎨 Design & UX

- **Design moderne** : Palette de couleurs professionnelles (bleu primaire, vert secondaire)
- **Responsive** : Compatible mobile, tablette et desktop
- **Accessibilité** : Contraste élevé, navigation claire
- **Performance** : CSS optimisé, JavaScript vanilla léger
- **UX professionnelle** : Navigation intuitive, CTA clairs, filtres en temps réel

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

### Ajout d'annonces

Les annonces sont définies dans `app/data.py`. Pour ajouter une annonce :

```python
{
    "id": 16,
    "title": "Titre de l'équipement",
    "category": "Catégorie",
    "location": "Région, Pays",
    "price": "Prix €",
    "condition": "État",
    "summary": "Résumé court",
    "description": "Description détaillée...",
    "year": "2023",
    "manufacturer": "Fabricant",
    "contact_email": "email@example.fr",
    "contact_phone": "+33 X XX XX XX XX",
    "image": "https://...",
}
```

## 🚀 Déploiement sur Render

L'application est configurée pour être déployée sur Render via le fichier `render.yaml`.

### Déploiement automatique

1. Connecter le dépôt GitHub à Render
2. Render détectera automatiquement `render.yaml`
3. L'application sera déployée avec les paramètres définis

### Configuration manuelle

Si vous préférez configurer manuellement sur Render :

- **Type** : Web Service
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment** : Python 3.11

## 📝 Notes

- Cette version est une démonstration statique (pas de base de données)
- Les formulaires (dépôt d'annonce, contact) affichent un message indiquant que les données ne sont pas sauvegardées
- Pour une version de production, il faudrait ajouter :
  - Base de données (PostgreSQL, MongoDB, etc.)
  - Système d'authentification (optionnel selon besoins)
  - Upload d'images
  - Envoi d'emails
  - Modération des annonces

## 📄 Licence

Ce projet est un prototype de démonstration.

## 🤝 Contact

Pour toute question : contact@pieces-methanisation.fr
