import React, { useEffect, useRef, useState } from 'react';
import useStore from './store';

const AudioRecorder = () => {
    const wsRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const [isRecording, setIsRecording] = useState(false);
    const [isConnected, setIsConnected] = useState(false);

    const isThinking = useStore(state => state.isThinking);
    const subtitle = useStore(state => state.subtitle);

    // WebSocket connection
    useEffect(() => {
        const connectWS = () => {
            wsRef.current = new WebSocket('ws://localhost:8000/ws/chat');

            wsRef.current.onopen = () => {
                console.log('✅ WebSocket connected');
                setIsConnected(true);
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    // console.log('📩 Received:', data.type); // Less verbose logging

                    if (data.type === 'audio_start') {
                        console.log('⚡ Stream Started');
                        // Visemes come in a separate message usually, but main.py sends them in 'viseme_data'
                    }
                    else if (data.type === 'viseme_data') {
                        // We assume audio_start came first or simultaneous.
                        // We need the text from audio_start to set subtitle? 
                        // Actually audio_start has the text.
                    }
                    else if (data.type === 'audio_start') {
                        // Handled above conceptually, but let's merge logic
                    }

                    switch (data.type) {
                        case 'audio_start':
                            useStore.getState().startStream(data.text, []);
                            break;
                        case 'viseme_data':
                            // Update the active stream with visemes
                            useStore.getState().activeVisemes = data.visemes; // Direct mutation or action? 
                            // Better use an action if we added one, currently startStream takes visemes
                            // Let's add a setAction? Or just re-call startStream? 
                            // We'll update state directly for perf or add a setter.
                            // useStore.setState({ activeVisemes: data.visemes }); 
                            useStore.setState(state => ({ activeVisemes: data.visemes }));
                            break;
                        case 'audio_chunk':
                            useStore.getState().addStreamChunk(data.audio);
                            break;
                        case 'audio_end':
                            console.log('⚡ Stream Ended');
                            useStore.getState().endStream();
                            break;
                        case 'audio_response': // Fallback
                            useStore.getState().addAudio(data);
                            useStore.getState().setIsThinking(false);
                            useStore.getState().setSubtitle(data.text);
                            break;
                    }

                } catch (e) {
                    console.error("Parse error:", e);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('❌ WebSocket Error:', error);
                setIsConnected(false);
            };

            wsRef.current.onclose = () => {
                console.log('🔌 WebSocket disconnected, reconnecting in 3s...');
                setIsConnected(false);
                setTimeout(connectWS, 3000);
            };
        };

        connectWS();

        return () => {
            if (wsRef.current) {
                wsRef.current.onclose = null; // Prevent reconnect on unmount
                wsRef.current.close();
            }
        };
    }, []);

    // Start Recording
    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });

            audioChunksRef.current = [];

            mediaRecorderRef.current = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                // Create blob and send
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                console.log('🎤 Recording stopped, blob size:', audioBlob.size);

                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && audioBlob.size > 0) {
                    console.log('📤 Sending audio to server...');
                    wsRef.current.send(audioBlob);
                    useStore.getState().setIsThinking(true);
                    useStore.getState().setSubtitle("Processing...");
                } else {
                    console.warn('⚠️ WebSocket not ready or empty audio');
                }

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start(100); // Collect chunks every 100ms
            setIsRecording(true);
            useStore.getState().setSubtitle("Listening...");
            console.log('🎙️ Recording started');

        } catch (err) {
            console.error("Microphone error:", err);
            alert("Could not access microphone. Please allow microphone permissions.");
        }
    };

    // Stop Recording
    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            console.log('⏹️ Recording stopped');
        }
    };

    // Toggle handler
    const handleToggle = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 flex flex-col items-center pb-8 bg-gradient-to-t from-gray-900/95 to-transparent pt-20">

            {/* Connection Status */}
            <div className={`absolute top-4 right-4 flex items-center gap-2 text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400 animate-pulse'}`} />
                {isConnected ? 'Connected' : 'Reconnecting...'}
            </div>

            {/* Subtitle Box */}
            {subtitle && (
                <div className="bg-black/80 border border-white/20 backdrop-blur-md px-6 py-4 rounded-xl text-white text-center max-w-lg mb-6 shadow-2xl">
                    <p className="text-lg leading-relaxed">{subtitle}</p>
                </div>
            )}

            {/* Mic Button */}
            <div className="relative">
                {isRecording && (
                    <div className="absolute -inset-4 bg-red-500/30 rounded-full animate-ping" />
                )}
                <button
                    onClick={handleToggle}
                    disabled={!isConnected || isThinking}
                    className={`relative w-20 h-20 rounded-full flex items-center justify-center shadow-xl border-4 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${isRecording
                        ? 'bg-red-600 border-red-400 hover:bg-red-700'
                        : 'bg-indigo-600 border-indigo-400 hover:bg-indigo-700'
                        }`}
                >
                    {isRecording ? (
                        // Stop icon
                        <div className="w-7 h-7 rounded-sm bg-white" />
                    ) : (
                        // Mic icon
                        <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                        </svg>
                    )}
                </button>
            </div>

            {/* Status Text */}
            <div className={`mt-4 text-sm font-semibold tracking-wider uppercase ${isThinking ? 'text-yellow-400' :
                isRecording ? 'text-red-400' :
                    'text-indigo-300'
                }`}>
                {isThinking ? '🤔 Thinking...' :
                    isRecording ? '🎙️ Recording - Click to Send' :
                        '👆 Tap to Speak'}
            </div>

            {/* Instructions */}
            <p className="mt-2 text-xs text-gray-500 max-w-xs text-center">
                Click once to start recording, click again to send your message to Este
            </p>
        </div>
    );
};

export default AudioRecorder;
