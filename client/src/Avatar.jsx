import { Float, MeshDistortMaterial, MeshWobbleMaterial, ContactShadows } from '@react-three/drei';
import useStore from './store';
import { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';

// Map visemes to mouth opening intensity
const VISEME_INTENSITY = {
  "sil": 0.0, "PP": 0.1, "FF": 0.2, "TH": 0.3,
  "DD": 0.3, "kk": 0.4, "CH": 0.5, "SS": 0.4,
  "nn": 0.3, "RR": 0.4, "aa": 1.0, "E": 0.8,
  "ih": 0.6, "oh": 0.9, "ou": 0.9
};

export default function Avatar() {
  const meshRef = useRef();
  const auraRef = useRef();

  // Audio & State synchronization
  const isPlayingRef = useRef(false);
  const audioContextRef = useRef(null);
  const audioStartTimeRef = useRef(0);
  const nextStartTimeRef = useRef(0);
  const processedChunksRef = useRef(0);

  const { streamQueue, isStreaming, activeVisemes } = useStore();

  // Initialize AudioContext
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    return () => {
      if (audioContextRef.current) audioContextRef.current.close();
    };
  }, []);

  // Process Stream Queue (Sync with WS logic)
  useEffect(() => {
    if (!isStreaming) {
      processedChunksRef.current = 0;
      nextStartTimeRef.current = 0;
      isPlayingRef.current = false;
      return;
    }

    const processQueue = async () => {
      if (streamQueue.length > processedChunksRef.current) {
        const ctx = audioContextRef.current;
        if (ctx.state === 'suspended') await ctx.resume();

        if (!isPlayingRef.current) {
          nextStartTimeRef.current = ctx.currentTime + 0.1;
          audioStartTimeRef.current = nextStartTimeRef.current;
          isPlayingRef.current = true;
        }

        for (let i = processedChunksRef.current; i < streamQueue.length; i++) {
          const chunkBase64 = streamQueue[i];
          const binaryString = atob(chunkBase64);
          const bytes = new Uint8Array(binaryString.length);
          for (let j = 0; j < binaryString.length; j++) bytes[j] = binaryString.charCodeAt(j);

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

  useFrame((state) => {
    const t = state.clock.getElapsedTime();

    if (meshRef.current) {
      // 1. Idle Animation (Breathing/Floating)
      const breathe = Math.sin(t * 1.5) * 0.05;
      meshRef.current.position.y = 0.5 + breathe;
      meshRef.current.rotation.z = Math.sin(t * 0.5) * 0.05;
      meshRef.current.rotation.y += 0.005;

      // 2. Lip Sync & Speaking Animation
      let targetScale = 1.0;
      let targetWobble = 0.1;

      if (isPlayingRef.current && audioContextRef.current) {
        const time = audioContextRef.current.currentTime - audioStartTimeRef.current;
        const activeViseme = activeVisemes.find(v => time >= v.time && time < v.time + v.duration);

        if (activeViseme) {
          const intensity = VISEME_INTENSITY[activeViseme.value] || 0.1;
          targetScale = 1.0 + intensity * 0.3;
          targetWobble = 0.5 + intensity;

          if (auraRef.current) {
            auraRef.current.visible = true;
            auraRef.current.scale.setScalar(1.2 + intensity * 0.5);
            auraRef.current.material.opacity = 0.3 + intensity * 0.4;
          }
        } else if (auraRef.current) {
          auraRef.current.visible = false;
        }

        if (time > nextStartTimeRef.current - audioStartTimeRef.current + 0.5 && !isStreaming) {
          isPlayingRef.current = false;
        }
      } else if (auraRef.current) {
        auraRef.current.visible = false;
      }

      // Smooth transformations
      meshRef.current.scale.lerp({ x: 1, y: targetScale, z: 1 }, 0.2);
    }
  });

  return (
    <group>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        {/* Main Avatar Body (Geometric & Stylized) */}
        <mesh ref={meshRef} position={[0, 0.5, 0]}>
          <octahedronGeometry args={[0.8, 2]} />
          <MeshWobbleMaterial
            color="#6366f1"
            factor={0.4}
            speed={2}
            roughness={0}
            metalness={0.8}
            envMapIntensity={2}
          />
        </mesh>

        {/* Aura Effect when speaking */}
        <mesh ref={auraRef} position={[0, 0.5, 0]} visible={false}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshBasicMaterial color="#a5b4fc" transparent opacity={0.3} wireframe />
        </mesh>
      </Float>

      {/* Decorative Elements */}
      <ContactShadows
        opacity={0.4}
        scale={10}
        blur={2}
        far={4}
        resolution={256}
        color="#000000"
      />

      {/* Floor Grid for depth */}
      <gridHelper args={[20, 20, "#333", "#222"]} position={[0, -1, 0]} />
    </group>
  );
}
