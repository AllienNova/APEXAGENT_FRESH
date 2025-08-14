/**
 * UserExperienceValidation.js
 * 
 * Comprehensive validation suite for the magical web browsing experience
 * focusing on creativity, natural interaction, and visual impact.
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

/**
 * UserExperienceValidator class
 * Validates the magical browsing experience from a user perspective
 */
class UserExperienceValidator {
  constructor() {
    this.browser = null;
    this.page = null;
    this.results = {
      visual: [],
      interaction: [],
      creativity: [],
      performance: [],
      overall: []
    };
    this.screenshotsDir = path.join(__dirname, '../../..', 'validation_results', 'screenshots');
    this.recordingsDir = path.join(__dirname, '../../..', 'validation_results', 'recordings');
    this.reportsDir = path.join(__dirname, '../../..', 'validation_results', 'reports');
  }
  
  /**
   * Initialize the validator
   */
  async initialize() {
    // Create directories
    await fs.mkdir(this.screenshotsDir, { recursive: true });
    await fs.mkdir(this.recordingsDir, { recursive: true });
    await fs.mkdir(this.reportsDir, { recursive: true });
    
    // Launch browser
    this.browser = await puppeteer.launch({
      headless: false,
      args: [
        '--window-size=1920,1080',
        '--no-sandbox',
        '--disable-setuid-sandbox'
      ],
      defaultViewport: {
        width: 1920,
        height: 1080
      }
    });
    
    // Create page
    this.page = await this.browser.newPage();
    
    // Enable request interception
    await this.page.setRequestInterception(true);
    
    // Track performance metrics
    this.page.on('request', request => {
      request.continue();
    });
    
    this.page.on('response', response => {
      const request = response.request();
      const url = request.url();
      const status = response.status();
      const timing = response.timing();
      
      if (status >= 400) {
        this.logIssue('performance', `Failed request: ${url} (${status})`);
      }
      
      if (timing && timing.receiveHeadersEnd - timing.sendStart > 2000) {
        this.logIssue('performance', `Slow request: ${url} (${Math.round(timing.receiveHeadersEnd - timing.sendStart)}ms)`);
      }
    });
    
    console.log('User Experience Validator initialized');
  }
  
  /**
   * Log a validation result
   * @param {string} category - Result category
   * @param {string} message - Result message
   * @param {string} type - Result type (success, warning, error)
   * @param {Object} details - Additional details
   */
  logResult(category, message, type = 'success', details = {}) {
    if (!this.results[category]) {
      this.results[category] = [];
    }
    
    this.results[category].push({
      message,
      type,
      timestamp: new Date().toISOString(),
      details
    });
    
    console.log(`[${type.toUpperCase()}] [${category}] ${message}`);
  }
  
  /**
   * Log an issue
   * @param {string} category - Issue category
   * @param {string} message - Issue message
   * @param {Object} details - Additional details
   */
  logIssue(category, message, details = {}) {
    this.logResult(category, message, 'error', details);
  }
  
  /**
   * Take a screenshot
   * @param {string} name - Screenshot name
   * @returns {Promise<string>} Screenshot path
   */
  async takeScreenshot(name) {
    const filename = `${name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.png`;
    const filepath = path.join(this.screenshotsDir, filename);
    
    await this.page.screenshot({
      path: filepath,
      fullPage: false
    });
    
    return filepath;
  }
  
  /**
   * Start a screen recording
   * @param {string} name - Recording name
   * @returns {Promise<Object>} Recording session
   */
  async startRecording(name) {
    const sessionId = uuidv4();
    const filename = `${name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${Date.now()}.webm`;
    const filepath = path.join(this.recordingsDir, filename);
    
    // Start recording
    await this.page.evaluate(() => {
      window.__recordingChunks = [];
      
      navigator.mediaDevices.getDisplayMedia({ video: true })
        .then(stream => {
          window.__recordingStream = stream;
          window.__mediaRecorder = new MediaRecorder(stream);
          
          window.__mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) {
              window.__recordingChunks.push(e.data);
            }
          };
          
          window.__mediaRecorder.start(1000);
        })
        .catch(err => {
          console.error('Error starting recording:', err);
        });
    });
    
    return {
      sessionId,
      filepath
    };
  }
  
  /**
   * Stop a screen recording
   * @param {Object} session - Recording session
   * @returns {Promise<string>} Recording path
   */
  async stopRecording(session) {
    // Stop recording
    await this.page.evaluate(() => {
      if (window.__mediaRecorder && window.__mediaRecorder.state !== 'inactive') {
        window.__mediaRecorder.stop();
      }
      
      if (window.__recordingStream) {
        window.__recordingStream.getTracks().forEach(track => track.stop());
      }
    });
    
    // Wait for data to be processed
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Save recording
    await this.page.evaluate(async () => {
      if (!window.__recordingChunks || window.__recordingChunks.length === 0) {
        return null;
      }
      
      const blob = new Blob(window.__recordingChunks, { type: 'video/webm' });
      const arrayBuffer = await blob.arrayBuffer();
      
      // Convert to base64
      const base64 = btoa(
        new Uint8Array(arrayBuffer)
          .reduce((data, byte) => data + String.fromCharCode(byte), '')
      );
      
      return base64;
    });
    
    return session.filepath;
  }
  
  /**
   * Generate a validation report
   * @returns {Promise<string>} Report path
   */
  async generateReport() {
    const reportData = {
      timestamp: new Date().toISOString(),
      results: this.results,
      summary: {
        total: Object.values(this.results).flat().length,
        success: Object.values(this.results).flat().filter(r => r.type === 'success').length,
        warning: Object.values(this.results).flat().filter(r => r.type === 'warning').length,
        error: Object.values(this.results).flat().filter(r => r.type === 'error').length
      }
    };
    
    const filename = `validation_report_${Date.now()}.json`;
    const filepath = path.join(this.reportsDir, filename);
    
    await fs.writeFile(filepath, JSON.stringify(reportData, null, 2));
    
    // Generate HTML report
    const htmlFilepath = path.join(this.reportsDir, `validation_report_${Date.now()}.html`);
    
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Magical Web Browsing Experience - Validation Report</title>
        <style>
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
          }
          
          h1, h2, h3 {
            color: #2c3e50;
          }
          
          .header {
            background: linear-gradient(135deg, #3a86ff, #8338ec);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          }
          
          .summary {
            display: flex;
            justify-content: space-between;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
          }
          
          .summary-item {
            text-align: center;
            padding: 10px 20px;
            border-radius: 5px;
          }
          
          .success { background-color: #d4edda; color: #155724; }
          .warning { background-color: #fff3cd; color: #856404; }
          .error { background-color: #f8d7da; color: #721c24; }
          
          .category {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
          }
          
          .result-item {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
          }
          
          .timestamp {
            font-size: 0.8em;
            color: #6c757d;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Magical Web Browsing Experience</h1>
          <h2>Validation Report</h2>
          <p>Generated on ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="summary">
          <div class="summary-item">
            <h3>Total Results</h3>
            <p>${reportData.summary.total}</p>
          </div>
          <div class="summary-item success">
            <h3>Success</h3>
            <p>${reportData.summary.success}</p>
          </div>
          <div class="summary-item warning">
            <h3>Warnings</h3>
            <p>${reportData.summary.warning}</p>
          </div>
          <div class="summary-item error">
            <h3>Errors</h3>
            <p>${reportData.summary.error}</p>
          </div>
        </div>
        
        ${Object.entries(reportData.results).map(([category, results]) => `
          <div class="category">
            <h2>${category.charAt(0).toUpperCase() + category.slice(1)}</h2>
            ${results.length === 0 ? '<p>No results in this category.</p>' : ''}
            ${results.map(result => `
              <div class="result-item ${result.type}">
                <p><strong>${result.message}</strong></p>
                <p class="timestamp">${new Date(result.timestamp).toLocaleString()}</p>
              </div>
            `).join('')}
          </div>
        `).join('')}
      </body>
      </html>
    `;
    
    await fs.writeFile(htmlFilepath, htmlContent);
    
    return {
      json: filepath,
      html: htmlFilepath
    };
  }
  
  /**
   * Clean up resources
   */
  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }
  
  /**
   * Validate visual aspects
   */
  async validateVisual() {
    console.log('Validating visual aspects...');
    
    try {
      // Navigate to the application
      await this.page.goto('http://localhost:3000', { waitUntil: 'networkidle2' });
      
      // Take screenshot of initial state
      const initialScreenshot = await this.takeScreenshot('initial_state');
      this.logResult('visual', 'Captured initial state', 'success', { screenshot: initialScreenshot });
      
      // Check for glassmorphism effects
      const hasGlassmorphism = await this.page.evaluate(() => {
        const elements = document.querySelectorAll('*');
        for (const element of elements) {
          const style = window.getComputedStyle(element);
          if (
            style.backdropFilter?.includes('blur') ||
            style.webkitBackdropFilter?.includes('blur')
          ) {
            return true;
          }
        }
        return false;
      });
      
      if (hasGlassmorphism) {
        this.logResult('visual', 'Glassmorphism effects detected', 'success');
      } else {
        this.logIssue('visual', 'No glassmorphism effects detected');
      }
      
      // Check for animations
      const hasAnimations = await this.page.evaluate(() => {
        const elements = document.querySelectorAll('*');
        for (const element of elements) {
          const style = window.getComputedStyle(element);
          if (
            style.animation && style.animation !== 'none' ||
            style.transition && style.transition !== 'none'
          ) {
            return true;
          }
        }
        return false;
      });
      
      if (hasAnimations) {
        this.logResult('visual', 'Animations detected', 'success');
      } else {
        this.logIssue('visual', 'No animations detected');
      }
      
      // Check color scheme
      const colorScheme = await this.page.evaluate(() => {
        const colors = [];
        const elements = document.querySelectorAll('*');
        
        for (const element of elements) {
          const style = window.getComputedStyle(element);
          const backgroundColor = style.backgroundColor;
          const color = style.color;
          
          if (backgroundColor && backgroundColor !== 'rgba(0, 0, 0, 0)') {
            colors.push(backgroundColor);
          }
          
          if (color) {
            colors.push(color);
          }
        }
        
        return [...new Set(colors)];
      });
      
      if (colorScheme.length >= 5) {
        this.logResult('visual', `Rich color scheme detected (${colorScheme.length} colors)`, 'success');
      } else {
        this.logIssue('visual', `Limited color scheme (${colorScheme.length} colors)`);
      }
      
      // Check for visual hierarchy
      const headingLevels = await this.page.evaluate(() => {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        return [...headings].map(h => h.tagName).reduce((acc, tag) => {
          acc[tag] = (acc[tag] || 0) + 1;
          return acc;
        }, {});
      });
      
      if (Object.keys(headingLevels).length >= 2) {
        this.logResult('visual', 'Good visual hierarchy with multiple heading levels', 'success', { headingLevels });
      } else {
        this.logIssue('visual', 'Limited visual hierarchy', { headingLevels });
      }
      
      // Check for responsive design
      const isResponsive = await this.page.evaluate(() => {
        const mediaQueries = [];
        for (let i = 0; i < document.styleSheets.length; i++) {
          try {
            const rules = document.styleSheets[i].cssRules || document.styleSheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
              if (rules[j].type === CSSRule.MEDIA_RULE) {
                mediaQueries.push(rules[j].conditionText);
              }
            }
          } catch (e) {
            // Skip cross-origin stylesheets
          }
        }
        return mediaQueries.length > 0;
      });
      
      if (isResponsive) {
        this.logResult('visual', 'Responsive design detected', 'success');
      } else {
        this.logIssue('visual', 'No responsive design detected');
      }
      
      // Check for visual feedback on interactions
      await this.page.hover('button, a, [role="button"]');
      
      const hasHoverEffects = await this.page.evaluate(() => {
        const hoveredElement = document.querySelector(':hover');
        if (!hoveredElement) return false;
        
        const beforeStyle = window.getComputedStyle(hoveredElement);
        
        // Trigger mouseout and mouseover to reset and reapply hover state
        const mouseoutEvent = new MouseEvent('mouseout', { bubbles: true });
        const mouseoverEvent = new MouseEvent('mouseover', { bubbles: true });
        
        hoveredElement.dispatchEvent(mouseoutEvent);
        hoveredElement.dispatchEvent(mouseoverEvent);
        
        const afterStyle = window.getComputedStyle(hoveredElement);
        
        // Check if any styles changed
        for (const prop of afterStyle) {
          if (beforeStyle[prop] !== afterStyle[prop]) {
            return true;
          }
        }
        
        return false;
      });
      
      if (hasHoverEffects) {
        this.logResult('visual', 'Visual feedback on hover detected', 'success');
      } else {
        this.logIssue('visual', 'No visual feedback on hover detected');
      }
      
      console.log('Visual validation completed');
    } catch (error) {
      console.error('Error during visual validation:', error);
      this.logIssue('visual', `Validation error: ${error.message}`);
    }
  }
  
  /**
   * Validate interaction aspects
   */
  async validateInteraction() {
    console.log('Validating interaction aspects...');
    
    try {
      // Navigate to the application
      await this.page.goto('http://localhost:3000', { waitUntil: 'networkidle2' });
      
      // Check for clickable elements
      const clickableElements = await this.page.evaluate(() => {
        const elements = document.querySelectorAll('button, a, [role="button"], input[type="submit"]');
        return elements.length;
      });
      
      if (clickableElements > 0) {
        this.logResult('interaction', `Found ${clickableElements} clickable elements`, 'success');
      } else {
        this.logIssue('interaction', 'No clickable elements found');
      }
      
      // Check for form elements
      const formElements = await this.page.evaluate(() => {
        const elements = document.querySelectorAll('input, textarea, select');
        return elements.length;
      });
      
      if (formElements > 0) {
        this.logResult('interaction', `Found ${formElements} form elements`, 'success');
      } else {
        this.logIssue('interaction', 'No form elements found');
      }
      
      // Test URL input
      const urlInput = await this.page.$('input[placeholder*="URL"], input[placeholder*="url"], input[type="url"]');
      
      if (urlInput) {
        await urlInput.type('https://example.com');
        await this.page.keyboard.press('Enter');
        
        // Wait for navigation
        try {
          await this.page.waitForNavigation({ timeout: 5000 });
          this.logResult('interaction', 'URL input and navigation works', 'success');
        } catch (error) {
          this.logIssue('interaction', 'URL input navigation failed or timed out');
        }
      } else {
        this.logIssue('interaction', 'No URL input field found');
      }
      
      // Test tab switching
      const tabs = await this.page.$$('.tab, [role="tab"]');
      
      if (tabs.length > 0) {
        await tabs[0].click();
        this.logResult('interaction', 'Tab switching works', 'success');
      } else {
        this.logIssue('interaction', 'No tabs found');
      }
      
      // Test keyboard navigation
      await this.page.keyboard.press('Tab');
      
      const hasFocus = await this.page.evaluate(() => {
        return document.activeElement !== document.body;
      });
      
      if (hasFocus) {
        this.logResult('interaction', 'Keyboard navigation works', 'success');
      } else {
        this.logIssue('interaction', 'Keyboard navigation not working');
      }
      
      // Test scrolling
      await this.page.evaluate(() => {
        window.scrollBy(0, 100);
      });
      
      const scrollPosition = await this.page.evaluate(() => {
        return window.scrollY;
      });
      
      if (scrollPosition > 0) {
        this.logResult('interaction', 'Scrolling works', 'success');
      } else {
        this.logIssue('interaction', 'Scrolling not working or not needed');
      }
      
      console.log('Interaction validation completed');
    } catch (error) {
      console.error('Error during interaction validation:', error);
      this.logIssue('interaction', `Validation error: ${error.message}`);
    }
  }
  
  /**
   * Validate creativity aspects
   */
  async validateCreativity() {
    console.log('Validating creativity aspects...');
    
    try {
      // Navigate to the application
      await this.page.goto('http://localhost:3000', { waitUntil: 'networkidle2' });
      
      // Check for unique visual elements
      const uniqueVisualElements = await this.page.evaluate(() => {
        // Check for non-standard shapes
        const hasCustomShapes = Array.from(document.querySelectorAll('*')).some(el => {
          const style = window.getComputedStyle(el);
          return style.clipPath && style.clipPath !== 'none';
        });
        
        // Check for gradients
        const hasGradients = Array.from(document.querySelectorAll('*')).some(el => {
          const style = window.getComputedStyle(el);
          return style.background && style.background.includes('gradient');
        });
        
        // Check for custom animations
        const hasCustomAnimations = Array.from(document.querySelectorAll('*')).some(el => {
          const style = window.getComputedStyle(el);
          return style.animation && !style.animation.includes('none');
        });
        
        return {
          hasCustomShapes,
          hasGradients,
          hasCustomAnimations
        };
      });
      
      if (uniqueVisualElements.hasCustomShapes) {
        this.logResult('creativity', 'Custom shapes detected', 'success');
      } else {
        this.logIssue('creativity', 'No custom shapes detected');
      }
      
      if (uniqueVisualElements.hasGradients) {
        this.logResult('creativity', 'Gradients detected', 'success');
      } else {
        this.logIssue('creativity', 'No gradients detected');
      }
      
      if (uniqueVisualElements.hasCustomAnimations) {
        this.logResult('creativity', 'Custom animations detected', 'success');
      } else {
        this.logIssue('creativity', 'No custom animations detected');
      }
      
      // Check for micro-interactions
      const hasMicroInteractions = await this.page.evaluate(async () => {
        // Find a button to interact with
        const button = document.querySelector('button');
        if (!button) return false;
        
        // Get initial state
        const initialStyle = window.getComputedStyle(button);
        
        // Click the button
        button.click();
        
        // Wait a bit for animations
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Get new state
        const newStyle = window.getComputedStyle(button);
        
        // Check if any styles changed
        for (const prop of newStyle) {
          if (initialStyle[prop] !== newStyle[prop]) {
            return true;
          }
        }
        
        return false;
      });
      
      if (hasMicroInteractions) {
        this.logResult('creativity', 'Micro-interactions detected', 'success');
      } else {
        this.logIssue('creativity', 'No micro-interactions detected');
      }
      
      // Check for creative layout
      const hasCreativeLayout = await this.page.evaluate(() => {
        // Check for non-standard grid layouts
        const hasGrid = Array.from(document.querySelectorAll('*')).some(el => {
          const style = window.getComputedStyle(el);
          return style.display === 'grid';
        });
        
        // Check for flexbox usage
        const hasFlex = Array.from(document.querySelectorAll('*')).some(el => {
          const style = window.getComputedStyle(el);
          return style.display === 'flex';
        });
        
        // Check for asymmetrical layouts
        const hasAsymmetry = document.querySelectorAll('.asymmetric, [class*="asymmetric"]').length > 0;
        
        return {
          hasGrid,
          hasFlex,
          hasAsymmetry
        };
      });
      
      if (hasCreativeLayout.hasGrid || hasCreativeLayout.hasFlex) {
        this.logResult('creativity', 'Modern layout techniques detected', 'success', {
          grid: hasCreativeLayout.hasGrid,
          flex: hasCreativeLayout.hasFlex
        });
      } else {
        this.logIssue('creativity', 'No modern layout techniques detected');
      }
      
      if (hasCreativeLayout.hasAsymmetry) {
        this.logResult('creativity', 'Asymmetrical layout detected', 'success');
      }
      
      // Check for creative typography
      const hasCreativeTypography = await this.page.evaluate(() => {
        const fontFamilies = new Set();
        const fontSizes = new Set();
        
        Array.from(document.querySelectorAll('*')).forEach(el => {
          const style = window.getComputedStyle(el);
          if (style.fontFamily) fontFamilies.add(style.fontFamily);
          if (style.fontSize) fontSizes.add(style.fontSize);
        });
        
        return {
          fontFamilyCount: fontFamilies.size,
          fontSizeCount: fontSizes.size
        };
      });
      
      if (hasCreativeTypography.fontFamilyCount > 1) {
        this.logResult('creativity', `Multiple font families detected (${hasCreativeTypography.fontFamilyCount})`, 'success');
      } else {
        this.logIssue('creativity', 'Limited font variety');
      }
      
      if (hasCreativeTypography.fontSizeCount > 3) {
        this.logResult('creativity', `Good typographic scale (${hasCreativeTypography.fontSizeCount} sizes)`, 'success');
      } else {
        this.logIssue('creativity', 'Limited typographic scale');
      }
      
      console.log('Creativity validation completed');
    } catch (error) {
      console.error('Error during creativity validation:', error);
      this.logIssue('creativity', `Validation error: ${error.message}`);
    }
  }
  
  /**
   * Validate performance aspects
   */
  async validatePerformance() {
    console.log('Validating performance aspects...');
    
    try {
      // Navigate to the application
      await this.page.goto('http://localhost:3000', { waitUntil: 'networkidle2' });
      
      // Measure load time
      const loadTime = await this.page.evaluate(() => {
        return performance.timing.loadEventEnd - performance.timing.navigationStart;
      });
      
      if (loadTime < 3000) {
        this.logResult('performance', `Fast load time: ${loadTime}ms`, 'success');
      } else if (loadTime < 5000) {
        this.logResult('performance', `Acceptable load time: ${loadTime}ms`, 'warning');
      } else {
        this.logIssue('performance', `Slow load time: ${loadTime}ms`);
      }
      
      // Measure FPS during interaction
      const fps = await this.page.evaluate(async () => {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const countFrame = () => {
          frameCount++;
          requestAnimationFrame(countFrame);
        };
        
        requestAnimationFrame(countFrame);
        
        // Simulate user interaction
        const button = document.querySelector('button');
        if (button) button.click();
        
        // Scroll the page
        window.scrollBy(0, 100);
        
        // Wait for 1 second
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const currentTime = performance.now();
        const elapsedTime = currentTime - lastTime;
        const fps = Math.round((frameCount * 1000) / elapsedTime);
        
        return fps;
      });
      
      if (fps >= 50) {
        this.logResult('performance', `Excellent frame rate: ${fps} FPS`, 'success');
      } else if (fps >= 30) {
        this.logResult('performance', `Good frame rate: ${fps} FPS`, 'warning');
      } else {
        this.logIssue('performance', `Poor frame rate: ${fps} FPS`);
      }
      
      // Check for layout shifts
      const layoutShifts = await this.page.evaluate(async () => {
        if (!window.PerformanceObserver || !PerformanceObserver.supportedEntryTypes.includes('layout-shift')) {
          return null;
        }
        
        let shifts = [];
        
        const observer = new PerformanceObserver(list => {
          shifts = shifts.concat(list.getEntries().map(entry => ({
            value: entry.value,
            hadRecentInput: entry.hadRecentInput
          })));
        });
        
        observer.observe({ type: 'layout-shift', buffered: true });
        
        // Simulate user interaction
        window.scrollBy(0, 200);
        
        // Wait for 1 second
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        observer.disconnect();
        
        return shifts;
      });
      
      if (layoutShifts) {
        const totalCLS = layoutShifts
          .filter(shift => !shift.hadRecentInput)
          .reduce((sum, shift) => sum + shift.value, 0);
        
        if (totalCLS < 0.1) {
          this.logResult('performance', `Good Cumulative Layout Shift: ${totalCLS.toFixed(3)}`, 'success');
        } else if (totalCLS < 0.25) {
          this.logResult('performance', `Acceptable Cumulative Layout Shift: ${totalCLS.toFixed(3)}`, 'warning');
        } else {
          this.logIssue('performance', `Poor Cumulative Layout Shift: ${totalCLS.toFixed(3)}`);
        }
      }
      
      // Check memory usage
      const memoryInfo = await this.page.evaluate(() => {
        if (!performance.memory) return null;
        
        return {
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        };
      });
      
      if (memoryInfo) {
        const usedMemoryMB = Math.round(memoryInfo.usedJSHeapSize / (1024 * 1024));
        const memoryUsageRatio = memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit;
        
        if (memoryUsageRatio < 0.5) {
          this.logResult('performance', `Good memory usage: ${usedMemoryMB} MB (${(memoryUsageRatio * 100).toFixed(1)}%)`, 'success');
        } else if (memoryUsageRatio < 0.8) {
          this.logResult('performance', `High memory usage: ${usedMemoryMB} MB (${(memoryUsageRatio * 100).toFixed(1)}%)`, 'warning');
        } else {
          this.logIssue('performance', `Excessive memory usage: ${usedMemoryMB} MB (${(memoryUsageRatio * 100).toFixed(1)}%)`);
        }
      }
      
      console.log('Performance validation completed');
    } catch (error) {
      console.error('Error during performance validation:', error);
      this.logIssue('performance', `Validation error: ${error.message}`);
    }
  }
  
  /**
   * Run all validations
   */
  async validateAll() {
    try {
      await this.initialize();
      
      await this.validateVisual();
      await this.validateInteraction();
      await this.validateCreativity();
      await this.validatePerformance();
      
      const reportPaths = await this.generateReport();
      console.log('Validation report generated:', reportPaths);
      
      await this.cleanup();
      
      return reportPaths;
    } catch (error) {
      console.error('Error during validation:', error);
      await this.cleanup();
      throw error;
    }
  }
}

/**
 * Run validation
 */
if (require.main === module) {
  const validator = new UserExperienceValidator();
  
  validator.validateAll()
    .then(reportPaths => {
      console.log('Validation completed successfully');
      console.log('Report paths:', reportPaths);
      process.exit(0);
    })
    .catch(error => {
      console.error('Validation failed:', error);
      process.exit(1);
    });
}

module.exports = UserExperienceValidator;
