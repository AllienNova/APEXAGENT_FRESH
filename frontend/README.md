# Aideon AI Lite Website

This repository contains the frontend code for the Aideon AI Lite website, built with React, TypeScript, and Vite.

## Overview

Aideon AI Lite is the world's first truly hybrid autonomous AI system that combines local PC processing with cloud intelligence. The website showcases the product's features, pricing, and capabilities while maintaining a consistent brand identity.

## Key Features

- **Modern React Components**: Built with React 18, TypeScript, and Vite for optimal performance
- **Responsive Design**: Fully responsive layout that works on all device sizes
- **Tailwind CSS**: Utilizes Tailwind for styling with custom design system
- **Interactive Elements**: Dynamic components like the Background Processing Notification
- **Comprehensive Pages**: Home, Features, How It Works, Documentation, Download, Support, About Us, and Community

## Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── global/         # Global components used across pages
│   ├── home/           # Components specific to the home page
│   └── layout/         # Layout components (header, footer)
├── pages/              # Page components
│   ├── HomePage.tsx
│   ├── FeaturesPage.tsx
│   ├── HowItWorksPage.tsx
│   ├── AboutUsPage.tsx
│   ├── CommunityPage.tsx
│   └── ...
├── assets/             # Static assets
├── App.tsx             # Main application component
└── main.tsx            # Application entry point
```

## Documentation

Additional documentation can be found in the `website_docs` directory:

- `content_mapping.md`: Maps content to website sections
- `content_validation_report.md`: Validation of content and branding consistency

## Recent Updates

The website has been comprehensively updated with:

1. **New Content**: Updated tagline "Intelligence Everywhere, Limits Nowhere" and supporting statements
2. **Pricing Model**: Corrected to reflect the subscription-based model with credit system
3. **New Pages**: Added How It Works, About Us, and Community pages
4. **Background Notification**: New component that informs users when Aideon continues working in the background
5. **Improved Navigation**: Enhanced site structure with clear pathways to all content

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

## Deployment

The built website can be deployed to any static hosting service. The production build will be in the `dist` directory.

```bash
# Preview production build locally
pnpm preview
```

## Contributing

Please refer to the project's contribution guidelines before submitting pull requests.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
