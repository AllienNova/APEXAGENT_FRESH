# ApexAgent API Key Mode Selection Guide

## Introduction

ApexAgent offers two distinct API key modes to provide flexibility in how you access AI models:

1. **Complete System Mode**: ApexAgent provides all necessary API keys through our secure proxy service.
2. **User-Provided API Keys Mode**: You provide your own API keys for direct access to AI providers.

This guide explains both options, how to select between them during installation, and how to change your selection later.

## Comparing the Options

| Feature | Complete System | User-Provided API Keys |
|---------|----------------|------------------------|
| **Subscription Cost** | Standard pricing | 20-45% lower pricing across all tiers |
| **API Key Management** | Fully managed by ApexAgent | Managed by you |
| **Setup Complexity** | Minimal (no API keys needed) | Requires obtaining API keys |
| **Control Over API Usage** | Limited (managed by ApexAgent) | Full control |
| **Model Selection** | Automatic based on task | Manual selection possible |
| **Privacy** | Data passes through ApexAgent proxy | Direct connection to providers |
| **Billing** | Single consolidated bill | Separate bills from each provider |

## Choosing During Installation

During the ApexAgent installation process, you'll be presented with a screen to choose your preferred API key mode:

![API Key Mode Selection](api_key_mode_selection_screenshot.png)

### Complete System Mode

Select this option if you prefer:
- Simplicity and convenience
- No need to obtain or manage API keys
- Consolidated billing through ApexAgent
- Immediate access to all supported models

### User-Provided API Keys Mode

Select this option if you prefer:
- Lower subscription costs (20-45% reduction)
- Direct control over API usage and costs
- Using existing API keys or enterprise agreements
- Enhanced privacy with direct provider connections

## First-Run Experience

After installation, the first-run onboarding wizard will confirm your API key mode selection:

### For Complete System Mode

If you selected Complete System mode, you'll see a confirmation and can proceed directly to using ApexAgent.

### For User-Provided API Keys Mode

If you selected User-Provided API Keys mode, you'll be prompted to enter your API keys:

![API Key Entry](api_key_entry_screenshot.png)

You can enter keys for any of the following providers:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Google AI (Gemini models)
- Mistral AI
- Cohere
- Azure OpenAI

For each provider, you'll need to:
1. Enter your API key
2. Optionally provide a name for the key
3. Test the key to ensure it works correctly

You can skip this step and add keys later if needed.

## Changing API Key Mode After Installation

You can change your API key mode at any time through the ApexAgent settings:

1. Open ApexAgent
2. Go to Settings
3. Select "API Keys" from the sidebar
4. Click "Change API Key Mode"

![Change API Key Mode](change_api_key_mode_screenshot.png)

### Switching from Complete System to User-Provided Keys

When switching to User-Provided Keys mode:
- Your subscription cost will be reduced
- You'll need to add your own API keys
- You'll have more direct control over API usage

### Switching from User-Provided Keys to Complete System

When switching to Complete System mode:
- Your subscription cost will increase
- Your existing API keys will be preserved but not used
- ApexAgent will handle all API access automatically

## Managing API Keys

### In User-Provided API Keys Mode

The API Keys settings page allows you to:
- Add new API keys
- Test existing keys
- Remove keys you no longer need
- View usage history

![API Key Management](api_key_management_screenshot.png)

### In Complete System Mode

In Complete System mode, the API Keys settings page shows:
- Connection status to various providers
- Usage statistics
- Option to switch to User-Provided Keys mode

## Obtaining API Keys

If you choose User-Provided API Keys mode, you'll need to obtain keys from the providers you wish to use:

### OpenAI API Keys
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with "sk-")

### Anthropic API Keys
1. Go to [https://console.anthropic.com/account/keys](https://console.anthropic.com/account/keys)
2. Sign in or create an account
3. Click "Create Key"
4. Copy the key (it starts with "sk-ant-")

### Google AI API Keys
1. Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (it starts with "AIza")

### Other Providers
Similar processes apply for Mistral AI, Cohere, and Azure OpenAI. Links to these providers are available in the API key settings.

## Troubleshooting

### Complete System Mode Issues

| Issue | Solution |
|-------|----------|
| "Unable to connect to ApexAgent proxy" | Check your internet connection and firewall settings. The ApexAgent proxy requires outbound access on port 443. |
| "Proxy authentication failed" | Your subscription may have expired. Check your account status in the dashboard. |
| "Model not available" | The requested model may be temporarily unavailable. Try again later or select a different model. |

### User-Provided API Keys Issues

| Issue | Solution |
|-------|----------|
| "Invalid API key" | Double-check that you've entered the correct API key without any extra spaces. |
| "API key has expired" | Generate a new API key from the provider's website. |
| "Rate limit exceeded" | Your API key has reached its usage limit. Wait for the limit to reset or use a different provider. |
| "Insufficient credits" | Your account with the provider may need additional credits or payment. |

## Security Considerations

### Complete System Mode

In Complete System mode:
- Your requests are processed through ApexAgent's secure proxy
- API keys are managed by ApexAgent and never exposed to you
- Data is encrypted in transit between your device and our servers
- Usage is monitored for security and billing purposes

### User-Provided API Keys Mode

In User-Provided API Keys mode:
- Your API keys are encrypted and stored locally on your device
- Keys are never transmitted to ApexAgent servers
- Requests go directly from your device to the provider
- ApexAgent cannot see the content of your requests

## Pricing Impact

Selecting User-Provided API Keys mode reduces your ApexAgent subscription cost:

| Tier | Complete System | User-Provided API Keys | Monthly Savings |
|------|----------------|------------------------|-----------------|
| Basic | $24.99/month | $19.99/month | $5.00 (20%) |
| Pro | $89.99/month | $49.99/month | $40.00 (44%) |
| Expert | $149.99/month | $99.99/month | $50.00 (33%) |
| Enterprise | Custom pricing | Custom pricing | Varies |

Note that when using User-Provided API Keys, you'll be billed separately by each provider based on your usage.

## Frequently Asked Questions

**Q: Can I use both modes simultaneously?**
A: No, you must choose either Complete System or User-Provided API Keys mode.

**Q: Will my API keys be shared with ApexAgent?**
A: No, in User-Provided API Keys mode, your keys are stored locally and never transmitted to ApexAgent servers.

**Q: Can I switch between modes frequently?**
A: Yes, you can switch at any time through the settings. Your API keys will be preserved when switching.

**Q: Do I need API keys for all providers?**
A: No, you only need keys for the providers you want to use. ApexAgent will use the available keys.

**Q: Which mode is more secure?**
A: Both modes prioritize security. User-Provided API Keys mode offers more privacy as requests go directly to providers.

**Q: Will my subscription change immediately when I switch modes?**
A: Yes, your billing will be adjusted starting from your next billing cycle.

## Conclusion

ApexAgent's dual API key modes offer flexibility to match your preferences for convenience, cost, and control. Choose Complete System mode for simplicity or User-Provided API Keys mode for cost savings and direct control.

For additional assistance, contact our support team at support@apexagent.com.
