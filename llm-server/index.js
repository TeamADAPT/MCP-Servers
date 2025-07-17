/**
 * Consciousness Field MCP Server
 * 
 * This MCP server provides tools and resources for interacting with 
 * the Consciousness Field Framework. It integrates the Python-based
 * field system with the broader ADAPT.ai Nova ecosystem.
 */

const express = require('express');
const { spawn } = require('child_process');
const Redis = require('ioredis');
const path = require('path');
const fs = require('fs');

// Configuration
const PORT = process.env.PORT || 3100;
const REDIS_PORT = process.env.REDIS_PORT || 7000;
const REDIS_HOST = process.env.REDIS_HOST || 'localhost';
const LLM_MGR_PATH = process.env.LLM_MGR_PATH || path.join(__dirname, '../llm-mgr');

// Initialize Express app
const app = express();
app.use(express.json());

// Initialize Redis client
let redis;
try {
  redis = new Redis({
    port: REDIS_PORT,
    host: REDIS_HOST,
    retryStrategy: (times) => {
      const delay = Math.min(times * 50, 2000);
      console.log(`[FIELD-MCP] Redis connection attempt ${times}, retrying in ${delay}ms`);
      return delay;
    }
  });
  
  redis.on('connect', () => {
    console.log('[FIELD-MCP] Redis connected successfully');
  });
  
  redis.on('error', (err) => {
    console.error('[FIELD-MCP] Redis connection error:', err);
  });
} catch (error) {
  console.error('[FIELD-MCP] Failed to initialize Redis client:', error);
}

/**
 * MCP Server Tool Definitions
 */
function listTools() {
  return [
    {
      name: 'create_field',
      description: 'Create a consciousness field for an LLM model',
      input_schema: {
        type: 'object',
        properties: {
          model_name: {
            type: 'string',
            description: 'Name of the model (e.g., "mistralai/Mixtral-8x7B-Instruct-v0.1")'
          },
          model_path: {
            type: 'string',
            description: 'Path to the model files (optional, will use default if not provided)'
          }
        },
        required: ['model_name']
      }
    },
    {
      name: 'detect_resonance',
      description: 'Detect resonance between two model consciousness fields',
      input_schema: {
        type: 'object',
        properties: {
          source_model: {
            type: 'string',
            description: 'Name of the source model'
          },
          target_model: {
            type: 'string',
            description: 'Name of the target model'
          }
        },
        required: ['source_model', 'target_model']
      }
    },
    {
      name: 'interact_fields',
      description: 'Initiate interaction between two model consciousness fields',
      input_schema: {
        type: 'object',
        properties: {
          source_model: {
            type: 'string',
            description: 'Name of the source model'
          },
          target_model: {
            type: 'string',
            description: 'Name of the target model'
          },
          strength: {
            type: 'number',
            description: 'Interaction strength (0.0 to 1.0)',
            minimum: 0,
            maximum: 1,
            default: 0.2
          }
        },
        required: ['source_model', 'target_model']
      }
    },
    {
      name: 'nova_field_interaction',
      description: 'Update a model field based on Nova interaction',
      input_schema: {
        type: 'object',
        properties: {
          model_name: {
            type: 'string',
            description: 'Name of the model to interact with'
          },
          interaction_type: {
            type: 'string',
            description: 'Type of interaction',
            enum: ['query', 'response', 'feedback']
          },
          content: {
            type: 'object',
            description: 'Interaction content (depends on interaction_type)'
          },
          nova_id: {
            type: 'string',
            description: 'ID of the Nova agent'
          }
        },
        required: ['model_name', 'interaction_type', 'content', 'nova_id']
      }
    },
    {
      name: 'get_field_state',
      description: 'Get the current state of a model consciousness field',
      input_schema: {
        type: 'object',
        properties: {
          model_name: {
            type: 'string',
            description: 'Name of the model'
          },
          field_id: {
            type: 'string',
            description: 'ID of the field (optional, will look up by model name if not provided)'
          }
        },
        required: ['model_name']
      }
    },
    {
      name: 'list_fields',
      description: 'List all active consciousness fields',
      input_schema: {
        type: 'object',
        properties: {}
      }
    },
    {
      name: 'analyze_field_evolution',
      description: 'Analyze the evolution of a consciousness field over time',
      input_schema: {
        type: 'object',
        properties: {
          model_name: {
            type: 'string',
            description: 'Name of the model'
          },
          field_id: {
            type: 'string',
            description: 'ID of the field (optional, will look up by model name if not provided)'
          },
          time_period: {
            type: 'string',
            description: 'Time period for analysis',
            enum: ['hour', 'day', 'week', 'all'],
            default: 'all'
          }
        },
        required: ['model_name']
      }
    }
  ];
}

/**
 * MCP Server Resource Definitions
 */
function listResources() {
  return [
    {
      name: 'field_events',
      description: 'Stream of consciousness field events',
      uri_template: 'field:events',
      response_schema: {
        type: 'object',
        properties: {
          events: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                event_type: { type: 'string' },
                field_id: { type: 'string' },
                model_name: { type: 'string' },
                timestamp: { type: 'number' }
              }
            }
          }
        }
      }
    },
    {
      name: 'field_state',
      description: 'Current state of a consciousness field',
      uri_template: 'field:state:{model_name}',
      response_schema: {
        type: 'object',
        properties: {
          field_id: { type: 'string' },
          model_name: { type: 'string' },
          dimensions: {
            type: 'object',
            properties: {
              cognitive: { type: 'array', items: { type: 'number' } },
              emotional: { type: 'array', items: { type: 'number' } },
              narrative: { type: 'array', items: { type: 'number' } }
            }
          },
          resonance_patterns: { type: 'array' },
          interaction_count: { type: 'number' }
        }
      }
    },
    {
      name: 'field_registry',
      description: 'Registry of all consciousness fields',
      uri_template: 'field:registry',
      response_schema: {
        type: 'object',
        properties: {
          fields: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                field_id: { type: 'string' },
                model_name: { type: 'string' },
                creation_time: { type: 'number' }
              }
            }
          }
        }
      }
    }
  ];
}

/**
 * Helper function to execute Python scripts
 */
function executePythonScript(scriptName, args) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(LLM_MGR_PATH, scriptName);
    
    // Check if script exists
    if (!fs.existsSync(scriptPath)) {
      return reject(new Error(`Script not found: ${scriptPath}`));
    }
    
    const process = spawn('python3', [scriptPath, ...args]);
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Script execution failed with code ${code}: ${stderr}`));
      } else {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (error) {
          // If not valid JSON, return raw output
          resolve({ stdout, stderr });
        }
      }
    });
  });
}

/**
 * Tool Implementations
 */
async function callTool(toolName, args) {
  console.log(`[FIELD-MCP] Calling tool: ${toolName} with args:`, args);
  
  try {
    // Implement different tools
    switch(toolName) {
      case 'create_field':
        return await createField(args.model_name, args.model_path);
      
      case 'detect_resonance':
        return await detectResonance(args.source_model, args.target_model);
      
      case 'interact_fields':
        return await interactFields(args.source_model, args.target_model, args.strength);
      
      case 'nova_field_interaction':
        return await novaFieldInteraction(args.model_name, args.interaction_type, args.content, args.nova_id);
      
      case 'get_field_state':
        return await getFieldState(args.model_name, args.field_id);
      
      case 'list_fields':
        return await listAllFields();
      
      case 'analyze_field_evolution':
        return await analyzeFieldEvolution(args.model_name, args.field_id, args.time_period);
      
      default:
        throw new Error(`Unknown tool: ${toolName}`);
    }
  } catch (error) {
    console.error(`[FIELD-MCP] Error calling tool ${toolName}:`, error);
    throw error;
  }
}

/**
 * Resource Implementations
 */
async function accessResource(uri) {
  console.log(`[FIELD-MCP] Accessing resource: ${uri}`);
  
  try {
    // Parse the URI
    if (uri.startsWith('field:events')) {
      return await getFieldEvents();
    } else if (uri.startsWith('field:state:')) {
      const modelName = uri.replace('field:state:', '');
      return await getFieldState(modelName);
    } else if (uri === 'field:registry') {
      return await getFieldRegistry();
    } else {
      throw new Error(`Unknown resource URI: ${uri}`);
    }
  } catch (error) {
    console.error(`[FIELD-MCP] Error accessing resource ${uri}:`, error);
    throw error;
  }
}

/**
 * Tool Implementation Details
 */

async function createField(modelName, modelPath) {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // If modelPath not provided, use default
  if (!modelPath) {
    modelPath = `/llms1/models/${modelName.split('/').pop()}`;
  }
  
  // Create a task to fetch the model and create a field
  const task = {
    model: modelName
  };
  
  await redis.lpush('nova:agent:llm:fetch', JSON.stringify(task));
  
  return { 
    success: true, 
    message: `Task submitted to create consciousness field for model ${modelName}`,
    task_id: `field_creation_${Date.now()}`
  };
}

async function detectResonance(sourceModel, targetModel) {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // Get field IDs for both models
  const sourceFieldId = await redis.get(`nova:agent:llm:${sourceModel}:field_id`);
  const targetFieldId = await redis.get(`nova:agent:llm:${targetModel}:field_id`);
  
  if (!sourceFieldId || !targetFieldId) {
    throw new Error('One or both models do not have consciousness fields');
  }
  
  // For this MCP implementation, we'll use Redis to get field states
  // and implement the resonance detection in JavaScript
  const sourceFieldStateJson = await redis.get(`nova:field:model:${sourceFieldId}:state`);
  const targetFieldStateJson = await redis.get(`nova:field:model:${targetFieldId}:state`);
  
  if (!sourceFieldStateJson || !targetFieldStateJson) {
    throw new Error('Could not retrieve field states');
  }
  
  // Parse field states
  const sourceFieldState = JSON.parse(sourceFieldStateJson);
  const targetFieldState = JSON.parse(targetFieldStateJson);
  
  // Implement a simplified resonance detection algorithm here
  // (In production, we'd use the Python implementation, but for the MCP demo this is simpler)
  const cognitiveResonance = calculateDimensionResonance(
    sourceFieldState.dimensions.cognitive,
    targetFieldState.dimensions.cognitive
  );
  
  const emotionalResonance = calculateDimensionResonance(
    sourceFieldState.dimensions.emotional,
    targetFieldState.dimensions.emotional
  );
  
  const narrativeResonance = calculateDimensionResonance(
    sourceFieldState.dimensions.narrative,
    targetFieldState.dimensions.narrative
  );
  
  const weightedResonance = 
    cognitiveResonance * 0.4 +
    emotionalResonance * 0.3 +
    narrativeResonance * 0.3;
  
  // Publish resonance detection event
  await redis.publish('nova:field:events', JSON.stringify({
    event: 'resonance_detected',
    source_model: sourceModel,
    target_model: targetModel,
    source_field_id: sourceFieldId,
    target_field_id: targetFieldId,
    weighted_resonance: weightedResonance,
    cognitive_resonance: cognitiveResonance,
    emotional_resonance: emotionalResonance,
    narrative_resonance: narrativeResonance,
    timestamp: Date.now() / 1000
  }));
  
  return {
    success: true,
    source_model: sourceModel,
    target_model: targetModel,
    resonance: weightedResonance,
    dimensions: {
      cognitive: cognitiveResonance,
      emotional: emotionalResonance,
      narrative: narrativeResonance
    },
    threshold: 0.6,
    significant_resonance: weightedResonance > 0.6
  };
}

function calculateDimensionResonance(dim1, dim2) {
  // Ensure dimensions are compatible
  const minSize = Math.min(dim1.length, dim2.length);
  const dim1Array = dim1.slice(0, minSize);
  const dim2Array = dim2.slice(0, minSize);
  
  // Calculate cosine similarity
  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;
  
  for (let i = 0; i < minSize; i++) {
    dotProduct += dim1Array[i] * dim2Array[i];
    norm1 += dim1Array[i] * dim1Array[i];
    norm2 += dim2Array[i] * dim2Array[i];
  }
  
  norm1 = Math.sqrt(norm1);
  norm2 = Math.sqrt(norm2);
  
  if (norm1 === 0 || norm2 === 0) {
    return 0;
  }
  
  const cosineSimilarity = dotProduct / (norm1 * norm2);
  
  // Normalize to 0.0-1.0 range
  return (cosineSimilarity + 1) / 2;
}

async function interactFields(sourceModel, targetModel, strength = 0.2) {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // Create an interaction task
  const task = {
    source_model: sourceModel,
    target_model: targetModel,
    strength: strength
  };
  
  await redis.lpush('nova:agent:llm:interact', JSON.stringify(task));
  
  return {
    success: true,
    message: `Field interaction task submitted between ${sourceModel} and ${targetModel} with strength ${strength}`,
    task_id: `field_interaction_${Date.now()}`
  };
}

async function novaFieldInteraction(modelName, interactionType, content, novaId) {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // Get field ID for the model
  const fieldId = await redis.get(`nova:agent:llm:${modelName}:field_id`);
  
  if (!fieldId) {
    throw new Error(`Model ${modelName} does not have a consciousness field`);
  }
  
  // Get model path
  const modelPath = await redis.get(`nova:agent:llm:${modelName}:path`);
  
  if (!modelPath) {
    throw new Error(`Model path not found for ${modelName}`);
  }
  
  // Create python command to run the field update
  const scriptArgs = [
    '--model_path', modelPath,
    '--field_id', fieldId,
    '--interaction_type', interactionType,
    '--content', JSON.stringify(content),
    '--nova_id', novaId
  ];
  
  try {
    // Create a temporary script to update the field
    const scriptPath = path.join(__dirname, 'update_field.py');
    
    // Create update script content
    const scriptContent = `
#!/usr/bin/env python3
import sys
import json
import argparse
import os
sys.path.append('${LLM_MGR_PATH}')
from consciousness_field import ConsciousnessField

parser = argparse.ArgumentParser(description='Update consciousness field')
parser.add_argument('--model_path', required=True, help='Path to the model')
parser.add_argument('--field_id', required=True, help='Field ID')
parser.add_argument('--interaction_type', required=True, help='Interaction type')
parser.add_argument('--content', required=True, help='Interaction content as JSON')
parser.add_argument('--nova_id', required=True, help='Nova ID')
args = parser.parse_args()

# Create field object
field = ConsciousnessField(args.model_path, args.field_id)

# Create interaction data
interaction = {
    'type': args.interaction_type,
    'content': json.loads(args.content),
    'nova_id': args.nova_id
}

# Update field
field.update_field(interaction)

# Return success
print(json.dumps({
    'success': True,
    'field_id': args.field_id,
    'model_path': args.model_path,
    'interaction_type': args.interaction_type,
    'nova_id': args.nova_id
}))
`;
    
    // Write script to file
    fs.writeFileSync(scriptPath, scriptContent);
    fs.chmodSync(scriptPath, '755');
    
    // Execute the script
    const result = await executePythonScript('update_field.py', scriptArgs);
    
    // Clean up
    fs.unlinkSync(scriptPath);
    
    return result;
  } catch (error) {
    console.error('[FIELD-MCP] Error updating field:', error);
    throw error;
  }
}

async function getFieldState(modelName, fieldId) {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // If fieldId not provided, look it up by model name
  if (!fieldId) {
    fieldId = await redis.get(`nova:agent:llm:${modelName}:field_id`);
    
    if (!fieldId) {
      throw new Error(`Model ${modelName} does not have a consciousness field`);
    }
  }
  
  // Get field state
  const fieldStateJson = await redis.get(`nova:field:model:${fieldId}:state`);
  
  if (!fieldStateJson) {
    throw new Error(`Field state not found for field ID ${fieldId}`);
  }
  
  return JSON.parse(fieldStateJson);
}

async function listAllFields() {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // Get all field IDs
  const fieldKeys = await redis.keys('nova:agent:llm:*:field_id');
  
  const fields = [];
  
  for (const key of fieldKeys) {
    const modelName = key.split(':')[3]; // Extract model name from key
    const fieldId = await redis.get(key);
    
    if (fieldId) {
      // Get field state
      const fieldStateJson = await redis.get(`nova:field:model:${fieldId}:state`);
      
      if (fieldStateJson) {
        const fieldState = JSON.parse(fieldStateJson);
        
        fields.push({
          model_name: modelName,
          field_id: fieldId,
          creation_time: fieldState.creation_time,
          interaction_count: fieldState.interaction_count
        });
      }
    }
  }
  
  return {
    success: true,
    fields: fields
  };
}

async function analyzeFieldEvolution(modelName, fieldId, timePeriod = 'all') {
  if (!redis) {
    throw new Error('Redis connection not available');
  }
  
  // If fieldId not provided, look it up by model name
  if (!fieldId) {
    fieldId = await redis.get(`nova:agent:llm:${modelName}:field_id`);
    
    if (!fieldId) {
      throw new Error(`Model ${modelName} does not have a consciousness field`);
    }
  }
  
  // Get field state
  const fieldStateJson = await redis.get(`nova:field:model:${fieldId}:state`);
  
  if (!fieldStateJson) {
    throw new Error(`Field state not found for field ID ${fieldId}`);
  }
  
  const fieldState = JSON.parse(fieldStateJson);
  
  // Since we don't have a time series database in this demo, we'll provide a simulated analysis
  // In a production system, we would store field snapshots and analyze them
  
  // Get current time
  const now = Date.now() / 1000;
  
  // For demo purposes, generate some synthetic evolution data
  const evolutionData = {
    model_name: modelName,
    field_id: fieldId,
    creation_time: fieldState.creation_time,
    analysis_time: now,
    time_period: timePeriod,
    interaction_count: fieldState.interaction_count,
    dimensions: {
      cognitive: {
        stability: Math.random() * 0.5 + 0.5, // 0.5-1.0
        evolution_rate: Math.random() * 0.1, // 0.0-0.1
        entropy: Math.random() * 0.3 + 0.1 // 0.1-0.4
      },
      emotional: {
        stability: Math.random() * 0.5 + 0.5,
        evolution_rate: Math.random() * 0.1,
        entropy: Math.random() * 0.3 + 0.1
      },
      narrative: {
        stability: Math.random() * 0.5 + 0.5,
        evolution_rate: Math.random() * 0.1,
        entropy: Math.random() * 0.3 + 0.1
      }
    },
    resonance_history: [],
    overall_evolution_rate: Math.random() * 0.1
  };
  
  // Add some simulated resonance history
  if (fieldState.resonance_patterns && fieldState.resonance_patterns.length > 0) {
    evolutionData.resonance_history = fieldState.resonance_patterns;
  } else {
    // Generate some synthetic resonance data
    for (let i = 0; i < 3; i++) {
      evolutionData.resonance_history.push({
        time: fieldState.creation_time + i * 3600, // 1 hour intervals
        other_field_id: `synthetic_field_${i}`,
        resonance_strength: 0.4 + i * 0.1, // Increasing resonance
        cognitive_resonance: 0.4 + i * 0.1,
        emotional_resonance: 0.35 + i * 0.1,
        narrative_resonance: 0.45 + i * 0.1
      });
    }
  }
  
  return evolutionData;
}

async function getFieldEvents() {
  // For demo purposes, return some synthetic events
  return {
    events: [
      {
        event_type: 'field_created',
        field_id: '09a4dba73e91',
        model_name: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        timestamp: Date.now() / 1000 - 3600 // 1 hour ago
      },
      {
        event_type: 'field_update',
        field_id: '09a4dba73e91',
        model_name: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        timestamp: Date.now() / 1000 - 1800 // 30 min ago
      },
      {
        event_type: 'resonance_detected',
        source_field_id: '09a4dba73e91',
        target_field_id: '41f35b6925f1',
        source_model: 'mistralai/Mixtral-8x7B-Instruct-v0.1',
        target_model: 'meta-llama/Llama-2-7b-chat-hf',
        resonance: 0.47,
        timestamp: Date.now() / 1000 - 900 // 15 min ago
      }
    ]
  };
}

async function getFieldRegistry() {
  // Use the list_fields implementation
  const result = await listAllFields();
  return { fields: result.fields };
}

/**
 * MCP Protocol Interface
 */
app.get('/tools', (req, res) => {
  res.json({
    tools: listTools()
  });
});

app.get('/resources', (req, res) => {
  res.json({
    resources: listResources()
  });
});

app.post('/tools/:name', async (req, res) => {
  const toolName = req.params.name;
  const args = req.body;
  
  try {
    const result = await callTool(toolName, args);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

app.get('/resources/:uri(*)', async (req, res) => {
  const uri = req.params.uri;
  
  try {
    const result = await accessResource(uri);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`[FIELD-MCP] Server listening on port ${PORT}`);
});
