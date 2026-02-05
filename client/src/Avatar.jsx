import React, { useEffect, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Text } from '@react-three/drei';
import useStore from './store';

// Map visemes to open/close intensity (0.0 to 1.0)
const VISEME_INTENSITY = {
  "sil": 0.0, "PP": 0.0, "FF": 0.2, "TH": 0.3,
  "DD": 0.3, "kk": 0.3, "CH": 0.5, "SS": 0.4,
  "nn": 0.3, "RR": 0.4, "aa": 1.0, "E": 0.8,
  "ih": 0.6, "oh": 0.9, "ou": 0.9
};

export default function Avatar() {
  const meshRef = useRef();

  // Audio playback state
  const audioQueue = useStore(state => state.audioQueue);
  const shiftAudio = useStore(state => state.shiftAudio);
  const currentAudioRef = useRef(null);
  const currentVisemesRef = useRef([]);
  const audioStartTimeRef = useRef(0);

  // Debug text state
  const [debugText, setDebugText] = useState("Idle");

  // Process Audio Queue
  useEffect(() => {
    if (audioQueue.length > 0 && !currentAudioRef.current) {
      const nextItem = audioQueue[0];

      // Convert base64 to blob/url
      const byteCharacters = atob(nextItem.audio);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      const audio = new Audio(url);
      currentAudioRef.current = audio;
      currentVisemesRef.current = nextItem.visemes; // Store visemes

      setDebugText(`Playing: ${nextItem.text?.substring(0, 20)}...`);

      audio.play().catch(e => console.error("Audio play error:", e));
      audioStartTimeRef.current = Date.now();

      audio.onended = () => {
        currentAudioRef.current = null;
        currentVisemesRef.current = [];
        setDebugText("Idle");
        shiftAudio();
      };
    }
  }, [audioQueue, shiftAudio]);

  // Streaming Audio State
  const streamQueue = useStore(state => state.streamQueue);
  const isStreaming = useStore(state => state.isStreaming);
  const activeVisemes = useStore(state => state.activeVisemes);

  const audioContextRef = useRef(null);
  const nextStartTimeRef = useRef(0);
  const isPlayingRef = useRef(false);
  const processedChunksRef = useRef(0);
  // audioStartTimeRef is already declared above

  // Initialize AudioContext
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    return () => {
      if (audioContextRef.current) audioContextRef.current.close();
    };
  }, []);

  // Process Stream Queue
  useEffect(() => {
    if (!isStreaming) {
      processedChunksRef.current = 0;
      nextStartTimeRef.current = 0;
      isPlayingRef.current = false;
      return;
    }

    const processQueue = async () => {
      // Only process new chunks
      if (streamQueue.length > processedChunksRef.current) {
        const ctx = audioContextRef.current;
        if (ctx.state === 'suspended') await ctx.resume();

        // Setup timing for first chunk
        if (!isPlayingRef.current) {
          nextStartTimeRef.current = ctx.currentTime + 0.1; // Small buffer
          audioStartTimeRef.current = nextStartTimeRef.current;
          isPlayingRef.current = true;
        }

        // Process all new chunks
        for (let i = processedChunksRef.current; i < streamQueue.length; i++) {
          const chunkBase64 = streamQueue[i];

          // Decode Base64
          const binaryString = atob(chunkBase64);
          const bytes = new Uint8Array(binaryString.length);
          for (let j = 0; j < binaryString.length; j++) {
            bytes[j] = binaryString.charCodeAt(j);
          }

          // Decode Audio Data
          // Note: decodeAudioData is async and might reorder if we aren't careful, 
          // but usually fast enough for small chunks. 
          // Ideally we map promise to index.
          try {
            const audioBuffer = await ctx.decodeAudioData(bytes.buffer.slice(0));

            const source = ctx.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(ctx.destination);

            source.start(nextStartTimeRef.current);
            nextStartTimeRef.current += audioBuffer.duration;
          } catch (err) {
            console.error("Error decoding chunk:", err);
          }
        }

        processedChunksRef.current = streamQueue.length;
      }
    };

    processQueue();

  }, [streamQueue, isStreaming]);

  useFrame(() => {
    if (meshRef.current) {
      let targetScale = 1.0;
      let targetColor = "hotpink";

      if (isPlayingRef.current && audioContextRef.current) {
        // Sync Visemes
        // Time relative to start of entire stream
        const time = audioContextRef.current.currentTime - audioStartTimeRef.current;

        const activeViseme = activeVisemes.find(v => time >= v.time && time < v.time + v.duration);

        if (activeViseme) {
          const intensity = VISEME_INTENSITY[activeViseme.value] || 0.1;
          targetScale = 1 + intensity;
          targetColor = "orange";
        }

        // Check if stream ended
        if (time > nextStartTimeRef.current - audioStartTimeRef.current + 0.5 && !isStreaming) {
          isPlayingRef.current = false;
        }
      }

      // Animate scale
      meshRef.current.scale.y += (targetScale - meshRef.current.scale.y) * 0.2;
      meshRef.current.rotation.y += 0.01;

      // Update color (rough way)
      meshRef.current.material.color.set(targetColor);
    }
  });

  return (
    <group>
      <mesh ref={meshRef} position={[0, 0.5, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>

      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#333" />
      </mesh>

      <Text position={[0, 2, 0]} fontSize={0.2} color="white">
        {debugText}
      </Text>
    </group>
  );
}
