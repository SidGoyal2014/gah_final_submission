
"use client";

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Camera, Send, X, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CameraViewProps {
  onSend: (photoDataUrl: string) => void;
  onClose: () => void;
}

export function CameraView({ onSend, onClose }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const getCameraPermission = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }, // Prefer back camera
          audio: false,
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (error) {
        console.error('Error accessing camera:', error);
        toast({
          variant: 'destructive',
          title: 'Camera Access Denied',
          description: 'Please enable camera permissions in your browser settings.',
        });
        onClose();
      }
    };

    getCameraPermission();

    return () => {
      // Cleanup: stop all tracks when the component unmounts
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once

  const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        const dataUrl = canvas.toDataURL('image/jpeg');
        setCapturedImage(dataUrl);

        // Stop the camera stream after capture
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }
      }
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    // Restart the camera stream
    const getCameraPermission = async () => {
        try {
          const mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' },
            audio: false,
          });
          setStream(mediaStream);
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }
        } catch (error) {
            console.error('Error restarting camera:', error);
            toast({
              variant: 'destructive',
              title: 'Camera Error',
              description: 'Could not restart the camera.',
            });
            onClose();
        }
    };
    getCameraPermission();
  };

  const handleSend = () => {
    if (capturedImage) {
      onSend(capturedImage);
    }
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center">
      <video
        ref={videoRef}
        className={cn(
          "w-full h-full object-cover",
          capturedImage ? "hidden" : "block"
        )}
        autoPlay
        playsInline
        muted
      />
      {capturedImage && (
        <img
          src={capturedImage}
          alt="Captured"
          className={cn(
              "w-full h-full object-contain"
          )}
        />
      )}

      <Button
        variant="ghost"
        size="icon"
        onClick={onClose}
        className="absolute top-4 left-4 text-white hover:text-white hover:bg-white/20 z-20"
        aria-label="Close camera"
      >
        <X className="h-6 w-6" />
      </Button>

      <div className="absolute bottom-0 left-0 right-0 p-4 flex items-center justify-center bg-black bg-opacity-30">
        {capturedImage ? (
          <div className="flex w-full items-center justify-between">
            <Button
              variant="ghost"
              onClick={handleRetake}
              className="text-white text-lg hover:text-white hover:bg-white/20"
            >
              <RefreshCw className="mr-2 h-5 w-5" />
              Retake
            </Button>
            <Button
              onClick={handleSend}
              className="bg-accent hover:bg-accent/90 rounded-full h-16 w-16"
              aria-label="Send photo"
            >
              <Send className="h-8 w-8" />
            </Button>
          </div>
        ) : (
          <button
            onClick={handleCapture}
            className="w-20 h-20 rounded-full bg-white border-4 border-black/30 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black"
            aria-label="Capture photo"
          >
             <Camera className="h-10 w-10 mx-auto text-black" />
          </button>
        )}
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
