/**
 * Registration script for Consciousness Field MCP Server
 * 
 * This script registers the MCP server with the main MCP registry,
 * making it discoverable by other components in the ADAPT.ai ecosystem.
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');

// Load configuration
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'mcp-config.json'), 'utf8'));

// Get server information
const hostname = os.hostname();
const serverPort = process.env.PORT || 3100;
const serverUrl = `http://${hostname}:${serverPort}`;

console.log(`Registering Consciousness Field MCP Server at ${serverUrl}`);

// Create registration data
const registrationData = {
  server_name: config.name,
  server_description: config.description,
  server_version: config.version,
  server_url: serverUrl,
  tools: config.tools.map(tool => ({
    name: tool.name,
    description: tool.description
  })),
  resources: config.resources.map(resource => ({
    name: resource.name,
    description: resource.description,
    uri_template: resource.uri_template
  })),
  status: "active",
  registration_time: new Date().toISOString()
};

// Write registration data to file
const registrationFile = path.join(__dirname, 'registration.json');
fs.writeFileSync(registrationFile, JSON.stringify(registrationData, null, 2));

console.log(`Registration data written to ${registrationFile}`);

// Optional: Submit registration to central registry if available
try {
  const registryUrl = process.env.MCP_REGISTRY_URL;
  if (registryUrl) {
    console.log(`Submitting registration to central registry at ${registryUrl}`);
    
    // Command to submit registration
    const command = `curl -X POST -H "Content-Type: application/json" -d @${registrationFile} ${registryUrl}/register`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Registration error: ${error.message}`);
        console.error(`Consider manually registering using the registration.json file`);
        return;
      }
      
      if (stderr) {
        console.error(`Registration warning: ${stderr}`);
      }
      
      console.log(`Registration response: ${stdout}`);
      console.log(`Server successfully registered with central MCP registry`);
    });
  } else {
    console.log('MCP_REGISTRY_URL not set. Skipping central registry registration.');
    console.log('To register with central registry, set MCP_REGISTRY_URL and run:');
    console.log(`curl -X POST -H "Content-Type: application/json" -d @${registrationFile} [MCP_REGISTRY_URL]/register`);
  }
} catch (error) {
  console.error(`Registration attempt error: ${error.message}`);
  console.log('Manual registration may be required');
}

console.log('Consciousness Field MCP server registration complete');
console.log(`Server is accessible at ${serverUrl}`);
console.log('Tools available:');
config.tools.forEach(tool => {
  console.log(`- ${tool.name}: ${tool.description}`);
});
