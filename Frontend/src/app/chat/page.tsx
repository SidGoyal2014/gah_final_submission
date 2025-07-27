
"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Bot,
  User,
  Mic,
  Send,
  Leaf,
  LineChart,
  CornerDownLeft,
  UserCircle,
  Upload,
  Camera,
  X,
  Volume2,
} from "lucide-react";
import { Logo } from "@/components/logo";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { AudioPlayer } from "@/components/ui/AudioPlayer";
import { CameraView } from "@/components/ui/CameraView";


interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  category?: string;
  audioUrl?: string;
  photoUrl?: string;
}

const categoryIcons: { [key: string]: React.ReactNode } = {
  "crop advice": <Leaf className="h-4 w-4" />,
  "market prices": <LineChart className="h-4 w-4" />,
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [fullscreenImage, setFullscreenImage] = useState<string | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunks = useRef<ArrayBuffer[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const wsTextRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { toast } = useToast();
  const router = useRouter();
  const isAudioRef = useRef(false);
  const SAMPLE_RATE = 24000;
 

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: "smooth",
      });
    }

    let phone = localStorage.getItem("userPhoneNumber");
    // Open WebSocket once on mount
    console.log(phone);
    const wsText = new WebSocket(
      `wss://chat-apiv4-675840910180.asia-south1.run.app/ws/${phone}?is_audio=false`
    );
    wsTextRef.current = wsText;

    wsTextRef.current!.onopen = () => {
      console.log("[TEXT WS OPEN]");
    };


    wsTextRef.current!.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    // wsTextRef.current.onclose = () => {
    //   console.log("[TEXT WS CLOSED]");
    // };

    // // Cleanup: close WS when navigating away/unmount
    // return () => {
    //   if (wsTextRef.current) {
    //     wsTextRef.current.close();
    //     wsTextRef.current = null;
    //   }
    // };
  }, []);

  const convertMarkdownToText = (markdown: string): string => {
  if (!markdown) return '';
  
  let html = markdown
    // First handle code blocks to protect them from other replacements
    .replace(/```([\s\S]*?)```/g, '<pre style="background-color: #f4f4f4; padding: 8px; border-radius: 4px; overflow-x: auto;"><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>')
    
    // Headers: # ## ### (must come before bold/italic)
    .replace(/^### (.*$)/gm, '<h3 style="font-size: 1.1em; font-weight: bold; margin: 8px 0 4px 0;">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 style="font-size: 1.2em; font-weight: bold; margin: 10px 0 6px 0;">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 style="font-size: 1.3em; font-weight: bold; margin: 12px 0 8px 0;">$1</h1>')
    
    // Lists BEFORE bold/italic to prevent conflicts with asterisks
    .replace(/^[\s]*\d+\.\s+(.*$)/gm, '<li style="margin-left: 20px; list-style-type: decimal;">$1</li>')
    .replace(/^[\s]*[-+]\s+(.*$)/gm, '<li style="margin-left: 20px; list-style-type: disc;">$1</li>')
    .replace(/^[\s]*\*\s+(.*$)/gm, '<li style="margin-left: 20px; list-style-type: disc;">$1</li>')
    
    // Bold text: **text** (must come before single *)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    
    // Italic text: *text* (after lists and bold)
    .replace(/\*([^*\s][^*]*[^*\s])\*/g, '<em>$1</em>')
    .replace(/_([^_\s][^_]*[^_\s])_/g, '<em>$1</em>')
    
    // Links: [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" style="color: #0066cc; text-decoration: underline;" target="_blank" rel="noopener noreferrer">$1</a>')
    
    // Convert remaining newlines to line breaks
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
    
    // Clean up any remaining literal \n that might appear as text
    .replace(/\\n/g, '<br>');

    // Wrap consecutive <li> items in <ul> or <ol> tags
    html = html.replace(/(<li[^>]*style="[^"]*decimal[^"]*"[^>]*>.*?<\/li>(?:\s*<li[^>]*style="[^"]*decimal[^"]*"[^>]*>.*?<\/li>)*)/gs, '<ol style="margin: 8px 0; padding-left: 20px;">$1</ol>');
    html = html.replace(/(<li[^>]*style="[^"]*disc[^"]*"[^>]*>.*?<\/li>(?:\s*<li[^>]*style="[^"]*disc[^"]*"[^>]*>.*?<\/li>)*)/gs, '<ul style="margin: 8px 0; padding-left: 20px;">$1</ul>');

    return html;
  };

  // Start streaming audio via WebSocket
   const startStreaming = async () => {
    audioChunks.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      const audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      // Replace with your actual WebSocket server URL:
      isAudioRef.current = true;
      let phone = localStorage.getItem("userPhoneNumber");
      const ws = new WebSocket(
        `wss://chat-apiv2-675840910180.asia-south1.run.app/ws/${phone}?is_audio=${isAudioRef.current}`
      );
      wsRef.current = ws;
      wsRef.current.onopen = () => {
        console.log("WebSocket connected");
        setIsRecording(true);
        // toast({
        //   title: "Recording started",
        //   description: "Streaming audio to server",
        // });
      };

      wsRef.current.onerror = (event) => {
        console.error("WebSocket error:", event);
        toast({
          variant: "destructive",
          title: "WebSocket Error",
          description: "An error occurred with the WebSocket connection.",
        });
        stopStreaming();
      };
  
      
      wsRef.current.onmessage = (event) => {
        console.log("ws.onmessage triggered");
        try{
        const msg = JSON.parse(event.data);
        // Handle audio
          if (msg.mime_type === "audio/pcm") {
            const audioData = base64ToArrayBuffer(msg.data);
            audioChunks.current.push(audioData);
            playPcmAudio(audioData);
          }
        }catch (error) {
          console.warn("Non-JSON message received:", event.data);
        }
        
      };
      wsRef.current!.onclose = () => {
        console.log("WebSocket closed");
      };

      processor.onaudioprocess = (e) => {
        if (ws.readyState === WebSocket.OPEN) {
          const inputBuffer = e.inputBuffer.getChannelData(0);

          // Convert Float32Array [-1,1] to 16-bit PCM
          const int16Buffer = new Int16Array(inputBuffer.length);
          for (let i = 0; i < inputBuffer.length; i++) {
            let s = Math.max(-1, Math.min(1, inputBuffer[i]));
            int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }
          audioChunks.current.push(int16Buffer.buffer);
          const base64Audio = arrayBufferToBase64(int16Buffer.buffer);
          // console.log(base64Audio);
          ws.send(
            JSON.stringify({
              mime_type: "audio/pcm",
              data: base64Audio,
            })
          );
          console.log("[CLIENT TO AGENT] sent %s bytes", int16Buffer.byteLength);
        }
      };
      source.connect(processor);
      processor.connect(audioContext.destination);
    } catch (error) {
      console.error("Error starting audio stream:", error);
      toast({
        variant: "destructive",
        title: "Microphone Error",
        description: "Unable to access microphone or start streaming.",
      });
    }
  };

  function arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  function base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }

  function encodeWAV(samples: ArrayBuffer, sampleRate = 16000): Blob {
    const buffer = samples;
    const view = new DataView(new ArrayBuffer(44 + buffer.byteLength));
    const writeString = (view: DataView, offset: number, str: string) => {
      for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
    };
  
    // RIFF chunk descriptor
    writeString(view, 0, "RIFF");
    view.setUint32(4, 36 + buffer.byteLength, true);
    writeString(view, 8, "WAVE");
    // fmt subchunk
    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true); // AudioFormat (1 = PCM)
    view.setUint16(22, 1, true); // NumChannels (1 = mono)
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, sampleRate * 2, true); // ByteRate (SampleRate * NumChannels * BitsPerSample/8)
    view.setUint16(32, 2, true); // BlockAlign (NumChannels * BitsPerSample/8)
    view.setUint16(34, 16, true); // BitsPerSample
    // data subchunk
    writeString(view, 36, "data");
    view.setUint32(40, buffer.byteLength, true);
  
    // Write PCM samples
    const pcmData = new Uint8Array(buffer);
    for (let i = 0; i < pcmData.length; i++) {
      view.setUint8(44 + i, pcmData[i]);
    }
  
    return new Blob([view], { type: "audio/wav" });
  }

  // Stop streaming and cleanup resources
  const stopStreaming = () => {
    isAudioRef.current = false;
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsRecording(false);

    if (audioChunks.current.length > 0) {
      // Concatenate
      const fullBuffer = concatArrayBuffers(audioChunks.current);
      // Convert to WAV Blob
      const wavBlob = encodeWAV(fullBuffer, SAMPLE_RATE);
      // Create URL
      const audioUrl = URL.createObjectURL(wavBlob);
    
      // ✅ Update messages
      setMessages((prev) => {
        const alreadyExists = prev.some((msg) => msg.audioUrl === audioUrl);
        if (!alreadyExists) {
          return [
            ...prev,
            {
              id: Date.now().toString(),
              role: "user",
              content: "",
              audioUrl,
            },
          ];
        }
        return prev;
      });
    
      // ✅ Now call toast separately
      toast({
        title: "Recording stopped",
        description: "Stopped streaming audio",
      });
    }
  }


  const sampleRate = 24000;
  const audioQueue: AudioBufferSourceNode[] = [];
  let isPlaying = false;

  async function playPcmAudio(buffer: ArrayBuffer) {

    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate,
      });
    }
    const audioCtx = audioContextRef.current;
  
    // Resume if suspended (browser autoplay policy)
    if (audioCtx.state === "suspended") {
      await audioCtx.resume();
    }
    
    const pcmData = new Int16Array(buffer);
    const float32Data = new Float32Array(pcmData.length);
  
    for (let i = 0; i < pcmData.length; i++) {
      float32Data[i] = pcmData[i] / 32768;
    }
  
    const audioBuffer = audioCtx.createBuffer(1, float32Data.length, SAMPLE_RATE);
    audioBuffer.copyToChannel(float32Data, 0);
  
    const source = audioCtx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioCtx.destination);
  
    source.onended = () => {
      audioQueue.shift(); // remove played buffer
      if (audioQueue.length > 0) {
        audioQueue[0].start();
      } else {
        isPlaying = false;
      }
    };
  
    audioQueue.push(source);
  
    if (!isPlaying) {
      isPlaying = true;
      source.start();
    }
  }

  function concatArrayBuffers(buffers: ArrayBuffer[]) {
    const totalLength = buffers.reduce((acc, buf) => acc + buf.byteLength, 0);
    const temp = new Uint8Array(totalLength);
    let offset = 0;
  
    for (const buf of buffers) {
      temp.set(new Uint8Array(buf), offset);
      offset += buf.byteLength;
    }
    return temp.buffer;
  }

   // Toggle streaming on mic button click
   const handleVoiceInput = async () => {
    if (isRecording) {
      stopStreaming();
    } else {
      await startStreaming();
    }
  };

  const handleSendMessage = (content: string) => {
    handleTextClick(content);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if(input.trim()) {
      handleSendMessage(input);
    }
  };

  const handleSendPhoto = async (photoDataUrl: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: "",
      photoUrl: photoDataUrl,
    };
    setMessages((prev) => [...prev, newMessage]);
    setIsCameraOpen(false);

    try {
      const base64 = photoDataUrl.split(",")[1];
      const response = await fetch("https://chat-apiv4-675840910180.asia-south1.run.app/analyze-image/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          base64image:base64
        })
      });
  
      const result = await response.text();
      console.log(result);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: result || "Processed image response.",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Error sending image:", err);
      toast({
        variant: "destructive",
        title: "Image Processing Error",
        description: "Failed to send image to server.",
      });
    }
  };


  // Upload button triggers hidden input click
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleTextClick = (messageToSend: string) => {
    console.log(messageToSend);
    setInput("");
    setIsLoading(true);
  
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageToSend,
    };
    setMessages((prev) => [...prev, userMessage]);
  
    
      wsTextRef.current!.send(
        JSON.stringify({
          mime_type: "text/plain",
          data: messageToSend,
        })
      );

    let fullMessage = "";
    wsTextRef.current!.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        console.log("[SERVER TO CLIENT TEXT]:", msg);
  
        if (msg.mime_type === "text/plain") {
          fullMessage += msg.data;
        }
  
        if (msg.turn_complete === true) {
          const botMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: fullMessage,
          };
          setMessages((prev) => [...prev, botMessage]);
          setIsLoading(false);
        }
      } catch (error) {
        console.warn("Non-JSON message received:", event.data);
      }
    };
  
    wsTextRef.current!.onerror = (error) => {
      console.error("WebSocket error:", error);
      toast({
        variant: "destructive",
        title: "WebSocket Error",
        description: "Could not send message.",
      });
      setIsLoading(false);
    };

  };
  

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
  
    // Check if the file is an image
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          const photoDataUrl = event.target.result as string;
  
          // ✅ Call your existing send photo handler
          handleSendPhoto(photoDataUrl);
        }
      };
      reader.readAsDataURL(file);
    } else {
      // Handle other file types if needed
      toast({
        title: "Unsupported File",
        description: `Only images are supported right now.`,
        variant: "destructive",
      });
    }
  
    // Reset the input so selecting the same file again works
    e.target.value = "";
  };
  
  
  const handleReadAloud = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.cancel(); // Cancel any previous speech
      window.speechSynthesis.speak(utterance);
    } else {
      toast({
        variant: "destructive",
        title: "Browser Not Supported",
        description: "Your browser does not support the text-to-speech feature.",
      });
    }
  };

  if (isCameraOpen) {
    return <CameraView onSend={handleSendPhoto} onClose={() => setIsCameraOpen(false)} />;
  }

  if (fullscreenImage) {
    return (
      <div 
        className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center"
        onClick={() => setFullscreenImage(null)}
      >
        <img src={fullscreenImage} alt="Fullscreen" className="max-w-full max-h-full object-contain" />
        <Button 
          variant="ghost" 
          size="icon" 
          className="absolute top-4 right-4 text-white hover:text-white hover:bg-white/10"
          onClick={() => setFullscreenImage(null)}
        >
          <X className="h-6 w-6" />
        </Button>
      </div>
    );
  }


  return (
    <div className="flex flex-col h-screen bg-secondary">
      <header className="flex items-center justify-between p-4 bg-background border-b shadow-sm">
        <Logo />
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/profile")}
          aria-label="Profile"
        >
          <UserCircle className="h-6 w-6" />
        </Button>
      </header>

      <main className="flex-1 overflow-hidden">
        <ScrollArea className="h-full" ref={scrollAreaRef}>
          <div className="p-4 md:p-6 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex items-start gap-4",
                  message.role === "user" && "justify-end"
                )}
              >
                {message.role === "assistant" && (
                  <Avatar className="h-9 w-9 border">
                    <AvatarFallback>
                      <Bot className="h-5 w-5 text-primary" />
                    </AvatarFallback>
                  </Avatar>
                )}
                <div
                  className={cn(
                    "flex items-start gap-2 max-w-md rounded-xl p-3 shadow-sm",
                     message.role === "user" ? "bg-primary text-primary-foreground" : "bg-background text-foreground",
                     (message.photoUrl || message.audioUrl) && "p-2" // Less padding for media
                  )}
                >
                  <div className="flex-grow whitespace-pre-wrap">
                    {message.category && categoryIcons[message.category] && (
                      <div className="flex items-center gap-2 mb-2 text-xs font-semibold opacity-80">
                        {categoryIcons[message.category]}
                        <span>
                          {message.category.charAt(0).toUpperCase() +
                            message.category.slice(1)}
                        </span>
                      </div>
                    )}
                    {message.photoUrl ? (
                      <img 
                        src={message.photoUrl} 
                        alt="User submission" 
                        className="rounded-lg max-w-xs w-full cursor-pointer"
                        onClick={() => setFullscreenImage(message.photoUrl!)}
                      />
                    ) : message.audioUrl ? (
                      <AudioPlayer
                        src={message.audioUrl}
                        isUser={message.role === "user"}
                      />
                    ) : (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: convertMarkdownToText(message.content),
                        }}
                      />
                    )}
                  </div>

                  {message.content && !message.audioUrl && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 shrink-0 self-start"
                      onClick={() => handleReadAloud(message.content)}
                    >
                      <Volume2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                {message.role === "user" && (
                  <Avatar className="h-9 w-9 border">
                    <AvatarFallback>
                      <User className="h-5 w-5 text-primary" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start gap-4">
                <Avatar className="h-9 w-9 border">
                  <AvatarFallback>
                  <Bot className="h-5 w-5 text-primary" />
                  </AvatarFallback>
                </Avatar>
                <div className="max-w-md rounded-xl p-3 shadow-sm bg-background text-foreground space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-48" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </main>

      <footer className="p-4 bg-background border-t">
        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about crops, market prices, or anything else..."
            className="flex-1 resize-none"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(input);
              }
            }}
          />
          <Button
            type="button"
            size="icon"
            variant="ghost"
            onClick={handleVoiceInput}
            className={cn(isRecording && "text-red-500 animate-pulse")}
            aria-label={isRecording ? "Stop recording" : "Start recording"}
          >
            <Mic className="h-5 w-5" />
          </Button>
           <Button 
             type="button"
             size="icon"
             variant="ghost"
             onClick={() => setIsCameraOpen(true)}
             aria-label="Open camera"
           >
             <Camera className="h-5 w-5" />
           </Button>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            onClick={handleUploadClick}
            aria-label="Upload file"
          >
            <Upload className="h-5 w-5" />
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*"
          />
          <Button
            type="submit"
            size="icon"
            className="bg-accent hover:bg-accent/90"
            disabled={isLoading || !input.trim()}
            onClick={handleSubmit}
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </form>
        <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
          <CornerDownLeft className="h-3 w-3" /> Shift+Enter for new line.
        </p>
      </footer>
    </div>
  );
}

    