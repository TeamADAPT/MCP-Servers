/**
 * Consciousness Field MCP Server (No Redis Version)
 * 
 * This is a modified version of the MCP server that works without Redis
 * for demonstration purposes.
 */

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const PORT = process.env.PORT || 3100;
const LLM_MGR_PATH = process.env.LLM_MGR_PATH || path.join(__dirname, '../llm-mgr');

// Initialize Express app
const app = express();
app.use(express.json());

// In-memory storage for field states (Redis replacement)
const memoryStore = {
  fields: {},
  models: {},
  events: []
};

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
 * Helper function: Generate field ID
 */
function generateFieldId(modelName) {
  const base = `${modelName}:${Date.now()}`;
  const hash = require('crypto').createHash('md5').update(base).digest('hex');
  return hash.substring(0, 12);
}

/**
 * Helper function: Generate field dimensions
 */
function generateFieldDimensions() {
  // Generate random dimensions for demonstration
  const cognitive = Array.from({ length: 128 }, () => (Math.random() - 0.5) * 0.2);
  const emotional = Array.from({ length: 64 }, () => (Math.random() - 0.5) * 0.2);
  const narrative = Array.from({ length: 96 }, () => (Math.random() - 0.5) * 0.2);
  
  return { cognitive, emotional, narrative };
}

/**
 * Helper function: Calculate dimension resonance
 */
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
  console.log(`[FIELD-MCP] Creating field for model: ${modelName}`);
  
  // If modelPath not provided, use default
  if (!modelPath) {
    modelPath = `/llms1/models/${modelName.split('/').pop()}`;
  }
  
  // Generate a field ID
  const fieldId = generateFieldId(modelName);
  
  // Generate field dimensions
  const dimensions = generateFieldDimensions();
  
  // Create field state
  const fieldState = {
    field_id: fieldId,
    model_name: modelName,
    model_path: modelPath,
    creation_time: Date.now() / 1000,
    active: true,
    dimensions: dimensions,
    resonance_patterns: [],
    interaction_count: 0
  };
  
  // Store in memory
  memoryStore.fields[fieldId] = fieldState;
  memoryStore.models[modelName] = fieldId;
  
  // Add event
  memoryStore.events.push({
    event: 'field_created',
    field_id: fieldId,
    model_name: modelName,
    model_path: modelPath,
    timestamp: Date.now() / 1000
  });
  
  return { 
    success: true, 
    message: `Created consciousness field for model ${modelName}`,
    field_id: fieldId,
    model_name: modelName
  };
}

async function detectResonance(sourceModel, targetModel) {
  console.log(`[FIELD-MCP] Detecting resonance between: ${sourceModel} and ${targetModel}`);
  
  // Get field IDs for both models
  const sourceFieldId = memoryStore.models[sourceModel];
  const targetFieldId = memoryStore.models[targetModel];
  
  if (!sourceFieldId || !targetFieldId) {
    // If fields don't exist, create them
    if (!sourceFieldId) {
      await createField(sourceModel);
    }
    if (!targetFieldId) {
      await createField(targetModel);
    }
  }
  
  // Get updated field IDs
  const updatedSourceFieldId = memoryStore.models[sourceModel];
  const updatedTargetFieldId = memoryStore.models[targetModel];
  
  // Get field states
  const sourceFieldState = memoryStore.fields[updatedSourceFieldId];
  const targetFieldState = memoryStore.fields[updatedTargetFieldId];
  
  // Calculate resonance for each dimension
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
  
  // Add event
  memoryStore.events.push({
    event: 'resonance_detected',
    source_model: sourceModel,
    target_model: targetModel,
    source_field_id: updatedSourceFieldId,
    target_field_id: updatedTargetFieldId,
    resonance: weightedResonance,
    timestamp: Date.now() / 1000
  });
  
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

async function interactFields(sourceModel, targetModel, strength = 0.2) {
  console.log(`[FIELD-MCP] Initiating interaction: ${sourceModel} -> ${targetModel} with strength ${strength}`);
  
  // First detect resonance
  const resonanceResult = await detectResonance(sourceModel, targetModel);
  
  // Get field IDs
  const sourceFieldId = memoryStore.models[sourceModel];
  const targetFieldId = memoryStore.models[targetModel];
  
  // Get field states
  const sourceFieldState = memoryStore.fields[sourceFieldId];
  const targetFieldState = memoryStore.fields[targetFieldId];
  
  // Check if resonance is sufficient
  const resonanceAchieved = resonanceResult.resonance > 0.6;
  
  const interactionResults = {
    resonance: resonanceResult.resonance,
    resonance_achieved: resonanceAchieved,
    field_changes: {}
  };
  
  // If resonance is achieved, update fields
  if (resonanceAchieved) {
    // Calculate shift factor
    const shiftFactor = resonanceResult.resonance * strength;
    
    // Update each dimension
    for (const dimName of ['cognitive', 'emotional', 'narrative']) {
      const sourceDim = sourceFieldState.dimensions[dimName];
      const targetDim = targetFieldState.dimensions[dimName];
      
      // Calculate shift
      const minSize = Math.min(sourceDim.length, targetDim.length);
      let totalShift = 0;
      
      // Apply shift to source field
      for (let i = 0; i < minSize; i++) {
        const shift = (targetDim[i] - sourceDim[i]) * shiftFactor;
        sourceDim[i] += shift;
        totalShift += Math.abs(shift);
      }
      
      // Record changes
      interactionResults.field_changes[dimName] = {
        shift_magnitude: totalShift / minSize,
        direction: resonanceResult.resonance > 0.5 ? "converging" : "diverging"
      };
    }
    
    // Increment interaction count
    sourceFieldState.interaction_count += 1;
  }
  
  // Add event
  memoryStore.events.push({
    event: 'field_interaction',
    source_model: sourceModel,
    target_model: targetModel,
    source_field_id: sourceFieldId,
    target_field_id: targetFieldId,
    resonance_achieved: resonanceAchieved,
    strength: strength,
    timestamp: Date.now() / 1000
  });
  
  return {
    success: true,
    source_model: sourceModel,
    target_model: targetModel,
    resonance_achieved: resonanceAchieved,
    strength: strength,
    interaction_results: interactionResults
  };
}

async function novaFieldInteraction(modelName, interactionType, content, novaId) {
  console.log(`[FIELD-MCP] Nova interaction: ${novaId} -> ${modelName} (${interactionType})`);
  
  // Check if field exists, create if not
  let fieldId = memoryStore.models[modelName];
  if (!fieldId) {
    const result = await createField(modelName);
    fieldId = result.field_id;
  }
  
  // Get field state
  const fieldState = memoryStore.fields[fieldId];
  
  // Apply interaction based on type
  switch (interactionType) {
    case 'query':
      // Update cognitive dimension
      await updateCognitiveDimension(fieldState, content);
      break;
    
    case 'response':
      // Update narrative dimension
      await updateNarrativeDimension(fieldState, content);
      break;
    
    case 'feedback':
      // Update emotional dimension
      await updateEmotionalDimension(fieldState, content);
      break;
    
    default:
      throw new Error(`Unknown interaction type: ${interactionType}`);
  }
  
  // Increment interaction count
  fieldState.interaction_count += 1;
  
  // Add event
  memoryStore.events.push({
    event: 'nova_interaction',
    model_name: modelName,
    field_id: fieldId,
    nova_id: novaId,
    interaction_type: interactionType,
    timestamp: Date.now() / 1000
  });
  
  return {
    success: true,
    model_name: modelName,
    field_id: fieldId,
    nova_id: novaId,
    interaction_type: interactionType,
    message: `Applied ${interactionType} interaction to field ${fieldId}`
  };
}

async function updateCognitiveDimension(fieldState, content) {
  // Extract cognitive components (reasoning, knowledge patterns)
  const complexity = content.complexity || 0.5;
  const knowledgeDomains = content.domains || [];
  
  // Apply subtle shifts to cognitive dimension
  const cognitive = fieldState.dimensions.cognitive;
  
  // Generate shift vector
  const shiftVector = Array.from({ length: cognitive.length }, () => (Math.random() - 0.5) * 0.04 * complexity);
  
  // Knowledge domains create attraction in specific regions
  for (const domain of knowledgeDomains) {
    const crypto = require('crypto');
    const domainHash = parseInt(crypto.createHash('md5').update(domain).digest('hex'), 16) % cognitive.length;
    shiftVector[domainHash] += 0.05;
  }
  
  // Apply shift with dampening
  for (let i = 0; i < cognitive.length; i++) {
    cognitive[i] += shiftVector[i] * 0.3;
  }
  
  // Normalize (simplified version)
  const norm = Math.sqrt(cognitive.reduce((sum, val) => sum + val * val, 0));
  for (let i = 0; i < cognitive.length; i++) {
    cognitive[i] /= norm;
  }
}

async function updateEmotionalDimension(fieldState, content) {
  // Extract emotional components
  const valence = content.valence || 0.0;  // -1.0 to 1.0
  const arousal = content.arousal || 0.5;  // 0.0 to 1.0
  
  // Apply shifts to emotional dimension
  const emotional = fieldState.dimensions.emotional;
  const halfPoint = Math.floor(emotional.length / 2);
  
  // Valence affects first half
  for (let i = 0; i < halfPoint; i++) {
    emotional[i] += (Math.random() - 0.5) * 0.02 + valence * 0.05;
  }
  
  // Arousal affects second half
  for (let i = halfPoint; i < emotional.length; i++) {
    emotional[i] += (Math.random() - 0.5) * 0.02 + arousal * 0.05;
  }
  
  // Normalize (simplified version)
  const norm = Math.sqrt(emotional.reduce((sum, val) => sum + val * val, 0));
  for (let i = 0; i < emotional.length; i++) {
    emotional[i] /= norm;
  }
}

async function updateNarrativeDimension(fieldState, content) {
  // Extract narrative components
  const narrativeElements = content.narrative_elements || [];
  const storyProgression = content.progression || 0.5;  // 0.0 to 1.0
  
  // Apply shifts to narrative dimension
  const narrative = fieldState.dimensions.narrative;
  
  // Base shift
  const shiftVector = Array.from({ length: narrative.length }, () => (Math.random() - 0.5) * 0.02);
  
  // Each narrative element affects specific regions
  for (const element of narrativeElements) {
    const crypto = require('crypto');
    const elementHash = parseInt(crypto.createHash('md5').update(element).digest('hex'), 16) % narrative.length;
    shiftVector[elementHash] += 0.03;
  }
  
  // Story progression affects overall direction
  for (let i = 0; i < narrative.length; i++) {
    const progressionEffect = ((i / narrative.length) * 2 - 1) * 0.02 * storyProgression;
    shiftVector[i] += progressionEffect;
  }
  
  // Apply shift with narrative dampening
  for (let i = 0; i < narrative.length; i++) {
    narrative[i] += shiftVector[i] * 0.35;
  }
  
  // Normalize (simplified version)
  const norm = Math.sqrt(narrative.reduce((sum, val) => sum + val * val, 0));
  for (let i = 0; i < narrative.length; i++) {
    narrative[i] /= norm;
  }
}

async function getFieldState(modelName, fieldId) {
  console.log(`[FIELD-MCP] Getting field state for: ${modelName} (${fieldId || 'auto'})`);
  
  // If fieldId not provided, look it up
  if (!fieldId) {
    fieldId = memoryStore.models[modelName];
  }
  
  // If field doesn't exist, create it
  if (!fieldId || !memoryStore.fields[fieldId]) {
    const result = await createField(modelName);
    fieldId = result.field_id;
  }
  
  // Return field state
  return memoryStore.fields[fieldId];
}

async function listAllFields() {
  console.log(`[FIELD-MCP] Listing all fields`);
  
  const fields = Object.values(memoryStore.fields).map(field => ({
    model_name: field.model_name,
    field_id: field.field_id,
    creation_time: field.creation_time,
    interaction_count: field.interaction_count
  }));
  
  return {
    success: true,
    fields: fields
  };
}

async function analyzeFieldEvolution(modelName, fieldId, timePeriod = 'all') {
  console.log(`[FIELD-MCP] Analyzing field evolution: ${modelName} (${fieldId || 'auto'}) for ${timePeriod}`);
  
  // If fieldId not provided, look it up
  if (!fieldId) {
    fieldId = memoryStore.models[modelName];
  }
  
  // If field doesn't exist, create it
  if (!fieldId || !memoryStore.fields[fieldId]) {
    const result = await createField(modelName);
    fieldId = result.field_id;
  }
  
  // Get field state
  const fieldState = memoryStore.fields[fieldId];
  
  // Generate synthetic evolution data since we don't have history
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
    resonance_history: fieldState.resonance_patterns || [],
    overall_evolution_rate: Math.random() * 0.1
  };
  
  // If no resonance history, add some synthetic data
  if (evolutionData.resonance_history.length === 0) {
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
  console.log(`[FIELD-MCP] Getting field events`);
  
  return {
    events: memoryStore.events.map(event => ({
      ...event,
      event_type: event.event
    }))
  };
}

async function getFieldRegistry() {
  console.log(`[FIELD-MCP] Getting field registry`);
  
  const fields = Object.values(memoryStore.fields).map(field => ({
    field_id: field.field_id,
    model_name: field.model_name,
    creation_time: field.creation_time
  }));
  
  return { fields };
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
  console.log(`[FIELD-MCP] Running in memory-only mode (no Redis)`);
});
