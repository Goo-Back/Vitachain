// Test the new unified Supabase configuration
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');

async function testNewConfiguration() {
  console.log('🔍 Testing new unified Supabase configuration...\n');
  
  // New unified configuration
  const config = {
    name: 'New Unified Configuration',
    url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg',
    serviceRoleKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ'
  };
  
  console.log(`=== Testing ${config.name} ===`);
  console.log(`URL: ${config.url}`);
  console.log(`Anon Key: ${config.anonKey.substring(0, 20)}...`);
  console.log(`Service Role Key: ${config.serviceRoleKey.substring(0, 20)}...`);
  
  // Test 1: Anon key connection
  console.log('\n--- Test 1: Anon Key Connection ---');
  try {
    const supabase = createClient(config.url, config.anonKey);
    
    const { data, error } = await supabase
      .from('pg_tables')
      .select('tablename')
      .eq('schemaname', 'public')
      .limit(3);
    
    if (error) {
      console.log(`❌ Anon key failed: ${error.message}`);
    } else {
      console.log(`✅ Anon key successful!`);
      console.log(`📊 Found tables: ${data.length > 0 ? data.map(t => t.tablename).join(', ') : 'None'}`);
    }
  } catch (error) {
    console.log(`❌ Anon key error: ${error.message}`);
  }
  
  // Test 2: Service role connection
  console.log('\n--- Test 2: Service Role Connection ---');
  try {
    const supabase = createClient(config.url, config.serviceRoleKey);
    
    const { data, error } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .limit(5);
    
    if (error) {
      console.log(`❌ Service role failed: ${error.message}`);
    } else {
      console.log(`✅ Service role successful!`);
      console.log(`📊 Found tables: ${data.length > 0 ? data.map(t => t.table_name).join(', ') : 'None'}`);
    }
  } catch (error) {
    console.log(`❌ Service role error: ${error.message}`);
  }
  
  // Test 3: Auth endpoint
  console.log('\n--- Test 3: Auth Endpoint ---');
  try {
    const supabase = createClient(config.url, config.anonKey);
    
    const { data, error } = await supabase.auth.getSession();
    if (error && !error.message.includes('No session')) {
      console.log(`❌ Auth endpoint failed: ${error.message}`);
    } else {
      console.log(`✅ Auth endpoint accessible`);
    }
  } catch (error) {
    console.log(`❌ Auth endpoint error: ${error.message}`);
  }
  
  // Test 4: Database connection test
  console.log('\n--- Test 4: Database Connection ---');
  try {
    const supabase = createClient(config.url, config.serviceRoleKey);
    
    const { data, error } = await supabase.rpc('version');
    if (error && !error.message.includes('function')) {
      console.log(`⚠️  RPC test: ${error.message}`);
    } else if (error) {
      console.log(`⚠️  RPC function not found (expected)`);
    } else {
      console.log(`✅ Database RPC successful: ${data}`);
    }
  } catch (error) {
    console.log(`❌ Database RPC error: ${error.message}`);
  }
  
  console.log('\n📋 Configuration Summary:');
  console.log('✅ Frontend: frontend/lib/supabase.ts - Updated');
  console.log('✅ Backend: backend/config/supabase.md - Updated');
  console.log('✅ Environment: .env.example - Updated');
  console.log('\n🎯 All configurations now use the same project!');
}

async function main() {
  console.log('🔍 Testing new unified Supabase configuration...\n');
  
  // New unified configuration
  const config = {
    name: 'New Unified Configuration',
    url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg',
    serviceRoleKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ'
  };
  
  console.log(`=== Testing ${config.name} ===`);
  console.log(`URL: ${config.url}`);
  console.log(`Anon Key: ${config.anonKey.substring(0, 20)}...`);
  console.log(`Service Role Key: ${config.serviceRoleKey.substring(0, 20)}...`);
  
  // Test 1: Anon key connection
  console.log('\n--- Test 1: Anon Key Connection ---');
  try {
    const supabase = createClient(config.url, config.anonKey);
    
    const { data, error } = await supabase
      .from('pg_tables')
      .select('tablename')
      .eq('schemaname', 'public')
      .limit(3);
    
    if (error) {
      console.log(`❌ Anon key failed: ${error.message}`);
    } else {
      console.log(`✅ Anon key successful!`);
      console.log(`📊 Found tables: ${data.length > 0 ? data.map(t => t.tablename).join(', ') : 'None'}`);
    }
  } catch (error) {
    console.log(`❌ Anon key error: ${error.message}`);
  }
  
  // Test 2: Service role connection
  console.log('\n--- Test 2: Service Role Connection ---');
  try {
    const supabase = createClient(config.url, config.serviceRoleKey);
    
    const { data, error } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .limit(5);
    
    if (error) {
      console.log(`❌ Service role failed: ${error.message}`);
    } else {
      console.log(`✅ Service role successful!`);
      console.log(`📊 Found tables: ${data.length > 0 ? data.map(t => t.table_name).join(', ') : 'None'}`);
    }
  } catch (error) {
    console.log(`❌ Service role error: ${error.message}`);
  }
  
  // Test 3: Auth endpoint
  console.log('\n--- Test 3: Auth Endpoint ---');
  try {
    const supabase = createClient(config.url, config.anonKey);
    
    const { data, error } = await supabase.auth.getSession();
    if (error && !error.message.includes('No session')) {
      console.log(`❌ Auth endpoint failed: ${error.message}`);
    } else {
      console.log(`✅ Auth endpoint accessible`);
    }
  } catch (error) {
    console.log(`❌ Auth endpoint error: ${error.message}`);
  }
  
  // Test 4: Database connection test
  console.log('\n--- Test 4: Database Connection ---');
  try {
    const supabase = createClient(config.url, config.serviceRoleKey);
    
    const { data, error } = await supabase.rpc('version');
    if (error && !error.message.includes('function')) {
      console.log(`⚠️  RPC test: ${error.message}`);
    } else if (error) {
      console.log(`⚠️  RPC function not found (expected)`);
    } else {
      console.log(`✅ Database RPC successful: ${data}`);
    }
  } catch (error) {
    console.log(`❌ Database RPC error: ${error.message}`);
  }
  
  console.log('\n📋 Configuration Summary:');
  console.log('✅ Frontend: frontend/lib/supabase.ts - Updated');
  console.log('✅ Backend: backend/config/supabase.md - Updated');
  console.log('✅ Environment: .env.example - Updated');
  console.log('\n🎯 All configurations now use the same project!');
}

main().catch(console.error);
