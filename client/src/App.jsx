import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment } from '@react-three/drei';
import Avatar from './Avatar';
import AudioRecorder from './AudioRecorder';
import './index.css';

function App() {
  return (
    <div className="h-screen w-full bg-gray-900 overflow-hidden relative">
      <Canvas camera={{ position: [0, 1.5, 4], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 7]} intensity={1.2} />
        <Environment preset="city" />

        <Suspense fallback={null}>
          <Avatar />
        </Suspense>
      </Canvas>
      <div className="absolute bottom-10 left-10 text-white z-10">
        <h1 className="text-4xl font-bold">Este</h1>
        <p>Local AI Kiosk Companion</p>
      </div>
      <AudioRecorder />
    </div>
  );
}

export default App;
