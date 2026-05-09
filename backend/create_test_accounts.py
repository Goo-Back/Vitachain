#!/usr/bin/env python3
"""
Script pour créer des comptes de test VitaChain pour chaque profil
Cela permettra de contourner le rate limiting Supabase et d'avoir des comptes prêts
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ACCOUNTS = [
    {
        "email": "farmer.test@vitachain.demo",
        "password": "FarmerTest123!",
        "role": "FARMER",
        "full_name": "Mohamed Ben Ali - Agriculteur Test"
    },
    {
        "email": "restaurant.test@vitachain.demo", 
        "password": "RestaurantTest123!",
        "role": "RESTAURANT",
        "full_name": "Le Gourmet Marocain - Restaurant Test"
    },
    {
        "email": "consumer.test@vitachain.demo",
        "password": "ConsumerTest123!", 
        "role": "CITIZEN",
        "full_name": "Fatima Zahra - Consommateur Test"
    },
    {
        "email": "admin.test@vitachain.demo",
        "password": "AdminTest123!",
        "role": "ADMIN", 
        "full_name": "Admin VitaChain - Test"
    }
]

def create_test_account(account_data, attempt=1):
    """Crée un compte de test avec retry en cas de rate limiting"""
    print(f"\n📝 Création du compte: {account_data['role']} - {account_data['email']}")
    print(f"   Tentative #{attempt}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=account_data,
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Compte créé avec succès!")
            print(f"   User ID: {result.get('user_id', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True, result
            
        elif response.status_code == 500:
            error_result = response.json()
            print(f"   ⚠️  Erreur serveur: {error_result}")
            
            if "rate limit" in str(error_result).lower() or "too many" in str(error_result).lower():
                print(f"   🕐 Rate limiting détecté - Attente de 30 secondes...")
                time.sleep(30)
                if attempt < 3:  # Max 3 tentatives
                    return create_test_account(account_data, attempt + 1)
                else:
                    print(f"   ❌ Max tentatives atteintes pour {account_data['email']}")
                    return False, error_result
            else:
                print(f"   ❌ Erreur interne du serveur")
                return False, error_result
                
        elif response.status_code == 422:
            error_result = response.json()
            print(f"   ❌ Erreur de validation: {error_result}")
            return False, error_result
            
        else:
            error_result = response.json()
            print(f"   ❌ Erreur inattendue: {error_result}")
            return False, error_result
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - Le serveur ne répond pas")
        if attempt < 2:
            print(f"   🔄 Retry dans 10 secondes...")
            time.sleep(10)
            return create_test_account(account_data, attempt + 1)
        return False, {"error": "timeout"}
        
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False, {"error": str(e)}

def test_login(account_data):
    """Test le login avec un compte créé"""
    print(f"\n🔐 Test login pour: {account_data['email']}")
    
    try:
        login_data = {
            "email": account_data["email"],
            "password": account_data["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login réussi!")
            print(f"   Access Token: {'✅ Généré' if result.get('access_token') else '❌ Manquant'}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True, result
        else:
            error_result = response.json()
            print(f"   ❌ Login échoué: {error_result}")
            return False, error_result
            
    except Exception as e:
        print(f"   ❌ Erreur login: {e}")
        return False, {"error": str(e)}

def main():
    """Fonction principale"""
    print("🌱 VITACHAIN - CRÉATION DES COMPTES DE TEST")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print(f"Nombre de comptes à créer: {len(TEST_ACCOUNTS)}")
    
    # Vérifier si le backend est accessible
    print(f"\n🏥 Vérification du backend...")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ Backend accessible")
        else:
            print(f"   ❌ Backend problème: {health_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Backend inaccessible: {e}")
        return
    
    # Création des comptes
    created_accounts = []
    failed_accounts = []
    
    for i, account in enumerate(TEST_ACCOUNTS, 1):
        print(f"\n{'='*50}")
        print(f"📊 Compte {i}/{len(TEST_ACCOUNTS)}")
        
        success, result = create_test_account(account)
        
        if success:
            created_accounts.append({
                "email": account["email"],
                "password": account["password"],
                "role": account["role"],
                "full_name": account["full_name"],
                "user_id": result.get("user_id")
            })
            
            # Test du login immédiatement après la création
            login_success, login_result = test_login(account)
            if not login_success:
                print(f"   ⚠️  Login échoué malgré la création réussie")
        else:
            failed_accounts.append({
                "email": account["email"],
                "role": account["role"],
                "error": result
            })
        
        # Pause entre les comptes pour éviter le rate limiting
        if i < len(TEST_ACCOUNTS):
            print(f"\n⏳ Pause de 10 secondes avant le prochain compte...")
            time.sleep(10)
    
    # Rapport final
    print(f"\n{'='*60}")
    print("📋 RAPPORT FINAL DE CRÉATION")
    print(f"{'='*60}")
    
    print(f"\n✅ Comptes créés avec succès ({len(created_accounts)}):")
    for account in created_accounts:
        print(f"   📧 {account['email']}")
        print(f"   🔐 Mot de passe: {account['password']}")
        print(f"   👤 Rôle: {account['role']}")
        print(f"   🆔 ID: {account.get('user_id', 'N/A')}")
        print()
    
    if failed_accounts:
        print(f"\n❌ Comptes échoués ({len(failed_accounts)}):")
        for account in failed_accounts:
            print(f"   📧 {account['email']}")
            print(f"   ❌ Erreur: {account['error']}")
            print()
    
    # Sauvegarder les comptes créés dans un fichier
    if created_accounts:
        with open("test_accounts_created.json", "w") as f:
            json.dump(created_accounts, f, indent=2)
        print(f"💾 Comptes sauvegardés dans: test_accounts_created.json")
    
    print(f"\n🎯 RÉSUMÉ:")
    print(f"   ✅ Créés: {len(created_accounts)}/{len(TEST_ACCOUNTS)}")
    print(f"   ❌ Échoués: {len(failed_accounts)}/{len(TEST_ACCOUNTS)}")
    
    if created_accounts:
        print(f"\n🚀 Les comptes de test sont prêts pour être utilisés!")
        print(f"   Attendez 30-60 minutes pour que le rate limiting Supabase se résolve")
        print(f"   Ensuite, vous pouvez tester l'authentification avec ces comptes")
    else:
        print(f"\n⚠️  Aucun compte n'a pu être créé. Réessayez plus tard.")

if __name__ == "__main__":
    main()
