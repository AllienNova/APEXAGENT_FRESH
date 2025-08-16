// Firebase Configuration for Aideon AI Lite Production
// Real Firebase project: aideonlite-ai

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";
import { getFunctions, connectFunctionsEmulator } from "firebase/functions";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCk-m_VQKMcZvdFqdWWhSWVBOrn0rf9y8U",
  authDomain: "aideonlite-ai.firebaseapp.com",
  projectId: "aideonlite-ai",
  storageBucket: "aideonlite-ai.firebasestorage.app",
  messagingSenderId: "278308184204",
  appId: "1:278308184204:web:feebd994bb8b80b6dd5ba9",
  measurementId: "G-E38JHJQ3BD"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
const analytics = getAnalytics(app);
const db = getFirestore(app);
const auth = getAuth(app);
const storage = getStorage(app);
const functions = getFunctions(app);

// Development environment configuration
if (process.env.NODE_ENV === 'development') {
  // Connect to emulators in development
  try {
    connectFirestoreEmulator(db, 'localhost', 8080);
    connectFunctionsEmulator(functions, 'localhost', 5001);
  } catch (error) {
    console.log('Emulators already connected or not available');
  }
}

// Export Firebase services for use throughout the application
export {
  app,
  analytics,
  db,
  auth,
  storage,
  functions,
  firebaseConfig
};

// Default export
export default app;

