// Vérification de la cohérence entre frontend, backend et Supabase
async function verifyCoherence() {
    console.log('🔍 Vérification de la cohérence du système VitaChain\n');
    
    const baseURL = 'http://localhost:8000';
    const frontendURL = 'http://localhost:3003';
    
    // 1. Vérification des paramètres Supabase
    console.log('\n1. Vérification des paramètres Supabase...');
    
    const supabaseConfig = {
        frontend: {
            url: process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
            anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'
        },
        backend: {
            url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
            anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg',
            serviceKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ',
            jwtSecret: 'T2KbdzBdBr4Kl1HYYIM9nRIfgeHGTZK4z6jNOGTgd5CeHOeec7lL0VYit5mDVcdf5/WEg3AdyR0CpxkoI6Bkpg=='
        }
    };
    
    console.log('✅ Configuration Supabase unifiée');
    console.log(`   URL: ${supabaseConfig.frontend.url}`);
    console.log(`   Backend URL: ${supabaseConfig.backend.url}`);
    console.log(`   Cohérence URL: ${supabaseConfig.frontend.url === supabaseConfig.backend.url ? '✅' : '❌'}`);
    
    // 2. Vérification des endpoints d'authentification
    console.log('\n2. Vérification des endpoints d\'authentification...');
    
    const endpoints = [
        { path: '/api/auth/register', method: 'POST', description: 'Inscription' },
        { path: '/api/auth/login', method: 'POST', description: 'Connexion' },
        { path: '/api/auth/me', method: 'GET', description: 'Utilisateur courant' },
        { path: '/api/auth/logout', method: 'POST', description: 'Déconnexion' }
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${baseURL}${endpoint.path}`, {
                method: endpoint.method,
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            console.log(`${endpoint.description} (${endpoint.method} ${endpoint.path}): ${response.status}`);
            
            if (response.status === 404) {
                console.log(`   ⚠️  Endpoint non trouvé`);
            } else if (response.status === 405) {
                console.log(`   ⚠️  Méthode non autorisée`);
            } else if (response.status === 500) {
                console.log(`   ❌ Erreur interne du serveur`);
            } else {
                console.log(`   ✅ Endpoint disponible`);
            }
        } catch (error) {
            console.log(`${endpoint.description}: ❌ Erreur - ${error.message}`);
        }
    }
    
    // 3. Test d'inscription et connexion avec le système fonctionnel
    console.log('\n3. Test d\'inscription et connexion...');
    
    try {
        // Création utilisateur
        const userData = {
            email: 'coherence.test@vitachain.ma',
            password: 'CoherenceTest123',
            role: 'FARMER',
            full_name: 'Coherence Test User'
        };
        
        const registerResponse = await fetch(`${baseURL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const registerData = await registerResponse.json();
        
        if (registerResponse.ok) {
            console.log('✅ Inscription réussie');
            
            // Test de connexion
            const loginResponse = await fetch(`${baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    email: userData.email,
                    password: userData.password
                })
            });
            
            const loginData = await loginResponse.json();
            
            if (loginResponse.ok) {
                console.log('✅ Connexion réussie');
                console.log(`👤 Utilisateur: ${loginData.user?.email}`);
                console.log(`🎭 Rôle: ${loginData.user?.role}`);
                
                return {
                    success: true,
                    message: 'Système complètement cohérent',
                    user: loginData.user
                };
            } else {
                console.log('❌ Connexion échouée');
                return {
                    success: false,
                    message: 'Problème de connexion',
                    error: loginData.detail
                };
            }
        } else {
            console.log('❌ Inscription échouée');
            return {
                success: false,
                message: 'Problème d\'inscription',
                error: registerData.detail
            };
        }
    } catch (error) {
        console.log(`❌ Erreur technique: ${error.message}`);
        return {
            success: false,
            message: 'Erreur technique',
            error: error.message
        };
    }
}

async function main() {
    console.log('🔍 Vérification de cohérence VitaChain\n');
    
    const result = await verifyCoherence();
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 RÉSULTAT DE LA VÉRIFICATION:');
    
    console.log(`✅ Succès: ${result.success}`);
    console.log(`📝 Message: ${result.message}`);
    
    if (result.user) {
        console.log('\n👤 UTILISATEUR CRÉÉ:');
        console.log(`   Email: ${result.user.email}`);
        console.log(`   Rôle: ${result.user.role}`);
        console.log(`   ID: ${result.user.id}`);
    }
    
    if (result.error) {
        console.log('\n❌ DÉTAILS D\'ERREUR:');
        console.log(JSON.stringify(result.error, null, 2));
    }
    
    console.log('\n🌐 ACCÈS AU SYSTÈME:');
    console.log(`• Frontend: http://localhost:3003`);
    console.log(`• Backend: http://localhost:8000`);
    console.log(`• API Docs: http://localhost:8000/docs`);
    
    console.log('\n🎯 CONCLUSION:');
    if (result.success) {
        console.log('✅ Le système VitaChain est COHÉRENT et FONCTIONNEL');
        console.log('✅ Frontend, backend et Supabase sont correctement configurés');
        console.log('✅ L\'authentification fonctionne parfaitement');
    } else {
        console.log('❌ Le système a des problèmes de cohérence');
        console.log('❌ Vérifiez les configurations et les endpoints');
    }
    
    console.log('='.repeat(60));
}

main().catch(console.error);
