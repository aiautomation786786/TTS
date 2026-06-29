import { useState, useRef, useEffect, useCallback } from 'react';

const useAudio = (src) => {
  const audioRef = useRef(new Audio());
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;

    if (src) {
      audio.src = src;
      audio.load();
    }

    const onLoadedMetadata = () => setDuration(audio.duration);
    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onEnded = () => { setIsPlaying(false); setCurrentTime(0); };
    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);

    audio.addEventListener('loadedmetadata', onLoadedMetadata);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);

    return () => {
      audio.removeEventListener('loadedmetadata', onLoadedMetadata);
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audio.removeEventListener('play', onPlay);
      audio.removeEventListener('pause', onPause);
      audio.pause();
    };
  }, [src]);

  const play = useCallback(() => {
    audioRef.current.play().catch(() => {});
  }, []);

  const pause = useCallback(() => {
    audioRef.current.pause();
  }, []);

  const toggle = useCallback(() => {
    if (audioRef.current.paused) {
      play();
    } else {
      pause();
    }
  }, [play, pause]);

  const seek = useCallback((time) => {
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  }, []);

  const setVolume = useCallback((vol) => {
    audioRef.current.volume = vol;
    setVolumeState(vol);
  }, []);

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return {
    isPlaying,
    currentTime,
    duration,
    progress,
    volume,
    play,
    pause,
    toggle,
    seek,
    setVolume,
    audioRef,
  };
};

export default useAudio;
