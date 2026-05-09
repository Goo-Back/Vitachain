#!/usr/bin/env python3
"""
Script pour attendre la résolution du rate limiting Supabase et créer des comptes de test
"""

import time
import requests
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

def check_rate_limit_resolved():
    """Vérifie si le rate limiting est résolu"""
    print("🕐 Vérification du rate limiting...")
    
    test_data = {
        "email": f"test.rate.limit.check@vitachain.demo",
        "password": "TestCheck123!",
        "role": "CITIZEN",
        "full_name": "Rate Limit Check Test"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Rate limiting résolu!")
            return True
        elif response.status_code == 500:
            error_result = response.json()
            if "rate limit" in str(error_result).lower() or "too many" in str(error_result).lower():
                print("   ❌ Rate limiting toujours actif")
                return False
            else:
                print("   ⚠️  Erreur 500 mais peut-être pas rate limiting")
                return False
        else:
            print(f"   ⚠️  Status inattendu: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def wait_for_rate_limit_resolution(max_wait_minutes=60):
    """Attend la résolution du rate limiting"""
    print(f"⏳ Attente de la résolution du rate limiting (max {max_wait_minutes} minutes)...")
    
    start_time = time.time()
    check_interval = 300  # 5 minutes
    
    while True:
        elapsed_minutes = (time.time() - start_time) / 60
        
        if elapsed_minutes >= max_wait_minutes:
            print(f"⏰ Temps d'attente maximum ({max_wait_minutes} minutes) atteint")
            return False
        
        if check_rate_limit_resolved():
            return True
        
        remaining_wait = max_wait_minutes - elapsed_minutes
        print(f"   ⏱️  Attendu {elapsed_minutes:.1f} minutes, reste {remaining_wait:.1f} minutes")
        print(f"   💤 Prochain check dans {check_interval/60} minutes...")
        
        time.sleep(check_interval)

def create_account(account_data):
    """Crée un compte de test"""
    print(f"\n📝 Création du compte: {account_data['role']} - {account_data['email']}")
    
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
            return True, result
        else:
            error_result = response.json()
            print(f"   ❌ Erreur: {error_result}")
            return False, error_result
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False, {"error": str(e)}

def main():
    """Fonction principale"""
    print("🌱 VITACHAIN - ATTENTE ET CRÉATION DES COMPTES DE TEST")
    print("=" * 60)
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
    
    # Attendre la résolution du rate limiting
    print(f"\n🕐 PHASE 1: Attente du rate limiting Supabase")
    print("=" * 50)
    
    if not wait_for_rate_limit_resolution(max_wait_minutes=60):
        print("\n❌ Le rate limiting n'a pas pu être résolu dans le temps imparti")
        print("💡 Options:")
        print("   1. Attendre plus longtemps (30-60 minutes supplémentaires)")
        print("   2. Créer manuellement les comptes via le dashboard Supabase")
        print("   3. Utiliser des comptes existants pour les tests")
        return
    
    # Création des comptes
    print(f"\n📝 PHASE 2: Création des comptes de test")
    print("=" * 50)
    
    created_accounts = []
    failed_accounts = []
    
    for i, account in enumerate(TEST_ACCOUNTS, 1):
        print(f"\n{'='*50}")
        print(f"📊 Compte {i}/{len(TEST_ACCOUNTS)}")
        
        success, result = create_account(account)
        
        if success:
            created_accounts.append({
                "email": account["email"],
                "password": account["password"],
                "role": account["role"],
                "full_name": account["full_name"],
                "user_id": result.get("user_id")
            })
        else:
            failed_accounts.append({
                "email": account["email"],
                "role": account["role"],
                "error": result
            })
        
        # Pause entre les comptes
        if i < len(TEST_ACCOUNTS):
            print(f"\n⏳ Pause de 5 secondes...")
            time.sleep(5)
    
    # Rapport final
    print(f"\n{'='*60}")
    print("📋 RAPPORT FINAL")
    print(f"{'='*60}")
    
    if created_accounts:
        print(f"\n✅ Comptes créés avec succès ({len(created_accounts)}):")
        for account in created_accounts:
            print(f"   📧 {account['email']}")
            print(f"   🔐 Mot de passe: {account['password']}")
            print(f"   👤 Rôle: {account['role']}")
            print(f"   🆔 ID: {account.get('user_id', 'N/A')}")
            print()
        
        # Sauvegarder les comptes
        with open("test_accounts_ready.json", "w") as f:
            json.dump(created_accounts, f, indent=2)
        print(f"💾 Comptes sauvegardés dans: test_accounts_ready.json")
        
        print(f"\n🚀 UTILISATION DES COMPTES:")
        print(f"   Frontend: http://localhost:3010/auth/login")
        print(f"   Utilisez les emails et mots de passe ci-dessus")
        
    else:
        print(f"\n❌ Aucun compte n'a pu être créé")
    
    if failed_accounts:
        print(f"\n❌ Comptes échoués ({len(failed_accounts)}):")
        for account in failed_accounts:
            print(f"   📧 {account['email']}")
            print(f"   ❌ Erreur: {account['error']}")
    
    print(f"\n🎯 RÉSUMÉ:")
    print(f"   ✅ Créés: {len(created_accounts)}/{len(TEST_ACCOUNTS)}")
    print(f"   ❌ Échoués: {len(failed_accounts)}/{len(TEST_ACCOUNTS)}")

if __name__ == "__main__":
    main()
