import React from 'react';
import Layout from '../components/layout/Layout';
import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import ToolIntegrationsSection from '../components/home/ToolIntegrationsSection';
import IDEIntegrationsSection from '../components/home/IDEIntegrationsSection';
import ComputerVisionSection from '../components/home/ComputerVisionSection';
import HybridAISection from '../components/home/HybridAISection';

const HomePage = () => {
  return (
    <Layout>
      <Hero />
      <HybridAISection />
      <Features />
      <ToolIntegrationsSection />
      <IDEIntegrationsSection />
      <ComputerVisionSection />
    </Layout>
  );
};

export default HomePage;
