import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Shield, 
  Zap, 
  Package, 
  Wrench, 
  Code, 
  Eye,
  CheckCircle,
  ArrowRight,
  Github,
  Palette,
  Stethoscope,
  Scale,
  Database,
  Briefcase
} from 'lucide-react'

const ActualFeaturesSection = () => {
  const [activeFeature, setActiveFeature] = useState(0)

  const coreFeatures = [
    {
      icon: Shield,
      title: "Complete Privacy",
      description: "Local processing with no cloud dependencies when you need maximum privacy",
      color: "from-green-400 to-emerald-500",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/30",
      details: [
        "Device-based AI models",
        "No data transmission required",
        "Offline capability",
        "Privacy-first architecture"
      ]
    },
    {
      icon: Zap,
      title: "Hybrid Processing",
      description: "Seamless switching between local and cloud processing for optimal performance",
      color: "from-blue-400 to-cyan-500",
      bgColor: "bg-blue-500/10", 
      borderColor: "border-blue-500/30",
      details: [
        "Smart processing location selection",
        "Automatic optimization",
        "Consistent user experience",
        "Performance-based routing"
      ]
    },
    {
      icon: Package,
      title: "Bundled Models",
      description: "Pre-installed AI models ready for immediate offline use",
      color: "from-purple-400 to-pink-500",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/30", 
      details: [
        "30+ AI models included",
        "Instant availability",
        "No setup required",
        "Regular model updates"
      ]
    },
    {
      icon: Wrench,
      title: "106+ Tool Integrations",
      description: "Cross-domain tool connectivity for comprehensive workflow automation",
      color: "from-orange-400 to-red-500",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/30",
      details: [
        "Software development tools",
        "Business productivity suites", 
        "Creative design platforms",
        "Industry-specific integrations"
      ]
    },
    {
      icon: Code,
      title: "IDE Integrations",
      description: "Native integration with popular development environments",
      color: "from-indigo-400 to-purple-500",
      bgColor: "bg-indigo-500/10",
      borderColor: "border-indigo-500/30",
      details: [
        "VS Code full integration",
        "JetBrains IDEs support",
        "Eclipse compatibility",
        "Sublime Text plugins"
      ]
    },
    {
      icon: Eye,
      title: "Computer Vision",
      description: "Advanced image analysis and optical character recognition capabilities",
      color: "from-cyan-400 to-blue-500",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/30",
      details: [
        "Image analysis & object detection",
        "OCR with multi-language support",
        "Facial recognition features",
        "Real-time camera integration"
      ]
    }
  ]

  const toolCategories = [
    {
      name: "Software Development",
      icon: Github,
      count: "25+",
      color: "text-blue-400",
      tools: ["Git", "GitHub", "VS Code", "JetBrains IDEs", "Docker", "Kubernetes"]
    },
    {
      name: "Data Science", 
      icon: Database,
      count: "20+",
      color: "text-green-400",
      tools: ["Jupyter", "Pandas", "NumPy", "Matplotlib", "Scikit-learn", "TensorFlow"]
    },
    {
      name: "Business & Productivity",
      icon: Briefcase,
      count: "18+", 
      color: "text-purple-400",
      tools: ["Microsoft Office", "Google Workspace", "Slack", "Notion", "Trello", "Asana"]
    },
    {
      name: "Healthcare",
      icon: Stethoscope,
      count: "15+",
      color: "text-red-400", 
      tools: ["EHR Systems", "Medical Databases", "DICOM Viewers", "Clinical Analytics"]
    },
    {
      name: "Legal",
      icon: Scale,
      count: "12+",
      color: "text-yellow-400",
      tools: ["Legal Research", "Document Management", "Contract Analysis", "Compliance Tools"]
    },
    {
      name: "Creative & Design",
      icon: Palette,
      count: "16+",
      color: "text-pink-400",
      tools: ["Adobe Creative Suite", "Figma", "Canva", "Sketch", "Blender", "AutoCAD"]
    }
  ]

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
            <CheckCircle className="w-3 h-3 mr-1" />
            Core Features
          </Badge>
          
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Powerful Features
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {" "}Built for Real Work
            </span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
            Every feature in Aideon AI Lite is designed and implemented to solve real-world problems 
            with privacy, performance, and reliability at the core.
          </p>
        </motion.div>

        {/* Core Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {coreFeatures.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                onMouseEnter={() => setActiveFeature(index)}
                className={`p-8 rounded-2xl backdrop-blur-sm border transition-all duration-500 cursor-pointer ${
                  activeFeature === index
                    ? `${feature.bgColor} ${feature.borderColor} shadow-lg`
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <div className={`p-4 rounded-xl bg-gradient-to-r ${feature.color} w-fit mb-6`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                
                <h3 className="text-2xl font-bold text-white mb-4">{feature.title}</h3>
                <p className="text-gray-400 mb-6 leading-relaxed">{feature.description}</p>
                
                <div className="space-y-2">
                  {feature.details.map((detail, detailIndex) => (
                    <motion.div
                      key={detail}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: activeFeature === index ? 1 : 0.7, x: 0 }}
                      transition={{ duration: 0.3, delay: detailIndex * 0.1 }}
                      className="flex items-center text-gray-300"
                    >
                      <CheckCircle className="w-4 h-4 text-green-400 mr-3 flex-shrink-0" />
                      <span className="text-sm">{detail}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Tool Integrations */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-white mb-4">
              106+ Tool Integrations
            </h3>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Connect with the tools you already use across six major domains
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {toolCategories.map((category, index) => {
              const Icon = category.icon
              return (
                <motion.div
                  key={category.name}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
                >
                  <div className="flex items-center mb-4">
                    <Icon className={`w-8 h-8 ${category.color} mr-3`} />
                    <div>
                      <h4 className="text-lg font-semibold text-white">{category.name}</h4>
                      <div className="text-sm text-gray-400">{category.count} tools</div>
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {category.tools.map((tool) => (
                      <span 
                        key={tool}
                        className="px-2 py-1 bg-white/10 rounded-lg text-xs text-gray-300"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Computer Vision Details */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 backdrop-blur-sm rounded-3xl p-12 border border-cyan-500/20"
        >
          <div className="text-center mb-8">
            <Eye className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
            <h3 className="text-3xl font-bold text-white mb-4">
              Advanced Computer Vision
            </h3>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Powerful computer vision features that work locally on your device for maximum privacy and performance
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: "Image Analysis",
                description: "Object detection, scene understanding, activity recognition",
                features: ["Object detection", "Scene understanding", "Activity recognition"]
              },
              {
                title: "OCR Technology", 
                description: "Multi-language text extraction with high accuracy",
                features: ["Multi-language support", "Handwriting recognition", "Document structure analysis"]
              },
              {
                title: "Facial Recognition",
                description: "Privacy-preserving face detection and analysis",
                features: ["Face detection", "Landmark detection", "Expression analysis"]
              },
              {
                title: "Camera Integration",
                description: "Real-time computer vision applications",
                features: ["Real-time video analysis", "AR capabilities", "QR/barcode scanning"]
              }
            ].map((capability, index) => (
              <motion.div
                key={capability.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white/5 rounded-xl p-6"
              >
                <h4 className="text-lg font-semibold text-white mb-2">{capability.title}</h4>
                <p className="text-gray-400 text-sm mb-4">{capability.description}</p>
                <div className="space-y-1">
                  {capability.features.map((feature) => (
                    <div key={feature} className="flex items-center text-xs text-gray-300">
                      <ArrowRight className="w-3 h-3 text-cyan-400 mr-2" />
                      {feature}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default ActualFeaturesSection

