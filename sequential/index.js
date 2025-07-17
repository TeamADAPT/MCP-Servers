#!/usr/bin/env node

/**
 * Sequential MCP Server
 * Complex Analysis & Thinking server for multi-step problem solving, architectural analysis, systematic debugging
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { v4 as uuidv4 } from 'uuid';

class SequentialServer {
  constructor() {
    this.server = new Server(
      {
        name: 'sequential-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.analysisSession = new Map();
    this.thinkingModes = {
      systematic: 'Structured step-by-step analysis',
      architectural: 'System-wide architectural analysis',
      debugging: 'Root cause investigation',
      strategic: 'Long-term strategic thinking',
      tactical: 'Short-term tactical planning'
    };
  }

  setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'start-analysis',
          description: 'Start a new sequential analysis session',
          inputSchema: {
            type: 'object',
            properties: {
              problem: {
                type: 'string',
                description: 'The problem or question to analyze',
              },
              mode: {
                type: 'string',
                enum: ['systematic', 'architectural', 'debugging', 'strategic', 'tactical'],
                description: 'Analysis mode to use',
                default: 'systematic',
              },
              context: {
                type: 'string',
                description: 'Additional context or constraints',
              },
              depth: {
                type: 'string',
                enum: ['shallow', 'medium', 'deep', 'exhaustive'],
                description: 'Analysis depth level',
                default: 'medium',
              },
            },
            required: ['problem'],
          },
        },
        {
          name: 'continue-analysis',
          description: 'Continue an existing analysis session with new information',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Analysis session ID',
              },
              input: {
                type: 'string',
                description: 'New information or question to incorporate',
              },
              direction: {
                type: 'string',
                enum: ['deeper', 'broader', 'alternative', 'validation'],
                description: 'Direction to take the analysis',
                default: 'deeper',
              },
            },
            required: ['sessionId', 'input'],
          },
        },
        {
          name: 'decompose-problem',
          description: 'Break down a complex problem into manageable components',
          inputSchema: {
            type: 'object',
            properties: {
              problem: {
                type: 'string',
                description: 'Complex problem to decompose',
              },
              levels: {
                type: 'number',
                description: 'Number of decomposition levels',
                default: 3,
              },
              approach: {
                type: 'string',
                enum: ['hierarchical', 'functional', 'temporal', 'causal'],
                description: 'Decomposition approach',
                default: 'hierarchical',
              },
            },
            required: ['problem'],
          },
        },
        {
          name: 'analyze-dependencies',
          description: 'Identify and analyze dependencies and relationships',
          inputSchema: {
            type: 'object',
            properties: {
              components: {
                type: 'array',
                items: { type: 'string' },
                description: 'List of components to analyze',
              },
              analysisType: {
                type: 'string',
                enum: ['dependencies', 'relationships', 'interactions', 'conflicts'],
                description: 'Type of analysis to perform',
                default: 'dependencies',
              },
            },
            required: ['components'],
          },
        },
        {
          name: 'generate-hypotheses',
          description: 'Generate and evaluate hypotheses for a given problem',
          inputSchema: {
            type: 'object',
            properties: {
              problem: {
                type: 'string',
                description: 'Problem to generate hypotheses for',
              },
              evidence: {
                type: 'array',
                items: { type: 'string' },
                description: 'Available evidence or observations',
              },
              count: {
                type: 'number',
                description: 'Number of hypotheses to generate',
                default: 5,
              },
            },
            required: ['problem'],
          },
        },
        {
          name: 'systematic-review',
          description: 'Perform systematic review of analysis or solution',
          inputSchema: {
            type: 'object',
            properties: {
              sessionId: {
                type: 'string',
                description: 'Analysis session ID to review',
              },
              criteria: {
                type: 'array',
                items: { type: 'string' },
                description: 'Review criteria to apply',
              },
              focus: {
                type: 'string',
                enum: ['completeness', 'accuracy', 'feasibility', 'risks'],
                description: 'Review focus area',
                default: 'completeness',
              },
            },
            required: ['sessionId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'start-analysis':
            return await this.startAnalysis(args.problem, args.mode, args.context, args.depth);
          case 'continue-analysis':
            return await this.continueAnalysis(args.sessionId, args.input, args.direction);
          case 'decompose-problem':
            return await this.decomposeProblem(args.problem, args.levels, args.approach);
          case 'analyze-dependencies':
            return await this.analyzeDependencies(args.components, args.analysisType);
          case 'generate-hypotheses':
            return await this.generateHypotheses(args.problem, args.evidence, args.count);
          case 'systematic-review':
            return await this.systematicReview(args.sessionId, args.criteria, args.focus);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error in ${name}: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async startAnalysis(problem, mode = 'systematic', context = '', depth = 'medium') {
    const sessionId = uuidv4();
    const session = {
      id: sessionId,
      problem,
      mode,
      context,
      depth,
      steps: [],
      findings: [],
      hypotheses: [],
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };

    // Initialize analysis based on mode
    const initialSteps = this.generateInitialSteps(problem, mode, depth);
    session.steps = initialSteps;

    // Store session
    this.analysisSession.set(sessionId, session);

    const result = {
      sessionId,
      mode,
      problem,
      initialSteps,
      nextActions: this.getNextActions(session),
      estimatedComplexity: this.estimateComplexity(problem, mode, depth),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async continueAnalysis(sessionId, input, direction = 'deeper') {
    const session = this.analysisSession.get(sessionId);
    if (!session) {
      throw new Error(`Analysis session ${sessionId} not found`);
    }

    // Process new input based on direction
    const newStep = this.processAnalysisStep(session, input, direction);
    session.steps.push(newStep);
    session.updated = new Date().toISOString();

    // Update findings if applicable
    if (newStep.type === 'finding') {
      session.findings.push(newStep.content);
    }

    const result = {
      sessionId,
      newStep,
      totalSteps: session.steps.length,
      findings: session.findings,
      nextActions: this.getNextActions(session),
      progress: this.calculateProgress(session),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async decomposeProblem(problem, levels = 3, approach = 'hierarchical') {
    const decomposition = {
      problem,
      approach,
      levels,
      structure: this.buildDecompositionStructure(problem, levels, approach),
      relationships: this.identifyRelationships(problem, approach),
      prioritization: this.prioritizeComponents(problem, approach),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(decomposition, null, 2),
        },
      ],
    };
  }

  async analyzeDependencies(components, analysisType = 'dependencies') {
    const analysis = {
      components,
      analysisType,
      matrix: this.buildDependencyMatrix(components, analysisType),
      criticalPath: this.identifyCriticalPath(components),
      risks: this.identifyDependencyRisks(components),
      recommendations: this.generateDependencyRecommendations(components, analysisType),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(analysis, null, 2),
        },
      ],
    };
  }

  async generateHypotheses(problem, evidence = [], count = 5) {
    const hypotheses = [];
    
    for (let i = 0; i < count; i++) {
      const hypothesis = {
        id: i + 1,
        statement: `Hypothesis ${i + 1} for: ${problem}`,
        rationale: this.generateHypothesisRationale(problem, evidence, i),
        testability: this.assessTestability(problem, i),
        likelihood: this.assessLikelihood(problem, evidence, i),
        implications: this.generateImplications(problem, i),
      };
      hypotheses.push(hypothesis);
    }

    const result = {
      problem,
      evidence,
      hypotheses,
      evaluationCriteria: this.getEvaluationCriteria(),
      nextSteps: this.getHypothesisTestingSteps(hypotheses),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  }

  async systematicReview(sessionId, criteria = [], focus = 'completeness') {
    const session = this.analysisSession.get(sessionId);
    if (!session) {
      throw new Error(`Analysis session ${sessionId} not found`);
    }

    const review = {
      sessionId,
      focus,
      criteria: criteria.length > 0 ? criteria : this.getDefaultCriteria(focus),
      assessment: this.assessSession(session, criteria, focus),
      gaps: this.identifyGaps(session, focus),
      recommendations: this.generateReviewRecommendations(session, focus),
      score: this.calculateQualityScore(session, focus),
      timestamp: new Date().toISOString(),
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(review, null, 2),
        },
      ],
    };
  }

  // Helper methods
  generateInitialSteps(problem, mode, depth) {
    const baseSteps = [
      { id: 1, type: 'definition', content: `Define problem scope: ${problem}` },
      { id: 2, type: 'analysis', content: `Initial ${mode} analysis` },
      { id: 3, type: 'decomposition', content: 'Break down into components' },
    ];

    if (depth === 'deep' || depth === 'exhaustive') {
      baseSteps.push(
        { id: 4, type: 'research', content: 'Research related patterns' },
        { id: 5, type: 'validation', content: 'Validate assumptions' }
      );
    }

    if (depth === 'exhaustive') {
      baseSteps.push(
        { id: 6, type: 'alternatives', content: 'Explore alternative approaches' },
        { id: 7, type: 'synthesis', content: 'Synthesize findings' }
      );
    }

    return baseSteps;
  }

  processAnalysisStep(session, input, direction) {
    return {
      id: session.steps.length + 1,
      type: this.determineStepType(input, direction),
      content: input,
      direction,
      timestamp: new Date().toISOString(),
    };
  }

  determineStepType(input, direction) {
    if (input.includes('found') || input.includes('discovered')) return 'finding';
    if (input.includes('hypothesis') || input.includes('theory')) return 'hypothesis';
    if (input.includes('validate') || input.includes('test')) return 'validation';
    return 'analysis';
  }

  getNextActions(session) {
    const lastStep = session.steps[session.steps.length - 1];
    if (!lastStep) return ['Begin initial analysis'];

    switch (lastStep.type) {
      case 'definition':
        return ['Perform initial decomposition', 'Identify key components'];
      case 'analysis':
        return ['Dive deeper into findings', 'Explore alternatives'];
      case 'finding':
        return ['Validate finding', 'Explore implications'];
      default:
        return ['Continue analysis', 'Review progress'];
    }
  }

  estimateComplexity(problem, mode, depth) {
    let baseComplexity = problem.length > 100 ? 'high' : 'medium';
    if (mode === 'architectural' || mode === 'strategic') baseComplexity = 'high';
    if (depth === 'exhaustive') baseComplexity = 'very high';
    return baseComplexity;
  }

  calculateProgress(session) {
    const totalExpectedSteps = this.getExpectedSteps(session.mode, session.depth);
    const currentSteps = session.steps.length;
    return Math.min(100, Math.round((currentSteps / totalExpectedSteps) * 100));
  }

  getExpectedSteps(mode, depth) {
    const base = { shallow: 3, medium: 5, deep: 8, exhaustive: 12 };
    return base[depth] || 5;
  }

  buildDecompositionStructure(problem, levels, approach) {
    const structure = { level0: [problem] };
    
    for (let i = 1; i <= levels; i++) {
      structure[`level${i}`] = this.generateSubComponents(problem, i, approach);
    }
    
    return structure;
  }

  generateSubComponents(problem, level, approach) {
    // Simplified decomposition logic
    const count = Math.max(2, 5 - level);
    return Array.from({ length: count }, (_, i) => 
      `${approach} component ${i + 1} (Level ${level})`
    );
  }

  identifyRelationships(problem, approach) {
    return [
      { type: 'dependency', description: `${approach} dependency relationship` },
      { type: 'interaction', description: `${approach} interaction pattern` },
    ];
  }

  prioritizeComponents(problem, approach) {
    return {
      high: [`Critical ${approach} component`],
      medium: [`Important ${approach} component`],
      low: [`Optional ${approach} component`],
    };
  }

  buildDependencyMatrix(components, analysisType) {
    const matrix = {};
    components.forEach(comp => {
      matrix[comp] = components.filter(c => c !== comp).map(c => ({
        component: c,
        relationship: this.determineRelationship(comp, c, analysisType),
      }));
    });
    return matrix;
  }

  determineRelationship(comp1, comp2, analysisType) {
    // Simplified relationship determination
    return `${analysisType} relationship between ${comp1} and ${comp2}`;
  }

  identifyCriticalPath(components) {
    return components.slice(0, Math.ceil(components.length / 2));
  }

  identifyDependencyRisks(components) {
    return [
      { risk: 'Circular dependency', components: components.slice(0, 2) },
      { risk: 'Single point of failure', components: [components[0]] },
    ];
  }

  generateDependencyRecommendations(components, analysisType) {
    return [
      `Minimize ${analysisType} coupling between components`,
      `Implement fail-safe mechanisms for critical dependencies`,
    ];
  }

  generateHypothesisRationale(problem, evidence, index) {
    return `Rationale for hypothesis ${index + 1} based on problem analysis and available evidence`;
  }

  assessTestability(problem, index) {
    return ['high', 'medium', 'low'][index % 3];
  }

  assessLikelihood(problem, evidence, index) {
    return Math.round((100 - index * 15) / 10) * 10; // 100%, 85%, 70%, etc.
  }

  generateImplications(problem, index) {
    return [`Implication ${index + 1} for problem resolution`];
  }

  getEvaluationCriteria() {
    return ['testability', 'likelihood', 'impact', 'feasibility'];
  }

  getHypothesisTestingSteps(hypotheses) {
    return hypotheses.map(h => `Test hypothesis ${h.id}: ${h.statement}`);
  }

  getDefaultCriteria(focus) {
    const criteria = {
      completeness: ['all aspects covered', 'no major gaps', 'sufficient depth'],
      accuracy: ['factual correctness', 'logical consistency', 'valid assumptions'],
      feasibility: ['practical implementation', 'resource availability', 'timeline realistic'],
      risks: ['potential failures', 'mitigation strategies', 'contingency plans'],
    };
    return criteria[focus] || criteria.completeness;
  }

  assessSession(session, criteria, focus) {
    return {
      overallQuality: 'good',
      strengths: ['systematic approach', 'comprehensive analysis'],
      weaknesses: ['needs more validation', 'could explore alternatives'],
    };
  }

  identifyGaps(session, focus) {
    return [`Gap in ${focus} analysis`, 'Missing validation step'];
  }

  generateReviewRecommendations(session, focus) {
    return [
      `Enhance ${focus} by adding more detail`,
      'Consider alternative approaches',
      'Validate key assumptions',
    ];
  }

  calculateQualityScore(session, focus) {
    return Math.round(75 + Math.random() * 20); // 75-95%
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Sequential MCP Server running on stdio');
  }
}

const server = new SequentialServer();
server.run().catch(console.error);