import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Shield, 
  Globe, 
  TrendingUp, 
  Clock, 
  Award,
  CheckCircle,
  Star,
  Building2,
  Zap,
  Lock,
  Activity
} from 'lucide-react'
import enterpriseDashboard from '../assets/enterprise-dashboard.png'

const EnterpriseSection = () => {
  const [activeMetric, setActiveMetric] = useState(0)
  const [liveMetrics, setLiveMetrics] = useState({
    users: 1000000,
    uptime: 99.99,
    threats: 325,
    regions: 5
  })

  const metrics = [
    {
      icon: Users,
      label: "Concurrent Users",
      value: "1M+",
      description: "Active users supported simultaneously",
      color: "from-blue-500 to-cyan-500",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/30"
    },
    {
      icon: Clock,
      label: "System Uptime", 
      value: "99.99%",
      description: "Guaranteed enterprise SLA",
      color: "from-green-500 to-emerald-500",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/30"
    },
    {
      icon: Shield,
      label: "Threats Blocked",
      value: "325K+",
      description: "Real-time security monitoring",
      color: "from-red-500 to-orange-500", 
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/30"
    },
    {
      icon: Globe,
      label: "Global Regions",
      value: "5+",
      description: "Multi-cloud deployment zones",
      color: "from-purple-500 to-pink-500",
      bgColor: "bg-purple-500/10", 
      borderColor: "border-purple-500/30"
    }
  ]

  const certifications = [
    {
      name: "SOC2 Type II",
      description: "Security & availability controls",
      icon: Shield,
      color: "text-blue-400"
    },
    {
      name: "HIPAA Compliant", 
      description: "Healthcare data protection",
      icon: Lock,
      color: "text-green-400"
    },
    {
      name: "GDPR Ready",
      description: "European data privacy",
      icon: CheckCircle,
      color: "text-purple-400"
    },
    {
      name: "ISO 27001",
      description: "Information security management",
      icon: Award,
      color: "text-orange-400"
    }
  ]

  const testimonials = [
    {
      company: "TechCorp Global",
      logo: "TC",
      quote: "Aideon AI Lite transformed our operations with 67% performance improvement and 34% cost savings.",
      author: "Sarah Chen, CTO",
      rating: 5
    },
    {
      company: "Healthcare Plus",
      logo: "HP", 
      quote: "HIPAA compliance and local processing gave us the confidence to deploy AI at scale.",
      author: "Dr. Michael Rodriguez, Chief Medical Officer",
      rating: 5
    },
    {
      company: "FinanceFirst",
      logo: "FF",
      quote: "The security features and real-time threat detection are unmatched in the industry.",
      author: "Jennifer Walsh, CISO",
      rating: 5
    }
  ]

  // Animate metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveMetric((prev) => (prev + 1) % metrics.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  // Animate live metrics
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveMetrics(prev => ({
        users: prev.users + Math.floor(Math.random() * 50),
        uptime: Math.min(99.99, prev.uptime + Math.random() * 0.001),
        threats: prev.threats + Math.floor(Math.random() * 5),
        regions: prev.regions
      }))
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="py-24 bg-gradient-to-b from-slate-800 to-slate-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500 rounded-full blur-3xl" />
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
          <Badge className="mb-4 bg-green-500/20 text-green-300 border-green-500/30">
            <Building2 className="w-3 h-3 mr-1" />
            Enterprise Excellence
          </Badge>
          
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Built for Scale,
            <span className="bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
              {" "}Designed for Security
            </span>
          </h2>
          
          <p className="text-xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
            Enterprise-grade infrastructure with military-level security, global scalability, 
            and compliance certifications that meet the most demanding requirements.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center mb-20">
          {/* Enterprise Dashboard */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="relative rounded-2xl overflow-hidden shadow-2xl">
              <img 
                src={enterpriseDashboard} 
                alt="Enterprise Dashboard"
                className="w-full h-auto"
              />
              
              {/* Live Overlay Metrics */}
              <div className="absolute top-4 right-4 space-y-2">
                <motion.div 
                  className="bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="text-green-400 text-sm font-mono">
                    LIVE: {liveMetrics.users.toLocaleString()}+ users
                  </div>
                </motion.div>
                
                <motion.div 
                  className="bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2"
                  animate={{ opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <div className="text-blue-400 text-sm font-mono">
                    {liveMetrics.uptime.toFixed(2)}% uptime
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>

          {/* Metrics Grid */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="grid grid-cols-2 gap-6"
          >
            {metrics.map((metric, index) => {
              const Icon = metric.icon
              return (
                <motion.div
                  key={metric.label}
                  className={`p-6 rounded-2xl backdrop-blur-sm border transition-all duration-500 ${
                    activeMetric === index
                      ? `${metric.bgColor} ${metric.borderColor} shadow-lg`
                      : 'bg-white/5 border-white/10'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${metric.color} w-fit mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  
                  <div className="text-3xl font-bold text-white mb-2">
                    {metric.value}
                  </div>
                  
                  <div className="text-lg font-semibold text-gray-300 mb-1">
                    {metric.label}
                  </div>
                  
                  <div className="text-sm text-gray-400">
                    {metric.description}
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        </div>

        {/* Certifications */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mb-20"
        >
          <h3 className="text-3xl font-bold text-white text-center mb-12">
            Security & Compliance Certifications
          </h3>
          
          <div className="grid md:grid-cols-4 gap-6">
            {certifications.map((cert, index) => {
              const Icon = cert.icon
              return (
                <motion.div
                  key={cert.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 text-center"
                >
                  <Icon className={`w-12 h-12 mx-auto mb-4 ${cert.color}`} />
                  <h4 className="text-lg font-semibold text-white mb-2">{cert.name}</h4>
                  <p className="text-sm text-gray-400">{cert.description}</p>
                </motion.div>
              )
            })}
          </div>
        </motion.div>

        {/* Customer Testimonials */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <h3 className="text-3xl font-bold text-white text-center mb-12">
            Trusted by Enterprise Leaders
          </h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.company}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.2 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.02 }}
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10"
              >
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center text-white font-bold text-lg mr-4">
                    {testimonial.logo}
                  </div>
                  <div>
                    <div className="font-semibold text-white">{testimonial.company}</div>
                    <div className="flex">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                      ))}
                    </div>
                  </div>
                </div>
                
                <blockquote className="text-gray-300 mb-4 italic">
                  "{testimonial.quote}"
                </blockquote>
                
                <div className="text-sm text-gray-400">
                  — {testimonial.author}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm rounded-3xl p-12 border border-white/10">
            <h3 className="text-3xl font-bold text-white mb-4">
              Ready for Enterprise Deployment?
            </h3>
            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of enterprises already using Aideon AI Lite to transform their operations.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold rounded-xl"
              >
                <Activity className="w-5 h-5 mr-2" />
                Schedule Enterprise Demo
              </Button>
              
              <Button 
                variant="outline"
                size="lg"
                className="border-white/30 text-white hover:bg-white/10 px-8 py-4 text-lg font-semibold rounded-xl"
              >
                <Zap className="w-5 h-5 mr-2" />
                Contact Sales Team
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default EnterpriseSection

