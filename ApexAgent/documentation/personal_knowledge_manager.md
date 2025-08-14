# Personal Knowledge Manager Documentation

## Overview

The PersonalKnowledgeManager is a core component of Aideon AI Lite that provides integrated knowledge management capabilities. It helps users organize, retrieve, and leverage their personal and professional knowledge across all tools and workflows, creating a centralized knowledge repository with powerful semantic search and context-aware retrieval.

## Key Features

- **Semantic Knowledge Search**: Find information based on meaning, not just keywords
- **Multi-format Knowledge Storage**: Store and retrieve text, documents, code, images, and more
- **Automatic Knowledge Capture**: Seamlessly capture knowledge from user activities
- **Knowledge Processing**: Extract insights, entities, and relationships from raw content
- **Vector Embeddings**: Use advanced embedding models for semantic understanding
- **Knowledge Graph**: Visualize and navigate relationships between knowledge items
- **Import/Export Capabilities**: Connect with external knowledge sources and destinations
- **Knowledge Analytics**: Gain insights into your knowledge base usage and patterns
- **Context-Aware Retrieval**: Surface relevant knowledge based on current context
- **Privacy-Focused Design**: Keep sensitive knowledge secure with local processing

## Architecture

The PersonalKnowledgeManager consists of five main components:

1. **Knowledge Base**: Core storage for knowledge items
2. **Vector Store**: Semantic search capabilities using vector embeddings
3. **Knowledge Sources**: Connectors to import knowledge from external sources
4. **Knowledge Processors**: Process and enhance raw knowledge content
5. **Knowledge Connectors**: Export knowledge to external destinations

## Usage Examples

### Initializing the PersonalKnowledgeManager

```javascript
// Get the PersonalKnowledgeManager from the Aideon core
const knowledgeManager = core.getPersonalKnowledgeManager();

// Initialize the manager
await knowledgeManager.initialize();
```

### Adding Knowledge Items

```javascript
// Add a new knowledge item
const noteId = await knowledgeManager.addKnowledgeItem({
  title: "Meeting Notes: Product Roadmap",
  content: "We discussed the Q3 roadmap and decided to prioritize the following features...",
  type: "note",
  tags: ["meeting", "roadmap", "product"],
  metadata: {
    date: "2025-06-05",
    participants: ["Alice", "Bob", "Charlie"]
  }
});

console.log(`Added knowledge item with ID: ${noteId}`);
```

### Updating Knowledge Items

```javascript
// Update an existing knowledge item
await knowledgeManager.updateKnowledgeItem(noteId, {
  content: "Updated meeting notes with additional action items...",
  metadata: {
    lastReviewed: Date.now()
  }
});
```

### Searching Knowledge

```javascript
// Search the knowledge base
const results = await knowledgeManager.searchKnowledge({
  query: "product roadmap priorities",
  filters: {
    type: "note",
    tags: ["meeting"]
  },
  limit: 5
});

// Display search results
results.forEach(result => {
  console.log(`Result: ${result.item.title}`);
  console.log(`Relevance: ${result.similarity * 100}%`);
  console.log(`Content: ${result.item.content.substring(0, 100)}...`);
});
```

### Importing Knowledge

```javascript
// Import knowledge from a file system source
const importResults = await knowledgeManager.importKnowledge("filesystem", {
  path: "/path/to/documents",
  recursive: true,
  fileTypes: ["md", "txt", "pdf"]
});

console.log(`Imported ${importResults.successful} out of ${importResults.total} items`);
```

### Exporting Knowledge

```javascript
// Export knowledge to Markdown format
const exportResults = await knowledgeManager.exportKnowledge("markdown", {
  outputPath: "/path/to/export",
  filters: {
    tags: ["important"]
  },
  includeMetadata: true
});

console.log(`Exported ${exportResults.successful} out of ${exportResults.total} items`);
```

### Analyzing Knowledge

```javascript
// Analyze the knowledge base
const analysis = await knowledgeManager.analyzeKnowledge();

console.log(`Total knowledge items: ${analysis.totalItems}`);
console.log(`Items by type:`, analysis.byType);
console.log(`Most used tags:`, analysis.byTag);
console.log(`Recently updated items:`, analysis.recentlyUpdated);
```

## Knowledge Sources

The PersonalKnowledgeManager comes with several built-in knowledge sources:

### File System Source

Imports knowledge from local files and directories:

```javascript
await knowledgeManager.importKnowledge("filesystem", {
  path: "/path/to/documents",
  recursive: true,
  fileTypes: ["md", "txt", "pdf", "docx"]
});
```

### Web Page Source

Imports knowledge from web pages:

```javascript
await knowledgeManager.importKnowledge("webpage", {
  url: "https://example.com/article",
  includeImages: true,
  depth: 1 // Follow links one level deep
});
```

### Email Source

Imports knowledge from email messages:

```javascript
await knowledgeManager.importKnowledge("email", {
  folder: "Important",
  since: "2025-01-01",
  includeAttachments: true
});
```

### Note Taking App Source

Imports knowledge from note-taking applications:

```javascript
await knowledgeManager.importKnowledge("notes", {
  application: "notion", // or "evernote", "onenote", etc.
  notebooks: ["Work", "Research"],
  since: "2025-01-01"
});
```

## Knowledge Processors

The PersonalKnowledgeManager includes several knowledge processors for different content types:

### Text Processor

Processes plain text content:
- Extracts key phrases and entities
- Identifies topics and themes
- Generates summaries

### Document Processor

Processes structured documents:
- Extracts headings and sections
- Identifies tables and figures
- Preserves document structure

### Code Processor

Processes programming code:
- Identifies functions, classes, and methods
- Extracts comments and documentation
- Recognizes programming languages and frameworks

### Image Processor

Processes images:
- Extracts text using OCR
- Identifies objects and scenes
- Generates image descriptions

## Knowledge Connectors

The PersonalKnowledgeManager includes several knowledge connectors for exporting:

### Markdown Connector

Exports knowledge as Markdown files:

```javascript
await knowledgeManager.exportKnowledge("markdown", {
  outputPath: "/path/to/export",
  template: "default", // or "academic", "project", etc.
  includeMetadata: true
});
```

### JSON Connector

Exports knowledge as JSON files:

```javascript
await knowledgeManager.exportKnowledge("json", {
  outputPath: "/path/to/export",
  pretty: true,
  includeVectors: false
});
```

### Web Connector

Exports knowledge as a static website:

```javascript
await knowledgeManager.exportKnowledge("web", {
  outputPath: "/path/to/website",
  theme: "light",
  includeSearch: true,
  title: "My Knowledge Base"
});
```

## Configuration Options

The PersonalKnowledgeManager can be configured through the Aideon AI Lite configuration system:

```javascript
{
  "knowledge": {
    "enabled": true,
    "vectorStore": {
      "dimensions": 384,
      "similarityThreshold": 0.7,
      "maxResults": 50
    },
    "sources": {
      "filesystem": {
        "enabled": true,
        "supportedFileTypes": ["md", "txt", "pdf", "docx", "html"]
      },
      "webpage": {
        "enabled": true,
        "maxSizeKB": 5000
      }
    },
    "processors": {
      "text": {
        "enabled": true,
        "summarize": true,
        "extractEntities": true
      },
      "document": {
        "enabled": true,
        "preserveFormatting": true
      },
      "code": {
        "enabled": true,
        "extractDocumentation": true
      }
    },
    "connectors": {
      "markdown": {
        "enabled": true,
        "templates": ["default", "academic", "project"]
      },
      "json": {
        "enabled": true
      }
    },
    "autoCaptureEnabled": true,
    "autoCaptureThreshold": 0.7,
    "privacy": {
      "localProcessingOnly": true,
      "encryptKnowledgeBase": false
    }
  }
}
```

## Events

The PersonalKnowledgeManager emits the following events:

- `knowledgeItemAdded`: Emitted when a new knowledge item is added
- `knowledgeItemUpdated`: Emitted when a knowledge item is updated
- `knowledgeItemDeleted`: Emitted when a knowledge item is deleted
- `knowledgeItemAccessed`: Emitted when a knowledge item is accessed
- `knowledgeSearched`: Emitted when a search is performed
- `knowledgeImportStarted`: Emitted when a knowledge import starts
- `knowledgeImportCompleted`: Emitted when a knowledge import completes
- `knowledgeImportFailed`: Emitted when a knowledge import fails
- `knowledgeExportStarted`: Emitted when a knowledge export starts
- `knowledgeExportCompleted`: Emitted when a knowledge export completes
- `knowledgeExportFailed`: Emitted when a knowledge export fails
- `knowledgeAnalyzed`: Emitted when knowledge analysis is performed

## Security and Privacy Considerations

The PersonalKnowledgeManager implements several security and privacy measures:

1. **Local Processing**: Knowledge is processed locally by default
2. **Encrypted Storage**: Option to encrypt the knowledge base
3. **Access Controls**: Permissions for knowledge access and modification
4. **Data Minimization**: Only essential data is stored
5. **Privacy Settings**: Fine-grained control over what knowledge is captured

## Best Practices

1. **Consistent Tagging**: Develop a consistent tagging system for knowledge items
2. **Regular Imports**: Set up regular imports from frequently used sources
3. **Knowledge Review**: Periodically review and update important knowledge items
4. **Contextual Retrieval**: Use the context-aware features to surface relevant knowledge
5. **Balanced Automation**: Configure auto-capture settings to balance convenience with privacy

## Integration with Other Aideon Components

The PersonalKnowledgeManager integrates with other Aideon AI Lite components:

- **ContextAwareAutomator**: Provides context for knowledge retrieval
- **DeviceSyncManager**: Synchronizes knowledge across devices
- **VoiceCommandSystem**: Enables voice access to knowledge
- **ToolManager**: Integrates knowledge with various tools
- **ConfigManager**: For configuration settings
- **LogManager**: For logging and diagnostics

## Limitations and Considerations

1. **Storage Requirements**: Large knowledge bases require significant storage
2. **Processing Overhead**: Semantic search and processing can be resource-intensive
3. **Learning Curve**: Effective knowledge management requires consistent practices
4. **Format Limitations**: Some complex document formats may not be fully supported
5. **Privacy Tradeoffs**: More powerful knowledge features generally require more data capture

## Future Enhancements

1. **Collaborative Knowledge**: Shared knowledge bases for teams
2. **Advanced Knowledge Graphs**: More sophisticated relationship mapping
3. **Multi-modal Knowledge**: Better support for video and audio knowledge
4. **Active Learning**: Proactive knowledge suggestions based on work context
5. **Knowledge Workflows**: Automated workflows triggered by knowledge changes
