# Changelog - Version 2: Simplification

## Vue d'ensemble

Cette version simplifie considérablement l'application de marketplace pour rendre l'expérience plus directe et intuitive.

## Changements Principaux

### 1. ✅ Limitation des Photos à 1 par Annonce

**Avant:** Les utilisateurs pouvaient télécharger jusqu'à 3 photos par annonce.

**Maintenant:** Les utilisateurs ne peuvent télécharger qu'**1 seule photo** par annonce.

**Fichiers modifiés:**
- `app/config.py`: `MAX_PHOTOS_PER_LISTING = 1` (était 3)
- `app/templates/wizard_step3.html`: 
  - Suppression de l'attribut `multiple` sur le champ de fichier
  - Mise à jour du texte d'aide: "Sélectionnez 1 photo"
  - Validation client mise à jour pour n'accepter qu'1 fichier
  - Interface de prévisualisation mise à jour

**Impact utilisateur:** Interface plus simple, création d'annonce plus rapide.

---

### 2. ✅ Affichage Direct des Coordonnées Vendeur

**Avant:** Les acheteurs devaient remplir un formulaire de contact, et un système de messagerie gérait les demandes.

**Maintenant:** Les coordonnées du vendeur (email et téléphone) sont **affichées directement** sur chaque page d'annonce.

**Fichiers modifiés:**
- `app/templates/detail.html`:
  - Suppression du formulaire de contact
  - Ajout d'une section "Coordonnées du vendeur" avec:
    - Email cliquable (lien `mailto:`)
    - Téléphone cliquable (lien `tel:`)
- `app/main.py`:
  - Suppression de la route `POST /annonces/{listing_id}/inquiry`
- `app/db.py`:
  - Suppression des fonctions:
    - `create_inquiry()`
    - `get_listing_inquiries()`
    - `count_listing_inquiries()`

**Base de données:**
- La table `inquiries` est supprimée (voir `MIGRATION_V2.sql`)

**Impact utilisateur:** Contact immédiat avec le vendeur, pas d'intermédiaire.

---

### 3. ✅ Suppression du Tableau de Bord

**Avant:** Les utilisateurs avaient accès à un tableau de bord pour gérer leurs annonces et voir les demandes de contact.

**Maintenant:** Le tableau de bord est **complètement supprimé**. L'accent est mis sur la création et la publication d'annonces de manière simple.

**Fichiers modifiés/supprimés:**
- `app/templates/dashboard.html`: **SUPPRIMÉ**
- `app/main.py`: Suppression de la route `GET /dashboard`
- `app/templates/base.html`: Suppression du lien "Tableau de bord" dans la navigation

**Navigation avant:**
```
Annonces | Déposer | Tableau de bord | Contact
```

**Navigation maintenant:**
```
Annonces | Déposer | Contact
```

**Impact utilisateur:** Interface simplifiée, focus sur la publication d'annonces.

---

### 4. ✅ Expiration Automatique après 30 Jours

**Avant:** Les annonces restaient publiées indéfiniment.

**Maintenant:** Les annonces expirent automatiquement **30 jours après publication**.

**Fichiers modifiés:**
- `app/db.py`:
  - `publish_listing()`: Définit automatiquement `expires_at = published_at + 30 jours`
  - `get_published_listings()`: Filtre les annonces expirées (ne retourne que les annonces avec `expires_at > NOW()`)
  - Nouvelle fonction `expire_old_listings()`: Marque les annonces expirées comme `status = 'expired'`

**Base de données:**
- Index ajouté sur `listings.expires_at`
- Migration pour définir `expires_at` sur les annonces existantes

**Automatisation:**

Vous devez configurer l'expiration automatique via l'une de ces méthodes:

#### Option A: Fonction PostgreSQL avec pg_cron (Recommandé pour Supabase)
```sql
SELECT cron.schedule('expire-listings-daily', '0 2 * * *', 'SELECT expire_old_listings();');
```

#### Option B: Cron job système
```bash
# Ajouter à crontab
0 2 * * * cd /chemin/vers/app && python -c "from app.db import expire_old_listings; expire_old_listings()"
```

#### Option C: Script manuel
```python
from app.db import expire_old_listings
expired_count = expire_old_listings()
print(f"{expired_count} annonces expirées")
```

**Impact utilisateur:** Les annonces restent fraîches et pertinentes, pas d'annonces obsolètes.

---

## Migration de Base de Données

Pour migrer une base de données existante, exécutez le script `MIGRATION_V2.sql` dans votre base de données Supabase.

Ce script va:
1. ✅ Supprimer la table `inquiries`
2. ✅ Ajouter `expires_at` aux annonces publiées existantes (30 jours après leur publication)
3. ✅ Marquer comme expirées les annonces dont la date d'expiration est dépassée
4. ✅ Créer la fonction `expire_old_listings()` pour automatiser l'expiration

**Important:** Sauvegardez votre base de données avant d'exécuter la migration!

---

## Fichiers Ajoutés

- `MIGRATION_V2.sql`: Script de migration de base de données
- `CHANGELOG_V2.md`: Ce fichier (documentation des changements)

## Fichiers Modifiés

- `app/config.py`
- `app/db.py`
- `app/main.py`
- `app/templates/base.html`
- `app/templates/detail.html`
- `app/templates/wizard_step3.html`
- `DATABASE_SCHEMA.md`

## Fichiers Supprimés

- `app/templates/dashboard.html`

---

## Avertissements Importants

### ⚠️ Coordonnées Publiques

Les vendeurs doivent être informés que leurs coordonnées (email et téléphone) seront **publiquement visibles** sur chaque annonce publiée.

**Recommandations:**
- Informer clairement les utilisateurs lors de la création d'annonce
- Ajouter un texte d'information à l'étape 5 du wizard
- Considérer l'ajout d'une case à cocher de consentement

### ⚠️ Expiration Automatique

L'expiration automatique nécessite une configuration supplémentaire (cron job ou pg_cron). Sans cette configuration, les annonces ne seront pas automatiquement expirées.

---

## Tests Recommandés

Après la migration, testez:

1. ✅ Création d'une nouvelle annonce avec 1 photo uniquement
2. ✅ Vérifier qu'une tentative d'upload de plusieurs photos est rejetée
3. ✅ Vérifier que les coordonnées du vendeur s'affichent sur la page de détail
4. ✅ Vérifier que le lien "Tableau de bord" n'apparaît plus dans la navigation
5. ✅ Créer et publier une annonce, vérifier que `expires_at` est défini
6. ✅ Exécuter `expire_old_listings()` manuellement pour tester l'expiration
7. ✅ Vérifier que les annonces expirées n'apparaissent pas dans la liste publique

---

## Support

Pour toute question ou problème lié à cette migration, référez-vous à:
- `DATABASE_SCHEMA.md`: Schema complet de la base de données
- `MIGRATION_V2.sql`: Script de migration avec commentaires détaillés
- `README.md`: Instructions générales de configuration
