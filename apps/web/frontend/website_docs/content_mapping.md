# Aideon AI Lite Website Content Mapping

## Overview
This document maps the new content to the existing website structure, identifying where content should be placed and where new pages need to be created.

## Navigation Structure
Based on the current website, the main navigation includes:
- Home
- Features
- Models
- Documentation
- Download
- Support
- Get Started (CTA)

## Footer Links
Additional pages accessible via footer:
- Blog
- Tutorials
- Community
- FAQ
- Changelog
- Privacy Policy
- Terms of Service
- Cookie Policy

## Content Mapping

### Home Page
**Source file:** `/home/ubuntu/home_page_content.md`
**Target:** Main landing page
**Status:** Update existing page
**Key sections to implement:**
- Updated hero section with tagline "Intelligence Everywhere, Limits Nowhere"
- Corrected comparison section with subscription model information
- Background processing notification component
- Updated pricing tiers section

### Features Page
**Source file:** `/home/ubuntu/features_page_content.md`
**Target:** Features page (accessible from main navigation)
**Status:** Update existing page
**Key sections to implement:**
- Complete feature list organized by category
- Feature comparison with competitors
- Use cases and examples

### How It Works Page
**Source file:** `/home/ubuntu/how_it_works_content.md`
**Target:** New page (not in current navigation)
**Status:** Create new page
**Proposed location:** Add to main navigation after Features
**Key sections to implement:**
- Hybrid AI architecture explanation
- Local vs cloud processing details
- Technical diagrams and workflow

### Models Page
**Source file:** No specific content file, use model inventory information
**Target:** Models page (accessible from main navigation)
**Status:** Update existing page
**Key sections to implement:**
- Complete model inventory
- Model capabilities and specifications
- Integration examples

### Getting Started Page
**Source file:** `/home/ubuntu/getting_started_content.md`
**Target:** Get Started page (accessible from CTA buttons)
**Status:** Update existing page
**Key sections to implement:**
- Installation instructions
- First-time setup guide
- Quick start tutorials

### Documentation Page
**Source file:** `/home/ubuntu/documentation_content.md`
**Target:** Documentation page (accessible from main navigation)
**Status:** Update existing page
**Key sections to implement:**
- User guides
- API documentation
- Integration tutorials
- Troubleshooting guides

### Community Page
**Source file:** `/home/ubuntu/community_content.md`
**Target:** Community page (accessible from footer)
**Status:** Create new page or update if exists
**Key sections to implement:**
- Forums and discussion groups
- Contribution guidelines
- Community events and webinars
- Showcase of community projects

### Support Page
**Source file:** `/home/ubuntu/support_content.md`
**Target:** Support page (accessible from main navigation)
**Status:** Update existing page
**Key sections to implement:**
- Support options and tiers
- FAQ section
- Contact information
- Troubleshooting resources

### About Us Page
**Source file:** `/home/ubuntu/about_us_content.md`
**Target:** New page (not in current navigation)
**Status:** Create new page
**Proposed location:** Add to footer links
**Key sections to implement:**
- Company mission and values
- Team information
- Vision and roadmap
- Contact information

### Blog Page
**Source file:** `/home/ubuntu/blog_content.md`
**Target:** Blog page (accessible from footer)
**Status:** Update existing page or create if doesn't exist
**Key sections to implement:**
- Blog post structure and categories
- Featured articles
- Newsletter signup

### Download/Pricing Page
**Source file:** `/home/ubuntu/download_pricing_content.md`
**Target:** Download page (accessible from main navigation)
**Status:** Update existing page
**Key sections to implement:**
- Updated pricing tiers with subscription model
- Credit-based usage system explanation
- Download options and requirements

## New Components to Implement

### Background Processing Notification
**Source file:** `/home/ubuntu/background_processing_notification.md` and `/home/ubuntu/aideon_ui_components/background_notification_demo.html`
**Target:** Global component for use across multiple pages
**Status:** Create new component
**Implementation notes:**
- Should be visible when Aideon is working in the background
- Must maintain consistent branding
- Should be minimizable to avoid disrupting user experience

## Implementation Priority
1. Home Page (highest visibility)
2. Download/Pricing Page (critical for business model accuracy)
3. Features Page (key for user understanding)
4. Models Page (important for technical users)
5. Documentation & Getting Started (important for user onboarding)
6. Support Page (important for user retention)
7. Remaining pages (Blog, Community, About Us, etc.)
