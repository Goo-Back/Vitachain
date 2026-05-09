# Guide d'Exécution Manuelle des Migrations Supabase

## Étape 1: Accéder au dashboard Supabase

1. Allez sur https://supabase.com/dashboard
2. Connectez-vous avec votre compte
3. Sélectionnez votre projet `bgdtqvpchfnrscupyyaa`

## Étape 2: Ouvrir l'éditeur SQL

1. Dans le menu de gauche, cliquez sur **"SQL Editor"**
2. Cliquez sur **"New query"** pour ouvrir un nouvel éditeur

## Étape 3: Exécuter les migrations dans l'ordre

### Migration 1: Schéma de base
1. Copiez le contenu de `database/migrations/01-schema.sql`
2. Collez-le dans l'éditeur SQL
3. Cliquez sur **"Run"** (ou `Ctrl+Enter`)
4. Attendez que l'exécution se termine

### Migration 2: Politiques RLS
1. Nettoyez l'éditeur (supprimez le contenu précédent)
2. Copiez le contenu de `database/migrations/02-rls-policies.sql`
3. Collez-le et exécutez-le

### Migration 3: Fonctions
1. Copiez et exécutez `database/migrations/03-functions.sql`

### Migration 4: Triggers
1. Copiez et exécutez `database/migrations/04-triggers.sql`

### Migration 5: Indexes
1. Copiez et exécutez `database/migrations/05-indexes.sql`

### Migration 6: Données de test
1. Copiez et exécutez `database/migrations/06-seed-data.sql`

## Étape 4: Configuration supplémentaire

### Extensions PostgreSQL
1. Copiez et exécutez `database/config/extensions.sql`

### Configuration de la base de données
1. Copiez et exécutez `database/config/database-config.sql`

## Étape 5: Vérification

Après avoir exécuté toutes les migrations, exécutez notre script de verification :

```bash
cd database
./scripts/verify-final.sh
```

Ou pour un test complet :

```bash
cd database
./scripts/test-working.sh
```

## 🚨 Points importants

1. **Ordre d'exécution** : Suivez exactement l'ordre numérique (01, 02, 03, 04, 05, 06)
2. **Attendre la fin** : Chaque migration peut prendre 1-2 minutes
3. **Vérifier les erreurs** : Si une migration échoue, notez l'erreur et corrigez-la avant de continuer
4. **Sauvegarder** : Le dashboard Supabase sauvegarde automatiquement votre travail

## 🔧 Alternative: Via psql (si vous avez accès)

Si vous préférez utiliser la ligne de commande :

```bash
# Connection string (utilisez votre mot de passe réel)
psql "postgresql://postgres:VOTRE_MOT_DE_PASSE@db.bgdtqvpchfnrscupyyaa.supabase.co:5432/postgres"

# Exécuter les migrations
\i migrations/01-schema.sql
\i migrations/02-rls-policies.sql
\i migrations/03-functions.sql
\i migrations/04-triggers.sql
\i migrations/05-indexes.sql
\i migrations/06-seed-data.sql
```

## ✅ Validation

Après l'exécution, vous devriez voir :
- Toutes les tables créées dans le dashboard
- Les données de test visibles dans les tables
- Les scripts de verification qui passent avec succès

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les messages d'erreur dans le dashboard
2. Assurez-vous que le format SQL est correct
3. Contactez le support Supabase si nécessaire
