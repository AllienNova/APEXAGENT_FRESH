import { useState } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import HomePage from './pages/HomePage';
import FeaturesPage from './pages/FeaturesPage';
import DocumentationPage from './pages/DocumentationPage';
import DownloadPage from './pages/DownloadPage';
import ContactPage from './pages/ContactPage';
import NotFoundPage from './pages/NotFoundPage';
import HowItWorksPage from './pages/HowItWorksPage';
import AboutUsPage from './pages/AboutUsPage';
import AdminPage from './pages/AdminPage';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import BackgroundNotification from './components/global/BackgroundNotification';

function App() {
  const [showNotification, setShowNotification] = useState(false);

  // Demo toggle for background notification
  const toggleNotification = () => {
    setShowNotification(!showNotification);
  };

  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Routes>
          {/* Admin Route - Full Screen */}
          <Route path="/admin/*" element={<AdminPage />} />
          
          {/* Marketing Website Routes */}
          <Route path="/*" element={
            <>
              <Header />
              <main className="flex-grow">
                <Routes>
                  <Route path="/" element={<HomePage toggleNotification={toggleNotification} />} />
                  <Route path="/features" element={<FeaturesPage />} />
                  <Route path="/how-it-works" element={<HowItWorksPage />} />
                  <Route path="/documentation" element={<DocumentationPage />} />
                  <Route path="/download" element={<DownloadPage />} />
                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/about" element={<AboutUsPage />} />
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </main>
              <Footer />
              <BackgroundNotification 
                isVisible={showNotification} 
                onClose={() => setShowNotification(false)} 
              />
            </>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
