-- Migration V2: Simplification de la marketplace
-- Ce script effectue les modifications suivantes :
-- 1. Supprime la table inquiries (système de messagerie)
-- 2. Met à jour les annonces existantes pour ajouter expires_at si non défini
-- 3. Crée une fonction optionnelle pour automatiser l'expiration via pg_cron

-- ============================================
-- 1. Supprimer la table inquiries
-- ============================================
DROP TABLE IF EXISTS inquiries CASCADE;

-- ============================================
-- 2. Mettre à jour les annonces existantes
-- ============================================

-- Ajouter expires_at aux annonces publiées qui n'ont pas encore cette valeur
-- Les annonces existantes expirent 30 jours après leur date de publication
UPDATE listings
SET expires_at = published_at + INTERVAL '30 days',
    updated_at = NOW()
WHERE status = 'published' 
  AND published_at IS NOT NULL 
  AND expires_at IS NULL;

-- Marquer comme expirées les annonces publiées dont la date d'expiration est dépassée
UPDATE listings
SET status = 'expired',
    updated_at = NOW()
WHERE status = 'published' 
  AND expires_at IS NOT NULL 
  AND expires_at < NOW();

-- ============================================
-- 3. Fonction optionnelle pour automatisation
-- ============================================

-- Cette fonction peut être appelée manuellement ou via pg_cron pour automatiser l'expiration
-- Exemple d'utilisation : SELECT expire_old_listings();
CREATE OR REPLACE FUNCTION expire_old_listings()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    -- Mettre à jour les annonces expirées
    UPDATE listings
    SET status = 'expired',
        updated_at = NOW()
    WHERE status = 'published' 
      AND expires_at < NOW();
    
    -- Récupérer le nombre de lignes modifiées
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4. Configuration optionnelle de pg_cron (Supabase/PostgreSQL)
-- ============================================

-- IMPORTANT : Cette configuration est optionnelle et dépend de votre environnement
-- Si vous utilisez Supabase avec pg_cron activé, décommentez la ligne suivante :
-- SELECT cron.schedule('expire-listings-daily', '0 2 * * *', 'SELECT expire_old_listings();');

-- Cela exécutera la fonction expire_old_listings() tous les jours à 2h du matin

-- ============================================
-- 5. Alternative : Cron job système
-- ============================================

-- Si vous préférez utiliser un cron job système, ajoutez cette ligne à votre crontab :
-- 0 2 * * * cd /chemin/vers/votre/app && python -c "from app.db import expire_old_listings; expire_old_listings()"

-- ============================================
-- 6. Vérification
-- ============================================

-- Vérifier les annonces publiées avec leur date d'expiration
-- SELECT id, title, status, published_at, expires_at
-- FROM listings
-- WHERE status IN ('published', 'expired')
-- ORDER BY published_at DESC;
