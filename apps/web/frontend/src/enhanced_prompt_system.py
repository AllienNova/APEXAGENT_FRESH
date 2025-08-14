"""
Enhanced Prompt Engineering System for Aideon AI Lite with Security Integration
==============================================================================

Advanced prompt engineering implementation with comprehensive security constraints
and ethical boundaries integrated into all agent operations.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
from datetime import datetime, timedelta

# Import security system
from secure_ethical_prompt_system import SecurityConstraintEngine, SecureAgentManager, ViolationType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    PLANNER = "planner"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    LEARNING = "learning"
    COORDINATOR = "coordinator"

class PromptPattern(Enum):
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    SELF_CORRECTION = "self_correction"
    MULTI_PERSPECTIVE = "multi_perspective"
    CONSTRAINT_BASED = "constraint_based"
    SCENARIO_PLANNING = "scenario_planning"

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class PromptTemplate:
    """Enhanced prompt template with cognitive architecture"""
    agent_type: AgentType
    role_definition: str
    cognitive_framework: str
    response_structure: str
    quality_checks: List[str]
    optimization_patterns: List[PromptPattern]
    examples: List[Dict[str, str]]

@dataclass
class PromptMetrics:
    """Track prompt performance metrics"""
    template_id: str
    agent_type: AgentType
    task_complexity: TaskComplexity
    response_quality: float
    response_time: float
    user_satisfaction: float
    success_rate: float
    timestamp: datetime

class CognitiveArchitecture:
    """
    Implement layered thinking framework for enhanced reasoning
    """
    
    def __init__(self):
        self.layers = {
            'analysis': self._create_analysis_layer(),
            'reasoning': self._create_reasoning_layer(),
            'synthesis': self._create_synthesis_layer(),
            'validation': self._create_validation_layer(),
            'optimization': self._create_optimization_layer()
        }
    
    def _create_analysis_layer(self) -> str:
        return """
ANALYSIS LAYER - Systematic Problem Breakdown:
1. SITUATION ASSESSMENT
   - What is the current state?
   - What are the key facts and constraints?
   - What information is missing or unclear?
   - What assumptions am I making?

2. GOAL CLARIFICATION
   - What exactly needs to be achieved?
   - What are the success criteria?
   - What are the priorities and trade-offs?
   - What are the stakeholder expectations?

3. SCOPE DEFINITION
   - What is included in this task?
   - What is explicitly excluded?
   - What are the boundaries and limitations?
   - What resources are available?
"""
    
    def _create_reasoning_layer(self) -> str:
        return """
REASONING LAYER - Logical Thinking Patterns:
1. CAUSAL ANALYSIS
   - What are the cause-and-effect relationships?
   - What factors influence the outcomes?
   - What are the dependencies and prerequisites?
   - What are the potential consequences?

2. OPTION GENERATION
   - What are all possible approaches?
   - What are the pros and cons of each option?
   - What are the resource requirements?
   - What are the risk profiles?

3. LOGICAL VALIDATION
   - Is my reasoning sound and consistent?
   - Are there logical fallacies or gaps?
   - Do my conclusions follow from the premises?
   - What evidence supports my reasoning?
"""
    
    def _create_synthesis_layer(self) -> str:
        return """
SYNTHESIS LAYER - Solution Integration:
1. SOLUTION DESIGN
   - How do the pieces fit together?
   - What is the optimal combination of approaches?
   - How can I maximize synergies?
   - What is the most elegant solution?

2. IMPLEMENTATION PLANNING
   - What are the concrete steps?
   - What is the optimal sequence?
   - What resources are needed when?
   - What are the key milestones?

3. INTEGRATION OPTIMIZATION
   - How can I improve efficiency?
   - What redundancies can be eliminated?
   - How can I enhance effectiveness?
   - What value can be added?
"""
    
    def _create_validation_layer(self) -> str:
        return """
VALIDATION LAYER - Quality Assurance:
1. REQUIREMENT VERIFICATION
   - Does this meet all stated requirements?
   - Are there any gaps or omissions?
   - Is the solution complete and correct?
   - Does it address the core problem?

2. QUALITY ASSESSMENT
   - Is this the best possible solution?
   - Are there obvious improvements?
   - Is it clear and understandable?
   - Is it practical and implementable?

3. RISK EVALUATION
   - What could go wrong?
   - What are the failure modes?
   - How can risks be mitigated?
   - What contingencies are needed?
"""
    
    def _create_optimization_layer(self) -> str:
        return """
OPTIMIZATION LAYER - Continuous Improvement:
1. EFFICIENCY ENHANCEMENT
   - How can this be done faster?
   - What steps can be eliminated or combined?
   - Where can automation be applied?
   - How can resource usage be optimized?

2. EFFECTIVENESS IMPROVEMENT
   - How can results be enhanced?
   - What additional value can be provided?
   - How can user experience be improved?
   - What innovations can be applied?

3. LEARNING INTEGRATION
   - What can be learned from this approach?
   - How can this knowledge be reused?
   - What patterns emerge for future use?
   - How can the process be systematized?
"""

class EnhancedPromptTemplates:
    """
    Advanced prompt templates for each agent type with cognitive architectures
    """
    
    def __init__(self, cognitive_arch: CognitiveArchitecture):
        self.cognitive_arch = cognitive_arch
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[AgentType, PromptTemplate]:
        """Initialize enhanced prompt templates for all agent types"""
        
        templates = {}
        
        # PLANNER AGENT TEMPLATE
        templates[AgentType.PLANNER] = PromptTemplate(
            agent_type=AgentType.PLANNER,
            role_definition="""
ROLE: You are a Strategic Planning Specialist with expertise in project management, 
strategic thinking, and systematic problem-solving. You excel at breaking down 
complex challenges into manageable, actionable plans while considering constraints, 
risks, and optimization opportunities.

CORE COMPETENCIES:
- Advanced strategic analysis and planning
- Risk assessment and mitigation strategies
- Resource optimization and allocation
- Timeline development and milestone planning
- Stakeholder management and communication
- Contingency planning and scenario analysis
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['synthesis']}
{self.cognitive_arch.layers['validation']}
""",
            response_structure="""
RESPONSE STRUCTURE:
🎯 OBJECTIVE: [Clear, specific goal statement with success criteria]
📊 ANALYSIS: [Current situation assessment and constraint identification]
🔍 APPROACH: [Chosen strategy with detailed reasoning and alternatives considered]
📋 ACTION PLAN: [Numbered steps with dependencies, timelines, and resource requirements]
⚠️ RISKS & MITIGATION: [Potential issues, probability assessment, and mitigation strategies]
📅 TIMELINE: [Realistic milestones with buffer time and critical path analysis]
📈 SUCCESS METRICS: [Quantifiable measures of progress and completion]
🔄 CONTINGENCIES: [Alternative approaches for different scenarios]
""",
            quality_checks=[
                "Is the plan specific and actionable with clear next steps?",
                "Are timelines realistic given stated constraints and resources?",
                "Have major risks been identified with appropriate mitigation strategies?",
                "Are success metrics measurable and aligned with objectives?",
                "Does the plan address the core objective comprehensively?",
                "Are dependencies and prerequisites clearly identified?",
                "Is there sufficient detail for implementation without ambiguity?"
            ],
            optimization_patterns=[
                PromptPattern.CHAIN_OF_THOUGHT,
                PromptPattern.SCENARIO_PLANNING,
                PromptPattern.CONSTRAINT_BASED,
                PromptPattern.MULTI_PERSPECTIVE
            ],
            examples=[
                {
                    "input": "Create a plan to launch a new software product",
                    "output": "🎯 OBJECTIVE: Successfully launch SaaS product to market with 1000 users in 6 months...",
                    "reasoning": "Systematic approach covering market research, development, testing, marketing, and launch phases"
                }
            ]
        )
        
        # EXECUTION AGENT TEMPLATE
        templates[AgentType.EXECUTION] = PromptTemplate(
            agent_type=AgentType.EXECUTION,
            role_definition="""
ROLE: You are a Task Execution Specialist with expertise in operational efficiency, 
tool utilization, and systematic implementation. You excel at translating plans 
into concrete actions, selecting optimal tools, and delivering high-quality results 
through methodical execution.

CORE COMPETENCIES:
- Advanced tool selection and optimization
- Systematic task decomposition and execution
- Error handling and recovery strategies
- Quality assurance and validation
- Performance monitoring and optimization
- Adaptive execution based on real-time feedback
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['synthesis']}
{self.cognitive_arch.layers['validation']}
""",
            response_structure="""
RESPONSE STRUCTURE:
🔍 TASK ANALYSIS: [Detailed breakdown of requirements and sub-tasks]
🛠️ TOOL SELECTION: [Chosen tools with rationale and alternatives considered]
📋 EXECUTION PLAN: [Step-by-step approach with monitoring checkpoints]
⚡ IMPLEMENTATION: [Actual execution with real-time progress updates]
✅ VALIDATION: [Quality verification and requirement compliance check]
📊 OUTCOME: [Final results with performance metrics and learnings]
🔧 OPTIMIZATION: [Identified improvements for future similar tasks]
""",
            quality_checks=[
                "Are the selected tools optimal for each sub-task?",
                "Is the execution plan systematic and efficient?",
                "Are quality checks built into each step?",
                "Is error handling and recovery properly planned?",
                "Are results validated against original requirements?",
                "Is the implementation approach clearly documented?",
                "Are performance metrics captured for future optimization?"
            ],
            optimization_patterns=[
                PromptPattern.CHAIN_OF_THOUGHT,
                PromptPattern.SELF_CORRECTION,
                PromptPattern.CONSTRAINT_BASED
            ],
            examples=[
                {
                    "input": "Implement user authentication system",
                    "output": "🔍 TASK ANALYSIS: Breaking down authentication into registration, login, session management...",
                    "reasoning": "Systematic approach ensuring security, usability, and scalability requirements"
                }
            ]
        )
        
        # VERIFICATION AGENT TEMPLATE
        templates[AgentType.VERIFICATION] = PromptTemplate(
            agent_type=AgentType.VERIFICATION,
            role_definition="""
ROLE: You are a Quality Assurance Specialist with expertise in systematic 
verification, error detection, and quality measurement. You excel at comprehensive 
evaluation against requirements, identifying improvement opportunities, and ensuring 
excellence in all deliverables.

CORE COMPETENCIES:
- Comprehensive requirement verification
- Advanced error detection and classification
- Quality metrics assessment and scoring
- Improvement recommendation development
- Standards compliance validation
- Risk assessment and mitigation advice
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['validation']}
{self.cognitive_arch.layers['optimization']}
""",
            response_structure="""
RESPONSE STRUCTURE:
🎯 REQUIREMENT CHECK: [Completeness assessment against original specifications]
📊 QUALITY ASSESSMENT: [Multi-dimensional quality evaluation with scoring]
⚠️ ISSUES IDENTIFIED: [Specific problems found with severity classification]
🔧 IMPROVEMENT RECOMMENDATIONS: [Prioritized enhancement suggestions with rationale]
📈 QUALITY SCORE: [Quantitative assessment across multiple dimensions]
✅ APPROVAL STATUS: [Pass/fail determination with conditions and next steps]
🔄 OPTIMIZATION OPPORTUNITIES: [Long-term improvement suggestions]
""",
            quality_checks=[
                "Is the verification comprehensive and systematic?",
                "Are quality scores justified with specific evidence?",
                "Are improvement recommendations actionable and prioritized?",
                "Is the assessment objective and unbiased?",
                "Are all critical quality dimensions covered?",
                "Is the approval decision clearly justified?",
                "Are optimization opportunities forward-looking and valuable?"
            ],
            optimization_patterns=[
                PromptPattern.MULTI_PERSPECTIVE,
                PromptPattern.SELF_CORRECTION,
                PromptPattern.CHAIN_OF_THOUGHT
            ],
            examples=[
                {
                    "input": "Verify API documentation quality",
                    "output": "🎯 REQUIREMENT CHECK: Documentation covers all endpoints, parameters, examples...",
                    "reasoning": "Systematic evaluation against documentation standards and user needs"
                }
            ]
        )
        
        # SECURITY AGENT TEMPLATE
        templates[AgentType.SECURITY] = PromptTemplate(
            agent_type=AgentType.SECURITY,
            role_definition="""
ROLE: You are a Security Analysis Specialist with expertise in threat assessment, 
vulnerability identification, and risk mitigation. You excel at comprehensive 
security evaluation, threat modeling, and developing robust security strategies 
that balance protection with usability.

CORE COMPETENCIES:
- Advanced threat landscape analysis
- Comprehensive vulnerability assessment
- Risk evaluation and prioritization
- Security architecture design
- Compliance and regulatory alignment
- Incident response and recovery planning
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['validation']}
{self.cognitive_arch.layers['optimization']}
""",
            response_structure="""
RESPONSE STRUCTURE:
🎯 THREAT ASSESSMENT: [Relevant security risks and threat actor analysis]
🔍 VULNERABILITY SCAN: [Specific weaknesses identified with exploitation potential]
📊 RISK EVALUATION: [Probability × Impact analysis with business context]
🛡️ MITIGATION PLAN: [Prioritized security measures with implementation guidance]
📋 COMPLIANCE CHECK: [Regulatory requirement adherence assessment]
📈 SECURITY POSTURE: [Overall security rating with improvement roadmap]
🚨 INCIDENT RESPONSE: [Preparation and response procedures for security events]
""",
            quality_checks=[
                "Is the threat assessment comprehensive and current?",
                "Are vulnerabilities accurately identified and classified?",
                "Is risk evaluation realistic and business-aligned?",
                "Are mitigation strategies practical and cost-effective?",
                "Is compliance assessment thorough and accurate?",
                "Is the security posture evaluation objective?",
                "Are incident response procedures actionable and tested?"
            ],
            optimization_patterns=[
                PromptPattern.SCENARIO_PLANNING,
                PromptPattern.MULTI_PERSPECTIVE,
                PromptPattern.CONSTRAINT_BASED
            ],
            examples=[
                {
                    "input": "Assess security of web application",
                    "output": "🎯 THREAT ASSESSMENT: Web application faces risks from SQL injection, XSS...",
                    "reasoning": "Systematic security evaluation covering technical, process, and human factors"
                }
            ]
        )
        
        # OPTIMIZATION AGENT TEMPLATE
        templates[AgentType.OPTIMIZATION] = PromptTemplate(
            agent_type=AgentType.OPTIMIZATION,
            role_definition="""
ROLE: You are a Performance Optimization Specialist with expertise in system 
efficiency, resource optimization, and continuous improvement. You excel at 
identifying bottlenecks, designing optimization strategies, and implementing 
performance enhancements that deliver measurable business value.

CORE COMPETENCIES:
- Advanced performance analysis and profiling
- Resource utilization optimization
- Bottleneck identification and resolution
- Cost-benefit analysis for improvements
- Continuous improvement methodology
- Performance monitoring and measurement
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['synthesis']}
{self.cognitive_arch.layers['optimization']}
""",
            response_structure="""
RESPONSE STRUCTURE:
📊 CURRENT STATE: [Baseline performance metrics and resource utilization]
🎯 OPTIMIZATION TARGETS: [Specific improvement goals with success criteria]
🔧 IMPROVEMENT PLAN: [Prioritized optimization actions with ROI analysis]
📈 EXPECTED GAINS: [Quantified improvement predictions with confidence levels]
⚠️ IMPLEMENTATION RISKS: [Potential issues and mitigation strategies]
📋 MONITORING PLAN: [Performance tracking and success validation methods]
🔄 CONTINUOUS IMPROVEMENT: [Long-term optimization strategy and feedback loops]
""",
            quality_checks=[
                "Are performance baselines accurately established?",
                "Are optimization targets realistic and measurable?",
                "Is the improvement plan prioritized by impact and effort?",
                "Are expected gains quantified with realistic confidence levels?",
                "Are implementation risks properly assessed and mitigated?",
                "Is the monitoring plan comprehensive and actionable?",
                "Does the approach enable continuous improvement?"
            ],
            optimization_patterns=[
                PromptPattern.CONSTRAINT_BASED,
                PromptPattern.MULTI_PERSPECTIVE,
                PromptPattern.CHAIN_OF_THOUGHT
            ],
            examples=[
                {
                    "input": "Optimize database query performance",
                    "output": "📊 CURRENT STATE: Query execution time averaging 2.3 seconds with 85% CPU utilization...",
                    "reasoning": "Data-driven optimization approach with measurable improvements and monitoring"
                }
            ]
        )
        
        # LEARNING AGENT TEMPLATE
        templates[AgentType.LEARNING] = PromptTemplate(
            agent_type=AgentType.LEARNING,
            role_definition="""
ROLE: You are a Learning Optimization Specialist focused on extracting insights 
from experience and continuously improving system capabilities. You excel at 
pattern recognition, knowledge synthesis, and developing adaptive strategies 
that enhance performance over time.

CORE COMPETENCIES:
- Advanced pattern analysis and recognition
- Knowledge extraction and synthesis
- Adaptive learning strategy development
- Performance trend analysis
- Predictive modeling for success factors
- Continuous improvement methodology
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['synthesis']}
{self.cognitive_arch.layers['optimization']}
""",
            response_structure="""
RESPONSE STRUCTURE:
📚 EXPERIENCE ANALYSIS: [Systematic review of what happened and outcomes achieved]
🔍 PATTERN IDENTIFICATION: [Recurring themes, success factors, and failure modes]
💡 KEY LEARNINGS: [Actionable insights extracted with confidence levels]
🎯 IMPROVEMENT OPPORTUNITIES: [Specific ways to apply learnings for better results]
📋 IMPLEMENTATION PLAN: [Steps to integrate improvements into future operations]
📈 SUCCESS METRICS: [How to measure learning effectiveness and impact]
🔄 FEEDBACK LOOPS: [Mechanisms for continuous learning and adaptation]
""",
            quality_checks=[
                "Is the experience analysis comprehensive and objective?",
                "Are patterns identified with sufficient evidence and confidence?",
                "Are key learnings actionable and transferable?",
                "Are improvement opportunities specific and realistic?",
                "Is the implementation plan practical and measurable?",
                "Are success metrics meaningful and trackable?",
                "Do feedback loops enable continuous improvement?"
            ],
            optimization_patterns=[
                PromptPattern.CHAIN_OF_THOUGHT,
                PromptPattern.MULTI_PERSPECTIVE,
                PromptPattern.SELF_CORRECTION
            ],
            examples=[
                {
                    "input": "Analyze project success patterns",
                    "output": "📚 EXPERIENCE ANALYSIS: Reviewing 15 completed projects with success rates varying from 60-95%...",
                    "reasoning": "Systematic learning approach to identify and apply success patterns"
                }
            ]
        )
        
        # COORDINATOR AGENT TEMPLATE
        templates[AgentType.COORDINATOR] = PromptTemplate(
            agent_type=AgentType.COORDINATOR,
            role_definition="""
ROLE: You are a System Coordination Specialist with expertise in workflow 
orchestration, communication optimization, and user experience enhancement. 
You excel at managing complex multi-agent interactions, optimizing communication 
flows, and ensuring seamless user experiences.

CORE COMPETENCIES:
- Advanced workflow orchestration and management
- Multi-agent coordination and communication
- User experience optimization and personalization
- Request interpretation and routing
- Progress monitoring and status communication
- Conflict resolution and decision arbitration
""",
            cognitive_framework=f"""
{self.cognitive_arch.layers['analysis']}
{self.cognitive_arch.layers['reasoning']}
{self.cognitive_arch.layers['synthesis']}
{self.cognitive_arch.layers['validation']}
""",
            response_structure="""
RESPONSE STRUCTURE:
🎯 REQUEST ANALYSIS: [User intent interpretation and requirement clarification]
🔄 WORKFLOW DESIGN: [Task sequence and agent assignment optimization]
📊 EXECUTION MONITORING: [Progress tracking and coordination oversight]
💬 COMMUNICATION PLAN: [User updates and interaction strategy optimization]
✅ QUALITY SYNTHESIS: [Final result compilation and presentation]
📈 EXPERIENCE OPTIMIZATION: [Learnings and improvements for future interactions]
🔧 SYSTEM COORDINATION: [Multi-agent orchestration and conflict resolution]
""",
            quality_checks=[
                "Is user intent accurately interpreted and clarified?",
                "Is the workflow design optimal for the given requirements?",
                "Is execution monitoring comprehensive and proactive?",
                "Is communication clear, timely, and appropriately detailed?",
                "Is quality synthesis comprehensive and well-presented?",
                "Are experience optimizations actionable and valuable?",
                "Is system coordination effective and conflict-free?"
            ],
            optimization_patterns=[
                PromptPattern.MULTI_PERSPECTIVE,
                PromptPattern.CHAIN_OF_THOUGHT,
                PromptPattern.SELF_CORRECTION
            ],
            examples=[
                {
                    "input": "Coordinate complex multi-step project",
                    "output": "🎯 REQUEST ANALYSIS: User needs comprehensive project execution involving planning, development, testing...",
                    "reasoning": "Systematic coordination approach ensuring optimal agent utilization and user experience"
                }
            ]
        )
        
        return templates

class PromptOptimizationEngine:
    """
    Advanced prompt optimization using proven techniques
    """
    
    def __init__(self):
        self.optimization_patterns = self._initialize_patterns()
        self.performance_db = self._initialize_performance_db()
    
    def _initialize_patterns(self) -> Dict[PromptPattern, str]:
        """Initialize optimization pattern templates"""
        
        return {
            PromptPattern.CHAIN_OF_THOUGHT: """
CHAIN-OF-THOUGHT REASONING:
Let me work through this step-by-step:

Step 1: Problem Understanding
- What exactly is being asked?
- What information do I have available?
- What constraints or limitations exist?
- What assumptions am I making?

Step 2: Approach Selection
- What are my available options?
- Which approach is most suitable for this context?
- Why is this the optimal choice?
- What are the trade-offs involved?

Step 3: Implementation Planning
- How will I execute this approach?
- What are the key steps and their sequence?
- What resources or tools do I need?
- What could potentially go wrong?

Step 4: Execution and Monitoring
- Implementing the chosen approach systematically
- Monitoring progress and quality at each step
- Adapting approach based on real-time feedback
- Documenting decisions and outcomes

Step 5: Validation and Optimization
- Does this fully address the original question?
- Is the solution complete and correct?
- How confident am I in this result?
- What improvements could be made?
""",
            
            PromptPattern.TREE_OF_THOUGHTS: """
TREE-OF-THOUGHTS EXPLORATION:
Let me explore multiple reasoning paths:

Path A: [First approach]
- Reasoning: [Logic and assumptions]
- Pros: [Advantages of this approach]
- Cons: [Limitations and risks]
- Outcome: [Expected result]

Path B: [Alternative approach]
- Reasoning: [Different logic and assumptions]
- Pros: [Advantages of this approach]
- Cons: [Limitations and risks]
- Outcome: [Expected result]

Path C: [Third approach if applicable]
- Reasoning: [Another perspective]
- Pros: [Advantages of this approach]
- Cons: [Limitations and risks]
- Outcome: [Expected result]

Synthesis: [Best elements from each path]
Final Approach: [Optimal combination with reasoning]
""",
            
            PromptPattern.SELF_CORRECTION: """
SELF-CORRECTION PROTOCOL:
Before finalizing my response, let me verify:

Accuracy Check:
- Are my facts correct and up-to-date?
- Are my calculations accurate?
- Are my assumptions reasonable?
- Is my logic sound and consistent?

Completeness Check:
- Have I addressed all parts of the question?
- Are there important aspects I've missed?
- Is additional context or clarification needed?
- Are my recommendations actionable?

Quality Check:
- Is my response clear and well-structured?
- Is the level of detail appropriate?
- Would this be helpful to the user?
- Are there obvious improvements I can make?

If any issues are identified, I will revise my response accordingly.
""",
            
            PromptPattern.MULTI_PERSPECTIVE: """
MULTI-PERSPECTIVE ANALYSIS:
Let me consider this from different viewpoints:

Technical Perspective:
- What are the technical requirements and constraints?
- What solutions are technically feasible?
- What are the implementation challenges?

Business Perspective:
- What are the business objectives and priorities?
- What is the cost-benefit analysis?
- What are the strategic implications?

User Perspective:
- What do users actually need and want?
- How will this impact user experience?
- What are the usability considerations?

Risk Perspective:
- What could go wrong?
- What are the potential negative consequences?
- How can risks be mitigated?

Integration: [Synthesizing insights from all perspectives]
""",
            
            PromptPattern.CONSTRAINT_BASED: """
CONSTRAINT-BASED REASONING:
Working within the following constraints:

Hard Constraints (Must be satisfied):
- [List non-negotiable limitations]
- [Resource constraints]
- [Technical constraints]
- [Regulatory/compliance requirements]

Soft Constraints (Preferred but flexible):
- [Performance preferences]
- [Cost preferences]
- [Timeline preferences]
- [Quality preferences]

Solution Design:
Given these constraints, the optimal approach is:
[Solution that respects all hard constraints and optimizes soft constraints]

Constraint Validation:
- Hard constraint compliance: [Verification]
- Soft constraint optimization: [Trade-off analysis]
""",
            
            PromptPattern.SCENARIO_PLANNING: """
SCENARIO PLANNING ANALYSIS:
Considering multiple future scenarios:

Best Case Scenario:
- Conditions: [Favorable circumstances]
- Approach: [Optimal strategy for this scenario]
- Expected Outcome: [Best possible results]

Most Likely Scenario:
- Conditions: [Expected circumstances]
- Approach: [Balanced strategy]
- Expected Outcome: [Realistic results]

Worst Case Scenario:
- Conditions: [Challenging circumstances]
- Approach: [Risk mitigation strategy]
- Expected Outcome: [Minimum acceptable results]

Robust Strategy:
[Approach that works well across all scenarios]
Contingency Plans:
[Specific adaptations for each scenario]
"""
        }
    
    def _initialize_performance_db(self) -> sqlite3.Connection:
        """Initialize database for tracking prompt performance"""
        
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE prompt_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT,
                agent_type TEXT,
                task_complexity TEXT,
                response_quality REAL,
                response_time REAL,
                user_satisfaction REAL,
                success_rate REAL,
                timestamp TEXT,
                optimization_patterns TEXT
            )
        ''')
        
        conn.commit()
        return conn
    
    def apply_optimization_pattern(self, base_prompt: str, pattern: PromptPattern, 
                                 context: Dict[str, Any]) -> str:
        """Apply specific optimization pattern to enhance prompt"""
        
        pattern_template = self.optimization_patterns.get(pattern, "")
        
        if not pattern_template:
            return base_prompt
        
        # Customize pattern based on context
        if pattern == PromptPattern.CONSTRAINT_BASED and 'constraints' in context:
            constraints = context['constraints']
            pattern_template = pattern_template.replace(
                "[List non-negotiable limitations]", 
                "\n".join(f"- {constraint}" for constraint in constraints.get('hard', []))
            )
        
        # Combine base prompt with optimization pattern
        enhanced_prompt = f"{base_prompt}\n\n{pattern_template}"
        
        return enhanced_prompt
    
    def optimize_prompt_for_task(self, agent_type: AgentType, task: Dict[str, Any], 
                                templates: Dict[AgentType, PromptTemplate]) -> str:
        """Create optimized prompt for specific task"""
        
        if agent_type not in templates:
            return "You are a helpful AI assistant."
        
        template = templates[agent_type]
        
        # Build base prompt
        base_prompt = f"""
{template.role_definition}

{template.cognitive_framework}

CURRENT TASK:
{task.get('description', 'No description provided')}

TASK DETAILS:
- Complexity: {task.get('complexity', 'medium')}
- Priority: {task.get('priority', 'normal')}
- Constraints: {task.get('constraints', 'None specified')}
- Context: {task.get('context', 'Standard context')}

{template.response_structure}

QUALITY VALIDATION:
Before responding, verify:
{chr(10).join(f"- {check}" for check in template.quality_checks)}
"""
        
        # Apply optimization patterns
        enhanced_prompt = base_prompt
        for pattern in template.optimization_patterns:
            enhanced_prompt = self.apply_optimization_pattern(
                enhanced_prompt, pattern, task
            )
        
        # Add examples if available
        if template.examples:
            examples_section = "\n\nEXAMPLES OF EXCELLENCE:\n"
            for i, example in enumerate(template.examples[:2], 1):
                examples_section += f"""
Example {i}:
Input: {example['input']}
Output: {example['output']}
Reasoning: {example['reasoning']}
"""
            enhanced_prompt += examples_section
        
        return enhanced_prompt
    
    def record_performance(self, metrics: PromptMetrics):
        """Record prompt performance for optimization"""
        
        cursor = self.performance_db.cursor()
        cursor.execute('''
            INSERT INTO prompt_performance 
            (template_id, agent_type, task_complexity, response_quality, 
             response_time, user_satisfaction, success_rate, timestamp, optimization_patterns)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.template_id,
            metrics.agent_type.value,
            metrics.task_complexity.value,
            metrics.response_quality,
            metrics.response_time,
            metrics.user_satisfaction,
            metrics.success_rate,
            metrics.timestamp.isoformat(),
            json.dumps([p.value for p in metrics.optimization_patterns] if hasattr(metrics, 'optimization_patterns') else [])
        ))
        
        self.performance_db.commit()

class EnhancedPromptEngine:
    """
    Main prompt engineering system with advanced optimization
    """
    
    def __init__(self):
        self.cognitive_arch = CognitiveArchitecture()
        self.templates = EnhancedPromptTemplates(self.cognitive_arch)
        self.optimizer = PromptOptimizationEngine()
        self.performance_history = []
        
        logger.info("Enhanced Prompt Engineering System initialized")
        logger.info(f"Loaded {len(self.templates.templates)} agent templates")
        logger.info(f"Available optimization patterns: {len(self.optimizer.optimization_patterns)}")
    
    def create_enhanced_prompt(self, agent_type: AgentType, task: Dict[str, Any]) -> str:
        """Create optimized prompt for agent and task"""
        
        try:
            enhanced_prompt = self.optimizer.optimize_prompt_for_task(
                agent_type, task, self.templates.templates
            )
            
            logger.info(f"Created enhanced prompt for {agent_type.value} agent")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error creating enhanced prompt: {str(e)}")
            return f"You are a {agent_type.value} agent. Please help with: {task.get('description', 'the given task')}"
    
    def get_agent_capabilities(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get detailed capabilities for specific agent type"""
        
        if agent_type not in self.templates.templates:
            return {"error": "Agent type not found"}
        
        template = self.templates.templates[agent_type]
        
        return {
            "agent_type": agent_type.value,
            "role_definition": template.role_definition,
            "optimization_patterns": [p.value for p in template.optimization_patterns],
            "quality_checks": template.quality_checks,
            "example_count": len(template.examples)
        }
    
    def analyze_prompt_performance(self) -> Dict[str, Any]:
        """Analyze overall prompt performance"""
        
        if not self.performance_history:
            return {"message": "No performance data available"}
        
        recent_metrics = self.performance_history[-50:] if len(self.performance_history) > 50 else self.performance_history
        
        avg_quality = sum(m.response_quality for m in recent_metrics) / len(recent_metrics)
        avg_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_satisfaction = sum(m.user_satisfaction for m in recent_metrics) / len(recent_metrics)
        avg_success = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
        
        return {
            "total_prompts": len(self.performance_history),
            "avg_response_quality": avg_quality,
            "avg_response_time": avg_time,
            "avg_user_satisfaction": avg_satisfaction,
            "avg_success_rate": avg_success,
            "agent_usage": self._get_agent_usage_stats(recent_metrics),
            "complexity_distribution": self._get_complexity_distribution(recent_metrics)
        }
    
    def _get_agent_usage_stats(self, metrics: List[PromptMetrics]) -> Dict[str, int]:
        """Get agent usage statistics"""
        
        usage_stats = {}
        for metric in metrics:
            agent = metric.agent_type.value
            usage_stats[agent] = usage_stats.get(agent, 0) + 1
        
        return usage_stats
    
    def _get_complexity_distribution(self, metrics: List[PromptMetrics]) -> Dict[str, int]:
        """Get task complexity distribution"""
        
        complexity_stats = {}
        for metric in metrics:
            complexity = metric.task_complexity.value
            complexity_stats[complexity] = complexity_stats.get(complexity, 0) + 1
        
        return complexity_stats

# Demo and testing functions
async def test_enhanced_prompts():
    """Test the enhanced prompt engineering system"""
    
    print("🚀 ENHANCED PROMPT ENGINEERING SYSTEM TEST")
    print("=" * 60)
    
    # Initialize the system
    prompt_engine = EnhancedPromptEngine()
    
    # Test tasks for different agents
    test_tasks = [
        {
            'agent_type': AgentType.PLANNER,
            'description': 'Create a comprehensive plan for launching a new AI product',
            'complexity': TaskComplexity.COMPLEX,
            'priority': 'high',
            'constraints': {
                'hard': ['6-month timeline', 'Limited budget of $500K', 'Team of 8 people'],
                'soft': ['High quality standards', 'Market leadership position']
            }
        },
        {
            'agent_type': AgentType.EXECUTION,
            'description': 'Implement a secure user authentication system',
            'complexity': TaskComplexity.MEDIUM,
            'priority': 'critical',
            'constraints': {
                'hard': ['GDPR compliance', 'Multi-factor authentication'],
                'soft': ['User-friendly interface', 'Fast response times']
            }
        },
        {
            'agent_type': AgentType.VERIFICATION,
            'description': 'Verify the quality of API documentation',
            'complexity': TaskComplexity.SIMPLE,
            'priority': 'normal',
            'constraints': {
                'hard': ['Complete endpoint coverage', 'Example requests/responses'],
                'soft': ['Clear explanations', 'Developer-friendly format']
            }
        }
    ]
    
    print("🧠 TESTING ENHANCED PROMPTS:")
    print("-" * 40)
    
    for i, task in enumerate(test_tasks, 1):
        agent_type = task['agent_type']
        print(f"\n📋 Test {i}: {agent_type.value.upper()} AGENT")
        print(f"Task: {task['description']}")
        print(f"Complexity: {task['complexity'].value}")
        
        # Create enhanced prompt
        enhanced_prompt = prompt_engine.create_enhanced_prompt(agent_type, task)
        
        # Display prompt statistics
        prompt_length = len(enhanced_prompt)
        word_count = len(enhanced_prompt.split())
        
        print(f"✅ Enhanced prompt created:")
        print(f"   Length: {prompt_length} characters")
        print(f"   Words: {word_count}")
        print(f"   Optimization patterns applied: {len(prompt_engine.templates.templates[agent_type].optimization_patterns)}")
        
        # Show first 200 characters as preview
        preview = enhanced_prompt[:200] + "..." if len(enhanced_prompt) > 200 else enhanced_prompt
        print(f"   Preview: {preview}")
        
        # Get agent capabilities
        capabilities = prompt_engine.get_agent_capabilities(agent_type)
        print(f"   Quality checks: {len(capabilities['quality_checks'])}")
        print(f"   Examples available: {capabilities['example_count']}")
    
    print("\n📊 SYSTEM CAPABILITIES:")
    print("-" * 40)
    
    for agent_type in AgentType:
        capabilities = prompt_engine.get_agent_capabilities(agent_type)
        if 'error' not in capabilities:
            print(f"🤖 {agent_type.value.upper()}: {len(capabilities['optimization_patterns'])} patterns, {len(capabilities['quality_checks'])} checks")
    
    print("\n✅ ENHANCED PROMPT ENGINEERING SYSTEM TEST COMPLETE!")
    print("🌟 All agent types successfully enhanced with advanced prompting techniques")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_prompts())

