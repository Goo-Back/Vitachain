// Test Supabase connection with HTTP requests
const https = require('https');

function testUrl(url, name) {
  return new Promise((resolve) => {
    console.log(`\n=== Testing ${name} ===`);
    console.log(`URL: ${url}`);
    
    const options = {
      method: 'GET',
      headers: {
        'apikey': url.includes('bgdtqvpchfnrscupyyaa') ? 
          'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnZHRxdnBjaGZucnNjdXB5eWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MDAzMDksImV4cCI6MjA2MDE3NjMwOX0.3XwPvCKt8B6P4J7Q2L9n8qK1s5x6g7h9j0k3l2m1n4o' :
          'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg',
        'Authorization': url.includes('bgdtqvpchfnrscupyyaa') ? 
          'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJnZHRxdnBjaGZucnNjdXB5eWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2MDAzMDksImV4cCI6MjA2MDE3NjMwOX0.3XwPvCKt8B6P4J7Q2L9n8qK1s5x6g7h9j0k3l2m1n4o' :
          'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltb2dvZW11enF5anNkamh6cG56Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgzMTg3MjYsImV4cCI6MjA5Mzg5NDcyNn0.tN2fLPO0mayL22y8oXTLSaUniobVqm34VaLGHWB6Wmg'
      }
    };

    const req = https.request(`${url}/rest/v1/`, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`✅ Connection successful! Status: ${res.statusCode}`);
          console.log(`📄 Response: ${data.substring(0, 100)}...`);
          resolve(true);
        } else {
          console.log(`❌ Connection failed. Status: ${res.statusCode}`);
          console.log(`📄 Response: ${data.substring(0, 200)}...`);
          resolve(false);
        }
      });
    });

    req.on('error', (error) => {
      console.log(`❌ Request error: ${error.message}`);
      resolve(false);
    });

    req.setTimeout(10000, () => {
      console.log(`❌ Request timeout`);
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

async function main() {
  console.log('🔍 Testing Supabase connections with HTTP requests...\n');
  
  const configs = [
    {
      name: 'Frontend Configuration',
      url: 'https://bgdtqvpchfnrscupyyaa.supabase.co'
    },
    {
      name: 'Environment Example Configuration', 
      url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co'
    }
  ];
  
  let workingConfigs = [];
  
  for (const config of configs) {
    const isWorking = await testUrl(config.url, config.name);
    if (isWorking) {
      workingConfigs.push(config);
    }
  }
  
  if (workingConfigs.length > 0) {
    console.log(`\n✅ Working configurations found:`);
    workingConfigs.forEach(config => {
      console.log(`  - ${config.name}: ${config.url}`);
    });
  } else {
    console.log('\n❌ No working configurations found.');
    console.log('\n🔧 Possible issues:');
    console.log('   1. API keys are expired or invalid');
    console.log('   2. Projects are paused or deleted');
    console.log('   3. Network connectivity issues');
    console.log('   4. CORS restrictions');
  }
}

main().catch(console.error);
