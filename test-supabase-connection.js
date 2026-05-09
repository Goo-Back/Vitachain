// Test script for Supabase connection
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');

// Test configurations from different sources
const configs = [
  {
    name: 'Frontend Configuration',
    url: 'https://bgdtqvpchfnrscupyyaa.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnZHRxdnBjaGZucnNjdXB5eWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MDAzMDksImV4cCI6MjA2MDE3NjMwOX0.3XwPvCKt8B6P4J7Q2L9n8qK1s5x6g7h9j0k3l2m1n4o'
  },
  {
    name: 'Environment Example Configuration',
    url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co',
    anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'
  }
];

async function testConnection(config) {
  console.log(`\n=== Testing ${config.name} ===`);
  console.log(`URL: ${config.url}`);
  
  try {
    const supabase = createClient(config.url, config.anonKey);
    
    // Test basic connection
    const { data, error } = await supabase.from('_info_').select('*').limit(1);
    
    if (error) {
      console.log(`❌ Connection failed: ${error.message}`);
      return false;
    }
    
    // Test health check
    const { data: healthData, error: healthError } = await supabase.rpc('get_schema_version');
    
    if (healthError && healthError.message.includes('function')) {
      console.log(`⚠️  Health check function not found, but connection is working`);
    } else if (healthError) {
      console.log(`❌ Health check failed: ${healthError.message}`);
    } else {
      console.log(`✅ Health check passed: ${healthData}`);
    }
    
    console.log(`✅ Connection successful`);
    return true;
    
  } catch (error) {
    console.log(`❌ Connection error: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('🔍 Testing Supabase connections...\n');
  
  let workingConfig = null;
  
  for (const config of configs) {
    const isWorking = await testConnection(config);
    if (isWorking) {
      workingConfig = config;
    }
  }
  
  if (workingConfig) {
    console.log(`\n✅ Working configuration found: ${workingConfig.name}`);
    console.log('📝 You should update your configurations to use this working setup.');
  } else {
    console.log('\n❌ No working configuration found.');
    console.log('🔧 Please check your Supabase project settings and API keys.');
  }
}

main().catch(console.error);
