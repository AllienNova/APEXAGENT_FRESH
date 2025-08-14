import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Download, ArrowRight, Users, Shield, Zap, Brain, CheckCircle, Code, Eye, Wrench } from 'lucide-react'
import heroBackground from '../assets/hero-background.png'

const HeroSection = () => {
  const [currentMetric, setCurrentMetric] = useState(0)

  const metrics = [
    { label: "Tool Integrations", value: "106+", icon: Wrench },
    { label: "AI Models", value: "30+", icon: Brain },
    { label: "IDE Support", value: "5+", icon: Code },
    { label: "Vision Features", value: "4", icon: Eye }
  ]

  const actualFeatures = [
    "Privacy-First Architecture",
    "Hybrid Local + Cloud Processing", 
    "106+ Tool Integrations",
    "Computer Vision Capabilities",
    "IDE Integrations",
    "Multi-Modal Processing"
  ]

  // Animate metrics rotation
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMetric((prev) => (prev + 1) % metrics.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Background Image */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url(${heroBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      />
      
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-blue-400 rounded-full opacity-20"
            animate={{
              x: [0, Math.random() * 100, 0],
              y: [0, Math.random() * 100, 0],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 10 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Trust Indicators */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex justify-center gap-4 mb-8"
        >
          <Badge variant="secondary" className="bg-blue-500/20 text-blue-300 border-blue-500/30">
            <Shield className="w-3 h-3 mr-1" />
            Privacy-First
          </Badge>
          <Badge variant="secondary" className="bg-green-500/20 text-green-300 border-green-500/30">
            <CheckCircle className="w-3 h-3 mr-1" />
            Hybrid Processing
          </Badge>
          <Badge variant="secondary" className="bg-purple-500/20 text-purple-300 border-purple-500/30">
            <Brain className="w-3 h-3 mr-1" />
            Multi-Modal AI
          </Badge>
        </motion.div>

        {/* Main Headline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Intelligence Everywhere,
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              {" "}Limits Nowhere
            </span>
          </h1>
          
          <h2 className="text-2xl md:text-3xl text-gray-300 mb-8 font-light">
            Aideon AI Lite - The World's First Truly Hybrid Autonomous AI System
          </h2>
          
          <p className="text-xl text-gray-400 mb-12 max-w-4xl mx-auto leading-relaxed">
            Experience the perfect balance of privacy and power with our revolutionary hybrid AI system 
            that seamlessly combines local PC processing with cloud intelligence. Complete privacy when you need it, 
            unlimited power when you want it.
          </p>
        </motion.div>

        {/* Feature Pills */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-wrap justify-center gap-3 mb-12"
        >
          {actualFeatures.map((feature, index) => (
            <motion.div
              key={feature}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
              className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm text-white border border-white/20"
            >
              {feature}
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
        >
          <Button 
            size="lg" 
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Now
          </Button>
          
          <Button 
            variant="outline" 
            size="lg"
            className="border-white/30 text-white hover:bg-white/10 px-8 py-4 text-lg font-semibold rounded-xl backdrop-blur-sm"
          >
            <Play className="w-5 h-5 mr-2" />
            Watch Demo
          </Button>
        </motion.div>

        {/* Real Metrics */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
        >
          {metrics.map((metric, index) => {
            const Icon = metric.icon
            return (
              <motion.div
                key={metric.label}
                className={`p-6 rounded-2xl backdrop-blur-sm border transition-all duration-500 ${
                  currentMetric === index 
                    ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-blue-400/50 shadow-lg shadow-blue-500/20' 
                    : 'bg-white/5 border-white/10'
                }`}
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Icon className={`w-8 h-8 mx-auto mb-3 ${
                  currentMetric === index ? 'text-blue-400' : 'text-gray-400'
                }`} />
                <div className={`text-2xl font-bold mb-1 ${
                  currentMetric === index ? 'text-white' : 'text-gray-300'
                }`}>
                  {metric.value}
                </div>
                <div className="text-sm text-gray-400">{metric.label}</div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="flex flex-col items-center text-gray-400"
          >
            <span className="text-sm mb-2">Discover More</span>
            <ArrowRight className="w-5 h-5 rotate-90" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

export default HeroSection

