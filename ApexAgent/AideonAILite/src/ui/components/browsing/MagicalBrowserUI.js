/**
 * MagicalBrowserUI.js
 * 
 * UI implementation of Aideon AI Lite's magical web browsing experience.
 * This module provides the visual components and interactions for the enhanced
 * browsing capabilities, creating a mesmerizing and natural user experience.
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated } from 'react-spring';
import styled, { keyframes, css } from 'styled-components';
import { FiSearch, FiClock, FiBookmark, FiStar, FiZap, FiLayers, FiMagic } from 'react-icons/fi';
import { RiRobot2Line } from 'react-icons/ri';
import { IoSparkles } from 'react-icons/io5';

// Glassmorphism styles
const glassMorphism = css`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

// Subtle glow animation
const subtleGlow = keyframes`
  0% {
    box-shadow: 0 0 10px rgba(120, 120, 255, 0.3);
  }
  50% {
    box-shadow: 0 0 20px rgba(120, 120, 255, 0.5);
  }
  100% {
    box-shadow: 0 0 10px rgba(120, 120, 255, 0.3);
  }
`;

// Magical sparkle animation
const sparkle = keyframes`
  0% {
    background-position: 0% 50%;
    opacity: 0.5;
  }
  50% {
    background-position: 100% 50%;
    opacity: 1;
  }
  100% {
    background-position: 0% 50%;
    opacity: 0.5;
  }
`;

// Container for the entire browser UI
const BrowserContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #ffffff;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
  position: relative;
`;

// Top navigation bar with glassmorphism effect
const NavigationBar = styled.div`
  ${glassMorphism}
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  height: 3.5rem;
  z-index: 10;
`;

// URL input with magical effects
const UrlInput = styled.input`
  flex: 1;
  height: 2.5rem;
  border-radius: 1.25rem;
  padding: 0 1rem 0 2.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    border-color: rgba(255, 255, 255, 0.5);
    animation: ${subtleGlow} 2s infinite;
    background: rgba(255, 255, 255, 0.15);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

// Search icon with animation
const SearchIcon = styled(FiSearch)`
  position: absolute;
  left: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
`;

// Navigation buttons container
const NavButtons = styled.div`
  display: flex;
  margin-left: 1rem;
  gap: 0.5rem;
`;

// Circular button with hover effects
const CircleButton = styled.button`
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

// Horizontal tabs container
const TabsContainer = styled.div`
  display: flex;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.5rem 1rem 0;
  scrollbar-width: none;
  
  &::-webkit-scrollbar {
    display: none;
  }
`;

// Individual tab with active state
const Tab = styled(motion.div)`
  ${glassMorphism}
  min-width: 180px;
  max-width: 220px;
  height: 2.5rem;
  margin-right: 0.5rem;
  border-radius: 0.5rem 0.5rem 0 0;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  
  ${props => props.active && css`
    background: rgba(255, 255, 255, 0.25);
    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #3a86ff, #8338ec, #ff006e);
      background-size: 200% 200%;
      animation: ${sparkle} 3s linear infinite;
    }
  `}
`;

// Tab favicon
const TabFavicon = styled.img`
  width: 16px;
  height: 16px;
  margin-right: 0.5rem;
  border-radius: 2px;
`;

// Tab title with ellipsis for overflow
const TabTitle = styled.span`
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
`;

// Close tab button
const CloseTab = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
    color: rgba(255, 255, 255, 0.9);
  }
`;

// Main content area
const ContentArea = styled.div`
  flex: 1;
  position: relative;
  overflow: hidden;
`;

// Browser frame for webpage content
const BrowserFrame = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
`;

// Iframe for web content
const WebFrame = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
`;

// Magical insights panel with glassmorphism
const InsightsPanel = styled(motion.div)`
  ${glassMorphism}
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 300px;
  border-radius: 1rem;
  padding: 1rem;
  z-index: 5;
  max-height: calc(100% - 2rem);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  &::-webkit-scrollbar {
    width: 5px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
  }
`;

// Insights panel header
const InsightsPanelHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  
  svg {
    margin-right: 0.5rem;
    font-size: 1.2rem;
    color: #8338ec;
  }
  
  h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
`;

// Individual insight card
const InsightCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }
  
  h4 {
    margin: 0 0 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    
    svg {
      margin-right: 0.5rem;
      font-size: 1rem;
    }
  }
  
  p {
    margin: 0;
    font-size: 0.8rem;
    opacity: 0.8;
    line-height: 1.4;
  }
`;

// Dr. Tardis assistant panel
const DrTardisPanel = styled(motion.div)`
  ${glassMorphism}
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  border-radius: 1rem;
  padding: 1rem;
  z-index: 5;
  display: flex;
  align-items: center;
  max-width: 80%;
`;

// Dr. Tardis avatar
const DrTardisAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3a86ff, #8338ec);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(58, 134, 255, 0.8), rgba(131, 56, 236, 0.8));
    opacity: 0.6;
    animation: ${subtleGlow} 2s infinite;
  }
  
  svg {
    font-size: 1.5rem;
    color: #ffffff;
    z-index: 1;
  }
`;

// Dr. Tardis message bubble
const DrTardisMessage = styled.div`
  flex: 1;
  
  p {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.4;
  }
`;

// Visual history panel
const VisualHistoryPanel = styled(motion.div)`
  ${glassMorphism}
  position: absolute;
  top: 4rem;
  left: 1rem;
  right: 1rem;
  max-height: 80%;
  border-radius: 1rem;
  padding: 1rem;
  z-index: 10;
  overflow-y: auto;
  
  h3 {
    margin: 0 0 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    
    svg {
      margin-right: 0.5rem;
    }
  }
`;

// Grid of visual history items
const HistoryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
`;

// Individual history item
const HistoryItem = styled(motion.div)`
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.75rem;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: scale(1.05);
  }
`;

// History item thumbnail
const HistoryThumbnail = styled.div`
  width: 100%;
  height: 120px;
  background-size: cover;
  background-position: center;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  }
`;

// History item info
const HistoryInfo = styled.div`
  padding: 0.75rem;
  
  h4 {
    margin: 0 0 0.25rem;
    font-size: 0.9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  p {
    margin: 0;
    font-size: 0.75rem;
    opacity: 0.7;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
`;

// Magical loading indicator
const MagicalLoader = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3a86ff, #8338ec, #ff006e);
  background-size: 200% 200%;
  animation: ${sparkle} 2s linear infinite;
  z-index: 20;
`;

// Suggestion bubble that appears contextually
const SuggestionBubble = styled(motion.div)`
  ${glassMorphism}
  position: absolute;
  border-radius: 1.5rem;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  max-width: 300px;
  z-index: 15;
  cursor: pointer;
  
  svg {
    margin-right: 0.75rem;
    font-size: 1.2rem;
    color: #ff006e;
  }
  
  p {
    margin: 0;
    font-size: 0.85rem;
  }
`;

/**
 * MagicalBrowserUI Component
 * Main component for the magical browser UI
 */
const MagicalBrowserUI = ({ core }) => {
  // State
  const [tabs, setTabs] = useState([]);
  const [activeTabId, setActiveTabId] = useState(null);
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState([]);
  const [showInsights, setShowInsights] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [drTardisMessage, setDrTardisMessage] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [activeSuggestion, setActiveSuggestion] = useState(null);
  
  // Refs
  const urlInputRef = useRef(null);
  
  // Effects
  
  // Initialize browser
  useEffect(() => {
    const initBrowser = async () => {
      if (!core) return;
      
      try {
        // Create initial tab
        const pageId = await core.createPage();
        
        // Add tab
        const newTab = {
          id: pageId,
          title: 'New Tab',
          url: '',
          favicon: ''
        };
        
        setTabs([newTab]);
        setActiveTabId(pageId);
        
        // Set up event listeners
        core.on('page:loaded', handlePageLoaded);
        core.on('page:navigated', handlePageNavigated);
        core.on('page:insights', handlePageInsights);
        core.on('history:updated', handleHistoryUpdated);
        core.on('suggestions:updated', handleSuggestionsUpdated);
      } catch (error) {
        console.error('Failed to initialize browser:', error);
      }
    };
    
    initBrowser();
    
    // Cleanup
    return () => {
      if (core) {
        core.off('page:loaded', handlePageLoaded);
        core.off('page:navigated', handlePageNavigated);
        core.off('page:insights', handlePageInsights);
        core.off('history:updated', handleHistoryUpdated);
        core.off('suggestions:updated', handleSuggestionsUpdated);
      }
    };
  }, [core]);
  
  // Event handlers
  
  // Handle page loaded event
  const handlePageLoaded = (data) => {
    const { pageId, url, title } = data;
    
    // Update tab
    setTabs(prevTabs => prevTabs.map(tab => {
      if (tab.id === pageId) {
        return {
          ...tab,
          title: title || 'Untitled',
          url,
          favicon: `https://www.google.com/s2/favicons?domain=${new URL(url).hostname}`
        };
      }
      return tab;
    }));
    
    // Update URL input
    if (pageId === activeTabId) {
      setUrl(url);
      setIsLoading(false);
    }
    
    // Show Dr. Tardis message
    setDrTardisMessage(`I've analyzed this page about ${title}. Ask me anything about it!`);
    
    // Show Dr. Tardis message for 5 seconds
    setTimeout(() => {
      setDrTardisMessage('');
    }, 5000);
  };
  
  // Handle page navigated event
  const handlePageNavigated = (data) => {
    const { pageId, url } = data;
    
    // Update URL input
    if (pageId === activeTabId) {
      setUrl(url);
      setIsLoading(true);
    }
  };
  
  // Handle page insights event
  const handlePageInsights = (data) => {
    const { pageId, insights: pageInsights, suggestions: pageSuggestions } = data;
    
    if (pageId === activeTabId) {
      // Transform insights into UI format
      const insightCards = [
        {
          id: 'summary',
          title: 'Page Summary',
          content: pageInsights.summary,
          icon: <FiLayers />
        },
        {
          id: 'topics',
          title: 'Key Topics',
          content: pageInsights.topics.join(', '),
          icon: <FiStar />
        }
      ];
      
      setInsights(insightCards);
      setSuggestions(pageSuggestions);
      
      // Show a random suggestion after a delay
      setTimeout(() => {
        if (pageSuggestions.length > 0) {
          const randomIndex = Math.floor(Math.random() * pageSuggestions.length);
          setActiveSuggestion(pageSuggestions[randomIndex]);
          
          // Hide suggestion after 10 seconds
          setTimeout(() => {
            setActiveSuggestion(null);
          }, 10000);
        }
      }, 3000);
    }
  };
  
  // Handle history updated event
  const handleHistoryUpdated = (data) => {
    setHistory(data.history);
  };
  
  // Handle suggestions updated event
  const handleSuggestionsUpdated = (data) => {
    const { pageId, suggestions: pageSuggestions } = data;
    
    if (pageId === activeTabId) {
      setSuggestions(pageSuggestions);
    }
  };
  
  // Handle URL input change
  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };
  
  // Handle URL input key press
  const handleUrlKeyPress = async (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      
      try {
        // Ensure URL has protocol
        let navigateUrl = url;
        if (!navigateUrl.startsWith('http://') && !navigateUrl.startsWith('https://')) {
          navigateUrl = `https://${navigateUrl}`;
        }
        
        // Navigate to URL
        setIsLoading(true);
        await core.navigateTo(activeTabId, navigateUrl);
      } catch (error) {
        console.error('Failed to navigate:', error);
        setIsLoading(false);
      }
    }
  };
  
  // Handle tab click
  const handleTabClick = (tabId) => {
    setActiveTabId(tabId);
    
    // Update URL input
    const tab = tabs.find(tab => tab.id === tabId);
    if (tab) {
      setUrl(tab.url || '');
    }
  };
  
  // Handle new tab click
  const handleNewTab = async () => {
    try {
      // Create new page
      const pageId = await core.createPage();
      
      // Add tab
      const newTab = {
        id: pageId,
        title: 'New Tab',
        url: '',
        favicon: ''
      };
      
      setTabs(prevTabs => [...prevTabs, newTab]);
      setActiveTabId(pageId);
      setUrl('');
    } catch (error) {
      console.error('Failed to create new tab:', error);
    }
  };
  
  // Handle close tab
  const handleCloseTab = async (tabId, e) => {
    e.stopPropagation();
    
    try {
      // Close page
      await core.closePage(tabId);
      
      // Remove tab
      setTabs(prevTabs => prevTabs.filter(tab => tab.id !== tabId));
      
      // If active tab is closed, activate another tab
      if (activeTabId === tabId) {
        const remainingTabs = tabs.filter(tab => tab.id !== tabId);
        if (remainingTabs.length > 0) {
          setActiveTabId(remainingTabs[0].id);
          setUrl(remainingTabs[0].url || '');
        } else {
          // Create new tab if all tabs are closed
          handleNewTab();
        }
      }
    } catch (error) {
      console.error('Failed to close tab:', error);
    }
  };
  
  // Handle history item click
  const handleHistoryItemClick = async (item) => {
    try {
      // Navigate to URL
      setIsLoading(true);
      await core.navigateTo(activeTabId, item.url);
      setShowHistory(false);
    } catch (error) {
      console.error('Failed to navigate to history item:', error);
      setIsLoading(false);
    }
  };
  
  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    // Handle suggestion based on type
    switch (suggestion.action?.type) {
      case 'refine_search':
        setDrTardisMessage('I can help you refine your search. What are you looking for?');
        break;
      case 'fill_form':
        setDrTardisMessage('I can help you fill out this form. What information would you like to use?');
        break;
      case 'read_aloud':
        setDrTardisMessage('I\'ll read this article for you. Just a moment...');
        break;
      case 'find_related':
        setDrTardisMessage('I\'ll find related content based on this page. One moment please...');
        break;
      default:
        break;
    }
    
    // Hide suggestion
    setActiveSuggestion(null);
  };
  
  // Animations
  
  // Tab animations
  const tabVariants = {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.3 } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.2 } }
  };
  
  // Panel animations
  const panelVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.3 } }
  };
  
  // Dr. Tardis animations
  const drTardisVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
  };
  
  // Suggestion bubble animations
  const suggestionVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 500, damping: 30 } }
  };
  
  // Render
  return (
    <BrowserContainer>
      {/* Navigation bar */}
      <NavigationBar>
        <SearchIcon />
        <UrlInput
          ref={urlInputRef}
          value={url}
          onChange={handleUrlChange}
          onKeyPress={handleUrlKeyPress}
          placeholder="Enter URL or search..."
        />
        <NavButtons>
          <CircleButton onClick={() => setShowInsights(!showInsights)}>
            <FiZap />
          </CircleButton>
          <CircleButton onClick={() => setShowHistory(!showHistory)}>
            <FiClock />
          </CircleButton>
          <CircleButton>
            <FiBookmark />
          </CircleButton>
          <CircleButton onClick={handleNewTab}>
            <span>+</span>
          </CircleButton>
        </NavButtons>
      </NavigationBar>
      
      {/* Tabs */}
      <TabsContainer>
        <AnimatePresence>
          {tabs.map(tab => (
            <Tab
              key={tab.id}
              active={tab.id === activeTabId}
              onClick={() => handleTabClick(tab.id)}
              variants={tabVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              layout
            >
              {tab.favicon && <TabFavicon src={tab.favicon} alt="" />}
              <TabTitle>{tab.title}</TabTitle>
              <CloseTab onClick={(e) => handleCloseTab(tab.id, e)}>×</CloseTab>
            </Tab>
          ))}
        </AnimatePresence>
      </TabsContainer>
      
      {/* Content area */}
      <ContentArea>
        {/* Loading indicator */}
        <AnimatePresence>
          {isLoading && (
            <MagicalLoader
              initial={{ scaleX: 0, transformOrigin: 'left' }}
              animate={{ scaleX: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 2 }}
            />
          )}
        </AnimatePresence>
        
        {/* Browser frames */}
        {tabs.map(tab => (
          <BrowserFrame key={tab.id} style={{ display: tab.id === activeTabId ? 'block' : 'none' }}>
            <WebFrame
              title={tab.title}
              src={tab.url || 'about:blank'}
              sandbox="allow-same-origin allow-scripts allow-forms"
            />
          </BrowserFrame>
        ))}
        
        {/* Insights panel */}
        <AnimatePresence>
          {showInsights && (
            <InsightsPanel
              variants={panelVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              <InsightsPanelHeader>
                <FiMagic />
                <h3>Page Insights</h3>
              </InsightsPanelHeader>
              
              {insights.map(insight => (
                <InsightCard
                  key={insight.id}
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <h4>{insight.icon} {insight.title}</h4>
                  <p>{insight.content}</p>
                </InsightCard>
              ))}
            </InsightsPanel>
          )}
        </AnimatePresence>
        
        {/* Visual history panel */}
        <AnimatePresence>
          {showHistory && (
            <VisualHistoryPanel
              variants={panelVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              <h3><FiClock /> Browsing History</h3>
              
              <HistoryGrid>
                {history.slice().reverse().map(item => (
                  <HistoryItem
                    key={item.id}
                    onClick={() => handleHistoryItemClick(item)}
                    whileHover={{ y: -5 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <HistoryThumbnail style={{ backgroundImage: `url(data:image/jpeg;base64,${item.screenshot})` }} />
                    <HistoryInfo>
                      <h4>{item.title}</h4>
                      <p>{item.url}</p>
                    </HistoryInfo>
                  </HistoryItem>
                ))}
              </HistoryGrid>
            </VisualHistoryPanel>
          )}
        </AnimatePresence>
        
        {/* Dr. Tardis assistant */}
        <AnimatePresence>
          {drTardisMessage && (
            <DrTardisPanel
              variants={drTardisVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
            >
              <DrTardisAvatar>
                <RiRobot2Line />
              </DrTardisAvatar>
              <DrTardisMessage>
                <p>{drTardisMessage}</p>
              </DrTardisMessage>
            </DrTardisPanel>
          )}
        </AnimatePresence>
        
        {/* Contextual suggestion bubble */}
        <AnimatePresence>
          {activeSuggestion && (
            <SuggestionBubble
              variants={suggestionVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              style={{
                top: '50%',
                right: '20%',
                transform: 'translateY(-50%)'
              }}
              onClick={() => handleSuggestionClick(activeSuggestion)}
            >
              <IoSparkles />
              <p>{activeSuggestion.description}</p>
            </SuggestionBubble>
          )}
        </AnimatePresence>
      </ContentArea>
    </BrowserContainer>
  );
};

export default MagicalBrowserUI;
