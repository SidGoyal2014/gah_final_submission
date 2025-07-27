// /public/audioWorkletProcessor.js

class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
      super();
    }
  
    process(inputs, outputs, parameters) {
      const input = inputs[0];
      if (input.length > 0) {
        const channelData = input[0];
        // Send Float32Array audio data to the main thread
        this.port.postMessage(channelData);
      }
      return true;
    }
  }
  
  registerProcessor('audio-processor', AudioProcessor);
  