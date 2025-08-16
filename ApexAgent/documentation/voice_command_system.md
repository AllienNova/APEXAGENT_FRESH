# VoiceCommandSystem Documentation

## Overview

The VoiceCommandSystem is a core component of Aideon AI Lite that enables comprehensive hands-free control through natural language voice commands. It integrates speech recognition, natural language understanding (NLU), command execution, and text-to-speech (TTS) capabilities to provide a seamless voice interface for all Aideon AI Lite features.

## Key Features

- **Natural Language Command Processing**: Understand and execute commands spoken in natural language
- **Activation Keyword Detection**: Respond only to commands prefixed with a configurable activation keyword
- **Tool Integration**: Execute any Aideon AI Lite tool through voice commands
- **Text-to-Speech Feedback**: Provide audible feedback and responses to user commands
- **Extensible Command Framework**: Easily add new voice commands and handlers
- **Multi-language Support**: Process commands in multiple languages (configurable)
- **Context Awareness**: Maintain context between commands for natural conversations
- **Noise Resilience**: Accurately recognize commands even in noisy environments
- **Offline Processing**: Process common commands locally without internet connectivity

## Architecture

The VoiceCommandSystem consists of four main components:

1. **Speech Recognition Service**: Converts spoken audio to text transcripts
2. **Natural Language Understanding (NLU) Service**: Extracts intents and entities from text
3. **Command Execution Engine**: Maps intents to actions and executes them
4. **Text-to-Speech (TTS) Service**: Converts text responses to spoken audio

## Usage Examples

### Initializing the VoiceCommandSystem

```javascript
// Get the VoiceCommandSystem from the Aideon core
const voiceCommandSystem = core.getVoiceCommandSystem();

// Initialize the system
await voiceCommandSystem.initialize();

// Start listening for voice commands
voiceCommandSystem.startListening();
```

### Processing Text Commands

```javascript
// Process a text command as if it were spoken
// Useful for testing or alternative input methods
await voiceCommandSystem.processTextCommand("Aideon summarize the latest meeting notes");
```

### Speaking Responses

```javascript
// Use the TTS service to speak a response
await voiceCommandSystem.speak("I've found 5 recent meeting notes. The latest one is from yesterday's marketing team meeting.");
```

### Registering Custom Command Handlers

```javascript
// Register a handler for a custom voice command intent
voiceCommandSystem.registerCommandHandler("create_presentation", async (entities, transcript) => {
  const topic = entities.topic || "general overview";
  const slides = entities.slides || 10;
  
  await voiceCommandSystem.speak(`Creating a presentation about ${topic} with ${slides} slides`);
  
  try {
    const result = await core.toolManager.executeTool(
      "ContentCommunicationTools", 
      "presentation_creator", 
      { topic, slides }
    );
    
    await voiceCommandSystem.speak(`Presentation created successfully. You can find it at ${result.filePath}`);
  } catch (error) {
    console.error("Error creating presentation:", error);
    await voiceCommandSystem.speak("Sorry, I encountered an error while creating the presentation.");
  }
});
```

### Listening for Voice Command Events

```javascript
// Listen for when a transcript is received
voiceCommandSystem.on("transcriptReceived", (transcript) => {
  console.log(`Received transcript: ${transcript}`);
});

// Listen for when a command is understood
voiceCommandSystem.on("commandUnderstood", ({ transcript, understanding }) => {
  console.log(`Understood command: ${understanding.intent}`);
  console.log(`Entities: ${JSON.stringify(understanding.entities)}`);
});

// Listen for when a command is executed
voiceCommandSystem.on("commandExecuted", ({ intent, entities, result }) => {
  console.log(`Executed command: ${intent}`);
  console.log(`Result: ${JSON.stringify(result)}`);
});

// Listen for command errors
voiceCommandSystem.on("commandError", ({ transcript, error }) => {
  console.error(`Error processing command "${transcript}":`, error);
});
```

## Supported Voice Commands

The VoiceCommandSystem comes with a set of built-in commands that cover common tasks:

### Document and Content Management

- "Open project [project name]"
- "Create new document titled [title]"
- "Save current document"
- "Close document"
- "Summarize this document"
- "Find documents about [topic]"
- "Read document [document name]"

### Email and Communication

- "Send email to [recipient] with subject [subject] body [body]"
- "Check my inbox"
- "Reply to last email"
- "Schedule meeting with [person] for [time]"
- "Join my next meeting"

### Information Retrieval

- "Search the web for [query]"
- "Find information about [topic]"
- "What is [concept]?"
- "How do I [task]?"
- "Summarize the latest news about [topic]"

### Task and Project Management

- "Add task [task description]"
- "Show my tasks for today"
- "Mark task [task number] as complete"
- "Create project [project name]"
- "Set reminder for [time] to [action]"

### System Control

- "Start listening"
- "Stop listening"
- "Increase volume"
- "Decrease volume"
- "Switch to [application]"
- "Take a screenshot"

### Tool Execution

- "Run [tool name] with [parameters]"
- "Execute [script name]"
- "Analyze data in [file name]"
- "Generate report about [topic]"

## Configuration Options

The VoiceCommandSystem can be configured through the Aideon AI Lite configuration system:

```javascript
{
  "voice": {
    "enabled": true,
    "activationKeyword": "aideon",
    "speechRecognition": {
      "engine": "webSpeech", // or "azure", "google", "local"
      "language": "en-US",
      "continuous": true,
      "interimResults": false,
      "maxAlternatives": 1
    },
    "nlu": {
      "engine": "local", // or "rasa", "dialogflow", "luis"
      "confidenceThreshold": 0.7,
      "contextRetention": 300 // seconds
    },
    "tts": {
      "engine": "webSpeech", // or "azure", "google", "local"
      "voice": "female",
      "rate": 1.0,
      "pitch": 1.0,
      "volume": 1.0
    },
    "feedback": {
      "acknowledgeCommands": true,
      "verboseMode": false,
      "errorDetails": true
    }
  }
}
```

## Events

The VoiceCommandSystem emits the following events:

- `listeningStarted`: Emitted when the system starts listening for commands
- `listeningStopped`: Emitted when the system stops listening for commands
- `transcriptReceived`: Emitted when a speech transcript is received
- `commandUnderstood`: Emitted when a command is understood by the NLU
- `commandExecuted`: Emitted when a command is successfully executed
- `commandError`: Emitted when an error occurs during command processing
- `spoke`: Emitted when the system speaks a response

## Security Considerations

The VoiceCommandSystem implements several security measures:

1. **Activation Keyword**: Requires a specific keyword to activate, preventing accidental execution
2. **Command Validation**: Validates commands before execution to prevent malicious actions
3. **Permission Controls**: Respects system permission settings for sensitive operations
4. **Privacy Options**: Configurable privacy settings for speech data handling
5. **Local Processing**: Option to process commands locally without sending data to the cloud

## Best Practices

1. **Clear Activation Keyword**: Choose a distinct activation keyword that won't be triggered accidentally
2. **Consistent Command Structure**: Design commands with consistent patterns for better recognition
3. **Provide Feedback**: Always give audible feedback when commands are recognized and executed
4. **Handle Ambiguity**: Implement clarification dialogs when commands are ambiguous
5. **Graceful Fallbacks**: Have fallback responses when commands cannot be understood or executed
6. **Context Awareness**: Maintain context between commands for more natural interactions

## Integration with Other Aideon Components

The VoiceCommandSystem integrates with other Aideon AI Lite components:

- **ToolManager**: Executes tools based on voice commands
- **ConfigManager**: For configuration settings
- **LogManager**: For logging and diagnostics
- **SecurityManager**: For permission validation
- **DeviceSyncManager**: For synchronizing voice command preferences across devices

## Limitations and Considerations

1. **Ambient Noise**: Performance may degrade in noisy environments
2. **Accent Variations**: Recognition accuracy may vary with different accents
3. **Complex Commands**: Very complex or highly technical commands may require clarification
4. **Privacy Concerns**: Voice data processing raises privacy considerations
5. **Battery Impact**: Continuous listening can impact battery life on mobile devices

## Future Enhancements

1. **Multi-turn Conversations**: More sophisticated dialog management for complex interactions
2. **Voice Identification**: Recognize different users by their voice
3. **Emotion Detection**: Detect user emotions from voice and adapt responses accordingly
4. **Proactive Suggestions**: Offer suggestions based on voice interaction patterns
5. **Custom Voice Profiles**: Allow users to customize the system's voice and speaking style
