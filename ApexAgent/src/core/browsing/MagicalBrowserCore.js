/**
 * MagicalBrowserCore.js
 * 
 * Core implementation of Aideon AI Lite's magical web browsing experience.
 * This module provides advanced browsing capabilities with AI-powered understanding,
 * proactive assistance, and seamless interactions.
 */

const EventEmitter = require('events');
const puppeteer = require('puppeteer');
const natural = require('natural');
const { v4: uuidv4 } = require('uuid');

/**
 * MagicalBrowserCore class
 * Provides enhanced web browsing capabilities with AI-powered features
 */
class MagicalBrowserCore extends EventEmitter {
  /**
   * Initialize the Magical Browser Core
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    super();
    this.core = core;
    this.logger = core.logManager.getLogger('magical-browser');
    this.config = core.configManager.getConfig().browser || {};
    this.modelFramework = core.modelIntegrationFramework;
    this.taskAwareModelSelector = core.taskAwareModelSelector;
    
    // Browser instance
    this.browser = null;
    
    // Active pages
    this.pages = new Map();
    
    // Page metadata and insights
    this.pageInsights = new Map();
    
    // Browsing history with enhanced metadata
    this.history = [];
    
    // Maximum history size
    this.maxHistorySize = this.config.maxHistorySize || 1000;
    
    // Page content cache
    this.contentCache = new Map();
    
    // Page content analyzer
    this.contentAnalyzer = new PageContentAnalyzer();
    
    // Visual memory system
    this.visualMemory = new VisualMemorySystem();
    
    // Proactive suggestions engine
    this.suggestionEngine = new ProactiveSuggestionEngine(this);
    
    // Interaction recorder
    this.interactionRecorder = new InteractionRecorder();
    
    // Initialized flag
    this.initialized = false;
    
    this.logger.info('Magical Browser Core initialized');
  }
  
  /**
   * Initialize the browser
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      this.logger.info('Initializing Magical Browser Core...');
      
      // Launch browser
      this.browser = await puppeteer.launch({
        headless: this.config.headless !== false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--disable-gpu',
          '--window-size=1920,1080'
        ],
        defaultViewport: {
          width: 1920,
          height: 1080
        }
      });
      
      // Initialize components
      await this.contentAnalyzer.initialize();
      await this.visualMemory.initialize();
      await this.suggestionEngine.initialize();
      
      // Set up event listeners
      this._setupEventListeners();
      
      this.initialized = true;
      this.logger.info('Magical Browser Core initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize Magical Browser Core:', error);
      throw error;
    }
  }
  
  /**
   * Set up event listeners
   * @private
   */
  _setupEventListeners() {
    // Listen for browser events
    this.browser.on('disconnected', () => {
      this.logger.warn('Browser disconnected');
      this.initialized = false;
    });
    
    // Listen for page events
    this.on('page:loaded', this._handlePageLoaded.bind(this));
    this.on('page:navigated', this._handlePageNavigated.bind(this));
    this.on('page:interaction', this._handlePageInteraction.bind(this));
  }
  
  /**
   * Handle page loaded event
   * @param {Object} data - Event data
   * @private
   */
  async _handlePageLoaded(data) {
    const { pageId, url, title } = data;
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        this.logger.warn(`Page ${pageId} not found`);
        return;
      }
      
      // Extract page content
      const content = await this._extractPageContent(page);
      
      // Cache content
      this.contentCache.set(pageId, content);
      
      // Analyze content
      const insights = await this.contentAnalyzer.analyze(content, url);
      
      // Store insights
      this.pageInsights.set(pageId, insights);
      
      // Generate visual memory
      await this.visualMemory.capturePageMemory(pageId, page, insights);
      
      // Generate suggestions
      const suggestions = await this.suggestionEngine.generateSuggestions(pageId, insights);
      
      // Emit insights event
      this.emit('page:insights', {
        pageId,
        url,
        title,
        insights,
        suggestions
      });
      
      this.logger.info(`Page ${pageId} loaded and analyzed`);
    } catch (error) {
      this.logger.error(`Failed to handle page loaded event for ${pageId}:`, error);
    }
  }
  
  /**
   * Handle page navigated event
   * @param {Object} data - Event data
   * @private
   */
  async _handlePageNavigated(data) {
    const { pageId, url, title, timestamp } = data;
    
    try {
      // Add to history
      this.history.push({
        id: uuidv4(),
        pageId,
        url,
        title,
        timestamp,
        screenshot: await this.visualMemory.getPageThumbnail(pageId)
      });
      
      // Trim history if needed
      if (this.history.length > this.maxHistorySize) {
        this.history = this.history.slice(-this.maxHistorySize);
      }
      
      // Emit history updated event
      this.emit('history:updated', {
        history: this.history
      });
      
      this.logger.info(`Page ${pageId} navigated to ${url}`);
    } catch (error) {
      this.logger.error(`Failed to handle page navigated event for ${pageId}:`, error);
    }
  }
  
  /**
   * Handle page interaction event
   * @param {Object} data - Event data
   * @private
   */
  async _handlePageInteraction(data) {
    const { pageId, type, target, value } = data;
    
    try {
      // Record interaction
      this.interactionRecorder.recordInteraction(pageId, type, target, value);
      
      // Update suggestions based on interaction
      const insights = this.pageInsights.get(pageId);
      
      if (insights) {
        const suggestions = await this.suggestionEngine.generateSuggestions(pageId, insights, {
          interactionType: type,
          interactionTarget: target,
          interactionValue: value
        });
        
        // Emit suggestions event
        this.emit('suggestions:updated', {
          pageId,
          suggestions
        });
      }
      
      this.logger.debug(`Page ${pageId} interaction: ${type} on ${target}`);
    } catch (error) {
      this.logger.error(`Failed to handle page interaction event for ${pageId}:`, error);
    }
  }
  
  /**
   * Create a new page
   * @returns {Promise<string>} Page ID
   */
  async createPage() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Create page
      const page = await this.browser.newPage();
      
      // Generate ID
      const pageId = uuidv4();
      
      // Store page
      this.pages.set(pageId, page);
      
      // Set up page event listeners
      await this._setupPageEventListeners(pageId, page);
      
      this.logger.info(`Created page ${pageId}`);
      
      return pageId;
    } catch (error) {
      this.logger.error('Failed to create page:', error);
      throw error;
    }
  }
  
  /**
   * Set up page event listeners
   * @param {string} pageId - Page ID
   * @param {Object} page - Puppeteer page
   * @returns {Promise<void>}
   * @private
   */
  async _setupPageEventListeners(pageId, page) {
    // Listen for page load
    page.on('load', async () => {
      try {
        const url = page.url();
        const title = await page.title();
        
        this.emit('page:loaded', {
          pageId,
          url,
          title,
          timestamp: Date.now()
        });
      } catch (error) {
        this.logger.error(`Failed to handle page load event for ${pageId}:`, error);
      }
    });
    
    // Listen for navigation
    page.on('framenavigated', async frame => {
      if (frame === page.mainFrame()) {
        try {
          const url = frame.url();
          const title = await frame.title();
          
          this.emit('page:navigated', {
            pageId,
            url,
            title,
            timestamp: Date.now()
          });
        } catch (error) {
          this.logger.error(`Failed to handle frame navigated event for ${pageId}:`, error);
        }
      }
    });
    
    // Listen for console messages
    page.on('console', message => {
      this.logger.debug(`Page ${pageId} console: ${message.type()}: ${message.text()}`);
    });
    
    // Listen for errors
    page.on('error', error => {
      this.logger.error(`Page ${pageId} error:`, error);
    });
    
    // Listen for page close
    page.on('close', () => {
      this.pages.delete(pageId);
      this.contentCache.delete(pageId);
      this.pageInsights.delete(pageId);
      this.visualMemory.deletePageMemory(pageId);
      
      this.logger.info(`Page ${pageId} closed`);
    });
    
    // Inject interaction tracking script
    await page.evaluateOnNewDocument(() => {
      // Track clicks
      document.addEventListener('click', event => {
        const target = event.target;
        const tagName = target.tagName.toLowerCase();
        const id = target.id;
        const className = target.className;
        const text = target.innerText;
        
        window.__aideonTrackInteraction('click', {
          tagName,
          id,
          className,
          text,
          x: event.clientX,
          y: event.clientY
        });
      });
      
      // Track form inputs
      document.addEventListener('input', event => {
        const target = event.target;
        const tagName = target.tagName.toLowerCase();
        const id = target.id;
        const className = target.className;
        const type = target.type;
        
        window.__aideonTrackInteraction('input', {
          tagName,
          id,
          className,
          type
        });
      });
      
      // Track scrolls
      document.addEventListener('scroll', event => {
        window.__aideonTrackInteraction('scroll', {
          scrollX: window.scrollX,
          scrollY: window.scrollY
        });
      });
      
      // Define tracking function
      window.__aideonTrackInteraction = (type, data) => {
        window.__aideonInteractions = window.__aideonInteractions || [];
        window.__aideonInteractions.push({
          type,
          data,
          timestamp: Date.now()
        });
      };
    });
    
    // Set up interval to collect interactions
    setInterval(async () => {
      try {
        const interactions = await page.evaluate(() => {
          const interactions = window.__aideonInteractions || [];
          window.__aideonInteractions = [];
          return interactions;
        });
        
        for (const interaction of interactions) {
          this.emit('page:interaction', {
            pageId,
            type: interaction.type,
            target: interaction.data,
            timestamp: interaction.timestamp
          });
        }
      } catch (error) {
        // Page might be closed
      }
    }, 1000);
  }
  
  /**
   * Navigate to URL
   * @param {string} pageId - Page ID
   * @param {string} url - URL to navigate to
   * @returns {Promise<void>}
   */
  async navigateTo(pageId, url) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Navigate to URL
      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 60000
      });
      
      this.logger.info(`Navigated page ${pageId} to ${url}`);
    } catch (error) {
      this.logger.error(`Failed to navigate page ${pageId} to ${url}:`, error);
      throw error;
    }
  }
  
  /**
   * Extract page content
   * @param {Object} page - Puppeteer page
   * @returns {Promise<Object>} Page content
   * @private
   */
  async _extractPageContent(page) {
    try {
      // Extract metadata
      const url = page.url();
      const title = await page.title();
      
      // Extract text content
      const textContent = await page.evaluate(() => {
        return document.body.innerText;
      });
      
      // Extract HTML content
      const htmlContent = await page.content();
      
      // Extract links
      const links = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links.map(link => ({
          text: link.innerText,
          href: link.href,
          title: link.title
        }));
      });
      
      // Extract images
      const images = await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        return images.map(img => ({
          src: img.src,
          alt: img.alt,
          width: img.width,
          height: img.height
        }));
      });
      
      // Extract headings
      const headings = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        return headings.map(heading => ({
          level: parseInt(heading.tagName.substring(1)),
          text: heading.innerText
        }));
      });
      
      // Extract main content
      const mainContent = await page.evaluate(() => {
        // Try to find main content element
        const selectors = [
          'main',
          'article',
          '#content',
          '.content',
          '#main',
          '.main'
        ];
        
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          
          if (element) {
            return element.innerText;
          }
        }
        
        // Fallback to body
        return document.body.innerText;
      });
      
      // Take screenshot
      const screenshot = await page.screenshot({
        type: 'jpeg',
        quality: 80,
        fullPage: false
      });
      
      return {
        url,
        title,
        textContent,
        htmlContent,
        links,
        images,
        headings,
        mainContent,
        screenshot: screenshot.toString('base64')
      };
    } catch (error) {
      this.logger.error('Failed to extract page content:', error);
      throw error;
    }
  }
  
  /**
   * Get page content
   * @param {string} pageId - Page ID
   * @returns {Promise<Object>} Page content
   */
  async getPageContent(pageId) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Check cache
      if (this.contentCache.has(pageId)) {
        return this.contentCache.get(pageId);
      }
      
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Extract content
      const content = await this._extractPageContent(page);
      
      // Cache content
      this.contentCache.set(pageId, content);
      
      return content;
    } catch (error) {
      this.logger.error(`Failed to get page content for ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get page insights
   * @param {string} pageId - Page ID
   * @returns {Promise<Object>} Page insights
   */
  async getPageInsights(pageId) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Check if insights exist
      if (this.pageInsights.has(pageId)) {
        return this.pageInsights.get(pageId);
      }
      
      // Get page content
      const content = await this.getPageContent(pageId);
      
      // Analyze content
      const insights = await this.contentAnalyzer.analyze(content, content.url);
      
      // Store insights
      this.pageInsights.set(pageId, insights);
      
      return insights;
    } catch (error) {
      this.logger.error(`Failed to get page insights for ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get page suggestions
   * @param {string} pageId - Page ID
   * @returns {Promise<Array<Object>>} Page suggestions
   */
  async getPageSuggestions(pageId) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page insights
      const insights = await this.getPageInsights(pageId);
      
      // Generate suggestions
      const suggestions = await this.suggestionEngine.generateSuggestions(pageId, insights);
      
      return suggestions;
    } catch (error) {
      this.logger.error(`Failed to get page suggestions for ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Click element
   * @param {string} pageId - Page ID
   * @param {Object} selector - Element selector
   * @returns {Promise<void>}
   */
  async clickElement(pageId, selector) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Click element
      if (typeof selector === 'string') {
        await page.click(selector);
      } else if (selector.index !== undefined) {
        // Click by element index
        await page.evaluate(index => {
          const elements = document.querySelectorAll('a, button, input[type="button"], input[type="submit"], [role="button"]');
          
          if (index >= 0 && index < elements.length) {
            elements[index].click();
            return true;
          }
          
          return false;
        }, selector.index);
      } else if (selector.x !== undefined && selector.y !== undefined) {
        // Click by coordinates
        await page.mouse.click(selector.x, selector.y);
      } else {
        throw new Error('Invalid selector');
      }
      
      this.logger.info(`Clicked element on page ${pageId}`);
    } catch (error) {
      this.logger.error(`Failed to click element on page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Type text
   * @param {string} pageId - Page ID
   * @param {string|Object} selector - Element selector
   * @param {string} text - Text to type
   * @returns {Promise<void>}
   */
  async typeText(pageId, selector, text) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Type text
      if (typeof selector === 'string') {
        await page.type(selector, text);
      } else if (selector.index !== undefined) {
        // Type by element index
        await page.evaluate((index, text) => {
          const elements = document.querySelectorAll('input[type="text"], input[type="search"], input[type="email"], input[type="password"], textarea');
          
          if (index >= 0 && index < elements.length) {
            elements[index].value = text;
            return true;
          }
          
          return false;
        }, selector.index, text);
      } else {
        throw new Error('Invalid selector');
      }
      
      this.logger.info(`Typed text on page ${pageId}`);
    } catch (error) {
      this.logger.error(`Failed to type text on page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Scroll page
   * @param {string} pageId - Page ID
   * @param {Object} options - Scroll options
   * @returns {Promise<void>}
   */
  async scrollPage(pageId, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Scroll page
      if (options.toBottom) {
        await page.evaluate(() => {
          window.scrollTo(0, document.body.scrollHeight);
        });
      } else if (options.toTop) {
        await page.evaluate(() => {
          window.scrollTo(0, 0);
        });
      } else {
        const distance = options.distance || 500;
        
        await page.evaluate(distance => {
          window.scrollBy(0, distance);
        }, distance);
      }
      
      this.logger.info(`Scrolled page ${pageId}`);
    } catch (error) {
      this.logger.error(`Failed to scroll page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Execute JavaScript
   * @param {string} pageId - Page ID
   * @param {string} script - JavaScript to execute
   * @returns {Promise<any>} Script result
   */
  async executeJavaScript(pageId, script) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Execute script
      const result = await page.evaluate(script => {
        // eslint-disable-next-line no-eval
        return eval(script);
      }, script);
      
      this.logger.info(`Executed JavaScript on page ${pageId}`);
      
      return result;
    } catch (error) {
      this.logger.error(`Failed to execute JavaScript on page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Take screenshot
   * @param {string} pageId - Page ID
   * @param {Object} options - Screenshot options
   * @returns {Promise<string>} Screenshot as base64
   */
  async takeScreenshot(pageId, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        throw new Error(`Page ${pageId} not found`);
      }
      
      // Take screenshot
      const screenshot = await page.screenshot({
        type: options.type || 'jpeg',
        quality: options.quality || 80,
        fullPage: options.fullPage || false
      });
      
      this.logger.info(`Took screenshot of page ${pageId}`);
      
      return screenshot.toString('base64');
    } catch (error) {
      this.logger.error(`Failed to take screenshot of page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Get browsing history
   * @param {number} limit - Maximum number of items to return
   * @returns {Array<Object>} Browsing history
   */
  getBrowsingHistory(limit = 100) {
    return this.history.slice(-limit);
  }
  
  /**
   * Clear browsing history
   * @returns {void}
   */
  clearBrowsingHistory() {
    this.history = [];
    
    // Emit history updated event
    this.emit('history:updated', {
      history: this.history
    });
    
    this.logger.info('Cleared browsing history');
  }
  
  /**
   * Close page
   * @param {string} pageId - Page ID
   * @returns {Promise<void>}
   */
  async closePage(pageId) {
    if (!this.initialized) {
      return;
    }
    
    try {
      // Get page
      const page = this.pages.get(pageId);
      
      if (!page) {
        this.logger.warn(`Page ${pageId} not found`);
        return;
      }
      
      // Close page
      await page.close();
      
      this.logger.info(`Closed page ${pageId}`);
    } catch (error) {
      this.logger.error(`Failed to close page ${pageId}:`, error);
      throw error;
    }
  }
  
  /**
   * Clean up resources
   * @returns {Promise<void>}
   */
  async shutdown() {
    if (!this.initialized) {
      return;
    }
    
    try {
      this.logger.info('Shutting down Magical Browser Core...');
      
      // Close all pages
      for (const [pageId, page] of this.pages.entries()) {
        try {
          await page.close();
          this.logger.info(`Closed page ${pageId}`);
        } catch (error) {
          this.logger.error(`Failed to close page ${pageId}:`, error);
        }
      }
      
      // Close browser
      await this.browser.close();
      
      // Clear data
      this.pages.clear();
      this.contentCache.clear();
      this.pageInsights.clear();
      
      this.initialized = false;
      this.logger.info('Magical Browser Core shut down successfully');
    } catch (error) {
      this.logger.error('Failed to shut down Magical Browser Core:', error);
      throw error;
    }
  }
}

/**
 * PageContentAnalyzer class
 * Analyzes page content to extract insights
 */
class PageContentAnalyzer {
  constructor() {
    // Tokenizer
    this.tokenizer = new natural.WordTokenizer();
    
    // TF-IDF
    this.tfidf = new natural.TfIdf();
    
    // Initialized flag
    this.initialized = false;
  }
  
  /**
   * Initialize the analyzer
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    // Initialize NLP components
    
    this.initialized = true;
  }
  
  /**
   * Analyze page content
   * @param {Object} content - Page content
   * @param {string} url - Page URL
   * @returns {Promise<Object>} Page insights
   */
  async analyze(content, url) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // Extract keywords
      const keywords = this._extractKeywords(content.textContent);
      
      // Extract topics
      const topics = this._extractTopics(content.textContent);
      
      // Extract entities
      const entities = this._extractEntities(content.textContent);
      
      // Extract sentiment
      const sentiment = this._extractSentiment(content.textContent);
      
      // Extract readability
      const readability = this._extractReadability(content.textContent);
      
      // Extract summary
      const summary = this._extractSummary(content.textContent);
      
      // Extract page type
      const pageType = this._extractPageType(content, url);
      
      return {
        keywords,
        topics,
        entities,
        sentiment,
        readability,
        summary,
        pageType
      };
    } catch (error) {
      console.error('Failed to analyze page content:', error);
      throw error;
    }
  }
  
  /**
   * Extract keywords from text
   * @param {string} text - Text to analyze
   * @returns {Array<Object>} Keywords
   * @private
   */
  _extractKeywords(text) {
    try {
      // Clear TF-IDF
      this.tfidf = new natural.TfIdf();
      
      // Add document
      this.tfidf.addDocument(text);
      
      // Extract keywords
      const keywords = [];
      
      this.tfidf.listTerms(0).slice(0, 10).forEach(term => {
        keywords.push({
          term: term.term,
          tfidf: term.tfidf
        });
      });
      
      return keywords;
    } catch (error) {
      console.error('Failed to extract keywords:', error);
      return [];
    }
  }
  
  /**
   * Extract topics from text
   * @param {string} text - Text to analyze
   * @returns {Array<string>} Topics
   * @private
   */
  _extractTopics(text) {
    try {
      // Simple topic extraction based on keyword clustering
      const keywords = this._extractKeywords(text);
      
      // Group similar keywords
      const topics = [];
      
      // For now, just return top keywords as topics
      keywords.slice(0, 5).forEach(keyword => {
        topics.push(keyword.term);
      });
      
      return topics;
    } catch (error) {
      console.error('Failed to extract topics:', error);
      return [];
    }
  }
  
  /**
   * Extract entities from text
   * @param {string} text - Text to analyze
   * @returns {Object} Entities
   * @private
   */
  _extractEntities(text) {
    try {
      // Simple entity extraction
      const entities = {
        persons: [],
        organizations: [],
        locations: [],
        dates: [],
        urls: []
      };
      
      // Extract URLs
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const urls = text.match(urlRegex) || [];
      
      entities.urls = urls;
      
      // For now, return basic entities
      return entities;
    } catch (error) {
      console.error('Failed to extract entities:', error);
      return {
        persons: [],
        organizations: [],
        locations: [],
        dates: [],
        urls: []
      };
    }
  }
  
  /**
   * Extract sentiment from text
   * @param {string} text - Text to analyze
   * @returns {Object} Sentiment
   * @private
   */
  _extractSentiment(text) {
    try {
      // Simple sentiment analysis
      const analyzer = new natural.SentimentAnalyzer('English', natural.PorterStemmer, 'afinn');
      
      // Tokenize text
      const tokens = this.tokenizer.tokenize(text);
      
      // Analyze sentiment
      const score = analyzer.getSentiment(tokens);
      
      return {
        score,
        label: score > 0.2 ? 'positive' : score < -0.2 ? 'negative' : 'neutral'
      };
    } catch (error) {
      console.error('Failed to extract sentiment:', error);
      return {
        score: 0,
        label: 'neutral'
      };
    }
  }
  
  /**
   * Extract readability from text
   * @param {string} text - Text to analyze
   * @returns {Object} Readability
   * @private
   */
  _extractReadability(text) {
    try {
      // Simple readability analysis
      const sentences = text.split(/[.!?]+/).filter(Boolean);
      const words = text.split(/\s+/).filter(Boolean);
      
      // Calculate average sentence length
      const avgSentenceLength = words.length / sentences.length;
      
      // Calculate average word length
      const avgWordLength = text.length / words.length;
      
      // Calculate readability score (simplified Flesch-Kincaid)
      const readabilityScore = 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgWordLength / 5);
      
      return {
        score: readabilityScore,
        level: readabilityScore > 90 ? 'very_easy' : readabilityScore > 80 ? 'easy' : readabilityScore > 70 ? 'fairly_easy' : readabilityScore > 60 ? 'standard' : readabilityScore > 50 ? 'fairly_difficult' : readabilityScore > 30 ? 'difficult' : 'very_difficult'
      };
    } catch (error) {
      console.error('Failed to extract readability:', error);
      return {
        score: 60,
        level: 'standard'
      };
    }
  }
  
  /**
   * Extract summary from text
   * @param {string} text - Text to analyze
   * @returns {string} Summary
   * @private
   */
  _extractSummary(text) {
    try {
      // Simple extractive summarization
      const sentences = text.split(/[.!?]+/).filter(Boolean).map(s => s.trim());
      
      if (sentences.length <= 3) {
        return text;
      }
      
      // Score sentences based on position and keyword overlap
      const keywords = this._extractKeywords(text);
      const keywordTerms = keywords.map(k => k.term);
      
      const scoredSentences = sentences.map((sentence, index) => {
        // Position score (favor beginning)
        const positionScore = 1 - (index / sentences.length);
        
        // Keyword score
        const words = sentence.toLowerCase().split(/\s+/);
        const keywordMatches = words.filter(word => keywordTerms.includes(word)).length;
        const keywordScore = keywordMatches / words.length;
        
        // Length score (favor medium-length sentences)
        const lengthScore = 1 - Math.abs(words.length - 20) / 20;
        
        // Combined score
        const score = (positionScore * 0.3) + (keywordScore * 0.5) + (lengthScore * 0.2);
        
        return {
          sentence,
          score
        };
      });
      
      // Sort by score
      scoredSentences.sort((a, b) => b.score - a.score);
      
      // Take top 3 sentences
      const topSentences = scoredSentences.slice(0, 3);
      
      // Sort by original position
      topSentences.sort((a, b) => {
        return sentences.indexOf(a.sentence) - sentences.indexOf(b.sentence);
      });
      
      // Join sentences
      return topSentences.map(s => s.sentence).join('. ') + '.';
    } catch (error) {
      console.error('Failed to extract summary:', error);
      return text.substring(0, 200) + '...';
    }
  }
  
  /**
   * Extract page type
   * @param {Object} content - Page content
   * @param {string} url - Page URL
   * @returns {string} Page type
   * @private
   */
  _extractPageType(content, url) {
    try {
      // Check URL patterns
      if (url.includes('/product') || url.includes('/item') || url.includes('/shop')) {
        return 'product';
      }
      
      if (url.includes('/article') || url.includes('/blog') || url.includes('/post')) {
        return 'article';
      }
      
      if (url.includes('/about')) {
        return 'about';
      }
      
      if (url.includes('/contact')) {
        return 'contact';
      }
      
      if (url.includes('/search')) {
        return 'search';
      }
      
      // Check content patterns
      if (content.htmlContent.includes('<form') && (content.htmlContent.includes('login') || content.htmlContent.includes('sign in'))) {
        return 'login';
      }
      
      if (content.htmlContent.includes('<form') && (content.htmlContent.includes('register') || content.htmlContent.includes('sign up'))) {
        return 'registration';
      }
      
      if (content.htmlContent.includes('<form') && content.htmlContent.includes('checkout')) {
        return 'checkout';
      }
      
      // Default to generic
      return 'generic';
    } catch (error) {
      console.error('Failed to extract page type:', error);
      return 'generic';
    }
  }
}

/**
 * VisualMemorySystem class
 * Manages visual memories of browsed pages
 */
class VisualMemorySystem {
  constructor() {
    // Page memories
    this.memories = new Map();
    
    // Initialized flag
    this.initialized = false;
  }
  
  /**
   * Initialize the visual memory system
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    this.initialized = true;
  }
  
  /**
   * Capture page memory
   * @param {string} pageId - Page ID
   * @param {Object} page - Puppeteer page
   * @param {Object} insights - Page insights
   * @returns {Promise<void>}
   */
  async capturePageMemory(pageId, page, insights) {
    try {
      // Take screenshot
      const screenshot = await page.screenshot({
        type: 'jpeg',
        quality: 60,
        fullPage: false
      });
      
      // Generate thumbnail
      const thumbnail = await this._generateThumbnail(screenshot);
      
      // Store memory
      this.memories.set(pageId, {
        screenshot: screenshot.toString('base64'),
        thumbnail: thumbnail.toString('base64'),
        insights,
        timestamp: Date.now()
      });
    } catch (error) {
      console.error(`Failed to capture page memory for ${pageId}:`, error);
    }
  }
  
  /**
   * Generate thumbnail
   * @param {Buffer} screenshot - Screenshot buffer
   * @returns {Promise<Buffer>} Thumbnail buffer
   * @private
   */
  async _generateThumbnail(screenshot) {
    // For now, just return the original screenshot
    // In a real implementation, this would resize the image
    return screenshot;
  }
  
  /**
   * Get page screenshot
   * @param {string} pageId - Page ID
   * @returns {string|null} Screenshot as base64
   */
  getPageScreenshot(pageId) {
    const memory = this.memories.get(pageId);
    
    if (!memory) {
      return null;
    }
    
    return memory.screenshot;
  }
  
  /**
   * Get page thumbnail
   * @param {string} pageId - Page ID
   * @returns {string|null} Thumbnail as base64
   */
  getPageThumbnail(pageId) {
    const memory = this.memories.get(pageId);
    
    if (!memory) {
      return null;
    }
    
    return memory.thumbnail;
  }
  
  /**
   * Delete page memory
   * @param {string} pageId - Page ID
   * @returns {void}
   */
  deletePageMemory(pageId) {
    this.memories.delete(pageId);
  }
}

/**
 * ProactiveSuggestionEngine class
 * Generates proactive suggestions based on page content and user behavior
 */
class ProactiveSuggestionEngine {
  /**
   * Initialize the Proactive Suggestion Engine
   * @param {MagicalBrowserCore} browserCore - Reference to the browser core
   */
  constructor(browserCore) {
    this.browserCore = browserCore;
    
    // Suggestion cache
    this.suggestionCache = new Map();
    
    // Initialized flag
    this.initialized = false;
  }
  
  /**
   * Initialize the suggestion engine
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    this.initialized = true;
  }
  
  /**
   * Generate suggestions
   * @param {string} pageId - Page ID
   * @param {Object} insights - Page insights
   * @param {Object} context - Context information
   * @returns {Promise<Array<Object>>} Suggestions
   */
  async generateSuggestions(pageId, insights, context = {}) {
    try {
      // Generate different types of suggestions
      const suggestions = [];
      
      // Add content-based suggestions
      const contentSuggestions = await this._generateContentSuggestions(insights);
      suggestions.push(...contentSuggestions);
      
      // Add action-based suggestions
      const actionSuggestions = await this._generateActionSuggestions(pageId, insights, context);
      suggestions.push(...actionSuggestions);
      
      // Add navigation suggestions
      const navigationSuggestions = await this._generateNavigationSuggestions(pageId, insights);
      suggestions.push(...navigationSuggestions);
      
      // Cache suggestions
      this.suggestionCache.set(pageId, {
        suggestions,
        timestamp: Date.now()
      });
      
      return suggestions;
    } catch (error) {
      console.error(`Failed to generate suggestions for page ${pageId}:`, error);
      return [];
    }
  }
  
  /**
   * Generate content-based suggestions
   * @param {Object} insights - Page insights
   * @returns {Promise<Array<Object>>} Suggestions
   * @private
   */
  async _generateContentSuggestions(insights) {
    const suggestions = [];
    
    // Add summary suggestion
    if (insights.summary) {
      suggestions.push({
        type: 'content',
        subtype: 'summary',
        title: 'Page Summary',
        description: insights.summary,
        priority: 0.9
      });
    }
    
    // Add keyword suggestion
    if (insights.keywords && insights.keywords.length > 0) {
      suggestions.push({
        type: 'content',
        subtype: 'keywords',
        title: 'Key Topics',
        description: insights.keywords.slice(0, 5).map(k => k.term).join(', '),
        priority: 0.7
      });
    }
    
    // Add sentiment suggestion
    if (insights.sentiment) {
      const sentimentEmoji = insights.sentiment.label === 'positive' ? '😊' : insights.sentiment.label === 'negative' ? '😟' : '😐';
      
      suggestions.push({
        type: 'content',
        subtype: 'sentiment',
        title: 'Content Tone',
        description: `${sentimentEmoji} This page has a ${insights.sentiment.label} tone`,
        priority: 0.5
      });
    }
    
    return suggestions;
  }
  
  /**
   * Generate action-based suggestions
   * @param {string} pageId - Page ID
   * @param {Object} insights - Page insights
   * @param {Object} context - Context information
   * @returns {Promise<Array<Object>>} Suggestions
   * @private
   */
  async _generateActionSuggestions(pageId, insights, context) {
    const suggestions = [];
    
    // Add search suggestion if on search page
    if (insights.pageType === 'search') {
      suggestions.push({
        type: 'action',
        subtype: 'search',
        title: 'Refine Search',
        description: 'I can help you refine your search query for better results',
        priority: 0.8,
        action: {
          type: 'refine_search',
          pageId
        }
      });
    }
    
    // Add form fill suggestion if on login or registration page
    if (insights.pageType === 'login' || insights.pageType === 'registration') {
      suggestions.push({
        type: 'action',
        subtype: 'form_fill',
        title: 'Fill Form',
        description: `I can help you fill this ${insights.pageType} form`,
        priority: 0.8,
        action: {
          type: 'fill_form',
          pageId,
          formType: insights.pageType
        }
      });
    }
    
    // Add read aloud suggestion for articles
    if (insights.pageType === 'article') {
      suggestions.push({
        type: 'action',
        subtype: 'read_aloud',
        title: 'Read Aloud',
        description: 'I can read this article to you',
        priority: 0.6,
        action: {
          type: 'read_aloud',
          pageId
        }
      });
    }
    
    return suggestions;
  }
  
  /**
   * Generate navigation suggestions
   * @param {string} pageId - Page ID
   * @param {Object} insights - Page insights
   * @returns {Promise<Array<Object>>} Suggestions
   * @private
   */
  async _generateNavigationSuggestions(pageId, insights) {
    const suggestions = [];
    
    // Add related pages suggestion
    suggestions.push({
      type: 'navigation',
      subtype: 'related',
      title: 'Explore Related',
      description: 'I can find related content based on this page',
      priority: 0.7,
      action: {
        type: 'find_related',
        pageId
      }
    });
    
    return suggestions;
  }
}

/**
 * InteractionRecorder class
 * Records user interactions with pages
 */
class InteractionRecorder {
  constructor() {
    // Interaction records
    this.records = new Map();
  }
  
  /**
   * Record interaction
   * @param {string} pageId - Page ID
   * @param {string} type - Interaction type
   * @param {Object} target - Interaction target
   * @param {any} value - Interaction value
   * @returns {void}
   */
  recordInteraction(pageId, type, target, value) {
    // Get or create page records
    if (!this.records.has(pageId)) {
      this.records.set(pageId, []);
    }
    
    const pageRecords = this.records.get(pageId);
    
    // Add record
    pageRecords.push({
      type,
      target,
      value,
      timestamp: Date.now()
    });
    
    // Limit records
    if (pageRecords.length > 1000) {
      pageRecords.shift();
    }
  }
  
  /**
   * Get page interactions
   * @param {string} pageId - Page ID
   * @param {number} limit - Maximum number of records to return
   * @returns {Array<Object>} Interaction records
   */
  getPageInteractions(pageId, limit = 100) {
    const pageRecords = this.records.get(pageId) || [];
    
    return pageRecords.slice(-limit);
  }
  
  /**
   * Clear page interactions
   * @param {string} pageId - Page ID
   * @returns {void}
   */
  clearPageInteractions(pageId) {
    this.records.delete(pageId);
  }
}

module.exports = MagicalBrowserCore;
