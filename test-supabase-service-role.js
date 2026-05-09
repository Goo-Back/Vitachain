// Test Supabase connection with service role key
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');

async function testServiceRoleConnection(url, serviceRoleKey, configName) {
  console.log(`\n=== Testing ${configName} (Service Role) ===`);
  console.log(`URL: ${url}`);
  console.log(`Key: ${serviceRoleKey.substring(0, 20)}...`);
  
  try {
    const supabase = createClient(url, serviceRoleKey);
    
    // Test with system tables access
    const { data, error } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .limit(5);
    
    if (error) {
      console.log(`❌ Connection failed: ${error.message}`);
      return false;
    }
    
    console.log(`✅ Service role connection successful!`);
    console.log(`📊 Found tables: ${data.length > 0 ? data.map(t => t.table_name).join(', ') : 'None'}`);
    
    // Test auth endpoint
    const { data: authData, error: authError } = await supabase.auth.getSession();
    if (authError && !authError.message.includes('No session')) {
      console.log(`⚠️  Auth endpoint issue: ${authError.message}`);
    } else {
      console.log(`✅ Auth endpoint accessible`);
    }
    
    return true;
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('🔍 Testing Supabase connections with Service Role keys...\n');
  
  // Test configurations with service role keys
  const configs = [
    {
      name: 'Environment Example (Service Role)',
      url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
      serviceRoleKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODMxODcyNiwiZXhwIjoyMDkzODk0NzI2fQ.R4bQF2C0t4sRAjpI1vocoPvGkhpdb0OM_IBypMupccQ'
    }
  ];
  
  let workingConfigs = [];
  
  for (const config of configs) {
    const isWorking = await testServiceRoleConnection(config.url, config.serviceRoleKey, config.name);
    if (isWorking) {
      workingConfigs.push(config);
    }
  }
  
  if (workingConfigs.length > 0) {
    console.log(`\n✅ Working service role configurations found:`);
    workingConfigs.forEach(config => {
      console.log(`  - ${config.name}: ${config.url}`);
    });
    console.log('\n💡 This means the project exists but anon key may be restricted');
  } else {
    console.log('\n❌ No working service role configurations found.');
    console.log('🔧 The project may be paused, deleted, or keys completely invalid');
  }
}

main().catch(console.error);
