# ApexAgent Main System Integration
# Restored and integrated features from archives

# Authentication System
from .auth import AuthManager, MFAManager, EnhancedRBAC, EnterpriseIdentityManager

# LLM Providers
from .plugins.llm_providers import (
    BaseProvider, OpenAIProvider, AnthropicProvider,
    GeminiProvider, TogetherAIProvider
)

# Tools and Automation
from .plugins.tools import (
    DesktopAutomationTool, FileSystemReaderTool, ShellExecutorTool
)
