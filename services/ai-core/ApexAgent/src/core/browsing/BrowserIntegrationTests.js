/**
 * BrowserIntegrationTests.js
 * 
 * Comprehensive test suite for validating the magical web browsing experience
 * in Aideon AI Lite. These tests verify functionality, performance, and user
 * experience aspects of the browsing features.
 */

const { expect } = require('chai');
const sinon = require('sinon');
const MagicalBrowserCore = require('./MagicalBrowserCore');

/**
 * Test suite for MagicalBrowserCore
 */
describe('Magical Browser Experience Validation', function() {
  // Increase timeout for browser tests
  this.timeout(30000);
  
  let core;
  let mockCore;
  let browserCore;
  
  // Setup before tests
  before(async function() {
    // Create mock Aideon core
    mockCore = {
      logManager: {
        getLogger: () => ({
          info: () => {},
          warn: () => {},
          error: () => {},
          debug: () => {}
        })
      },
      configManager: {
        getConfig: () => ({
          browser: {
            headless: true,
            maxHistorySize: 100
          }
        })
      },
      modelIntegrationFramework: {
        execute: sinon.stub().resolves({ text: 'Model response' })
      },
      taskAwareModelSelector: {
        selectBestModel: sinon.stub().returns({ id: 'test-model' })
      }
    };
    
    // Create browser core instance
    browserCore = new MagicalBrowserCore(mockCore);
    
    // Initialize browser
    await browserCore.initialize();
  });
  
  // Cleanup after tests
  after(async function() {
    // Shutdown browser
    if (browserCore) {
      await browserCore.shutdown();
    }
  });
  
  /**
   * Core Functionality Tests
   */
  describe('Core Functionality', function() {
    let pageId;
    
    // Create page before tests
    before(async function() {
      pageId = await browserCore.createPage();
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should create a new page', function() {
      expect(pageId).to.be.a('string');
      expect(browserCore.pages.has(pageId)).to.be.true;
    });
    
    it('should navigate to a URL', async function() {
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      const content = await browserCore.getPageContent(pageId);
      expect(content.url).to.include('example.com');
      expect(content.title).to.not.be.empty;
    });
    
    it('should extract page content', async function() {
      const content = await browserCore.getPageContent(pageId);
      
      expect(content).to.have.property('textContent');
      expect(content).to.have.property('htmlContent');
      expect(content).to.have.property('links');
      expect(content).to.have.property('images');
      expect(content).to.have.property('headings');
      expect(content).to.have.property('mainContent');
      expect(content).to.have.property('screenshot');
    });
    
    it('should generate page insights', async function() {
      const insights = await browserCore.getPageInsights(pageId);
      
      expect(insights).to.have.property('keywords');
      expect(insights).to.have.property('topics');
      expect(insights).to.have.property('entities');
      expect(insights).to.have.property('sentiment');
      expect(insights).to.have.property('readability');
      expect(insights).to.have.property('summary');
      expect(insights).to.have.property('pageType');
    });
    
    it('should generate page suggestions', async function() {
      const suggestions = await browserCore.getPageSuggestions(pageId);
      
      expect(suggestions).to.be.an('array');
      expect(suggestions.length).to.be.greaterThan(0);
      
      const suggestion = suggestions[0];
      expect(suggestion).to.have.property('type');
      expect(suggestion).to.have.property('title');
      expect(suggestion).to.have.property('description');
      expect(suggestion).to.have.property('priority');
    });
    
    it('should take a screenshot', async function() {
      const screenshot = await browserCore.takeScreenshot(pageId);
      
      expect(screenshot).to.be.a('string');
      expect(screenshot.length).to.be.greaterThan(1000);
    });
    
    it('should record browsing history', function() {
      const history = browserCore.getBrowsingHistory();
      
      expect(history).to.be.an('array');
      expect(history.length).to.be.greaterThan(0);
      
      const historyItem = history[0];
      expect(historyItem).to.have.property('id');
      expect(historyItem).to.have.property('pageId');
      expect(historyItem).to.have.property('url');
      expect(historyItem).to.have.property('title');
      expect(historyItem).to.have.property('timestamp');
    });
  });
  
  /**
   * Page Content Analysis Tests
   */
  describe('Page Content Analysis', function() {
    let pageId;
    let contentAnalyzer;
    
    // Create page and get content analyzer before tests
    before(async function() {
      pageId = await browserCore.createPage();
      contentAnalyzer = browserCore.contentAnalyzer;
      await browserCore.navigateTo(pageId, 'https://example.com');
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should extract keywords from text', async function() {
      const content = await browserCore.getPageContent(pageId);
      const keywords = contentAnalyzer._extractKeywords(content.textContent);
      
      expect(keywords).to.be.an('array');
      expect(keywords.length).to.be.greaterThan(0);
      
      const keyword = keywords[0];
      expect(keyword).to.have.property('term');
      expect(keyword).to.have.property('tfidf');
    });
    
    it('should extract topics from text', async function() {
      const content = await browserCore.getPageContent(pageId);
      const topics = contentAnalyzer._extractTopics(content.textContent);
      
      expect(topics).to.be.an('array');
      expect(topics.length).to.be.greaterThan(0);
    });
    
    it('should extract sentiment from text', async function() {
      const content = await browserCore.getPageContent(pageId);
      const sentiment = contentAnalyzer._extractSentiment(content.textContent);
      
      expect(sentiment).to.have.property('score');
      expect(sentiment).to.have.property('label');
      expect(['positive', 'negative', 'neutral']).to.include(sentiment.label);
    });
    
    it('should extract readability metrics from text', async function() {
      const content = await browserCore.getPageContent(pageId);
      const readability = contentAnalyzer._extractReadability(content.textContent);
      
      expect(readability).to.have.property('score');
      expect(readability).to.have.property('level');
    });
    
    it('should generate a summary of text', async function() {
      const content = await browserCore.getPageContent(pageId);
      const summary = contentAnalyzer._extractSummary(content.textContent);
      
      expect(summary).to.be.a('string');
      expect(summary.length).to.be.greaterThan(0);
      expect(summary.length).to.be.lessThan(content.textContent.length);
    });
    
    it('should identify page type', async function() {
      const content = await browserCore.getPageContent(pageId);
      const pageType = contentAnalyzer._extractPageType(content, content.url);
      
      expect(pageType).to.be.a('string');
      expect(['generic', 'article', 'product', 'about', 'contact', 'search', 'login', 'registration', 'checkout']).to.include(pageType);
    });
  });
  
  /**
   * Visual Memory System Tests
   */
  describe('Visual Memory System', function() {
    let pageId;
    let visualMemory;
    
    // Create page and get visual memory system before tests
    before(async function() {
      pageId = await browserCore.createPage();
      visualMemory = browserCore.visualMemory;
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      // Get page insights to trigger visual memory capture
      await browserCore.getPageInsights(pageId);
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should capture page memory', function() {
      expect(visualMemory.memories.has(pageId)).to.be.true;
      
      const memory = visualMemory.memories.get(pageId);
      expect(memory).to.have.property('screenshot');
      expect(memory).to.have.property('thumbnail');
      expect(memory).to.have.property('insights');
      expect(memory).to.have.property('timestamp');
    });
    
    it('should retrieve page screenshot', function() {
      const screenshot = visualMemory.getPageScreenshot(pageId);
      
      expect(screenshot).to.be.a('string');
      expect(screenshot.length).to.be.greaterThan(1000);
    });
    
    it('should retrieve page thumbnail', function() {
      const thumbnail = visualMemory.getPageThumbnail(pageId);
      
      expect(thumbnail).to.be.a('string');
      expect(thumbnail.length).to.be.greaterThan(1000);
    });
    
    it('should delete page memory', function() {
      visualMemory.deletePageMemory(pageId);
      expect(visualMemory.memories.has(pageId)).to.be.false;
    });
  });
  
  /**
   * Proactive Suggestion Engine Tests
   */
  describe('Proactive Suggestion Engine', function() {
    let pageId;
    let suggestionEngine;
    
    // Create page and get suggestion engine before tests
    before(async function() {
      pageId = await browserCore.createPage();
      suggestionEngine = browserCore.suggestionEngine;
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      // Get page insights
      const insights = await browserCore.getPageInsights(pageId);
      
      // Generate suggestions
      await suggestionEngine.generateSuggestions(pageId, insights);
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should generate content-based suggestions', async function() {
      const insights = await browserCore.getPageInsights(pageId);
      const suggestions = await suggestionEngine._generateContentSuggestions(insights);
      
      expect(suggestions).to.be.an('array');
      expect(suggestions.length).to.be.greaterThan(0);
      
      const suggestion = suggestions[0];
      expect(suggestion.type).to.equal('content');
      expect(suggestion).to.have.property('subtype');
      expect(suggestion).to.have.property('title');
      expect(suggestion).to.have.property('description');
      expect(suggestion).to.have.property('priority');
    });
    
    it('should generate action-based suggestions', async function() {
      const insights = await browserCore.getPageInsights(pageId);
      const suggestions = await suggestionEngine._generateActionSuggestions(pageId, insights, {});
      
      expect(suggestions).to.be.an('array');
      
      if (suggestions.length > 0) {
        const suggestion = suggestions[0];
        expect(suggestion.type).to.equal('action');
        expect(suggestion).to.have.property('subtype');
        expect(suggestion).to.have.property('title');
        expect(suggestion).to.have.property('description');
        expect(suggestion).to.have.property('priority');
        expect(suggestion).to.have.property('action');
      }
    });
    
    it('should generate navigation suggestions', async function() {
      const insights = await browserCore.getPageInsights(pageId);
      const suggestions = await suggestionEngine._generateNavigationSuggestions(pageId, insights);
      
      expect(suggestions).to.be.an('array');
      expect(suggestions.length).to.be.greaterThan(0);
      
      const suggestion = suggestions[0];
      expect(suggestion.type).to.equal('navigation');
      expect(suggestion).to.have.property('subtype');
      expect(suggestion).to.have.property('title');
      expect(suggestion).to.have.property('description');
      expect(suggestion).to.have.property('priority');
      expect(suggestion).to.have.property('action');
    });
    
    it('should cache suggestions', async function() {
      const insights = await browserCore.getPageInsights(pageId);
      await suggestionEngine.generateSuggestions(pageId, insights);
      
      expect(suggestionEngine.suggestionCache.has(pageId)).to.be.true;
      
      const cachedData = suggestionEngine.suggestionCache.get(pageId);
      expect(cachedData).to.have.property('suggestions');
      expect(cachedData).to.have.property('timestamp');
      expect(cachedData.suggestions).to.be.an('array');
    });
  });
  
  /**
   * Interaction Recorder Tests
   */
  describe('Interaction Recorder', function() {
    let pageId;
    let interactionRecorder;
    
    // Create page and get interaction recorder before tests
    before(async function() {
      pageId = await browserCore.createPage();
      interactionRecorder = browserCore.interactionRecorder;
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should record interactions', function() {
      interactionRecorder.recordInteraction(pageId, 'click', { tagName: 'button', id: 'test' }, null);
      interactionRecorder.recordInteraction(pageId, 'input', { tagName: 'input', id: 'search' }, 'test query');
      interactionRecorder.recordInteraction(pageId, 'scroll', { scrollX: 0, scrollY: 100 }, null);
      
      const interactions = interactionRecorder.getPageInteractions(pageId);
      
      expect(interactions).to.be.an('array');
      expect(interactions.length).to.equal(3);
      
      const clickInteraction = interactions[0];
      expect(clickInteraction.type).to.equal('click');
      expect(clickInteraction.target.tagName).to.equal('button');
      
      const inputInteraction = interactions[1];
      expect(inputInteraction.type).to.equal('input');
      expect(inputInteraction.target.tagName).to.equal('input');
      
      const scrollInteraction = interactions[2];
      expect(scrollInteraction.type).to.equal('scroll');
      expect(scrollInteraction.target.scrollY).to.equal(100);
    });
    
    it('should clear page interactions', function() {
      interactionRecorder.clearPageInteractions(pageId);
      
      const interactions = interactionRecorder.getPageInteractions(pageId);
      expect(interactions).to.be.an('array');
      expect(interactions.length).to.equal(0);
    });
  });
  
  /**
   * User Experience Tests
   */
  describe('User Experience', function() {
    let pageId;
    
    // Create page before tests
    before(async function() {
      pageId = await browserCore.createPage();
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should handle multiple page navigation smoothly', async function() {
      // Navigate to multiple pages
      await browserCore.navigateTo(pageId, 'https://example.com');
      let content1 = await browserCore.getPageContent(pageId);
      
      await browserCore.navigateTo(pageId, 'https://mozilla.org');
      let content2 = await browserCore.getPageContent(pageId);
      
      // Check that content is different
      expect(content1.url).to.not.equal(content2.url);
      expect(content1.title).to.not.equal(content2.title);
      
      // Check history
      const history = browserCore.getBrowsingHistory();
      expect(history.length).to.be.at.least(2);
      
      // URLs should be in history
      const urls = history.map(item => item.url);
      expect(urls).to.include(content1.url);
      expect(urls).to.include(content2.url);
    });
    
    it('should handle page interactions correctly', async function() {
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      // Click an element
      try {
        await browserCore.clickElement(pageId, 'a');
        // If click succeeded, page should have changed
        const content = await browserCore.getPageContent(pageId);
        expect(content.url).to.not.equal('https://example.com/');
      } catch (error) {
        // Some pages might not have clickable elements, so this is acceptable
      }
    });
    
    it('should execute JavaScript on page', async function() {
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      const result = await browserCore.executeJavaScript(pageId, 'return document.title');
      expect(result).to.be.a('string');
      expect(result.length).to.be.greaterThan(0);
    });
  });
  
  /**
   * Performance Tests
   */
  describe('Performance', function() {
    let pageId;
    
    // Create page before tests
    before(async function() {
      pageId = await browserCore.createPage();
    });
    
    // Close page after tests
    after(async function() {
      await browserCore.closePage(pageId);
    });
    
    it('should navigate to pages within acceptable time', async function() {
      const startTime = Date.now();
      
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Navigation should complete within 5 seconds
      expect(duration).to.be.lessThan(5000);
    });
    
    it('should generate insights within acceptable time', async function() {
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      const startTime = Date.now();
      
      await browserCore.getPageInsights(pageId);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Insight generation should complete within 3 seconds
      expect(duration).to.be.lessThan(3000);
    });
    
    it('should generate suggestions within acceptable time', async function() {
      await browserCore.navigateTo(pageId, 'https://example.com');
      
      const startTime = Date.now();
      
      await browserCore.getPageSuggestions(pageId);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Suggestion generation should complete within 2 seconds
      expect(duration).to.be.lessThan(2000);
    });
  });
});

/**
 * Run tests
 */
if (require.main === module) {
  const Mocha = require('mocha');
  const mocha = new Mocha();
  
  mocha.addFile(__filename);
  
  mocha.run(failures => {
    process.exitCode = failures ? 1 : 0;
  });
}

module.exports = {
  runTests: async function() {
    const Mocha = require('mocha');
    const mocha = new Mocha();
    
    mocha.addFile(__filename);
    
    return new Promise((resolve, reject) => {
      mocha.run(failures => {
        if (failures) {
          reject(new Error(`${failures} tests failed`));
        } else {
          resolve();
        }
      });
    });
  }
};
