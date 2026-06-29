
import { useState, useRef, useEffect } from 'react';

export const useAudioPlayer = () => {
    const [playingId, setPlayingId] = useState(null);
    const audioRef = useRef(new Audio());

    useEffect(() => {
        const audio = audioRef.current;
        const handleEnded = () => setPlayingId(null);
        audio.addEventListener('ended', handleEnded);
        return () => {
            audio.removeEventListener('ended', handleEnded);
            audio.pause();
        };
    }, []);

    const play = (id, url) => {
        if (playingId === id) {
            audioRef.current.pause();
            setPlayingId(null);
        } else {
            audioRef.current.src = url;
            audioRef.current.play().catch(console.error);
            setPlayingId(id);
        }
    };

    const stop = () => {
        audioRef.current.pause();
        setPlayingId(null);
    };

    return { playingId, play, stop };
};
