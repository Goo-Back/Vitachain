// Test Supabase project health and availability
const https = require('https');

function testProjectHealth(url, configName) {
  return new Promise((resolve) => {
    console.log(`\n=== Testing ${configName} Health ===`);
    console.log(`URL: ${url}`);
    
    // Test basic project availability
    const options = {
      method: 'GET',
      headers: {
        'User-Agent': 'VitaChain-Health-Check/1.0'
      }
    };

    const req = https.request(`${url}/health`, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log(`📊 Health endpoint status: ${res.statusCode}`);
        if (res.statusCode === 200) {
          console.log(`✅ Project is active and healthy`);
          console.log(`📄 Response: ${data}`);
          resolve({ status: 'healthy', statusCode: res.statusCode, data });
        } else if (res.statusCode === 404) {
          console.log(`⚠️  Health endpoint not found, but project may be active`);
          resolve({ status: 'unknown', statusCode: res.statusCode, data });
        } else {
          console.log(`❌ Health check failed`);
          resolve({ status: 'unhealthy', statusCode: res.statusCode, data });
        }
      });
    });

    req.on('error', (error) => {
      console.log(`❌ Network error: ${error.message}`);
      resolve({ status: 'error', error: error.message });
    });

    req.setTimeout(10000, () => {
      console.log(`❌ Request timeout`);
      req.destroy();
      resolve({ status: 'timeout' });
    });

    req.end();
  });
}

function testRestEndpoint(url, configName) {
  return new Promise((resolve) => {
    console.log(`\n=== Testing ${configName} REST API ===`);
    
    const options = {
      method: 'GET',
      headers: {
        'User-Agent': 'VitaChain-Health-Check/1.0'
      }
    };

    const req = https.request(`${url}/rest/v1/`, options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log(`📊 REST API status: ${res.statusCode}`);
        if (res.statusCode === 200) {
          console.log(`✅ REST API is accessible`);
          resolve({ status: 'accessible', statusCode: res.statusCode });
        } else if (res.statusCode === 401) {
          console.log(`⚠️  REST API requires authentication (expected)`);
          resolve({ status: 'requires_auth', statusCode: res.statusCode });
        } else {
          console.log(`❌ REST API not accessible`);
          resolve({ status: 'not_accessible', statusCode: res.statusCode });
        }
      });
    });

    req.on('error', (error) => {
      console.log(`❌ Network error: ${error.message}`);
      resolve({ status: 'error', error: error.message });
    });

    req.setTimeout(10000, () => {
      console.log(`❌ Request timeout`);
      req.destroy();
      resolve({ status: 'timeout' });
    });

    req.end();
  });
}

async function main() {
  console.log('🏥 Testing Supabase Project Health...\n');
  
  const configs = [
    {
      name: 'Frontend Project',
      url: 'https://bgdtqvpchfnrscupyyaa.supabase.co'
    },
    {
      name: 'Environment Example Project',
      url: 'https://ymogoemuzqyjsdjhzpnz.supabase.co'
    }
  ];
  
  for (const config of configs) {
    console.log(`\n${'='.repeat(50)}`);
    console.log(`Testing: ${config.name}`);
    console.log(`${'='.repeat(50)}`);
    
    const healthResult = await testProjectHealth(config.url, config.name);
    const restResult = await testRestEndpoint(config.url, config.name);
    
    // Summary
    console.log(`\n📋 Summary for ${config.name}:`);
    if (healthResult.status === 'healthy' || healthResult.status === 'unknown') {
      if (restResult.status === 'requires_auth' || restResult.status === 'accessible') {
        console.log(`✅ Project appears to be ACTIVE and accessible`);
        console.log(`💡 The issue is likely with API keys, not project availability`);
      } else {
        console.log(`⚠️  Project may have issues with REST API`);
      }
    } else {
      console.log(`❌ Project appears to be INACTIVE or has network issues`);
    }
  }
}

main().catch(console.error);
