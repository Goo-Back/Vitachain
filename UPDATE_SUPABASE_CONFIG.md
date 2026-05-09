# Mise à jour Configuration Supabase

## 📝 Informations requises

Veuillez fournir les détails de votre nouveau projet Supabase :

### 1. URL du projet
```
https://[votre-projet-id].supabase.co
```

### 2. Clés API (depuis Settings > API)
- **Anon Key**: `eyJ...`
- **Service Role Key**: `eyJ...`

### 3. URL Base de données
```
postgresql://postgres:[votre-password]@db.[votre-projet-id].supabase.co:5432/postgres
```

### 4. JWT Secret
```
eyJ... (depuis Settings > API > JWT Secret)
```

## 🔄 Actions automatiques

Une fois les informations fournies, je vais :

1. ✅ Mettre à jour `frontend/lib/supabase.ts`
2. ✅ Mettre à jour `.env.example` 
3. ✅ Mettre à jour `backend/config/supabase.md`
4. ✅ Créer un script de test pour la nouvelle configuration
5. ✅ Tester la connexion

## 📋 Fichiers à modifier

- `frontend/lib/supabase.ts`
- `.env.example`
- `backend/config/supabase.md`

---

**Prêt à mettre à jour dès que vous fournissez les informations !**
