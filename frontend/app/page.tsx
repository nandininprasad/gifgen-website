'use client'
import React, { useState, useRef, useEffect, ChangeEvent, DragEvent } from 'react'
import { SparklesText } from '@/components/magicui/sparkles-text'
import { ShinyButton } from "@/components/magicui/shiny-button";
import { CoolMode } from "@/components/magicui/cool-mode";
import {
  ArrowUpTrayIcon,
  TrashIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline'

// Helper function to convert a File object to a Base64 Data URL string
async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file); // Reads the file as "data:image/png;base64,..."
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
  });
}

export default function Page() {
  /* ───────── Placeholder Typewriter Setup ───────── */
  const placeholders = [
    'A cat playing a piano in space...',
    'A dog skateboarding and wearing sunglasses',
    'Lo-fi vibes, girl studying at her desk',
    'Abstract colorful liquid motion',
  ]
  const [placeholder, setPlaceholder] = useState('')
  const indexRef = useRef(0)
  const typeInterval = useRef<number>()
  const deleteInterval = useRef<number>()
  
  const API_ADDRESS = "http://gifgen.nandiniprasad.me/api/generate_gif"; // Ensure this is HTTPS if Cloudflare provides it

  useEffect(() => {
    const typeText = (text: string) => {
      let i = 0
      typeInterval.current = window.setInterval(() => {
        if (i < text.length) {
          setPlaceholder(prev => prev + text.charAt(i))
          i++
        } else {
          clearInterval(typeInterval.current)
          setTimeout(() => deleteText(), 2000)
        }
      }, 100)
    }

    const deleteText = () => {
      let text = placeholders[indexRef.current]
      let i = text.length
      deleteInterval.current = window.setInterval(() => {
        if (i > 0) {
          i--
          setPlaceholder(text.slice(0, i))
        } else {
          clearInterval(deleteInterval.current)
          indexRef.current = (indexRef.current + 1) % placeholders.length
          setTimeout(() => typeText(placeholders[indexRef.current]), 500)
        }
      }, 50)
    }

    typeText(placeholders[indexRef.current])
    return () => {
      clearInterval(typeInterval.current)
      clearInterval(deleteInterval.current)
    }
  }, [])

  /* ───────── Component State ───────── */
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('Realistic')
  const [file, setFile] = useState<File | null>(null) // State for the selected File object
  const [showStyleOptions, setShowStyleOptions] = useState(false)
  const styleDropdownRef = useRef<HTMLDivElement>(null)

  const [generatedGifUrl, setGeneratedGifUrl] = useState<string | null>(null)
  const [generatedGifName, setGeneratedGifName] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)


  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (styleDropdownRef.current && !styleDropdownRef.current.contains(e.target as Node)) {
        setShowStyleOptions(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  async function handleGenerate() {
    console.log("GENERATE BUTTON CLICKED");
    setErrorMessage(null);
    setGeneratedGifUrl(null);
    setGeneratedGifName(null);
    setIsLoading(true);

    console.log("Prompt: ", prompt);
    console.log("Style: ", style);

    if (prompt.trim() === "" || style.trim() === '') {
      setErrorMessage("Please provide both a prompt and a style.");
      setIsLoading(false);
      return;
    }
    
    console.log("CONDITIONS SATISFIED");
    
    let imageBase64Data: string | null = null; // Will hold the Base64 Data URL or null

    if (file) { // Check if a file is selected in the state
      try {
        console.log("Converting uploaded image to Base64...");
        imageBase64Data = await fileToBase64(file); // Convert the File object
        // console.log("Image converted (first 100 chars):", imageBase64Data.substring(0, 100));
      } catch (error) {
        console.error("Error converting file to Base64:", error);
        setErrorMessage("Failed to process the uploaded image. Please try again.");
        setIsLoading(false);
        return; 
      }
    }

    const requestPayload = {
      "text_prompt": prompt,
      "style_string": style,
      "image": imageBase64Data // Send the Base64 Data URL string, or null if no file was selected/processed
    };

    console.log("Trying to send payload (image data might be long, showing type): ", 
        {...requestPayload, image_type: imageBase64Data ? typeof imageBase64Data : null }
    );

    try {
      const response = await fetch(API_ADDRESS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload)
      });
      
      console.log("Sent request to server.");
      console.log("Response status code: ", response.status);
      console.log("Response ok? ", response.ok);

      const serverResponseData = await response.json();
      console.log("Parsed server response data:", serverResponseData);

      if (!response.ok) {
        const errorMsg = `Server Error (${response.status}): ${serverResponseData.message || serverResponseData.error || 'Unknown server error.'}`;
        throw new Error(errorMsg);
      }

      const gifNameFromServer = serverResponseData["gif-name"];
      const chatgptPromptFromServer = serverResponseData["chatgpt-prompt"];
      const gifBase64DataFromServer = serverResponseData["gif-data"];
      const gifMimetype = serverResponseData["mimetype"];

      if (!gifBase64DataFromServer || !gifMimetype) {
        throw new Error("Received incomplete GIF data from server.");
      }

      setPrompt(chatgptPromptFromServer);
      setGeneratedGifName(gifNameFromServer);

      const gifDataURL = `data:${gifMimetype};base64,${gifBase64DataFromServer}`;
      setGeneratedGifUrl(gifDataURL);
      console.log("GIF processed and ready for display.");

    } catch (error: any) {
      console.error("Error during fetch or processing:", error);
      setErrorMessage(error.message || "An unexpected error occurred.");
      setGeneratedGifUrl(null);
      setGeneratedGifName(null);
    } finally {
      setIsLoading(false);
    }
  }
  
  // ... (handleFile, handleFileChange, handleDrop, handleRemoveFile, handleDownloadGif, and JSX return remain the same as the last version) ...
  // Ensure these handlers correctly update the `file` state. For example:
  const handleFile = (f: File) => {
    setFile(f); // This sets the selected file into state
    setGeneratedGifUrl(null); 
    setErrorMessage(null);
  }
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
        handleFile(e.target.files[0]);
    }
  }
  const handleDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
    }
  }
  const handleRemoveFile = () => {
    setFile(null); // Clears the file from state
    setGeneratedGifUrl(null); 
  }

  const handleDownloadGif = () => {
    if (generatedGifUrl && generatedGifName) {
      const link = document.createElement('a');
      link.href = generatedGifUrl;
      link.download = `${generatedGifName.replace(/[^a-z0-9_.-]/gi, '_')}.gif`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <main
      className="min-h-screen bg-black text-white flex flex-col items-center py-10 px-4
                     bg-[radial-gradient(var(--tw-gradient-stops))]
                     from-transparent via-transparent to-transparent
                     [--tw-gradient-stops:theme(colors.white/5)_0%,theme(colors.white/5)_1px,transparent_1px]
                     [background-size:20px_20px]"
    >
      {/* Hero */}
      <header className="py-10 md:py-20 px-6 text-center">
        <SparklesText className="block text-6xl md:text-8xl lg:text-9xl font-extrabold">
          GIFgen
        </SparklesText>
      </header>

      {/* Input Container */}
      <div
        className="relative z-10 w-[90vw] max-w-6xl rounded-2xl p-6 md:p-8 mb-10
                     bg-[rgba(35,35,38,0.8)] border border-[#35353a]
                      flex flex-col md:flex-row gap-6"
      >
        {/* Left column */}
        <div className="flex-1 space-y-6">
          {/* Prompt textarea */}
          <div>
            <label
              htmlFor="prompt"
              className="block text-sm font-medium text-gray-300 mb-1"
            >
              Describe your GIF
            </label>
            <textarea
              id="prompt"
              rows={4}
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder={placeholder}
              className="w-full bg-black/30 border border-white/20 rounded
                         px-4 py-2 text-white placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-indigo-500
                         resize-vertical"
            />
          </div>

          {/* Style + Generate Button */}
          <div className="flex items-center justify-between">
            {/* Style dropdown */}
            <div className="flex items-center space-x-2 cursor-pointer group relative" ref={styleDropdownRef}>
              <div onClick={() => setShowStyleOptions(v => !v)} className="flex flex-col">
                <div className="text-xs uppercase tracking-widest text-[#a1a1aa] font-semibold">
                  Style
                </div>
                <div className="flex items-center text-white font-semibold">
                  {style || 'Realistic'}
                  <svg
                    className="ml-1 w-4 h-4 text-[#a1a1aa] group-hover:text-white transition"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              {showStyleOptions && (
                <div className="absolute left-0 mt-2 bg-[#232326] border border-[#35353a] rounded-lg shadow-lg z-20 top-full min-w-[120px]">
                  {['Realistic', 'Animation', 'Painting'].map(option => (
                    <div
                      key={option}
                      className="px-4 py-2 hover:bg-[#35353a] cursor-pointer"
                      onClick={() => {
                        setStyle(option)
                        setShowStyleOptions(false)
                      }}
                    >
                      {option}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Generate GIF button */}
            <CoolMode>
            <ShinyButton
              onClick={handleGenerate}
              disabled={isLoading}
              className="px-4 py-2 bg-[#e2e2e2] hover:bg-white rounded-md font-semibold text-black disabled:opacity-50"
            >
              {isLoading ? 'Generating...' : 'Generate GIF'}
            </ShinyButton>
            </CoolMode>
          </div>
        </div>

        {/* Right column – uploader */}
        <div className="w-full md:w-80 space-y-4">
          <label
            htmlFor="file"
            onDragOver={e => e.preventDefault()}
            onDrop={handleDrop}
            className="group flex flex-col items-center justify-center
                       h-60 rounded-xl cursor-pointer bg-black/20
                       border-2 border-dashed border-white/30
                       transition hover:bg-white/5"
          >
            <ArrowUpTrayIcon className="h-16 w-16 text-gray-400 mb-4 group-hover:text-gray-200" />
            <p className="text-lg font-medium">(Optional)</p>
            <p className="text-center text-sm text-gray-300">
              Browse&nbsp;or&nbsp;Drag&nbsp;&amp;&nbsp;Drop&nbsp;File&nbsp;to&nbsp;Upload
            </p>
            <input
              id="file"
              type="file" 
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>

          {file && (
            <div className="flex items-center justify-between px-4 py-2 bg-black/30 rounded-lg border border-white/15">
                <div className="flex items-center gap-2 overflow-hidden">
                  <DocumentTextIcon className="h-5 w-5 text-indigo-400" />
                  <span className="truncate text-sm">{file.name}</span>
                </div>
                <button
                  onClick={handleRemoveFile}
                  className="p-1 hover:text-red-400 text-gray-300"
                  aria-label="Remove file"
                >
                  <TrashIcon className="h-5 w-5" />
                </button>
            </div>
          )}
           {!file && (
             <div className="flex items-center justify-center px-4 py-2 bg-black/30 rounded-lg border border-white/15 h-[42px]">
                <span className="text-sm text-gray-400">No file selected</span>
             </div>
           )}
        </div>
      </div>

      {/* GIF Display Area */}
      {(isLoading || errorMessage || generatedGifUrl) && (
        <div className="w-[90vw] max-w-6xl rounded-2xl p-6 md:p-8 mt-10
                        bg-[rgba(35,35,38,0.8)] border border-[#35353a]">
          {isLoading && (
            <div className="text-center py-10">
              <p className="text-xl font-semibold animate-pulse">Generating your GIF, please wait...</p>
            </div>
          )}
          {errorMessage && (
            <div className="text-center py-10 text-red-400">
              <p className="text-xl font-semibold">Error:</p>
              <p>{errorMessage}</p>
            </div>
          )}
          {generatedGifUrl && !isLoading && !errorMessage && (
            <div className="text-center"> 
              {generatedGifName && (
                <h2 className="text-2xl font-semibold mb-4">{generatedGifName}</h2>
              )}
              <img
                src={generatedGifUrl}
                alt={generatedGifName || 'Generated GIF'}
                className="max-w-full h-auto mx-auto rounded-lg border border-white/20 mb-6" 
                style={{ maxHeight: '70vh' }}
              />
              <div className="flex justify-center mt-4">
                <CoolMode>
                  <ShinyButton
                    onClick={handleDownloadGif}
                    className="px-6 py-3 bg-gray-500 hover:bg-gray-600 rounded-md font-semibold text-white flex items-center justify-center gap-2"
                  >
                    <ArrowDownTrayIcon className="h-5 w-5" />
                    Download GIF
                  </ShinyButton>
                </CoolMode>
              </div>
            </div>
          )}
        </div>
      )}
    </main>
  )
}