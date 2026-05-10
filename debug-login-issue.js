// Debug du problème de connexion
async function debugLoginIssue() {
    console.log('🔍 Debug du problème de connexion\n');
    
    const baseURL = 'http://localhost:8000';
    
    // Étape 1: Vérifier les utilisateurs existants
    console.log('1. Vérification des utilisateurs existants...');
    try {
        const response = await fetch(`${baseURL}/api/auth/test-users`);
        const data = await response.json();
        
        if (response.ok) {
            console.log(`✅ ${data.count} utilisateur(s) trouvé(s):`);
            data.users.forEach(user => {
                console.log(`   📧 Email: ${user.email}`);
                console.log(`   🔑 Password: ${user.password.substring(0, 8)}...`);
                console.log(`   🎭 Role: ${user.role}`);
                console.log(`   🆔 ID: ${user.id}`);
                console.log('---');
            });
        } else {
            console.log('❌ Impossible de récupérer la liste des utilisateurs');
        }
    } catch (error) {
        console.log(`❌ Erreur: ${error.message}`);
    }
    
    // Étape 2: Test de connexion avec le premier utilisateur trouvé
    console.log('\n2. Test de connexion avec le premier utilisateur...');
    try {
        const usersResponse = await fetch(`${baseURL}/api/auth/test-users`);
        const usersData = await usersResponse.json();
        
        if (usersResponse.ok && usersData.users.length > 0) {
            const testUser = usersData.users[0];
            console.log(`🧪 Test avec: ${testUser.email}`);
            
            const loginData = {
                email: testUser.email,
                password: testUser.password
            };
            
            const loginResponse = await fetch(`${baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(loginData)
            });
            
            const loginResult = await loginResponse.json();
            console.log(`📝 Status connexion: ${loginResponse.status}`);
            console.log(`📄 Response: ${JSON.stringify(loginResult, null, 2)}`);
            
            if (loginResponse.ok) {
                console.log('✅ Connexion réussie !');
                console.log(`👤 Utilisateur: ${loginResult.user?.email}`);
                console.log(`🎭 Rôle: ${loginResult.user?.role}`);
            } else {
                console.log('❌ Connexion échouée');
                console.log(`🔍 Détails erreur: ${loginResult.detail?.message || loginResult.message}`);
                
                // Analyse du problème
                if (loginResult.detail?.code === 'INVALID_CREDENTIALS') {
                    console.log('💡 Problème: Identifiants invalides');
                    console.log('💡 Solution: Vérifiez email et mot de passe');
                } else if (loginResult.detail?.code === 'USER_NOT_FOUND') {
                    console.log('💡 Problème: Utilisateur non trouvé');
                    console.log('💡 Solution: Créez d\'abord le compte');
                } else {
                    console.log(`💡 Erreur inattendue: ${JSON.stringify(loginResult.detail)}`);
                }
            }
        } else {
            console.log('❌ Aucun utilisateur trouvé pour le test');
        }
    } catch (error) {
        console.log(`❌ Erreur test connexion: ${error.message}`);
    }
    
    // Étape 3: Test de création d'un nouvel utilisateur
    console.log('\n3. Test de création d\'un nouvel utilisateur...');
    try {
        const newUser = {
            email: `debug.test.${Date.now()}@vitachain.ma`,
            password: 'DebugTest123',
            role: 'FARMER',
            full_name: 'Debug Test User'
        };
        
        const registerResponse = await fetch(`${baseURL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newUser)
        });
        
        const registerResult = await registerResponse.json();
        console.log(`📝 Status inscription: ${registerResponse.status}`);
        
        if (registerResponse.ok) {
            console.log('✅ Nouvel utilisateur créé');
            console.log(`📧 Email: ${newUser.email}`);
            console.log(`🔑 Password: ${newUser.password}`);
            
            // Test immédiat de connexion
            console.log('\n4. Test de connexion immédiate...');
            const loginResponse2 = await fetch(`${baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    email: newUser.email,
                    password: newUser.password
                })
            });
            
            const loginResult2 = await loginResponse2.json();
            console.log(`📝 Status connexion 2: ${loginResponse2.status}`);
            
            if (loginResponse2.ok) {
                console.log('✅ Connexion immédiate réussie !');
            } else {
                console.log('❌ Connexion immédiate échouée');
                console.log(`🔍 Erreur: ${JSON.stringify(loginResult2.detail)}`);
            }
        } else {
            console.log('❌ Création utilisateur échouée');
            console.log(`🔍 Erreur: ${JSON.stringify(registerResult.detail)}`);
        }
    } catch (error) {
        console.log(`❌ Erreur création utilisateur: ${error.message}`);
    }
}

async function main() {
    console.log('🚀 Debug du problème de connexion VitaChain\n');
    
    await debugLoginIssue();
    
    console.log('\n📊 Analyse terminée');
    console.log('💡 Solutions possibles:');
    console.log('1. Vérifiez que vous utilisez le bon email/mot de passe');
    console.log('2. Assurez-vous que le compte a bien été créé');
    console.log('3. Essayez avec un nouvel utilisateur pour tester');
    console.log('4. Vérifiez les logs du backend pour plus de détails');
}

main().catch(console.error);
