import { JSDOM } from "jsdom";
import TurndownService from "turndown";
import { RequestPayload, RecursiveRequestPayload } from "./types.js";

class RecursiveFetcher {
  private visited = new Set<string>();
  private baseUrl: string;
  private maxDepth: number;
  private includeAssets: boolean;
  private followPattern?: RegExp;

  constructor(baseUrl: string, options: RecursiveRequestPayload) {
    this.baseUrl = new URL(baseUrl).origin;
    this.maxDepth = options.maxDepth;
    this.includeAssets = options.includeAssets;
    this.followPattern = options.followPattern ? new RegExp(options.followPattern) : undefined;
  }

  private isValidUrl(url: string): boolean {
    try {
      const parsed = new URL(url);
      return parsed.origin === this.baseUrl && 
             (!this.followPattern || this.followPattern.test(url));
    } catch {
      return false;
    }
  }

  private extractLinks(html: string, baseUrl: string): string[] {
    const dom = new JSDOM(html);
    const links = new Set<string>();
    
    // Extract page links
    dom.window.document.querySelectorAll('a[href]').forEach((link: Element) => {
      try {
        const href = new URL(link.getAttribute('href') || '', baseUrl).toString();
        if (this.isValidUrl(href)) {
          links.add(href);
        }
      } catch {}
    });

    // Extract asset links if enabled
    if (this.includeAssets) {
      ['img[src]', 'script[src]', 'link[href]'].forEach(selector => {
        dom.window.document.querySelectorAll(selector).forEach(element => {
          try {
            const url = new URL(
              element.getAttribute('src') || element.getAttribute('href') || '',
              baseUrl
            ).toString();
            if (this.isValidUrl(url)) {
              links.add(url);
            }
          } catch {}
        });
      });
    }

    return Array.from(links);
  }

  async fetch(url: string, depth = 1, headers?: Record<string, string>): Promise<Map<string, string>> {
    if (depth > this.maxDepth || this.visited.has(url)) {
      return new Map();
    }

    this.visited.add(url);
    const results = new Map<string, string>();

    try {
      const response = await fetch(url, { headers });
      const contentType = response.headers.get('content-type') || '';
      const content = await response.text();
      results.set(url, content);

      if (contentType.includes('text/html')) {
        const links = this.extractLinks(content, url);
        for (const link of links) {
          const subResults = await this.fetch(link, depth + 1, headers);
          subResults.forEach((value, key) => results.set(key, value));
        }
      }
    } catch (error) {
      console.error(`Error fetching ${url}:`, error);
    }

    return results;
  }
}

export class Fetcher {
  private static async _fetch({
    url,
    headers,
  }: RequestPayload): Promise<Response> {
    try {
      const response = await fetch(url, {
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
          ...headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      return response;
    } catch (e: unknown) {
      if (e instanceof Error) {
        throw new Error(`Failed to fetch ${url}: ${e.message}`);
      } else {
        throw new Error(`Failed to fetch ${url}: Unknown error`);
      }
    }
  }

  static async html(requestPayload: RequestPayload) {
    try {
      const response = await this._fetch(requestPayload);
      const html = await response.text();
      return { content: [{ type: "text", text: html }], isError: false };
    } catch (error) {
      return {
        content: [{ type: "text", text: (error as Error).message }],
        isError: true,
      };
    }
  }

  static async json(requestPayload: RequestPayload) {
    try {
      const response = await this._fetch(requestPayload);
      const json = await response.json();
      return {
        content: [{ type: "text", text: JSON.stringify(json) }],
        isError: false,
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: (error as Error).message }],
        isError: true,
      };
    }
  }

  static async txt(requestPayload: RequestPayload) {
    try {
      const response = await this._fetch(requestPayload);
      const html = await response.text();

      const dom = new JSDOM(html);
      const document = dom.window.document;

      const scripts = document.getElementsByTagName("script");
      const styles = document.getElementsByTagName("style");
      Array.from(scripts).forEach((script) => script.remove());
      Array.from(styles).forEach((style) => style.remove());

      const text = document.body.textContent || "";

      const normalizedText = text.replace(/\s+/g, " ").trim();

      return {
        content: [{ type: "text", text: normalizedText }],
        isError: false,
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: (error as Error).message }],
        isError: true,
      };
    }
  }

  static async markdown(requestPayload: RequestPayload) {
    try {
      const response = await this._fetch(requestPayload);
      const html = await response.text();
      const turndownService = new TurndownService();
      const markdown = turndownService.turndown(html);
      return { content: [{ type: "text", text: markdown }], isError: false };
    } catch (error) {
      return {
        content: [{ type: "text", text: (error as Error).message }],
        isError: true,
      };
    }
  }
}
