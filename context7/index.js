#!/usr/bin/env node

/**
 * Context7 MCP Server
 * Documentation & Research server for library documentation, code examples, best practices
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';
import * as cheerio from 'cheerio';

class Context7Server {
  constructor() {
    this.server = new Server(
      {
        name: 'context7-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.libraryCache = new Map();
    this.documentationSources = {
      npm: 'https://YOUR-CREDENTIALS@YOUR-DOMAIN// Query npm registry for library info
      const response = await axios.get(`${this.documentationSources.npm}/${libraryName}`);
      const packageData = response.data;

      const libraryId = {
        name: packageData.name,
        version: version || packageData['dist-tags'].latest,
        description: packageData.description,
        repository: packageData.repository?.url,
        homepage: packageData.homepage,
        keywords: packageData.keywords || [],
        id: `npm:${packageData.name}@${version || packageData['dist-tags'].latest}`
      };

      // Cache the result
      this.libraryCache.set(cacheKey, {
        content: [
          {
            type: 'text',
            text: JSON.stringify(libraryId, null, 2),
          },
        ],
      });

      return this.libraryCache.get(cacheKey);
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to resolve library ${libraryName}: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async getLibraryDocs(libraryId, topic, includeExamples = true) {
    try {
      const [source, nameVersion] = libraryId.split(':');
      const [name] = nameVersion.split('@');

      let documentation = '';
      let examples = '';

      // Fetch from multiple sources
      const sources = await Promise.allSettled([
        this.fetchNpmDocs(name, topic),
        this.fetchGithubDocs(name, topic),
        this.fetchDevDocs(name, topic),
      ]);

      // Combine successful results
      documentation = sources
        .filter(result => result.status === 'fulfilled' && result.value)
        .map(result => result.value)
        .join('\n\n---\n\n');

      if (includeExamples) {
        examples = await this.fetchCodeExamples(name, topic);
      }

      const result = {
        library: name,
        topic: topic || 'general',
        documentation,
        examples: includeExamples ? examples : null,
        sources: ['npm', 'github', 'devdocs'],
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
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to get documentation for ${libraryId}: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async searchPatterns(query, language, framework) {
    try {
      const searchResults = {
        query,
        language,
        framework,
        patterns: [],
        timestamp: new Date().toISOString(),
      };

      // Search multiple pattern sources
      const patterns = await Promise.allSettled([
        this.searchGithubPatterns(query, language, framework),
        this.searchStackOverflowPatterns(query, language),
        this.searchDevDocsPatterns(query, framework),
      ]);

      // Combine and deduplicate results
      patterns
        .filter(result => result.status === 'fulfilled' && result.value)
        .forEach(result => {
          searchResults.patterns.push(...result.value);
        });

      // Sort by relevance (simplified scoring)
      searchResults.patterns.sort((a, b) => (b.score || 0) - (a.score || 0));

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(searchResults, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to search patterns: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  async getBestPractices(technology, category) {
    try {
      const bestPractices = {
        technology,
        category: category || 'general',
        practices: [],
        sources: [],
        timestamp: new Date().toISOString(),
      };

      // Fetch from curated best practices sources
      const practices = await Promise.allSettled([
        this.fetchOfficialBestPractices(technology, category),
        this.fetchCommunityBestPractices(technology, category),
        this.fetchSecurityBestPractices(technology, category),
      ]);

      practices
        .filter(result => result.status === 'fulfilled' && result.value)
        .forEach(result => {
          bestPractices.practices.push(...result.value.practices);
          bestPractices.sources.push(...result.value.sources);
        });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(bestPractices, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Failed to get best practices: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  // Helper methods for fetching from different sources
  async fetchNpmDocs(name, topic) {
    try {
      const response = await axios.get(`${this.documentationSources.npm}/${name}`);
      return response.data.readme || `Documentation for ${name}`;
    } catch {
      return null;
    }
  }

  async fetchGithubDocs(name, topic) {
    // Simplified GitHub API integration
    return `GitHub documentation for ${name}${topic ? ` - ${topic}` : ''}`;
  }

  async fetchDevDocs(name, topic) {
    // Simplified DevDocs integration
    return `DevDocs reference for ${name}${topic ? ` - ${topic}` : ''}`;
  }

  async fetchCodeExamples(name, topic) {
    // Simplified code examples fetching
    return `Code examples for ${name}${topic ? ` - ${topic}` : ''}`;
  }

  async searchGithubPatterns(query, language, framework) {
    // Simplified GitHub pattern search
    return [
      {
        title: `Pattern: ${query}`,
        description: `Implementation pattern for ${query}`,
        language,
        framework,
        score: 0.8,
      },
    ];
  }

  async searchStackOverflowPatterns(query, language) {
    // Simplified Stack Overflow search
    return [
      {
        title: `SO Pattern: ${query}`,
        description: `Community pattern for ${query}`,
        language,
        score: 0.7,
      },
    ];
  }

  async searchDevDocsPatterns(query, framework) {
    // Simplified DevDocs pattern search
    return [
      {
        title: `DevDocs Pattern: ${query}`,
        description: `Official pattern for ${query}`,
        framework,
        score: 0.9,
      },
    ];
  }

  async fetchOfficialBestPractices(technology, category) {
    // Simplified official best practices
    return {
      practices: [
        {
          title: `Official ${technology} Best Practice`,
          description: `Best practice for ${technology}${category ? ` - ${category}` : ''}`,
          category: category || 'general',
          source: 'official',
        },
      ],
      sources: ['official-docs'],
    };
  }

  async fetchCommunityBestPractices(technology, category) {
    // Simplified community best practices
    return {
      practices: [
        {
          title: `Community ${technology} Best Practice`,
          description: `Community-driven best practice for ${technology}`,
          category: category || 'general',
          source: 'community',
        },
      ],
      sources: ['community'],
    };
  }

  async fetchSecurityBestPractices(technology, category) {
    // Simplified security best practices
    if (category === 'security' || !category) {
      return {
        practices: [
          {
            title: `Security Best Practice for ${technology}`,
            description: `Security-focused best practice for ${technology}`,
            category: 'security',
            source: 'security',
          },
        ],
        sources: ['security-guides'],
      };
    }
    return { practices: [], sources: [] };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Context7 MCP Server running on stdio');
  }
}

const server = new Context7Server();
server.run().catch(console.error);