# 🌱 VITACHAIN - COMPTES DE TEST MANUEL

## 📋 **COMPTES DE TEST PRÉDÉFINIS**

### 🚨 **SITUATION ACTUELLE**
Le rate limiting Supabase empêche la création automatique des comptes. Voici les comptes de test manuels à créer via le dashboard Supabase ou à utiliser une fois le rate limiting résolu.

### 👥 **COMPTES PAR PROFIL**

#### **1. AGRICULTEUR (FARMER)**
```
📧 Email: farmer.test@vitachain.demo
🔐 Mot de passe: FarmerTest123!
👤 Nom complet: Mohamed Ben Ali - Agriculteur Test
🎭 Rôle: FARMER
```

#### **2. RESTAURANT**
```
📧 Email: restaurant.test@vitachain.demo
🔐 Mot de passe: RestaurantTest123!
👤 Nom complet: Le Gourmet Marocain - Restaurant Test
🎭 Rôle: RESTAURANT
```

#### **3. CONSOMMATEUR (CITIZEN)**
```
📧 Email: consumer.test@vitachain.demo
🔐 Mot de passe: ConsumerTest123!
👤 Nom complet: Fatima Zahra - Consommateur Test
🎭 Rôle: CITIZEN
```

#### **4. ADMINISTRATEUR (ADMIN)**
```
📧 Email: admin.test@vitachain.demo
🔐 Mot de passe: AdminTest123!
👤 Nom complet: Admin VitaChain - Test
🎭 Rôle: ADMIN
```

## 🔧 **PROCÉDURE DE CRÉATION**

### **Option 1: Via Dashboard Supabase**
1. Accéder au dashboard Supabase: https://ymogoemuzqyjsdjhzpnz.supabase.co
2. Aller dans "Authentication" → "Users"
3. Cliquer sur "Add user"
4. Remplir les informations ci-dessus pour chaque profil
5. Activer "Auto-confirm" pour éviter l'email verification

### **Option 2: Attendre le Rate Limiting**
1. Attendre 30-60 minutes pour que le rate limiting se résolve
2. Exécuter: `python wait_and_create_accounts.py`
3. Le script créera automatiquement tous les comptes

### **Option 3: Via Frontend**
1. Accéder à: `http://localhost:3010/auth/register`
2. Créer manuellement chaque compte avec les informations ci-dessus
3. Attendre entre chaque création pour éviter le rate limiting

## 🎯 **UTILISATION DES COMPTES**

### **Test d'Inscription**
```bash
# Via API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer.test@vitachain.demo",
    "password": "FarmerTest123!",
    "role": "FARMER",
    "full_name": "Mohamed Ben Ali - Agriculteur Test"
  }'
```

### **Test de Login**
```bash
# Via API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer.test@vitachain.demo",
    "password": "FarmerTest123!"
  }'
```

### **Via Frontend**
1. Accéder à: `http://localhost:3010/auth/login`
2. Utiliser les identifiants ci-dessus
3. Tester chaque profil

## 📊 **SCÉNARIOS DE TEST**

### **1. Test Complet - Agriculteur**
1. **Inscription**: `farmer.test@vitachain.demo`
2. **Login**: Vérifier l'accès au dashboard farmer
3. **Fonctionnalités**: Test des features spécifiques agriculteur

### **2. Test Complet - Restaurant**
1. **Inscription**: `restaurant.test@vitachain.demo`
2. **Login**: Vérifier l'accès au dashboard restaurant
3. **Fonctionnalités**: Test des features spécifiques restaurant

### **3. Test Complet - Consommateur**
1. **Inscription**: `consumer.test@vitachain.demo`
2. **Login**: Vérifier l'accès au dashboard consommateur
3. **Fonctionnalités**: Test des features spécifiques consommateur

### **4. Test Complet - Admin**
1. **Inscription**: `admin.test@vitachain.demo`
2. **Login**: Vérifier l'accès au dashboard admin
3. **Fonctionnalités**: Test des features d'administration

## 🔄 **AUTOMATION FUTURE**

Une fois le rate limiting résolu, les scripts suivants seront disponibles:

- `create_test_accounts.py` : Création immédiate des comptes
- `wait_and_create_accounts.py` : Attente + création automatique
- `test_all_accounts.py` : Test complet de tous les comptes

## 📝 **NOTES IMPORTANTES**

- **Rate Limiting**: Supabase limite les créations d'utilisateurs
- **Temps d'attente**: 30-60 minutes recommandé
- **Emails Uniques**: Chaque email doit être unique
- **Mots de passe**: Minimum 8 caractères
- **Rôles**: Doivent correspondre aux enums définis dans le backend

## 🎉 **QUAND LES COMPTES SERONT PRÊTS**

Une fois les comptes créés, vous pourrez:

1. ✅ Tester l'inscription complète
2. ✅ Tester le login avec chaque profil
3. ✅ Valider les permissions par rôle
4. ✅ Tester les workflows métier
5. ✅ Démontrer le système complet

**Le système VitaChain sera alors 100% opérationnel pour les tests utilisateurs !** 🚀
