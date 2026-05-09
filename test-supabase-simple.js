// Simple test for Supabase connection
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');

async function testBasicConnection(url, anonKey, configName) {
  console.log(`\n=== Testing ${configName} ===`);
  console.log(`URL: ${url}`);
  console.log(`Key: ${anonKey.substring(0, 20)}...`);
  
  try {
    const supabase = createClient(url, anonKey);
    
    // Test with a simple health check
    const { data, error } = await supabase
      .from('pg_tables')
      .select('tablename')
      .eq('schemaname', 'public')
      .limit(1);
    
    if (error) {
      console.log(`❌ Connection failed: ${error.message}`);
      return false;
    }
    
    console.log(`✅ Connection successful!`);
    console.log(`📊 Found tables: ${data.length > 0 ? data[0].tablename : 'None'}`);
    return true;
    
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('🔍 Testing Supabase connections with simple method...\n');
  
  // Test configurations
  const configs = [
    {
      name: 'Frontend Configuration',
      url: 'https://bgdtqvpchfnrscupyyaa.supabase.co',
      key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnZHRxdnBjaGZucnNjdXB5eWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MDAzMDksImV4cCI6MjA2MDE3NjMwOX0.3XwPvCKt8B6P4J7Q2L9n8qK1s5x6g7h9j0k3l2m1n4o'
    },
    {
      name: 'Environment Example Configuration',
      url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
      key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'
    }
  ];
  
  let workingConfigs = [];
  
  for (const config of configs) {
    const isWorking = await testBasicConnection(config.url, config.key, config.name);
    if (isWorking) {
      workingConfigs.push(config);
    }
  }
  
  if (workingConfigs.length > 0) {
    console.log(`\n✅ Found ${workingConfigs.length} working configuration(s):`);
    workingConfigs.forEach(config => {
      console.log(`  - ${config.name}`);
    });
  } else {
    console.log('\n❌ No working configurations found.');
    console.log('🔧 Please check:');
    console.log('   1. Supabase project URL is correct');
    console.log('   2. API keys are valid and not expired');
    console.log('   3. Project is active and not paused');
  }
}

main().catch(console.error);
