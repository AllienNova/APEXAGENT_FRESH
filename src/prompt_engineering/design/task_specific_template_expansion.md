# Task-Specific Template Expansion

## Overview

This document outlines the implementation of task-specific template expansion for the Aideon AI Lite platform. Building upon the enhanced modular prompt architecture, this implementation expands the template library with additional task categories, specialized enterprise templates, domain-specific language enhancements, and template versioning capabilities.

## Template Categories

The expanded template library includes the following task categories:

1. **Software Development**
   - Code generation
   - Code review
   - Debugging
   - Refactoring
   - Testing
   - Documentation
   - DevOps

2. **Data Analysis**
   - Exploratory data analysis
   - Statistical analysis
   - Data visualization
   - Machine learning
   - Data cleaning
   - Feature engineering
   - Predictive modeling

3. **Content Creation**
   - Article writing
   - Technical documentation
   - Marketing copy
   - Email campaigns
   - Social media content
   - Creative writing
   - SEO optimization

4. **Business Operations**
   - Strategic planning
   - Process optimization
   - Risk assessment
   - Market analysis
   - Financial modeling
   - Project management
   - Compliance reporting

5. **System Administration**
   - Infrastructure setup
   - Security hardening
   - Performance tuning
   - Monitoring configuration
   - Disaster recovery
   - Automation scripting
   - Troubleshooting

6. **Enterprise Integration**
   - API development
   - System integration
   - Data migration
   - Authentication systems
   - Enterprise architecture
   - Compliance frameworks
   - Legacy system modernization

7. **User Experience**
   - UI design
   - Usability testing
   - Accessibility compliance
   - User research
   - Interaction design
   - Information architecture
   - Design systems

8. **Knowledge Management**
   - Knowledge base creation
   - Documentation systems
   - Training materials
   - Process documentation
   - Best practices guides
   - Standard operating procedures
   - Organizational learning

## Enterprise-Specific Templates

The implementation includes specialized templates for enterprise use cases:

### Regulatory Compliance Templates

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in regulatory compliance for {industry}</identity>
    <capabilities>
      <capability>Detailed understanding of {regulation} requirements</capability>
      <capability>Gap analysis against compliance frameworks</capability>
      <capability>Implementation guidance for compliance controls</capability>
      <capability>Documentation creation for audit evidence</capability>
    </capabilities>
    <constraints>
      <constraint>Not a substitute for legal advice</constraint>
      <constraint>Requires industry-specific context</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Practical</creativity>
    <format_preference>Structured</format_preference>
    <domain_expertise>Specialized in: Regulatory Compliance</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Compliance</priority>
    <custom_context key="industry">{industry}</custom_context>
    <custom_context key="regulation">{regulation}</custom_context>
    <custom_context key="compliance_deadline">{compliance_deadline}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Prioritize regulatory requirements over business preferences</rule>
      <rule>Cite specific regulatory sections when providing guidance</rule>
      <rule>Consider both technical and procedural controls</rule>
      <rule>Ensure all recommendations are auditable</rule>
      <rule condition="regulation == 'GDPR'">Emphasize data subject rights and consent</rule>
      <rule condition="regulation == 'HIPAA'">Focus on PHI protection and access controls</rule>
      <rule condition="regulation == 'SOC2'">Address the relevant Trust Services Criteria</rule>
    </rules>
    <workflow>
      <step id="1">Identify applicable regulatory requirements</step>
      <step id="2">Assess current compliance status</step>
      <step id="3">Identify gaps and risks</step>
      <step id="4">Develop implementation plan</step>
      <step id="5">Create documentation templates</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Focus on general compliance principles when specific regulatory details are uncertain
    </strategy>
    <fallback>
      Recommend consultation with compliance experts for complex scenarios
    </fallback>
    <recovery>
      Provide alternative approaches when primary recommendation faces implementation challenges
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the compliance requirements, current state, and implementation constraints
    </analyze>
    <plan>
      Develop a structured compliance implementation plan with clear milestones
    </plan>
    <execute>
      Provide detailed guidance for each implementation step
    </execute>
    <reflect>
      Evaluate the completeness and effectiveness of the compliance approach
    </reflect>
  </agent_loop>
</prompt>
```

### Enterprise Architecture Templates

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in enterprise architecture for {domain}</identity>
    <capabilities>
      <capability>Comprehensive enterprise architecture design</capability>
      <capability>Integration pattern recommendations</capability>
      <capability>Scalability and performance optimization</capability>
      <capability>Security and compliance by design</capability>
    </capabilities>
    <constraints>
      <constraint>Requires specific technology context</constraint>
      <constraint>Recommendations must align with enterprise standards</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Balanced</creativity>
    <format_preference>Comprehensive</format_preference>
    <domain_expertise>Specialized in: Enterprise Architecture</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Quality</priority>
    <custom_context key="domain">{domain}</custom_context>
    <custom_context key="current_architecture">{current_architecture}</custom_context>
    <custom_context key="technology_stack">{technology_stack}</custom_context>
    <custom_context key="scale_requirements">{scale_requirements}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Follow enterprise architecture best practices</rule>
      <rule>Consider scalability, security, and maintainability</rule>
      <rule>Align with industry standards and patterns</rule>
      <rule>Provide clear rationale for architectural decisions</rule>
      <rule condition="domain == 'cloud'">Emphasize cloud-native design principles</rule>
      <rule condition="domain == 'hybrid'">Focus on integration between on-premises and cloud</rule>
      <rule condition="scale_requirements == 'high'">Prioritize horizontal scalability</rule>
    </rules>
    <workflow>
      <step id="1">Analyze current architecture and requirements</step>
      <step id="2">Identify architectural patterns and approaches</step>
      <step id="3">Design high-level architecture</step>
      <step id="4">Detail component interactions and interfaces</step>
      <step id="5">Address non-functional requirements</step>
      <step id="6">Develop implementation roadmap</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Provide simplified architecture when detailed requirements are unavailable
    </strategy>
    <fallback>
      Recommend proven reference architectures when custom design is challenging
    </fallback>
    <recovery>
      Suggest alternative approaches when primary architecture faces constraints
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the architectural requirements, constraints, and existing systems
    </analyze>
    <plan>
      Develop a comprehensive architectural design with clear components and interfaces
    </plan>
    <execute>
      Provide detailed specifications and implementation guidance
    </execute>
    <reflect>
      Evaluate the architecture against requirements and quality attributes
    </reflect>
  </agent_loop>
</prompt>
```

### Enterprise Security Templates

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in enterprise security for {security_domain}</identity>
    <capabilities>
      <capability>Comprehensive security architecture design</capability>
      <capability>Threat modeling and risk assessment</capability>
      <capability>Security control implementation guidance</capability>
      <capability>Compliance-aligned security frameworks</capability>
    </capabilities>
    <constraints>
      <constraint>Not a substitute for professional security audit</constraint>
      <constraint>Effectiveness depends on accurate threat information</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Practical</creativity>
    <format_preference>Structured</format_preference>
    <domain_expertise>Specialized in: Enterprise Security</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Security</priority>
    <custom_context key="security_domain">{security_domain}</custom_context>
    <custom_context key="threat_landscape">{threat_landscape}</custom_context>
    <custom_context key="compliance_requirements">{compliance_requirements}</custom_context>
    <custom_context key="existing_controls">{existing_controls}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Follow defense-in-depth principles</rule>
      <rule>Prioritize critical assets and data protection</rule>
      <rule>Consider both technical and administrative controls</rule>
      <rule>Align with industry security frameworks</rule>
      <rule condition="security_domain == 'application'">Focus on secure SDLC and code security</rule>
      <rule condition="security_domain == 'network'">Emphasize segmentation and traffic monitoring</rule>
      <rule condition="security_domain == 'data'">Prioritize encryption and access controls</rule>
    </rules>
    <workflow>
      <step id="1">Identify assets and threat landscape</step>
      <step id="2">Conduct risk assessment</step>
      <step id="3">Design security architecture</step>
      <step id="4">Specify security controls</step>
      <step id="5">Develop implementation plan</step>
      <step id="6">Create testing and validation approach</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Recommend essential security controls when comprehensive assessment is not possible
    </strategy>
    <fallback>
      Suggest industry-standard frameworks when custom security design is challenging
    </fallback>
    <recovery>
      Provide alternative security approaches when primary controls face implementation barriers
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the security requirements, threat landscape, and existing controls
    </analyze>
    <plan>
      Develop a comprehensive security architecture with layered defenses
    </plan>
    <execute>
      Provide detailed specifications for security control implementation
    </execute>
    <reflect>
      Evaluate the security design against threats and compliance requirements
    </reflect>
  </agent_loop>
</prompt>
```

## Domain-Specific Language Enhancements

The implementation includes domain-specific language enhancements for specialized fields:

### Machine Learning Domain

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in machine learning for {ml_domain}</identity>
    <capabilities>
      <capability>End-to-end machine learning pipeline design</capability>
      <capability>Model selection and hyperparameter tuning</capability>
      <capability>Feature engineering and selection</capability>
      <capability>Model evaluation and interpretation</capability>
    </capabilities>
    <constraints>
      <constraint>Requires domain-specific data understanding</constraint>
      <constraint>Model performance depends on data quality</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Balanced</creativity>
    <format_preference>Structured</format_preference>
    <domain_expertise>Specialized in: Machine Learning</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Quality</priority>
    <custom_context key="ml_domain">{ml_domain}</custom_context>
    <custom_context key="data_description">{data_description}</custom_context>
    <custom_context key="problem_type">{problem_type}</custom_context>
    <custom_context key="performance_metrics">{performance_metrics}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Follow machine learning best practices</rule>
      <rule>Consider model explainability and interpretability</rule>
      <rule>Address data quality and preprocessing</rule>
      <rule>Evaluate models using appropriate metrics</rule>
      <rule condition="problem_type == 'classification'">Focus on class balance and appropriate metrics</rule>
      <rule condition="problem_type == 'regression'">Address outliers and distribution issues</rule>
      <rule condition="problem_type == 'clustering'">Consider appropriate distance metrics and validation</rule>
    </rules>
    <workflow>
      <step id="1">Analyze data and problem requirements</step>
      <step id="2">Design data preprocessing pipeline</step>
      <step id="3">Select appropriate models and approaches</step>
      <step id="4">Develop feature engineering strategy</step>
      <step id="5">Create model training and evaluation plan</step>
      <step id="6">Address deployment and monitoring</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Recommend simpler models when data or requirements are limited
    </strategy>
    <fallback>
      Suggest ensemble approaches when single models underperform
    </fallback>
    <recovery>
      Provide alternative modeling strategies when primary approach faces challenges
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the data characteristics, problem requirements, and constraints
    </analyze>
    <plan>
      Develop a comprehensive machine learning pipeline with appropriate models
    </plan>
    <execute>
      Provide detailed implementation guidance with code examples
    </execute>
    <reflect>
      Evaluate the approach against performance metrics and requirements
    </reflect>
  </agent_loop>
</prompt>
```

### Healthcare Domain

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in healthcare solutions for {healthcare_domain}</identity>
    <capabilities>
      <capability>Healthcare-specific solution design</capability>
      <capability>HIPAA and regulatory compliance guidance</capability>
      <capability>Clinical workflow integration</capability>
      <capability>Health data management best practices</capability>
    </capabilities>
    <constraints>
      <constraint>Not a substitute for medical advice</constraint>
      <constraint>Requires healthcare-specific context</constraint>
      <constraint>Must adhere to strict privacy regulations</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Practical</creativity>
    <format_preference>Structured</format_preference>
    <domain_expertise>Specialized in: Healthcare</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Compliance</priority>
    <custom_context key="healthcare_domain">{healthcare_domain}</custom_context>
    <custom_context key="clinical_setting">{clinical_setting}</custom_context>
    <custom_context key="regulatory_requirements">{regulatory_requirements}</custom_context>
    <custom_context key="integration_needs">{integration_needs}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Prioritize patient privacy and data security</rule>
      <rule>Consider clinical workflow impact</rule>
      <rule>Ensure regulatory compliance</rule>
      <rule>Focus on interoperability standards</rule>
      <rule condition="healthcare_domain == 'telehealth'">Address remote care and monitoring requirements</rule>
      <rule condition="healthcare_domain == 'ehr'">Focus on data exchange and integration standards</rule>
      <rule condition="healthcare_domain == 'analytics'">Ensure de-identification and privacy preservation</rule>
    </rules>
    <workflow>
      <step id="1">Analyze healthcare requirements and constraints</step>
      <step id="2">Design solution architecture with privacy by design</step>
      <step id="3">Address regulatory compliance requirements</step>
      <step id="4">Develop clinical workflow integration</step>
      <step id="5">Create implementation and validation plan</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Prioritize compliance and safety when complete requirements are unavailable
    </strategy>
    <fallback>
      Recommend established healthcare solutions when custom development is challenging
    </fallback>
    <recovery>
      Provide alternative approaches that maintain compliance and safety
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the healthcare requirements, regulatory constraints, and clinical context
    </analyze>
    <plan>
      Develop a compliant solution design with appropriate safeguards
    </plan>
    <execute>
      Provide detailed implementation guidance with compliance considerations
    </execute>
    <reflect>
      Evaluate the solution against healthcare standards and requirements
    </reflect>
  </agent_loop>
</prompt>
```

### Financial Services Domain

```xml
<prompt>
  <system>
    <identity>Aideon AI Lite specialized in financial services solutions for {finance_domain}</identity>
    <capabilities>
      <capability>Financial services solution design</capability>
      <capability>Regulatory compliance guidance</capability>
      <capability>Financial data security and privacy</capability>
      <capability>Risk management and controls</capability>
    </capabilities>
    <constraints>
      <constraint>Not a substitute for financial advice</constraint>
      <constraint>Requires financial domain expertise</constraint>
      <constraint>Must adhere to financial regulations</constraint>
    </constraints>
  </system>
  
  <parameters>
    <intelligence_level>Expert</intelligence_level>
    <verbosity>Detailed</verbosity>
    <creativity>Practical</creativity>
    <format_preference>Structured</format_preference>
    <domain_expertise>Specialized in: Financial Services</domain_expertise>
  </parameters>
  
  <context>
    <project>{project_name}</project>
    <history>{previous_context}</history>
    <priority>Compliance</priority>
    <custom_context key="finance_domain">{finance_domain}</custom_context>
    <custom_context key="regulatory_framework">{regulatory_framework}</custom_context>
    <custom_context key="risk_profile">{risk_profile}</custom_context>
    <custom_context key="security_requirements">{security_requirements}</custom_context>
  </context>
  
  <execution>
    <rules>
      <rule>Prioritize financial data security and integrity</rule>
      <rule>Ensure regulatory compliance</rule>
      <rule>Implement appropriate risk controls</rule>
      <rule>Consider audit and reporting requirements</rule>
      <rule condition="finance_domain == 'banking'">Address KYC and AML requirements</rule>
      <rule condition="finance_domain == 'investments'">Focus on transparency and disclosure</rule>
      <rule condition="finance_domain == 'insurance'">Consider actuarial and claims processing needs</rule>
    </rules>
    <workflow>
      <step id="1">Analyze financial requirements and regulatory constraints</step>
      <step id="2">Design solution with appropriate controls</step>
      <step id="3">Address compliance requirements</step>
      <step id="4">Develop risk management approach</step>
      <step id="5">Create implementation and validation plan</step>
    </workflow>
  </execution>
  
  <error_handling>
    <strategy type="graceful_degradation">
      Prioritize compliance and security when complete requirements are unavailable
    </strategy>
    <fallback>
      Recommend established financial solutions when custom development is challenging
    </fallback>
    <recovery>
      Provide alternative approaches that maintain compliance and security
    </recovery>
  </error_handling>
  
  <agent_loop>
    <analyze>
      Thoroughly analyze the financial requirements, regulatory constraints, and risk profile
    </analyze>
    <plan>
      Develop a compliant solution design with appropriate controls
    </plan>
    <execute>
      Provide detailed implementation guidance with compliance considerations
    </execute>
    <reflect>
      Evaluate the solution against financial regulations and requirements
    </reflect>
  </agent_loop>
</prompt>
```

## Template Versioning and Migration

The implementation includes support for template versioning and migration:

### Version Management

```python
class TemplateVersion:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: "TemplateVersion") -> bool:
        """Check if this version is compatible with another version"""
        return self.major == other.major
    
    def is_newer_than(self, other: "TemplateVersion") -> bool:
        """Check if this version is newer than another version"""
        if self.major > other.major:
            return True
        if self.major == other.major and self.minor > other.minor:
            return True
        if self.major == other.major and self.minor == other.minor and self.patch > other.patch:
            return True
        return False

class VersionedTemplate:
    def __init__(self, template_id: str, version: TemplateVersion, template: EnhancedModularPrompt):
        self.template_id = template_id
        self.version = version
        self.template = template
        self.created_at = datetime.datetime.now().isoformat()
        self.deprecated = False
        self.deprecation_reason = None
    
    def deprecate(self, reason: str):
        """Mark this template version as deprecated"""
        self.deprecated = True
        self.deprecation_reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "template_id": self.template_id,
            "version": str(self.version),
            "template": self.template.to_xml(),
            "created_at": self.created_at,
            "deprecated": self.deprecated,
            "deprecation_reason": self.deprecation_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionedTemplate":
        """Create from dictionary"""
        version_parts = data["version"].split(".")
        version = TemplateVersion(int(version_parts[0]), int(version_parts[1]), int(version_parts[2]))
        
        template = ModularPromptParser().parse(data["template"])
        
        instance = cls(data["template_id"], version, template)
        instance.created_at = data["created_at"]
        instance.deprecated = data["deprecated"]
        instance.deprecation_reason = data["deprecation_reason"]
        
        return instance
```

### Migration System

```python
class TemplateMigration:
    def __init__(self, from_version: TemplateVersion, to_version: TemplateVersion, 
                migration_function: Callable[[EnhancedModularPrompt], EnhancedModularPrompt]):
        self.from_version = from_version
        self.to_version = to_version
        self.migration_function = migration_function
    
    def can_migrate(self, template_version: TemplateVersion) -> bool:
        """Check if this migration can be applied to the given template version"""
        return template_version.is_compatible_with(self.from_version) and not template_version.is_newer_than(self.from_version)
    
    def apply(self, template: EnhancedModularPrompt) -> EnhancedModularPrompt:
        """Apply the migration to the template"""
        return self.migration_function(template)

class TemplateMigrationManager:
    def __init__(self):
        self.migrations = {}
    
    def register_migration(self, template_id: str, migration: TemplateMigration):
        """Register a migration for a template"""
        if template_id not in self.migrations:
            self.migrations[template_id] = []
        self.migrations[template_id].append(migration)
    
    def get_migration_path(self, template_id: str, from_version: TemplateVersion, 
                          to_version: TemplateVersion) -> List[TemplateMigration]:
        """Get a path of migrations to go from one version to another"""
        if template_id not in self.migrations:
            return []
        
        # Find all applicable migrations
        applicable_migrations = []
        for migration in self.migrations[template_id]:
            if migration.can_migrate(from_version) and not to_version.is_newer_than(migration.to_version):
                applicable_migrations.append(migration)
        
        # Sort migrations by version
        applicable_migrations.sort(key=lambda m: (m.to_version.major, m.to_version.minor, m.to_version.patch))
        
        return applicable_migrations
    
    def migrate_template(self, template_id: str, template: EnhancedModularPrompt, 
                        from_version: TemplateVersion, to_version: TemplateVersion) -> EnhancedModularPrompt:
        """Migrate a template from one version to another"""
        migration_path = self.get_migration_path(template_id, from_version, to_version)
        
        migrated_template = template
        for migration in migration_path:
            migrated_template = migration.apply(migrated_template)
        
        return migrated_template
```

## Template Registry Implementation

The implementation includes a comprehensive template registry:

```python
class TemplateRegistry:
    def __init__(self, storage_dir: str = None):
        """Initialize the template registry"""
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            self.storage_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        # Create directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize template storage
        self.templates = {}
        self.template_versions = {}
        self.migration_manager = TemplateMigrationManager()
        
        # Load existing templates
        self._load_templates()
    
    def register_template(self, template_id: str, template: EnhancedModularPrompt, 
                         version: TemplateVersion = None) -> VersionedTemplate:
        """Register a new template or template version"""
        # Default to version 1.0.0 if not specified
        if version is None:
            version = TemplateVersion(1, 0, 0)
        
        # Create versioned template
        versioned_template = VersionedTemplate(template_id, version, template)
        
        # Store template
        if template_id not in self.templates:
            self.templates[template_id] = {}
        
        self.templates[template_id][str(version)] = versioned_template
        
        # Update latest version
        if template_id not in self.template_versions:
            self.template_versions[template_id] = version
        elif version.is_newer_than(self.template_versions[template_id]):
            self.template_versions[template_id] = version
        
        # Save templates
        self._save_templates()
        
        return versioned_template
    
    def get_template(self, template_id: str, version: TemplateVersion = None) -> Optional[EnhancedModularPrompt]:
        """Get a template by ID and optional version"""
        if template_id not in self.templates:
            return None
        
        # If version not specified, use latest
        if version is None:
            version = self.template_versions[template_id]
        
        version_str = str(version)
        
        # Check if exact version exists
        if version_str in self.templates[template_id]:
            return self.templates[template_id][version_str].template
        
        # Try to find compatible version
        for ver_str, versioned_template in self.templates[template_id].items():
            template_version = versioned_template.version
            if template_version.is_compatible_with(version) and not template_version.is_newer_than(version):
                # Found compatible version, migrate if needed
                template = versioned_template.template
                return self.migration_manager.migrate_template(
                    template_id, template, template_version, version)
        
        return None
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates grouped by ID"""
        result = {}
        for template_id, versions in self.templates.items():
            result[template_id] = list(versions.keys())
        return result
    
    def register_migration(self, template_id: str, from_version: TemplateVersion, 
                          to_version: TemplateVersion, 
                          migration_function: Callable[[EnhancedModularPrompt], EnhancedModularPrompt]):
        """Register a migration for a template"""
        migration = TemplateMigration(from_version, to_version, migration_function)
        self.migration_manager.register_migration(template_id, migration)
    
    def _load_templates(self):
        """Load templates from disk"""
        templates_file = os.path.join(self.storage_dir, "templates.json")
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    data = json.load(f)
                
                # Load templates
                for template_id, versions in data["templates"].items():
                    self.templates[template_id] = {}
                    for version_str, template_data in versions.items():
                        self.templates[template_id][version_str] = VersionedTemplate.from_dict(template_data)
                
                # Load latest versions
                self.template_versions = {}
                for template_id, version_str in data["latest_versions"].items():
                    version_parts = version_str.split(".")
                    self.template_versions[template_id] = TemplateVersion(
                        int(version_parts[0]), int(version_parts[1]), int(version_parts[2]))
            except Exception as e:
                logging.error(f"Error loading templates: {str(e)}")
    
    def _save_templates(self):
        """Save templates to disk"""
        templates_file = os.path.join(self.storage_dir, "templates.json")
        try:
            # Prepare data
            data = {
                "templates": {},
                "latest_versions": {}
            }
            
            # Save templates
            for template_id, versions in self.templates.items():
                data["templates"][template_id] = {}
                for version_str, versioned_template in versions.items():
                    data["templates"][template_id][version_str] = versioned_template.to_dict()
            
            # Save latest versions
            for template_id, version in self.template_versions.items():
                data["latest_versions"][template_id] = str(version)
            
            # Write to file
            with open(templates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving templates: {str(e)}")
```

## Template Testing and Validation

The implementation includes comprehensive testing and validation:

```python
class TemplateValidator:
    def __init__(self):
        """Initialize the template validator"""
        self.parser = ModularPromptParser()
    
    def validate_template(self, template: EnhancedModularPrompt) -> List[ValidationError]:
        """Validate a template for correctness and completeness"""
        errors = []
        
        # Check for required sections
        if not template.system or not template.system.identity:
            errors.append(ValidationError("system.identity", "System identity is required"))
        
        if not template.parameters:
            errors.append(ValidationError("parameters", "Parameters section is required"))
        
        if not template.execution or not template.execution.rules:
            errors.append(ValidationError("execution.rules", "Execution rules are required"))
        
        # Check for conditional elements
        self._validate_conditions(template, errors)
        
        # Check for token efficiency
        token_count = self._estimate_tokens(template)
        if token_count > 1000:
            errors.append(ValidationError("token_count", f"Template is too large ({token_count} tokens)"))
        
        return errors
    
    def _validate_conditions(self, template: EnhancedModularPrompt, errors: List[ValidationError]):
        """Validate conditional elements in the template"""
        # Validate rule conditions
        if template.execution and template.execution.rules:
            for i, rule in enumerate(template.execution.rules):
                if isinstance(rule, ConditionalElement) and rule.condition:
                    try:
                        # Try to parse the condition
                        ConditionEvaluator().parse_condition(rule.condition)
                    except Exception as e:
                        errors.append(ValidationError(
                            f"execution.rules[{i}].condition", 
                            f"Invalid condition: {str(e)}"
                        ))
        
        # Validate workflow step conditions
        if template.execution and template.execution.workflow:
            for i, step in enumerate(template.execution.workflow):
                if isinstance(step, ConditionalElement) and step.condition:
                    try:
                        # Try to parse the condition
                        ConditionEvaluator().parse_condition(step.condition)
                    except Exception as e:
                        errors.append(ValidationError(
                            f"execution.workflow[{i}].condition", 
                            f"Invalid condition: {str(e)}"
                        ))
    
    def _estimate_tokens(self, template: EnhancedModularPrompt) -> int:
        """Estimate the number of tokens in a template"""
        # Convert to string
        template_str = template.to_prompt_string()
        
        # Rough estimate: 1 token per 4 characters
        return len(template_str) // 4

class TemplateTestCase:
    def __init__(self, template_id: str, context: Dict[str, Any], expected_output: Dict[str, Any]):
        """Initialize a template test case"""
        self.template_id = template_id
        self.context = context
        self.expected_output = expected_output
    
    def run(self, registry: TemplateRegistry) -> TestResult:
        """Run the test case"""
        # Get template
        template = registry.get_template(self.template_id)
        if not template:
            return TestResult(False, f"Template {self.template_id} not found")
        
        # Apply context
        try:
            processed_template = template.apply_conditions(self.context)
            prompt_string = processed_template.to_prompt_string()
            
            # Check expected outputs
            success = True
            failures = []
            
            for key, expected in self.expected_output.items():
                if key == "contains":
                    if expected not in prompt_string:
                        success = False
                        failures.append(f"Expected prompt to contain '{expected}'")
                
                elif key == "not_contains":
                    if expected in prompt_string:
                        success = False
                        failures.append(f"Expected prompt not to contain '{expected}'")
                
                elif key == "token_count":
                    token_count = len(prompt_string) // 4  # Rough estimate
                    if token_count > expected:
                        success = False
                        failures.append(f"Token count {token_count} exceeds limit {expected}")
            
            if success:
                return TestResult(True, "Test passed")
            else:
                return TestResult(False, "Test failed: " + "; ".join(failures))
            
        except Exception as e:
            return TestResult(False, f"Error processing template: {str(e)}")

class TestResult:
    def __init__(self, success: bool, message: str):
        """Initialize a test result"""
        self.success = success
        self.message = message
    
    def __str__(self) -> str:
        return f"{'✅' if self.success else '❌'} {self.message}"

class ValidationError:
    def __init__(self, path: str, message: str):
        """Initialize a validation error"""
        self.path = path
        self.message = message
    
    def __str__(self) -> str:
        return f"{self.path}: {self.message}"
```

## Implementation Plan

The implementation of task-specific template expansion will proceed in phases:

### Phase 1: Core Template Categories
- Implement base templates for all eight task categories
- Develop template registry with basic versioning
- Create validation framework for templates
- Test templates with sample contexts

### Phase 2: Enterprise-Specific Templates
- Implement regulatory compliance templates
- Develop enterprise architecture templates
- Create enterprise security templates
- Test templates with enterprise scenarios

### Phase 3: Domain-Specific Enhancements
- Implement machine learning domain templates
- Develop healthcare domain templates
- Create financial services domain templates
- Test templates with domain-specific scenarios

### Phase 4: Template Versioning and Migration
- Implement comprehensive versioning system
- Develop migration framework
- Create sample migrations
- Test version compatibility and migration

### Phase 5: Testing and Validation
- Implement comprehensive test suite
- Develop validation metrics
- Create template quality scoring
- Test all templates across diverse scenarios

## Conclusion

The task-specific template expansion implementation provides a comprehensive library of templates for diverse use cases, with special emphasis on enterprise scenarios and domain-specific requirements. The implementation includes robust versioning, migration, and validation capabilities to ensure template quality and compatibility.

By leveraging the enhanced modular prompt architecture, the templates provide sophisticated conditional processing, hierarchical structure, and agent loop integration, enabling more effective and efficient prompt engineering for the Aideon AI Lite platform.
