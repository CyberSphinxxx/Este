import { useState, useRef, useEffect, useCallback } from 'react';

const useAudioRecorder = ({ onAudioData, silenceThreshold = 0.02, silenceDuration = 1000 }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0);
    const mediaRecorderRef = useRef(null);
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const silenceStartRef = useRef(null);
    const rafIdRef = useRef(null);

    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Setup Audio Context for VAD
            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 512;
            source.connect(analyserRef.current);

            // Setup MediaRecorder
            mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0 && onAudioData) {
                    onAudioData(event.data);
                }
            };

            mediaRecorderRef.current.start(100); // Collect 100ms chunks
            setIsRecording(true);
            checkAudioLevel();

        } catch (err) {
            console.error("Error accessing microphone:", err);
        }
    }, [onAudioData]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);
            setIsSpeaking(false);
            setAudioLevel(0);

            if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
            if (audioContextRef.current) audioContextRef.current.close();
        }
    }, [isRecording]);

    const checkAudioLevel = () => {
        if (!analyserRef.current) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);

        // Calculate RMS (Root Mean Square) to get average volume
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length) / 255;
        setAudioLevel(rms); // Update state for UI

        // VAD Logic
        if (rms > silenceThreshold) {
            setIsSpeaking(true);
            silenceStartRef.current = null;
        } else {
            if (!silenceStartRef.current) {
                silenceStartRef.current = Date.now();
            } else if (Date.now() - silenceStartRef.current > silenceDuration) {
                setIsSpeaking(false);
            }
        }

        rafIdRef.current = requestAnimationFrame(checkAudioLevel);
    };

    useEffect(() => {
        return () => {
            if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
            if (audioContextRef.current) audioContextRef.current.close();
        };
    }, []);

    return { isRecording, isSpeaking, startRecording, stopRecording, audioLevel };
};

export default useAudioRecorder;
