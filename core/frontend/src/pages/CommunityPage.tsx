import React from 'react';
import { Book, Users, MessageSquare, HelpCircle, FileText } from 'lucide-react';

const CommunityPage = () => {
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
              Join Our Community
            </h1>
            <p className="mt-6 max-w-3xl mx-auto text-xl text-indigo-100">
              Connect with other Aideon AI Lite users, share experiences, and discover new ways to enhance your AI journey.
            </p>
          </div>
        </div>
      </div>

      {/* Community resources section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Community Resources
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              Explore our growing ecosystem of resources created by and for the Aideon AI community
            </p>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Resource 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <MessageSquare className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Discussion Forums</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  <p>
                    Join our active discussion forums where you can ask questions, share insights, and connect with other Aideon AI Lite users from around the world.
                  </p>
                  <div className="mt-4">
                    <a href="#/forums" className="text-indigo-600 hover:text-indigo-900 font-medium">
                      Visit Forums →
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Resource 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Book className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">Knowledge Base</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  <p>
                    Explore our community-contributed knowledge base with tutorials, guides, and best practices for getting the most out of Aideon AI Lite.
                  </p>
                  <div className="mt-4">
                    <a href="#/knowledge-base" className="text-indigo-600 hover:text-indigo-900 font-medium">
                      Browse Knowledge Base →
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Resource 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200 transition-all duration-300 hover:shadow-xl hover:border-indigo-100">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-md p-3">
                    <Users className="h-6 w-6 text-white" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">User Groups</h3>
                  </div>
                </div>
                <div className="mt-4 text-base text-gray-500">
                  <p>
                    Find and join user groups focused on specific industries, use cases, or interests. Connect with like-minded users and share specialized knowledge.
                  </p>
                  <div className="mt-4">
                    <a href="#/user-groups" className="text-indigo-600 hover:text-indigo-900 font-medium">
                      Find User Groups →
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Community events section */}
      <div className="bg-gray-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Upcoming Community Events
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              Join us for virtual and in-person events to learn, share, and connect
            </p>
          </div>

          <div className="mt-12 space-y-8">
            {/* Event 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="sm:flex sm:items-start sm:justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Monthly Community Webinar</h3>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>June 15, 2025 • 2:00 PM EST</p>
                      <p className="mt-1">Virtual Event</p>
                    </div>
                    <div className="mt-3 text-base text-gray-500">
                      <p>Join us for our monthly community webinar featuring new features, user showcases, and Q&A with the Aideon AI team.</p>
                    </div>
                  </div>
                  <div className="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center">
                    <a
                      href="#/events/monthly-webinar"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Register
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Event 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="sm:flex sm:items-start sm:justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Aideon AI Developer Workshop</h3>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>July 8, 2025 • 10:00 AM - 4:00 PM EST</p>
                      <p className="mt-1">Virtual Event</p>
                    </div>
                    <div className="mt-3 text-base text-gray-500">
                      <p>A hands-on workshop for developers looking to extend and customize Aideon AI Lite. Learn about our API, integration options, and custom model development.</p>
                    </div>
                  </div>
                  <div className="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center">
                    <a
                      href="#/events/developer-workshop"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Register
                    </a>
                  </div>
                </div>
              </div>
            </div>

            {/* Event 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="sm:flex sm:items-start sm:justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">Aideon AI User Conference</h3>
                    <div className="mt-2 text-sm text-gray-500">
                      <p>September 22-24, 2025</p>
                      <p className="mt-1">San Francisco, CA & Virtual</p>
                    </div>
                    <div className="mt-3 text-base text-gray-500">
                      <p>Our annual user conference featuring keynotes, workshops, networking opportunities, and a showcase of innovative uses of Aideon AI Lite from around the world.</p>
                    </div>
                  </div>
                  <div className="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center">
                    <a
                      href="#/events/user-conference"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Learn More
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-10 text-center">
            <a href="#/events" className="text-base font-medium text-indigo-600 hover:text-indigo-900">
              View all upcoming events →
            </a>
          </div>
        </div>
      </div>

      {/* Community showcase section */}
      <div className="py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Community Showcase
            </h2>
            <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
              See how others are using Aideon AI Lite to transform their work and creativity
            </p>
          </div>

          <div className="mt-12 grid gap-8 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {/* Showcase 1 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="h-48 w-full overflow-hidden">
                <img 
                  src="https://via.placeholder.com/600x300/4F46E5/FFFFFF?text=Project+Showcase+1" 
                  alt="Project showcase 1"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Healthcare Research Assistant</h3>
                <p className="mt-2 text-sm text-gray-500">By Dr. Sarah Chen</p>
                <p className="mt-3 text-base text-gray-500">
                  How a medical researcher used Aideon AI Lite to analyze patient data while maintaining strict privacy requirements.
                </p>
                <div className="mt-4">
                  <a href="#/showcase/healthcare" className="text-indigo-600 hover:text-indigo-900 font-medium">
                    Read Case Study →
                  </a>
                </div>
              </div>
            </div>

            {/* Showcase 2 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="h-48 w-full overflow-hidden">
                <img 
                  src="https://via.placeholder.com/600x300/4F46E5/FFFFFF?text=Project+Showcase+2" 
                  alt="Project showcase 2"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Creative Writing Companion</h3>
                <p className="mt-2 text-sm text-gray-500">By James Wilson</p>
                <p className="mt-3 text-base text-gray-500">
                  A novelist's journey using Aideon AI Lite to overcome writer's block and enhance his creative process.
                </p>
                <div className="mt-4">
                  <a href="#/showcase/creative-writing" className="text-indigo-600 hover:text-indigo-900 font-medium">
                    Read Case Study →
                  </a>
                </div>
              </div>
            </div>

            {/* Showcase 3 */}
            <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
              <div className="h-48 w-full overflow-hidden">
                <img 
                  src="https://via.placeholder.com/600x300/4F46E5/FFFFFF?text=Project+Showcase+3" 
                  alt="Project showcase 3"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900">Small Business Automation</h3>
                <p className="mt-2 text-sm text-gray-500">By Maria Rodriguez</p>
                <p className="mt-3 text-base text-gray-500">
                  How a small business owner automated customer service and inventory management using Aideon AI Lite.
                </p>
                <div className="mt-4">
                  <a href="#/showcase/small-business" className="text-indigo-600 hover:text-indigo-900 font-medium">
                    Read Case Study →
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-10 text-center">
            <a href="#/showcase" className="text-base font-medium text-indigo-600 hover:text-indigo-900">
              View all showcase projects →
            </a>
          </div>
        </div>
      </div>

      {/* Contribution section */}
      <div className="bg-gray-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
            <div>
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                Contribute to the Community
              </h2>
              <p className="mt-3 max-w-3xl text-lg text-gray-500">
                Share your knowledge, experience, and creations with the Aideon AI community. There are many ways to contribute, regardless of your technical expertise.
              </p>
              <div className="mt-8 space-y-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <FileText className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Share Your Use Cases</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Submit your Aideon AI Lite projects and use cases to inspire others and showcase innovative applications.
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <Book className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Create Tutorials</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Help others learn by creating tutorials, guides, or articles about using Aideon AI Lite effectively.
                    </p>
                  </div>
                </div>
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                      <HelpCircle className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Answer Questions</h3>
                    <p className="mt-2 text-base text-gray-500">
                      Share your expertise by answering questions in our forums and helping other users solve problems.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-10 lg:mt-0">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg font-medium text-gray-900">Contribution Guidelines</h3>
                  <p className="mt-3 text-base text-gray-500">
                    We welcome contributions from all community members. To ensure a positive and productive experience for everyone, please review our contribution guidelines.
                  </p>
                  <div className="mt-6">
                    <a
                      href="#/contribution-guidelines"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      View Guidelines
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA section */}
      <div className="bg-indigo-700">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Join the Aideon AI community today</span>
            <span className="block">Start connecting, learning, and sharing</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-indigo-200">
            Become part of a growing community of innovators using Aideon AI Lite to transform how they work and create.
          </p>
          <div className="mt-8 flex justify-center">
            <div className="inline-flex rounded-md shadow">
              <a
                href="#/register"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50"
              >
                Create Account
              </a>
            </div>
            <div className="ml-3 inline-flex">
              <a
                href="#/forums"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-800 hover:bg-indigo-900"
              >
                Visit Forums
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommunityPage;
