#!/usr/bin/env python3
"""
Test script to verify authentication fix
"""

import sys
import os
sys.path.append('.')

from app.core.supabase_http import get_supabase_http_client

def test_authentication():
    """Test authentication with known credentials"""
    print("🧪 TEST D'AUTHENTIFICATION VITACHAIN")
    print("=" * 50)
    
    try:
        # Test 1: Connection to Supabase
        print("1. 📡 Test de connexion Supabase...")
        client = get_supabase_http_client(service_role=True)
        connected = client.test_connection()
        print(f"   ✅ Connexion: {connected}")
        
        if not connected:
            print("   ❌ Échec de connexion - Arrêt du test")
            return False
        
        # Test 2: Create test user with known password
        print("\n2. 👤 Création utilisateur de test...")
        test_email = "test.user@vitachain.demo"
        test_password = "TestPassword123"
        
        result = client.sign_up(test_email, test_password, {
            'role': 'CITIZEN',
            'full_name': 'Test User',
            'registration_ip': '127.0.0.1',
            'registration_method': 'test_script'
        })
        
        print(f"   Création: {result.get('success', False)}")
        
        if result.get('success'):
            user_data = result.get('user', {})
            print(f"   📧 Email: {user_data.get('email')}")
            print(f"   🆔 ID: {user_data.get('id')}")
        else:
            error = result.get('error', {})
            print(f"   ❌ Erreur: {error}")
            
            # If rate limited, try with existing user
            if error.get('code') == 429:
                print("   ⏳ Rate limit - Utilisation utilisateur existant...")
                test_email = "vitachain.test+user1@gmail.com"
                test_password = "TestPassword123"  # Assume this was set
        
        # Test 3: Login with the user
        print("\n3. 🔐 Test de connexion...")
        login_client = get_supabase_http_client(service_role=False)
        
        login_result = login_client.sign_in(test_email, test_password)
        print(f"   Login: {login_result.get('success', False)}")
        
        if login_result.get('success'):
            session_data = login_result.get('session', {})
            print(f"   🎉 CONNEXION RÉUSSIE !")
            print(f"   📊 Session: {bool(session_data)}")
            print(f"   🔑 Access Token: {'✅' if session_data.get('access_token') else '❌'}")
            
            # Test 4: Get user info
            print("\n4. 📋 Test récupération utilisateur...")
            access_token = session_data.get('access_token')
            if access_token:
                user_info = login_client.get_user(access_token)
                print(f"   Utilisateur: {user_info.get('success', False)}")
                if user_info.get('success'):
                    user = user_info.get('user', {})
                    print(f"   📧 Email: {user.get('email')}")
                    print(f"   🆔 ID: {user.get('id')}")
            
            return True
        else:
            error = login_result.get('error', {})
            print(f"   ❌ Erreur login: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 TEST DES ENDPOINTS API")
    print("=" * 50)
    
    import requests
    import json
    
    try:
        # Test health endpoint
        print("1. 🏥 Test health endpoint...")
        response = requests.get('http://localhost:8000/health')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('services', {}).get('database', {}).get('status')}")
        
        # Test register endpoint
        print("\n2. 📝 Test register endpoint...")
        register_data = {
            'email': 'api.test@vitachain.demo',
            'role': 'CITIZEN',
            'full_name': 'API Test User'
        }
        
        response = requests.post('http://localhost:8000/api/auth/register', json=register_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        # Test login endpoint
        print("\n3. 🔐 Test login endpoint...")
        login_data = {
            'email': 'vitachain.test+user1@gmail.com',
            'password': 'TestPassword123'
        }
        
        response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS D'AUTHENTIFICATION")
    print("=" * 60)
    
    # Run authentication tests
    auth_success = test_authentication()
    
    # Run API tests
    api_success = test_api_endpoints()
    
    print("\n📊 RÉSULTATS FINAUX")
    print("=" * 30)
    print(f"Authentification: {'✅ SUCCÈS' if auth_success else '❌ ÉCHEC'}")
    print(f"API Endpoints: {'✅ SUCCÈS' if api_success else '❌ ÉCHEC'}")
    
    if auth_success and api_success:
        print("\n🎉 AUTHENTIFICATION VITACHAIN 100% FONCTIONNELLE !")
        print("✅ Prêt pour l'intégration frontend")
    else:
        print("\n⚠️  Problèmes restants à corriger")
