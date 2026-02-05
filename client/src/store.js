import { create } from 'zustand';

const useStore = create((set) => ({
    visemes: [],
    // Standard Queue (Legacy/Fallback)
    audioQueue: [],

    // Streaming State
    streamQueue: [],      // Array of base64 chunks
    isStreaming: false,
    activeVisemes: [],    // For current stream

    setVisemes: (newVisemes) => set({ visemes: newVisemes }),
    addAudio: (audioData) => set((state) => ({ audioQueue: [...state.audioQueue, audioData] })),
    shiftAudio: () => set((state) => ({ audioQueue: state.audioQueue.slice(1) })),

    // Stream Actions
    startStream: (text, visemes) => set({
        isStreaming: true,
        streamQueue: [],
        activeVisemes: visemes,
        subtitle: text,
        isThinking: false
    }),
    addStreamChunk: (chunk) => set((state) => ({ streamQueue: [...state.streamQueue, chunk] })),
    endStream: () => set({ isStreaming: false }),

    setIsThinking: (thinking) => set({ isThinking: thinking }),
    setSubtitle: (text) => set({ subtitle: text }),
}));

export default useStore;
