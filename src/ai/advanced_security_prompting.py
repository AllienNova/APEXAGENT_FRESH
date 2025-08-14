"""
Sophisticated AI Prompting and Reasoning Engine for Cybersecurity
Advanced AI capabilities with specialized cybersecurity knowledge and reasoning
"""

import json
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    THREAT_ANALYSIS = "threat_analysis"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    INCIDENT_RESPONSE = "incident_response"
    FORENSIC_ANALYSIS = "forensic_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_AUDIT = "compliance_audit"

class PromptTemplate(Enum):
    SECURITY_ANALYST = "security_analyst"
    PENETRATION_TESTER = "penetration_tester"
    INCIDENT_RESPONDER = "incident_responder"
    FORENSIC_INVESTIGATOR = "forensic_investigator"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    THREAT_HUNTER = "threat_hunter"

@dataclass
class SecurityContext:
    """Security context for AI reasoning"""
    organization_type: str
    industry: str
    compliance_requirements: List[str]
    threat_landscape: List[str]
    security_maturity: str
    risk_tolerance: str

@dataclass
class AnalysisRequest:
    """Request for AI security analysis"""
    request_id: str
    reasoning_type: ReasoningType
    context: SecurityContext
    data: Dict[str, Any]
    priority: str
    timestamp: datetime

class AdvancedSecurityPrompting:
    """
    Sophisticated AI prompting system for cybersecurity operations
    """
    
    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()
        self.reasoning_chains = self._initialize_reasoning_chains()
        self.security_knowledge_base = self._initialize_security_knowledge()
        self.analysis_history = []
        
    def _initialize_prompt_templates(self) -> Dict[str, Dict]:
        """Initialize specialized cybersecurity prompt templates"""
        return {
            PromptTemplate.SECURITY_ANALYST.value: {
                "system_prompt": """You are an expert cybersecurity analyst with 15+ years of experience in threat detection, vulnerability assessment, and security architecture. You have deep knowledge of:

- Advanced Persistent Threats (APTs) and their tactics, techniques, and procedures (TTPs)
- MITRE ATT&CK framework and threat modeling
- Vulnerability assessment methodologies (OWASP, NIST, SANS)
- Security frameworks (ISO 27001, NIST CSF, CIS Controls)
- Incident response and forensic analysis
- Risk assessment and management
- Compliance requirements (SOX, HIPAA, PCI-DSS, GDPR)

Your analysis should be:
1. Technically accurate and detailed
2. Risk-focused with clear impact assessment
3. Actionable with specific remediation steps
4. Compliant with industry standards
5. Contextual to the organization's threat landscape

Always provide confidence levels for your assessments and explain your reasoning process.""",
                
                "analysis_prompt": """Analyze the following security data and provide a comprehensive assessment:

CONTEXT:
- Organization Type: {org_type}
- Industry: {industry}
- Compliance Requirements: {compliance}
- Current Threat Landscape: {threats}
- Security Maturity Level: {maturity}

DATA TO ANALYZE:
{analysis_data}

Please provide:
1. Executive Summary (2-3 sentences)
2. Detailed Technical Analysis
3. Risk Assessment (with CVSS scores where applicable)
4. Threat Actor Attribution (if applicable)
5. Impact Analysis
6. Recommended Actions (prioritized)
7. Compliance Implications
8. Confidence Level (1-10) with justification

Format your response in structured sections with clear headings.""",
                
                "follow_up_prompts": [
                    "What additional data would strengthen this analysis?",
                    "How does this finding relate to current threat intelligence?",
                    "What are the potential attack vectors we should monitor?",
                    "How can we improve our detection capabilities for similar threats?"
                ]
            },
            
            PromptTemplate.PENETRATION_TESTER.value: {
                "system_prompt": """You are an expert penetration tester and ethical hacker with extensive experience in:

- Network penetration testing and vulnerability exploitation
- Web application security testing (OWASP Top 10)
- Wireless security assessment
- Social engineering and physical security testing
- Red team operations and adversary simulation
- Security tool development and automation
- Exploit development and reverse engineering
- Post-exploitation techniques and lateral movement

Your approach should be:
1. Methodical and systematic
2. Risk-aware and responsible
3. Comprehensive in scope
4. Detailed in documentation
5. Focused on business impact

Always consider legal and ethical implications, and provide clear remediation guidance.""",
                
                "analysis_prompt": """Conduct a penetration testing analysis of the following target:

TARGET INFORMATION:
- Scope: {scope}
- Authorized Testing Methods: {methods}
- Business Context: {business_context}
- Compliance Requirements: {compliance}

RECONNAISSANCE DATA:
{recon_data}

Please provide:
1. Attack Surface Analysis
2. Vulnerability Prioritization (with exploitability assessment)
3. Potential Attack Chains
4. Exploitation Scenarios
5. Post-Exploitation Possibilities
6. Business Risk Assessment
7. Remediation Recommendations (with timelines)
8. Testing Methodology Used

Include specific commands, tools, and techniques where appropriate.""",
                
                "follow_up_prompts": [
                    "What additional reconnaissance would improve attack success probability?",
                    "How can we chain these vulnerabilities for maximum impact?",
                    "What defensive measures would be most effective against these attacks?",
                    "How can we automate detection of similar vulnerabilities?"
                ]
            },
            
            PromptTemplate.INCIDENT_RESPONDER.value: {
                "system_prompt": """You are an expert incident response specialist with deep experience in:

- Incident detection, analysis, and containment
- Digital forensics and evidence preservation
- Malware analysis and reverse engineering
- Threat hunting and IOC development
- Crisis management and communication
- Legal and regulatory compliance during incidents
- Recovery planning and business continuity
- Lessons learned and process improvement

Your response should be:
1. Rapid and decisive
2. Evidence-based and forensically sound
3. Compliant with legal requirements
4. Focused on containment and recovery
5. Comprehensive in documentation

Always consider the incident lifecycle: Preparation, Detection, Analysis, Containment, Eradication, Recovery, Lessons Learned.""",
                
                "analysis_prompt": """Analyze the following security incident and provide immediate response guidance:

INCIDENT DETAILS:
- Incident Type: {incident_type}
- Discovery Time: {discovery_time}
- Affected Systems: {affected_systems}
- Business Impact: {business_impact}
- Regulatory Requirements: {regulatory}

EVIDENCE COLLECTED:
{evidence_data}

Please provide:
1. Incident Classification and Severity
2. Immediate Containment Actions
3. Evidence Preservation Requirements
4. Investigation Plan
5. Communication Strategy
6. Recovery Procedures
7. Legal/Regulatory Considerations
8. Lessons Learned Recommendations

Prioritize actions by urgency and impact.""",
                
                "follow_up_prompts": [
                    "What additional evidence should we collect?",
                    "How can we prevent similar incidents in the future?",
                    "What are the legal notification requirements?",
                    "How can we improve our incident response process?"
                ]
            },
            
            PromptTemplate.THREAT_HUNTER.value: {
                "system_prompt": """You are an expert threat hunter with advanced skills in:

- Proactive threat detection and hunting methodologies
- Behavioral analysis and anomaly detection
- Threat intelligence analysis and application
- Advanced persistent threat (APT) identification
- SIEM/SOAR platform optimization
- Custom detection rule development
- Threat landscape analysis
- Attribution and campaign tracking

Your hunting approach should be:
1. Hypothesis-driven and systematic
2. Data-driven with statistical analysis
3. Intelligence-informed
4. Iterative and adaptive
5. Focused on unknown threats

Always consider the threat hunting cycle: Hypothesis, Investigation, Discovery, Response.""",
                
                "analysis_prompt": """Conduct threat hunting analysis based on the following intelligence:

HUNTING CONTEXT:
- Environment: {environment}
- Threat Intelligence: {threat_intel}
- Available Data Sources: {data_sources}
- Hunting Hypothesis: {hypothesis}
- Time Range: {time_range}

ANALYSIS DATA:
{hunting_data}

Please provide:
1. Threat Hunting Assessment
2. Behavioral Analysis
3. Anomaly Identification
4. IOC Development
5. Attribution Analysis
6. Campaign Tracking
7. Detection Rule Recommendations
8. Further Hunting Opportunities

Include specific queries, signatures, and hunting techniques.""",
                
                "follow_up_prompts": [
                    "What additional data sources would enhance this hunt?",
                    "How can we develop better detection capabilities?",
                    "What are the indicators of compromise we should monitor?",
                    "How does this relate to known threat actor TTPs?"
                ]
            }
        }
    
    def _initialize_reasoning_chains(self) -> Dict[str, List[str]]:
        """Initialize reasoning chains for different security scenarios"""
        return {
            ReasoningType.THREAT_ANALYSIS.value: [
                "Identify threat indicators and patterns",
                "Correlate with known threat intelligence",
                "Assess threat actor capabilities and motivations",
                "Evaluate potential impact and likelihood",
                "Determine attribution confidence level",
                "Recommend defensive measures"
            ],
            
            ReasoningType.VULNERABILITY_ASSESSMENT.value: [
                "Catalog identified vulnerabilities",
                "Assess exploitability and impact",
                "Prioritize based on risk factors",
                "Consider environmental context",
                "Evaluate existing controls",
                "Recommend remediation strategy"
            ],
            
            ReasoningType.INCIDENT_RESPONSE.value: [
                "Classify incident type and severity",
                "Assess immediate containment needs",
                "Identify evidence preservation requirements",
                "Evaluate business impact",
                "Determine investigation scope",
                "Plan recovery procedures"
            ],
            
            ReasoningType.FORENSIC_ANALYSIS.value: [
                "Preserve evidence integrity",
                "Reconstruct attack timeline",
                "Identify attack vectors and methods",
                "Analyze malware and tools used",
                "Determine scope of compromise",
                "Document findings for legal proceedings"
            ],
            
            ReasoningType.RISK_ASSESSMENT.value: [
                "Identify assets and their value",
                "Catalog threats and vulnerabilities",
                "Assess likelihood and impact",
                "Calculate risk scores",
                "Evaluate existing controls",
                "Recommend risk treatment options"
            ]
        }
    
    def _initialize_security_knowledge(self) -> Dict[str, Any]:
        """Initialize cybersecurity knowledge base"""
        return {
            "mitre_attack": {
                "tactics": [
                    "Initial Access", "Execution", "Persistence", "Privilege Escalation",
                    "Defense Evasion", "Credential Access", "Discovery", "Lateral Movement",
                    "Collection", "Command and Control", "Exfiltration", "Impact"
                ],
                "common_techniques": {
                    "T1566": "Phishing",
                    "T1078": "Valid Accounts",
                    "T1055": "Process Injection",
                    "T1003": "OS Credential Dumping",
                    "T1082": "System Information Discovery",
                    "T1021": "Remote Services",
                    "T1041": "Exfiltration Over C2 Channel"
                }
            },
            
            "vulnerability_categories": {
                "web_application": [
                    "SQL Injection", "Cross-Site Scripting (XSS)", "Cross-Site Request Forgery (CSRF)",
                    "Insecure Direct Object References", "Security Misconfiguration",
                    "Sensitive Data Exposure", "Broken Authentication", "XML External Entities (XXE)"
                ],
                "network": [
                    "Unencrypted Communications", "Weak Protocols", "Open Ports",
                    "Default Credentials", "Buffer Overflows", "Denial of Service"
                ],
                "system": [
                    "Privilege Escalation", "Code Injection", "Memory Corruption",
                    "Race Conditions", "Information Disclosure"
                ]
            },
            
            "threat_actors": {
                "apt_groups": {
                    "APT1": {"origin": "China", "targets": "Intellectual Property", "ttps": ["Spear Phishing", "RATs"]},
                    "APT28": {"origin": "Russia", "targets": "Government, Military", "ttps": ["Zero-days", "Living off the Land"]},
                    "APT29": {"origin": "Russia", "targets": "Government, Healthcare", "ttps": ["Supply Chain", "Cloud Exploitation"]},
                    "Lazarus": {"origin": "North Korea", "targets": "Financial, Cryptocurrency", "ttps": ["Destructive Malware", "Financial Theft"]}
                },
                "cybercriminal_groups": {
                    "Conti": {"type": "Ransomware", "targets": "Healthcare, Government", "ttps": ["Double Extortion", "RaaS"]},
                    "REvil": {"type": "Ransomware", "targets": "MSPs, Supply Chain", "ttps": ["Zero-day Exploitation", "Big Game Hunting"]}
                }
            },
            
            "compliance_frameworks": {
                "NIST_CSF": {
                    "functions": ["Identify", "Protect", "Detect", "Respond", "Recover"],
                    "categories": ["Asset Management", "Access Control", "Awareness Training", "Data Security"]
                },
                "ISO_27001": {
                    "domains": ["Information Security Policies", "Organization of Information Security",
                              "Human Resource Security", "Asset Management", "Access Control"]
                },
                "CIS_Controls": {
                    "basic": ["Inventory of Hardware", "Inventory of Software", "Continuous Vulnerability Management"],
                    "foundational": ["Controlled Use of Administrative Privileges", "Secure Configuration"],
                    "organizational": ["Security Awareness Training", "Incident Response Management"]
                }
            }
        }
    
    async def analyze_security_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Perform sophisticated AI analysis of security data
        """
        logger.info(f"Starting security analysis for request {request.request_id}")
        
        # Select appropriate prompt template
        template = self._select_prompt_template(request.reasoning_type)
        
        # Build context-aware prompt
        prompt = self._build_contextual_prompt(template, request)
        
        # Execute reasoning chain
        reasoning_steps = await self._execute_reasoning_chain(request.reasoning_type, request.data)
        
        # Generate AI analysis
        analysis_result = await self._generate_ai_analysis(prompt, reasoning_steps, request)
        
        # Post-process and validate results
        validated_result = self._validate_and_enhance_analysis(analysis_result, request)
        
        # Store analysis history
        self.analysis_history.append({
            "request_id": request.request_id,
            "timestamp": request.timestamp,
            "reasoning_type": request.reasoning_type.value,
            "result": validated_result
        })
        
        return validated_result
    
    def _select_prompt_template(self, reasoning_type: ReasoningType) -> Dict[str, Any]:
        """Select appropriate prompt template based on reasoning type"""
        template_mapping = {
            ReasoningType.THREAT_ANALYSIS: PromptTemplate.SECURITY_ANALYST,
            ReasoningType.VULNERABILITY_ASSESSMENT: PromptTemplate.PENETRATION_TESTER,
            ReasoningType.INCIDENT_RESPONSE: PromptTemplate.INCIDENT_RESPONDER,
            ReasoningType.FORENSIC_ANALYSIS: PromptTemplate.FORENSIC_INVESTIGATOR,
            ReasoningType.RISK_ASSESSMENT: PromptTemplate.SECURITY_ANALYST
        }
        
        selected_template = template_mapping.get(reasoning_type, PromptTemplate.SECURITY_ANALYST)
        return self.prompt_templates[selected_template.value]
    
    def _build_contextual_prompt(self, template: Dict[str, Any], request: AnalysisRequest) -> str:
        """Build context-aware prompt for AI analysis"""
        context = request.context
        
        # Format the analysis prompt with context
        formatted_prompt = template["analysis_prompt"].format(
            org_type=context.organization_type,
            industry=context.industry,
            compliance=", ".join(context.compliance_requirements),
            threats=", ".join(context.threat_landscape),
            maturity=context.security_maturity,
            analysis_data=json.dumps(request.data, indent=2)
        )
        
        # Combine system prompt with analysis prompt
        full_prompt = f"{template['system_prompt']}\n\n{formatted_prompt}"
        
        return full_prompt
    
    async def _execute_reasoning_chain(self, reasoning_type: ReasoningType, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute reasoning chain for systematic analysis"""
        reasoning_steps = self.reasoning_chains[reasoning_type.value]
        executed_steps = []
        
        for step in reasoning_steps:
            step_result = await self._execute_reasoning_step(step, data)
            executed_steps.append({
                "step": step,
                "result": step_result,
                "confidence": self._calculate_step_confidence(step_result)
            })
        
        return executed_steps
    
    async def _execute_reasoning_step(self, step: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual reasoning step"""
        # This would integrate with actual AI models
        # For now, we'll simulate reasoning based on the step type
        
        if "threat" in step.lower():
            return self._analyze_threat_indicators(data)
        elif "vulnerability" in step.lower():
            return self._analyze_vulnerabilities(data)
        elif "impact" in step.lower():
            return self._assess_impact(data)
        elif "attribution" in step.lower():
            return self._analyze_attribution(data)
        else:
            return {"analysis": f"Completed reasoning step: {step}", "findings": []}
    
    def _analyze_threat_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze threat indicators in the data"""
        indicators = {
            "iocs": [],
            "ttps": [],
            "threat_level": "medium",
            "confidence": 0.7
        }
        
        # Extract potential IOCs
        if "ip_addresses" in data:
            indicators["iocs"].extend([{"type": "ip", "value": ip} for ip in data["ip_addresses"]])
        
        if "domains" in data:
            indicators["iocs"].extend([{"type": "domain", "value": domain} for domain in data["domains"]])
        
        if "file_hashes" in data:
            indicators["iocs"].extend([{"type": "hash", "value": hash_val} for hash_val in data["file_hashes"]])
        
        # Analyze TTPs based on observed behavior
        if "network_connections" in data:
            indicators["ttps"].append("T1041 - Exfiltration Over C2 Channel")
        
        if "privilege_escalation" in data:
            indicators["ttps"].append("T1068 - Exploitation for Privilege Escalation")
        
        return indicators
    
    def _analyze_vulnerabilities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze vulnerabilities in the data"""
        vuln_analysis = {
            "vulnerabilities": [],
            "risk_score": 0,
            "exploitability": "medium",
            "remediation_priority": "medium"
        }
        
        # Analyze different vulnerability types
        if "web_vulnerabilities" in data:
            for vuln in data["web_vulnerabilities"]:
                vuln_analysis["vulnerabilities"].append({
                    "type": vuln.get("type", "Unknown"),
                    "severity": vuln.get("severity", "medium"),
                    "cvss_score": self._calculate_cvss_score(vuln),
                    "exploitability": self._assess_exploitability(vuln)
                })
        
        if "network_vulnerabilities" in data:
            for vuln in data["network_vulnerabilities"]:
                vuln_analysis["vulnerabilities"].append({
                    "type": vuln.get("type", "Unknown"),
                    "severity": vuln.get("severity", "medium"),
                    "cvss_score": self._calculate_cvss_score(vuln),
                    "exploitability": self._assess_exploitability(vuln)
                })
        
        # Calculate overall risk score
        vuln_analysis["risk_score"] = sum(v.get("cvss_score", 5) for v in vuln_analysis["vulnerabilities"])
        
        return vuln_analysis
    
    def _assess_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential impact of security findings"""
        impact_analysis = {
            "business_impact": "medium",
            "affected_systems": [],
            "data_at_risk": [],
            "financial_impact": "medium",
            "regulatory_impact": "low"
        }
        
        # Analyze affected systems
        if "affected_systems" in data:
            impact_analysis["affected_systems"] = data["affected_systems"]
            
            # Assess criticality based on system types
            critical_systems = ["domain_controller", "database", "payment_system"]
            if any(sys in str(data["affected_systems"]).lower() for sys in critical_systems):
                impact_analysis["business_impact"] = "high"
                impact_analysis["financial_impact"] = "high"
        
        # Assess data at risk
        if "data_types" in data:
            sensitive_data = ["pii", "phi", "financial", "intellectual_property"]
            if any(dt in str(data["data_types"]).lower() for dt in sensitive_data):
                impact_analysis["regulatory_impact"] = "high"
        
        return impact_analysis
    
    def _analyze_attribution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze threat actor attribution"""
        attribution = {
            "likely_actors": [],
            "confidence_level": "low",
            "attribution_factors": [],
            "geopolitical_context": ""
        }
        
        # Analyze TTPs for attribution
        if "ttps" in data:
            ttps = data["ttps"]
            
            # Simple attribution logic based on known TTPs
            if "spear_phishing" in str(ttps).lower():
                attribution["likely_actors"].append("APT1")
                attribution["attribution_factors"].append("Spear phishing campaign")
            
            if "supply_chain" in str(ttps).lower():
                attribution["likely_actors"].append("APT29")
                attribution["attribution_factors"].append("Supply chain compromise")
            
            if "ransomware" in str(ttps).lower():
                attribution["likely_actors"].append("Conti")
                attribution["attribution_factors"].append("Ransomware deployment")
        
        # Assess confidence based on number of matching factors
        if len(attribution["attribution_factors"]) >= 3:
            attribution["confidence_level"] = "high"
        elif len(attribution["attribution_factors"]) >= 2:
            attribution["confidence_level"] = "medium"
        
        return attribution
    
    def _calculate_cvss_score(self, vulnerability: Dict[str, Any]) -> float:
        """Calculate CVSS score for vulnerability"""
        # Simplified CVSS calculation
        severity_mapping = {
            "critical": 9.5,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5
        }
        
        severity = vulnerability.get("severity", "medium").lower()
        return severity_mapping.get(severity, 5.0)
    
    def _assess_exploitability(self, vulnerability: Dict[str, Any]) -> str:
        """Assess exploitability of vulnerability"""
        vuln_type = vulnerability.get("type", "").lower()
        
        high_exploitability = ["sql injection", "remote code execution", "buffer overflow"]
        medium_exploitability = ["xss", "csrf", "directory traversal"]
        
        if any(he in vuln_type for he in high_exploitability):
            return "high"
        elif any(me in vuln_type for me in medium_exploitability):
            return "medium"
        else:
            return "low"
    
    def _calculate_step_confidence(self, step_result: Dict[str, Any]) -> float:
        """Calculate confidence level for reasoning step"""
        # Simple confidence calculation based on data quality and completeness
        confidence = 0.5  # Base confidence
        
        if "error" not in step_result:
            confidence += 0.2
        
        if len(step_result.get("findings", [])) > 0:
            confidence += 0.2
        
        if step_result.get("confidence"):
            confidence = (confidence + step_result["confidence"]) / 2
        
        return min(1.0, confidence)
    
    async def _generate_ai_analysis(self, prompt: str, reasoning_steps: List[Dict], request: AnalysisRequest) -> Dict[str, Any]:
        """Generate AI analysis using sophisticated prompting"""
        # This would integrate with actual AI models (GPT-4, Claude, etc.)
        # For now, we'll simulate AI analysis based on the reasoning steps
        
        analysis = {
            "executive_summary": self._generate_executive_summary(reasoning_steps, request),
            "detailed_analysis": self._generate_detailed_analysis(reasoning_steps, request),
            "risk_assessment": self._generate_risk_assessment(reasoning_steps, request),
            "recommendations": self._generate_recommendations(reasoning_steps, request),
            "confidence_score": self._calculate_overall_confidence(reasoning_steps),
            "reasoning_chain": reasoning_steps
        }
        
        return analysis
    
    def _generate_executive_summary(self, reasoning_steps: List[Dict], request: AnalysisRequest) -> str:
        """Generate executive summary of analysis"""
        threat_level = "medium"
        key_findings = []
        
        for step in reasoning_steps:
            if "threat" in step["step"].lower():
                threat_indicators = step["result"].get("iocs", [])
                if len(threat_indicators) > 5:
                    threat_level = "high"
                    key_findings.append(f"Multiple threat indicators detected ({len(threat_indicators)} IOCs)")
            
            if "vulnerability" in step["step"].lower():
                vulnerabilities = step["result"].get("vulnerabilities", [])
                critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
                if critical_vulns:
                    threat_level = "high"
                    key_findings.append(f"Critical vulnerabilities identified ({len(critical_vulns)} critical)")
        
        summary = f"Security analysis reveals {threat_level} risk level for {request.context.organization_type} organization. "
        if key_findings:
            summary += "Key findings include: " + "; ".join(key_findings) + ". "
        summary += "Immediate attention and remediation actions are recommended."
        
        return summary
    
    def _generate_detailed_analysis(self, reasoning_steps: List[Dict], request: AnalysisRequest) -> Dict[str, Any]:
        """Generate detailed technical analysis"""
        detailed_analysis = {
            "threat_landscape": {},
            "vulnerability_assessment": {},
            "attack_vectors": [],
            "impact_analysis": {},
            "technical_details": {}
        }
        
        for step in reasoning_steps:
            step_name = step["step"].lower()
            step_result = step["result"]
            
            if "threat" in step_name:
                detailed_analysis["threat_landscape"] = step_result
            elif "vulnerability" in step_name:
                detailed_analysis["vulnerability_assessment"] = step_result
            elif "impact" in step_name:
                detailed_analysis["impact_analysis"] = step_result
        
        # Generate attack vectors based on findings
        if detailed_analysis["vulnerability_assessment"].get("vulnerabilities"):
            for vuln in detailed_analysis["vulnerability_assessment"]["vulnerabilities"]:
                if vuln.get("exploitability") == "high":
                    detailed_analysis["attack_vectors"].append({
                        "vector": vuln.get("type"),
                        "likelihood": "high",
                        "impact": vuln.get("severity")
                    })
        
        return detailed_analysis
    
    def _generate_risk_assessment(self, reasoning_steps: List[Dict], request: AnalysisRequest) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        risk_assessment = {
            "overall_risk_score": 0,
            "risk_factors": [],
            "likelihood": "medium",
            "impact": "medium",
            "risk_matrix": {},
            "compliance_impact": []
        }
        
        # Calculate risk score from reasoning steps
        total_score = 0
        step_count = 0
        
        for step in reasoning_steps:
            if "risk_score" in step["result"]:
                total_score += step["result"]["risk_score"]
                step_count += 1
        
        if step_count > 0:
            risk_assessment["overall_risk_score"] = total_score / step_count
        
        # Determine risk level
        if risk_assessment["overall_risk_score"] > 7:
            risk_assessment["likelihood"] = "high"
            risk_assessment["impact"] = "high"
        elif risk_assessment["overall_risk_score"] > 4:
            risk_assessment["likelihood"] = "medium"
            risk_assessment["impact"] = "medium"
        
        # Assess compliance impact
        for compliance_req in request.context.compliance_requirements:
            if compliance_req.upper() in ["HIPAA", "PCI-DSS", "GDPR"]:
                risk_assessment["compliance_impact"].append({
                    "framework": compliance_req,
                    "impact_level": "high",
                    "requirements_affected": ["Data Protection", "Access Control", "Incident Response"]
                })
        
        return risk_assessment
    
    def _generate_recommendations(self, reasoning_steps: List[Dict], request: AnalysisRequest) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # Analyze findings to generate specific recommendations
        for step in reasoning_steps:
            step_result = step["result"]
            
            if "vulnerabilities" in step_result:
                for vuln in step_result["vulnerabilities"]:
                    if vuln.get("severity") in ["critical", "high"]:
                        recommendations.append({
                            "priority": "immediate",
                            "category": "vulnerability_management",
                            "title": f"Address {vuln.get('type')} vulnerability",
                            "description": f"Remediate {vuln.get('severity')} severity {vuln.get('type')} vulnerability",
                            "effort": "medium",
                            "timeline": "1-7 days"
                        })
            
            if "iocs" in step_result:
                if len(step_result["iocs"]) > 0:
                    recommendations.append({
                        "priority": "high",
                        "category": "threat_response",
                        "title": "Investigate threat indicators",
                        "description": f"Investigate {len(step_result['iocs'])} identified indicators of compromise",
                        "effort": "high",
                        "timeline": "immediate"
                    })
        
        # Add general security recommendations based on context
        if request.context.security_maturity == "basic":
            recommendations.append({
                "priority": "medium",
                "category": "security_program",
                "title": "Enhance security program maturity",
                "description": "Implement comprehensive security controls and monitoring",
                "effort": "high",
                "timeline": "3-6 months"
            })
        
        # Sort recommendations by priority
        priority_order = {"immediate": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
    
    def _calculate_overall_confidence(self, reasoning_steps: List[Dict]) -> float:
        """Calculate overall confidence in analysis"""
        if not reasoning_steps:
            return 0.0
        
        total_confidence = sum(step["confidence"] for step in reasoning_steps)
        return total_confidence / len(reasoning_steps)
    
    def _validate_and_enhance_analysis(self, analysis: Dict[str, Any], request: AnalysisRequest) -> Dict[str, Any]:
        """Validate and enhance analysis results"""
        # Add metadata
        analysis["metadata"] = {
            "analysis_id": hashlib.md5(f"{request.request_id}{datetime.now()}".encode()).hexdigest(),
            "request_id": request.request_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "reasoning_type": request.reasoning_type.value,
            "context": {
                "organization_type": request.context.organization_type,
                "industry": request.context.industry,
                "security_maturity": request.context.security_maturity
            }
        }
        
        # Validate confidence scores
        if analysis["confidence_score"] < 0.3:
            analysis["warnings"] = ["Low confidence analysis - additional data recommended"]
        
        # Add compliance mapping
        analysis["compliance_mapping"] = self._map_to_compliance_frameworks(analysis, request.context)
        
        # Add MITRE ATT&CK mapping
        analysis["mitre_mapping"] = self._map_to_mitre_attack(analysis)
        
        return analysis
    
    def _map_to_compliance_frameworks(self, analysis: Dict[str, Any], context: SecurityContext) -> Dict[str, List[str]]:
        """Map findings to compliance framework requirements"""
        compliance_mapping = {}
        
        for framework in context.compliance_requirements:
            if framework.upper() == "NIST_CSF":
                compliance_mapping["NIST_CSF"] = ["DE.CM-1", "DE.CM-7", "RS.RP-1", "PR.IP-12"]
            elif framework.upper() == "ISO_27001":
                compliance_mapping["ISO_27001"] = ["A.12.6.1", "A.16.1.1", "A.16.1.2", "A.16.1.5"]
            elif framework.upper() == "PCI_DSS":
                compliance_mapping["PCI_DSS"] = ["Req 6", "Req 10", "Req 11", "Req 12"]
        
        return compliance_mapping
    
    def _map_to_mitre_attack(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Map findings to MITRE ATT&CK framework"""
        mitre_mapping = {
            "tactics": [],
            "techniques": [],
            "procedures": []
        }
        
        # Extract TTPs from analysis
        detailed_analysis = analysis.get("detailed_analysis", {})
        threat_landscape = detailed_analysis.get("threat_landscape", {})
        
        if "ttps" in threat_landscape:
            for ttp in threat_landscape["ttps"]:
                if "T1" in ttp:  # MITRE technique ID
                    technique_id = re.search(r'T\d+', ttp)
                    if technique_id:
                        mitre_mapping["techniques"].append(technique_id.group())
        
        return mitre_mapping

    def generate_security_playbook(self, scenario: str, context: SecurityContext) -> Dict[str, Any]:
        """
        Generate security playbook for specific scenarios
        """
        playbook = {
            "scenario": scenario,
            "context": context,
            "phases": [],
            "roles_responsibilities": {},
            "tools_required": [],
            "success_criteria": [],
            "escalation_procedures": []
        }
        
        if "incident_response" in scenario.lower():
            playbook = self._generate_incident_response_playbook(scenario, context)
        elif "threat_hunting" in scenario.lower():
            playbook = self._generate_threat_hunting_playbook(scenario, context)
        elif "vulnerability_assessment" in scenario.lower():
            playbook = self._generate_vulnerability_assessment_playbook(scenario, context)
        
        return playbook
    
    def _generate_incident_response_playbook(self, scenario: str, context: SecurityContext) -> Dict[str, Any]:
        """Generate incident response playbook"""
        return {
            "scenario": scenario,
            "phases": [
                {
                    "phase": "Preparation",
                    "duration": "Ongoing",
                    "activities": [
                        "Maintain incident response team contact list",
                        "Ensure tools and access are available",
                        "Review and update incident response procedures"
                    ]
                },
                {
                    "phase": "Detection and Analysis",
                    "duration": "1-4 hours",
                    "activities": [
                        "Validate the incident",
                        "Classify incident type and severity",
                        "Collect initial evidence",
                        "Determine scope of impact"
                    ]
                },
                {
                    "phase": "Containment",
                    "duration": "2-8 hours",
                    "activities": [
                        "Implement short-term containment",
                        "Preserve evidence",
                        "Implement long-term containment",
                        "Update stakeholders"
                    ]
                },
                {
                    "phase": "Eradication and Recovery",
                    "duration": "1-7 days",
                    "activities": [
                        "Remove malware and vulnerabilities",
                        "Restore systems from clean backups",
                        "Implement additional monitoring",
                        "Validate system functionality"
                    ]
                },
                {
                    "phase": "Post-Incident Activity",
                    "duration": "1-2 weeks",
                    "activities": [
                        "Document lessons learned",
                        "Update incident response procedures",
                        "Conduct post-incident review",
                        "Implement preventive measures"
                    ]
                }
            ],
            "roles_responsibilities": {
                "Incident Commander": "Overall incident coordination and decision making",
                "Security Analyst": "Technical analysis and evidence collection",
                "IT Operations": "System containment and recovery",
                "Legal Counsel": "Legal and regulatory guidance",
                "Communications": "Internal and external communications"
            },
            "tools_required": [
                "SIEM platform", "Forensic imaging tools", "Network monitoring",
                "Malware analysis sandbox", "Communication platform"
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize AI prompting system
    ai_prompting = AdvancedSecurityPrompting()
    
    # Create sample security context
    context = SecurityContext(
        organization_type="Healthcare Provider",
        industry="Healthcare",
        compliance_requirements=["HIPAA", "NIST_CSF"],
        threat_landscape=["Ransomware", "Data Theft", "Insider Threats"],
        security_maturity="intermediate",
        risk_tolerance="low"
    )
    
    # Create sample analysis request
    request = AnalysisRequest(
        request_id="SEC-2024-001",
        reasoning_type=ReasoningType.THREAT_ANALYSIS,
        context=context,
        data={
            "ip_addresses": ["192.168.1.100", "10.0.0.50"],
            "domains": ["suspicious-domain.com"],
            "network_connections": ["outbound_443", "outbound_80"],
            "file_hashes": ["abc123def456"]
        },
        priority="high",
        timestamp=datetime.now()
    )
    
    # Perform analysis
    import asyncio
    result = asyncio.run(ai_prompting.analyze_security_data(request))
    
    print(f"Analysis completed with confidence: {result['confidence_score']:.2f}")
    print(f"Executive Summary: {result['executive_summary']}")
    print(f"Recommendations: {len(result['recommendations'])} actions identified")
    
    print("Advanced AI prompting and reasoning engine initialized and ready for cybersecurity operations.")

