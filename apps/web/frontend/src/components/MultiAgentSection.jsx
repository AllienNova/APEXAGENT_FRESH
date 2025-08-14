import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, Cog, Shield, CheckCircle, TrendingUp, GraduationCap, Activity, Zap } from 'lucide-react'
import multiAgentDiagram from '../assets/multi-agent-diagram.png'

const MultiAgentSection = () => {
  const [activeAgent, setActiveAgent] = useState(0)
  const [isAnimating, setIsAnimating] = useState(true)

  const agents = [
    {
      id: 0,
      name: "Planner Agent",
      icon: Brain,
      color: "from-cyan-400 to-blue-500",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/30",
      description: "Advanced reasoning and task decomposition",
      capabilities: [
        "Complex problem analysis",
        "Multi-step task planning", 
        "Resource optimization",
        "Strategic decision making"
      ],
      metrics: {
        "Success Rate": "94.7%",
        "Avg Planning Time": "1.2s",
        "Tasks Planned": "2.4M+"
      }
    },
    {
      id: 1,
      name: "Execution Agent", 
      icon: Cog,
      color: "from-purple-400 to-pink-500",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/30",
      description: "100+ tool integrations and task execution",
      capabilities: [
        "Multi-tool orchestration",
        "Real-time execution",
        "Error handling & recovery",
        "Performance monitoring"
      ],
      metrics: {
        "Tools Integrated": "106+",
        "Execution Speed": "0.8s",
        "Success Rate": "96.2%"
      }
    },
    {
      id: 2,
      name: "Verification Agent",
      icon: CheckCircle,
      color: "from-green-400 to-emerald-500", 
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/30",
      description: "Quality control and validation",
      capabilities: [
        "Output verification",
        "Quality assurance",
        "Compliance checking",
        "Result validation"
      ],
      metrics: {
        "Accuracy Rate": "99.1%",
        "Checks Performed": "5.7M+",
        "Issues Detected": "12.3K+"
      }
    },
    {
      id: 3,
      name: "Security Agent",
      icon: Shield,
      color: "from-red-400 to-orange-500",
      bgColor: "bg-red-500/10", 
      borderColor: "border-red-500/30",
      description: "Real-time threat monitoring and compliance",
      capabilities: [
        "Threat detection",
        "Access control",
        "Compliance monitoring",
        "Incident response"
      ],
      metrics: {
        "Threats Blocked": "847K+",
        "Response Time": "0.3s",
        "Compliance Score": "100%"
      }
    },
    {
      id: 4,
      name: "Optimization Agent",
      icon: TrendingUp,
      color: "from-yellow-400 to-orange-500",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/30", 
      description: "Performance tuning and resource management",
      capabilities: [
        "Resource allocation",
        "Performance optimization",
        "Cost management",
        "Scalability planning"
      ],
      metrics: {
        "Cost Savings": "34%",
        "Performance Gain": "67%",
        "Resource Efficiency": "89%"
      }
    },
    {
      id: 5,
      name: "Learning Agent",
      icon: GraduationCap,
      color: "from-indigo-400 to-purple-500",
      bgColor: "bg-indigo-500/10",
      borderColor: "border-indigo-500/30",
      description: "Federated learning and personalization", 
      capabilities: [
        "Continuous learning",
        "Model adaptation",
        "Pattern recognition",
        "Personalization"
      ],
      metrics: {
        "Models Trained": "1.2K+",
        "Accuracy Improvement": "23%",
        "Learning Speed": "4.7x"
      }
    }
  ]

  // Auto-rotate through agents
  useEffect(() => {
    if (!isAnimating) return
    
    const interval = setInterval(() => {
      setActiveAgent((prev) => (prev + 1) % agents.length)
    }, 4000)
    
    return () => clearInterval(interval)
  }, [isAnimating, agents.length])

  const handleAgentClick = (index) => {
    setActiveAgent(index)
    setIsAnimating(false)
    setTimeout(() => setIsAnimating(true), 10000) // Resume auto-rotation after 10s
  }

  return (
    <section className="py-24 bg-gradient-to-b from-slate-900 to-slate-800 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, #3b82f6 0%, transparent 50%), 
                           radial-gradient(circle at 75% 75%, #8b5cf6 0%, transparent 50%)`,
        }} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <Badge className="mb-4 bg-blue-500/20 text-blue-300 border-blue-500/30">
            <Activity className="w-3 h-3 mr-1" />
            Multi-Agent Architecture
          </Badge>
          
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Six Intelligent Agents
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {" "}Working in Perfect Harmony
            </span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
            Our revolutionary multi-agent system orchestrates specialized AI agents that collaborate 
            seamlessly to deliver unprecedented performance, security, and intelligence.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Agent Diagram */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="relative">
              <img 
                src={multiAgentDiagram} 
                alt="Multi-Agent Architecture"
                className="w-full h-auto rounded-2xl"
              />
              
              {/* Interactive Agent Dots */}
              <div className="absolute inset-0">
                {agents.map((agent, index) => {
                  const positions = [
                    { top: '15%', left: '50%' }, // Planner (top)
                    { top: '30%', right: '15%' }, // Execution (top-right)
                    { bottom: '30%', right: '15%' }, // Verification (bottom-right)
                    { bottom: '15%', left: '50%' }, // Security (bottom)
                    { bottom: '30%', left: '15%' }, // Optimization (bottom-left)
                    { top: '30%', left: '15%' }, // Learning (top-left)
                  ]
                  
                  return (
                    <motion.button
                      key={agent.id}
                      className={`absolute w-4 h-4 rounded-full transform -translate-x-1/2 -translate-y-1/2 ${
                        activeAgent === index 
                          ? 'bg-white shadow-lg shadow-white/50 scale-150' 
                          : 'bg-white/60 hover:bg-white/80'
                      } transition-all duration-300`}
                      style={positions[index]}
                      onClick={() => handleAgentClick(index)}
                      whileHover={{ scale: 1.2 }}
                      whileTap={{ scale: 0.9 }}
                    />
                  )
                })}
              </div>
            </div>
          </motion.div>

          {/* Agent Details */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeAgent}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <Card className={`${agents[activeAgent].bgColor} ${agents[activeAgent].borderColor} border backdrop-blur-sm`}>
                  <CardContent className="p-8">
                    <div className="flex items-center mb-6">
                      <div className={`p-3 rounded-xl bg-gradient-to-r ${agents[activeAgent].color} mr-4`}>
                        {React.createElement(agents[activeAgent].icon, {
                          className: "w-8 h-8 text-white"
                        })}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white">{agents[activeAgent].name}</h3>
                        <p className="text-gray-400">{agents[activeAgent].description}</p>
                      </div>
                    </div>

                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-white mb-3">Core Capabilities</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {agents[activeAgent].capabilities.map((capability, index) => (
                          <motion.div
                            key={capability}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="flex items-center text-gray-300"
                          >
                            <Zap className="w-4 h-4 text-blue-400 mr-2 flex-shrink-0" />
                            <span className="text-sm">{capability}</span>
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3">Performance Metrics</h4>
                      <div className="grid grid-cols-3 gap-4">
                        {Object.entries(agents[activeAgent].metrics).map(([key, value], index) => (
                          <motion.div
                            key={key}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="text-center"
                          >
                            <div className="text-2xl font-bold text-white mb-1">{value}</div>
                            <div className="text-xs text-gray-400">{key}</div>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </AnimatePresence>

            {/* Agent Navigation */}
            <div className="flex flex-wrap gap-2">
              {agents.map((agent, index) => (
                <motion.button
                  key={agent.id}
                  onClick={() => handleAgentClick(index)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                    activeAgent === index
                      ? `bg-gradient-to-r ${agent.color} text-white shadow-lg`
                      : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <React.createElement(agent.icon, { className: "w-4 h-4 inline mr-2" })}
                  {agent.name.split(' ')[0]}
                </motion.button>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

export default MultiAgentSection

