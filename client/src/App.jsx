import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import Avatar from './Avatar';
import AudioRecorder from './AudioRecorder';
import './index.css';

import useStore from './store';

function App() {
  const { isThinking, subtitle, setTextQuery } = useStore();

  const quickQuestions = [
    "How do I enroll?",
    "Where is the Registrar?",
    "What are the IT programs?",
    "Library hours?"
  ];

  const handleQuickQuestion = (q) => {
    if (isThinking) return;
    setTextQuery(q);
  };

  return (
    <div className="h-screen w-full bg-gray-900 overflow-hidden relative font-sans">
      {/* 3D Scene */}
      <div className="absolute inset-0 z-0">
        <Canvas camera={{ position: [0, 1.2, 3.5], fov: 40 }}>
          <ambientLight intensity={0.5} />
          <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          <Environment preset="night" />

          <Suspense fallback={null}>
            <Avatar />
          </Suspense>
        </Canvas>
      </div>

      {/* Header */}
      <div className="absolute top-10 left-10 text-white z-10 pointer-events-none">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/50">
            <span className="text-2xl font-black">E</span>
          </div>
          <div>
            <h1 className="text-5xl font-extrabold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              ESTE
            </h1>
            <p className="text-xs uppercase tracking-widest text-indigo-400 font-bold">USTP AI COMPANION</p>
          </div>
        </div>
      </div>

      {/* Overlay: Thinking & Subtitles */}
      <div className="absolute inset-0 flex flex-col items-center justify-end pb-48 pointer-events-none">
        {isThinking && (
          <div className="mb-8 flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20 animate-pulse">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
            </div>
            <span className="text-xs text-indigo-200 font-medium">Processing...</span>
          </div>
        )}
      </div>

      {/* Quick Questions (Experimental) */}
      <div className="absolute left-10 bottom-40 flex flex-col gap-3 z-20 hidden md:flex">
        <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Suggested Inquiries</p>
        {quickQuestions.map((q, i) => (
          <button
            key={i}
            className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 transition-all text-left backdrop-blur-sm"
            onClick={() => handleQuickQuestion(q)}
          >
            {q}
          </button>
        ))}
      </div>

      <AudioRecorder />
    </div>
  );
}

export default App;
