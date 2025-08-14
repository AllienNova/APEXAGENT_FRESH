# LLM Provider Expansion Plan for ApexAgent

## Overview

This document outlines the plan for expanding ApexAgent's LLM provider support to include AWS Bedrock and Azure OpenAI Service. This expansion will significantly increase the flexibility of ApexAgent by allowing users to choose from multiple LLM providers based on their specific needs, compliance requirements, or existing cloud infrastructure.

## 1. AWS Bedrock Provider Implementation

### 1.1 Research and Requirements Analysis

#### AWS Bedrock Overview
AWS Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon through a unified API. It provides access to models like Claude, Llama 2, Cohere Command, and Amazon Titan.

#### Key Requirements
1. **Authentication**: AWS credentials (access key, secret key) and region configuration
2. **Model Support**: Access to various models (Claude, Llama 2, etc.) with appropriate parameters
3. **API Integration**: Proper handling of AWS SDK (boto3) for Bedrock API calls
4. **Error Handling**: Robust handling of AWS-specific errors and rate limits
5. **Streaming Support**: Implementation of streaming responses where supported
6. **Security**: Secure storage of AWS credentials using the enhanced ApiKeyManager

### 1.2 Design Specification

#### Class Structure
```python
class BedrockProvider(BaseLlmProvider):
    """Provider for AWS Bedrock LLM services."""
    
    def __init__(self, api_key_manager=None, aws_region=None):
        """Initialize the Bedrock provider."""
        super().__init__(api_key_manager)
        self.aws_region = aws_region or os.environ.get("AWS_REGION", "us-east-1")
        self.session = None
        self.bedrock_runtime = None
        
    def initialize(self):
        """Initialize the AWS Bedrock client."""
        # Get AWS credentials from ApiKeyManager
        # Initialize boto3 session and bedrock-runtime client
        
    def get_available_models(self):
        """Return list of available models on AWS Bedrock."""
        # Query available foundation models
        
    def generate_text(self, prompt, model=None, max_tokens=None, temperature=None, **kwargs):
        """Generate text using AWS Bedrock."""
        # Format request based on selected model
        # Send request to appropriate model endpoint
        # Parse and return response
        
    def generate_text_stream(self, prompt, model=None, max_tokens=None, temperature=None, **kwargs):
        """Generate streaming text using AWS Bedrock."""
        # Similar to generate_text but with streaming response
        
    def _format_request(self, model, prompt, max_tokens, temperature, **kwargs):
        """Format request based on model provider."""
        # Different models (Claude, Llama, etc.) have different request formats
        
    def _parse_response(self, model, response):
        """Parse response based on model provider."""
        # Different models have different response formats
```

#### Configuration Parameters
- `aws_access_key_id`: AWS access key ID
- `aws_secret_access_key`: AWS secret access key
- `aws_region`: AWS region (default: us-east-1)
- `default_model`: Default model to use (e.g., "anthropic.claude-v2")

#### Model Mapping
Map common model names to AWS Bedrock model IDs:
```python
MODEL_MAPPING = {
    "claude": "anthropic.claude-v2",
    "claude-instant": "anthropic.claude-instant-v1",
    "llama2": "meta.llama2-13b-chat-v1",
    "titan": "amazon.titan-text-express-v1",
    # Add more as they become available
}
```

### 1.3 Implementation Plan

1. **Create Basic Structure**:
   - Create `bedrock_provider.py` with class skeleton
   - Implement initialization and credential handling

2. **Implement Core Functionality**:
   - Implement `generate_text` for basic text generation
   - Add model-specific request formatting
   - Add response parsing for different models

3. **Add Streaming Support**:
   - Implement `generate_text_stream` for streaming responses
   - Ensure compatibility with ApexAgent's streaming framework

4. **Error Handling and Retries**:
   - Implement robust error handling for AWS-specific errors
   - Add retry logic for transient failures
   - Add rate limit handling

5. **Testing and Validation**:
   - Create unit tests with mocked AWS responses
   - Develop integration tests for actual API calls
   - Validate with different models and parameters

## 2. Azure OpenAI Service Provider Implementation

### 2.1 Research and Requirements Analysis

#### Azure OpenAI Service Overview
Azure OpenAI Service provides REST API access to OpenAI's models, including GPT-4, GPT-3.5-Turbo, and Embeddings, with the security and enterprise promise of Azure. It differs from OpenAI's direct API in its deployment-based model and Azure-specific authentication.

#### Key Requirements
1. **Authentication**: Azure API key and endpoint URL
2. **Deployment Management**: Support for Azure's deployment-based model access
3. **API Integration**: Proper handling of Azure OpenAI SDK or REST API
4. **Error Handling**: Robust handling of Azure-specific errors and rate limits
5. **Streaming Support**: Implementation of streaming responses
6. **Security**: Secure storage of Azure credentials using the enhanced ApiKeyManager

### 2.2 Design Specification

#### Class Structure
```python
class AzureOpenAIProvider(BaseLlmProvider):
    """Provider for Azure OpenAI Service."""
    
    def __init__(self, api_key_manager=None, api_base=None, api_version=None):
        """Initialize the Azure OpenAI provider."""
        super().__init__(api_key_manager)
        self.api_base = api_base
        self.api_version = api_version or "2023-05-15"
        self.client = None
        
    def initialize(self):
        """Initialize the Azure OpenAI client."""
        # Get Azure API key from ApiKeyManager
        # Initialize OpenAI client with Azure configuration
        
    def get_available_models(self):
        """Return list of available deployments on Azure OpenAI."""
        # Query available deployments
        
    def generate_text(self, prompt, deployment_id=None, max_tokens=None, temperature=None, **kwargs):
        """Generate text using Azure OpenAI."""
        # Format request for Azure OpenAI
        # Send request to specified deployment
        # Parse and return response
        
    def generate_text_stream(self, prompt, deployment_id=None, max_tokens=None, temperature=None, **kwargs):
        """Generate streaming text using Azure OpenAI."""
        # Similar to generate_text but with streaming response
        
    def _get_deployment_model(self, deployment_id):
        """Get the model type for a deployment ID."""
        # Map deployment ID to model type if needed
```

#### Configuration Parameters
- `azure_api_key`: Azure OpenAI API key
- `azure_api_base`: Azure OpenAI endpoint URL
- `azure_api_version`: API version (default: "2023-05-15")
- `default_deployment`: Default deployment ID to use

### 2.3 Implementation Plan

1. **Create Basic Structure**:
   - Create `azure_openai_provider.py` with class skeleton
   - Implement initialization and credential handling

2. **Implement Core Functionality**:
   - Implement `generate_text` for basic text generation
   - Add deployment-based request handling
   - Add response parsing

3. **Add Streaming Support**:
   - Implement `generate_text_stream` for streaming responses
   - Ensure compatibility with ApexAgent's streaming framework

4. **Error Handling and Retries**:
   - Implement robust error handling for Azure-specific errors
   - Add retry logic for transient failures
   - Add rate limit handling

5. **Testing and Validation**:
   - Create unit tests with mocked Azure responses
   - Develop integration tests for actual API calls
   - Validate with different deployments and parameters

## 3. Integration with ApiKeyManager

### 3.1 Credential Management

Both providers will use the enhanced ApiKeyManager for secure credential storage:

#### AWS Bedrock
```python
# Storing credentials
api_key_manager.set_api_key("aws_bedrock", {
    "aws_access_key_id": "YOUR_ACCESS_KEY",
    "aws_secret_access_key": "YOUR_SECRET_KEY",
    "aws_region": "us-east-1"
})

# Retrieving credentials
aws_creds = api_key_manager.get_api_key("aws_bedrock")
```

#### Azure OpenAI
```python
# Storing credentials
api_key_manager.set_api_key("azure_openai", {
    "api_key": "YOUR_API_KEY",
    "api_base": "https://your-resource-name.openai.azure.com/",
    "api_version": "2023-05-15"
})

# Retrieving credentials
azure_creds = api_key_manager.get_api_key("azure_openai")
```

### 3.2 Access Control

Leverage the new access control features in ApiKeyManager:
```python
# Set permissions for plugins
api_key_manager.set_plugin_permissions("my_plugin", ["aws_bedrock", "azure_openai"])

# Secure retrieval with access control
aws_creds = api_key_manager.get_api_key_secure("my_plugin", "aws_bedrock")
```

## 4. Documentation and Examples

### 4.1 Provider Documentation

Create comprehensive documentation for each provider:
- Installation requirements
- Configuration parameters
- Available models/deployments
- Usage examples
- Error handling
- Best practices

### 4.2 Example Usage

#### AWS Bedrock Example
```python
from src.providers.bedrock_provider import BedrockProvider

# Initialize provider
provider = BedrockProvider()
provider.initialize()

# Generate text
response = provider.generate_text(
    prompt="Explain quantum computing in simple terms.",
    model="claude",
    max_tokens=500,
    temperature=0.7
)
print(response)

# Generate streaming text
for chunk in provider.generate_text_stream(
    prompt="Write a short story about a robot learning to paint.",
    model="claude",
    max_tokens=1000,
    temperature=0.8
):
    print(chunk, end="", flush=True)
```

#### Azure OpenAI Example
```python
from src.providers.azure_openai_provider import AzureOpenAIProvider

# Initialize provider
provider = AzureOpenAIProvider()
provider.initialize()

# Generate text
response = provider.generate_text(
    prompt="Explain the theory of relativity in simple terms.",
    deployment_id="gpt-4",
    max_tokens=500,
    temperature=0.7
)
print(response)

# Generate streaming text
for chunk in provider.generate_text_stream(
    prompt="Write a poem about the changing seasons.",
    deployment_id="gpt-4",
    max_tokens=1000,
    temperature=0.8
):
    print(chunk, end="", flush=True)
```

## 5. Implementation Timeline

### Phase 1: AWS Bedrock Provider (5-7 days)
- Day 1-2: Research and basic implementation
- Day 3-4: Core functionality and streaming support
- Day 5-6: Error handling and testing
- Day 7: Documentation and examples

### Phase 2: Azure OpenAI Provider (5-7 days)
- Day 1-2: Research and basic implementation
- Day 3-4: Core functionality and streaming support
- Day 5-6: Error handling and testing
- Day 7: Documentation and examples

### Phase 3: Integration and Validation (3-4 days)
- Day 1-2: Integration with ApiKeyManager
- Day 3-4: Comprehensive testing and validation

## 6. Conclusion

This expansion will significantly enhance ApexAgent's capabilities by providing users with access to a wider range of LLM providers. The implementation will leverage the enhanced ApiKeyManager for secure credential storage and access control, ensuring that sensitive API keys are properly protected. The providers will be designed to be consistent with the existing BaseLlmProvider interface, making it easy for users to switch between providers as needed.
