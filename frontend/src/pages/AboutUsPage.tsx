import React from 'react';
import { Users, Target, Heart, Mail } from 'lucide-react';

const AboutUsPage = () => {
  return (
    <div className="bg-white">
      {/* Hero section */}
      <div className="relative bg-gradient-to-r from-indigo-600 to-purple-600 py-16 sm:py-24">
        <div className="absolute inset-0 overflow-hidden">
          <svg
            className="absolute right-0 top-0 transform translate-x-1/3 -translate-y-1/4 lg:translate-x-1/2 xl:-translate-y-1/2 opacity-20"
            width="404"
            height="784"
            fill="none"
            viewBox="0 0 404 784"
          >
            <defs>
              <pattern
                id="pattern-1"
                x="0"
                y="0"
                width="20"
                height="20"
                patternUnits="userSpaceOnUse"
              >
                <rect x="0" y="0" width="4" height="4" className="text-white" fill="currentColor" opacity="0.3" />
              </pattern>
            </defs>
            <rect width="404" height="784" fill="url(#pattern-1)" />
          </svg>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              About Aideon AI
            </h1>
            <p className="mt-6 max-w-3xl mx-auto text-xl text-indigo-100">
              We're on a mission to create AI that respects your privacy, adapts to your needs, and works everywhere.
            </p>
          </div>
        </div>
      </div>

      {/* Mission section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                Our Mission
              </h2>
              <p className="mt-3 max-w-3xl text-lg text-gray-500">
                At Aideon AI, we're building the world's first truly hybrid autonomous AI system that combines local PC processing with cloud intelligence. Our mission is to definitively surpass all existing competitors in privacy, performance, and reliability.
              </p>
              <div className="mt-8 space-y-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <Users className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">User-Centric Design</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We believe AI should adapt to humans, not the other way around. Every feature we build starts with the user experience in mind.
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <Heart className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Privacy by Design</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We believe privacy is a fundamental right. Our hybrid architecture ensures your sensitive data never leaves your device unless you explicitly want it to.
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <Target className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Continuous Innovation</h3>
                    <p className="mt-2 text-base text-gray-500">
                      We're committed to pushing the boundaries of what's possible with AI, constantly improving our models and expanding our capabilities.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-10 lg:mt-0">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <img 
                    src="./assets/mission-image.jpg" 
                    alt="Aideon AI mission visualization"
                    className="w-full rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src = 'https://via.placeholder.com/600x400/4F46E5/FFFFFF?text=Our+Mission';
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Values section */}
      <div className="bg-gray-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Our Values
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              The principles that guide everything we do
            </p>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Value 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">Privacy</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We believe your data belongs to you. Period. Our technology is designed to keep your information private by default, giving you complete control over what data is shared and when.</p>
                </div>
              </div>
            </div>

            {/* Value 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">Transparency</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We're committed to being open about how our technology works, what data is used for, and how decisions are made. No black boxes, no hidden processes.</p>
                </div>
              </div>
            </div>

            {/* Value 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">Accessibility</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We believe powerful AI should be available to everyone, regardless of technical expertise or resources. Our products are designed to be intuitive and accessible to all.</p>
                </div>
              </div>
            </div>

            {/* Value 4 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">Reliability</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We build technology you can count on. Our hybrid architecture ensures you can work without interruption, even when internet connectivity is limited or unavailable.</p>
                </div>
              </div>
            </div>

            {/* Value 5 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">Innovation</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We're constantly pushing the boundaries of what's possible with AI, exploring new approaches and technologies to deliver ever-improving experiences.</p>
                </div>
              </div>
            </div>

            {/* Value 6 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 text-center">User Empowerment</h3>
                <div className="mt-2 text-base text-gray-500">
                  <p>We design our products to enhance human capabilities, not replace them. Our goal is to give you tools that amplify your creativity, productivity, and potential.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Team section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Our Team
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              Meet the passionate individuals behind Aideon AI
            </p>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {/* Team member placeholders - would be replaced with actual team members */}
            {[1, 2, 3, 4, 5, 6].map((index) => (
              <div key={index} className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
                <div className="px-4 py-5 sm:p-6 text-center">
                  <div className="mx-auto h-32 w-32 rounded-full overflow-hidden bg-gray-200">
                    <img 
                      src={`https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Team+Member+${index}`}
                      alt={`Team member ${index}`}
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <h3 className="mt-6 text-lg font-medium text-gray-900">Team Member {index}</h3>
                  <p className="text-sm text-indigo-600">Position Title</p>
                  <p className="mt-3 text-base text-gray-500">
                    Brief bio about the team member and their role at Aideon AI.
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Vision section */}
      <div className="bg-indigo-700">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            Our Vision for the Future
          </h2>
          <div className="mt-6 text-xl text-indigo-100 max-w-3xl">
            <p>
              We envision a world where AI enhances human capabilities while respecting privacy and autonomy. Our goal is to create technology that seamlessly integrates into your life, adapting to your needs and preferences without compromising your values.
            </p>
            <p className="mt-4">
              As we look to the future, we're committed to expanding the capabilities of Aideon AI Lite while maintaining our core principles of privacy, transparency, and user empowerment. We're working on new models, tools, and features that will make AI even more accessible and valuable to everyone.
            </p>
            <p className="mt-4">
              We believe the best AI is AI that works for you, not the other way around. That's the future we're building at Aideon AI.
            </p>
          </div>
        </div>
      </div>

      {/* Contact section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Get in Touch
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              Have questions or want to learn more about Aideon AI? We'd love to hear from you.
            </p>
          </div>

          <div className="mt-12 max-w-lg mx-auto">
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Mail className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div className="ml-3 text-base text-gray-500">
                    <p>Email: support@aideonai.com</p>
                  </div>
                </div>
                <div className="mt-6">
                  <a
                    href="#/contact"
                    className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    Contact Us
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutUsPage;
