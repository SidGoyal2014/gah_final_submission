import { useState, useRef, useEffect } from "react";
import { Play, Pause } from "lucide-react";

interface AudioPlayerProps {
  src: string;
  isUser: boolean;
}

export function AudioPlayer({ src, isUser }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleTimeUpdate = () => {
      setProgress(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setProgress(0);
    };

    audio.addEventListener("loadedmetadata", handleLoadedMetadata);
    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("ended", handleEnded);
    };
  }, [src]);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch((err) => {
        console.error("Play failed:", err);
      });
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div
      style={{
        backgroundColor: "#308c8c", // tealish color, adjust as needed
        borderRadius: "9999px",
        padding: "8px 16px",
        maxWidth: "320px",
        width: "100%",
        display: "flex",
        alignItems: "center",
        userSelect: "none",
      }}
    >
      <button
        onClick={togglePlay}
        aria-label={isPlaying ? "Pause audio" : "Play audio"}
        style={{
          backgroundColor: "#e0f7f7",
          color: "#076767",
          width: 32,
          height: 32,
          borderRadius: "50%",
          border: "2px solid #076767",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          flexShrink: 0,
        }}
      >
        {isPlaying ? <Pause size={20} /> : <Play size={20} />}
      </button>

      <div
        style={{
          flex: 1,
          margin: "0 12px",
          height: 8,
          backgroundColor: "52a7a7",
          borderRadius: 9999,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            backgroundColor: "#d3f3f3",
            width: duration ? `${(progress / duration) * 100}%` : "0%",
            transition: "width 0.1s linear",
          }}
        />
      </div>

      <span
        style={{
          color: "#e0f7f7",
          fontFamily: "monospace",
          fontSize: 12,
          minWidth: 40,
          textAlign: "right",
          userSelect: "none",
        }}
      >
        {formatTime(progress)}
      </span>

      <audio ref={audioRef} src={src} preload="auto" />
    </div>
  );
}
