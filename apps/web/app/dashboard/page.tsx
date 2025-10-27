"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useToast } from "hooks/use-toast";

const API_URL = "http://localhost:5001/api";

export default function Dashboard() {
  const [cameraActive, setCameraActive] = useState(false);
  const [detectionResult, setDetectionResult] = useState<any>(null);
  const [knownFaces, setKnownFaces] = useState<string[]>([]);
  const [newPersonName, setNewPersonName] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  // Load known faces on mount
  useEffect(() => {
    fetchKnownFaces();
    checkCameraStatus();
  }, []);

  const checkCameraStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/camera/status`);
      const data = await res.json();
      setCameraActive(data.active);
    } catch (error) {
      console.error("Failed to check camera status", error);
    }
  };

  const fetchKnownFaces = async () => {
    try {
      const res = await fetch(`${API_URL}/face/list`);
      const data = await res.json();
      setKnownFaces(data.faces);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load known faces",
        variant: "destructive",
      });
    }
  };

  const toggleCamera = async () => {
    try {
      const endpoint = cameraActive ? "stop" : "start";
      const res = await fetch(`${API_URL}/camera/${endpoint}`, {
        method: "POST",
      });
      
      if (res.ok) {
        setCameraActive(!cameraActive);
        toast({
          title: cameraActive ? "Camera Stopped" : "Camera Started",
          description: `Camera is now ${cameraActive ? "inactive" : "active"}`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to toggle camera",
        variant: "destructive",
      });
    }
  };

  const runDetection = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_URL}/detect`, {
        method: "POST",
      });
      const data = await res.json();
      setDetectionResult(data);
      
      toast({
        title: "Detection Complete",
        description: `Found ${data.objects.length} objects and ${data.faces.length} faces`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Detection failed",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const describeScene = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_URL}/describe`, {
        method: "POST",
      });
      const data = await res.json();
      
      toast({
        title: "Scene Description",
        description: data.description,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to describe scene",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const addPerson = async () => {
    if (!newPersonName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a name",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    try {
      const res = await fetch(`${API_URL}/face/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newPersonName }),
      });
      
      const data = await res.json();
      
      if (res.ok) {
        toast({
          title: "Success",
          description: data.message,
        });
        setNewPersonName("");
        fetchKnownFaces();
      } else {
        toast({
          title: "Error",
          description: data.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add person",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const deletePerson = async (name: string) => {
    try {
      const res = await fetch(`${API_URL}/face/delete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      
      const data = await res.json();
      
      if (res.ok) {
        toast({
          title: "Success",
          description: data.message,
        });
        fetchKnownFaces();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete person",
        variant: "destructive",
      });
    }
  };

  const listenForVoiceCommand = async () => {
    setIsProcessing(true);
    toast({
      title: "Listening...",
      description: "Speak your command now",
    });

    try {
      const res = await fetch(`${API_URL}/voice/listen`, {
        method: "POST",
      });
      const data = await res.json();
      
      if (data.status === "success") {
        toast({
          title: `You said: "${data.text}"`,
          description: data.response,
        });
        
        // Refresh data after voice command
        runDetection();
        fetchKnownFaces();
      } else {
        toast({
          title: "No speech detected",
          description: "Please try again",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Voice recognition failed",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl font-bold text-white mb-8"
        >
          Vision-Mate Dashboard
        </motion.h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Camera Control */}
          <Card className="p-6 bg-slate-900 border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Camera</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Status:</span>
                <span className={`font-semibold ${cameraActive ? "text-green-500" : "text-red-500"}`}>
                  {cameraActive ? "Active" : "Inactive"}
                </span>
              </div>
              <Button
                onClick={toggleCamera}
                className="w-full"
                variant={cameraActive ? "destructive" : "default"}
              >
                {cameraActive ? "Stop Camera" : "Start Camera"}
              </Button>
            </div>
          </Card>

          {/* Detection Controls */}
          <Card className="p-6 bg-slate-900 border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Detection</h2>
            <div className="space-y-3">
              <Button
                onClick={runDetection}
                disabled={!cameraActive || isProcessing}
                className="w-full"
              >
                🔍 Detect Objects & Faces
              </Button>
              <Button
                onClick={describeScene}
                disabled={!cameraActive || isProcessing}
                className="w-full"
                variant="secondary"
              >
                📝 Describe Scene (Voice)
              </Button>
              <Button
                onClick={listenForVoiceCommand}
                disabled={isProcessing}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                🎤 Voice Command
              </Button>
            </div>
          </Card>

          {/* Face Management */}
          <Card className="p-6 bg-slate-900 border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Add Person</h2>
            <div className="space-y-3">
              <div>
                <Label htmlFor="personName" className="text-gray-400">Name</Label>
                <Input
                  id="personName"
                  value={newPersonName}
                  onChange={(e) => setNewPersonName(e.target.value)}
                  placeholder="Enter person's name"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <Button
                onClick={addPerson}
                disabled={!cameraActive || isProcessing}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                💾 Save Person
              </Button>
            </div>
          </Card>
        </div>

        {/* Detection Results */}
        {detectionResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <Card className="p-6 bg-slate-900 border-slate-700">
              <h2 className="text-xl font-semibold text-white mb-4">Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-300 mb-2">Objects Detected</h3>
                  <ul className="space-y-2">
                    {detectionResult.objects.map((obj: any, idx: number) => (
                      <li key={idx} className="text-gray-400">
                        {obj.label} ({(obj.confidence * 100).toFixed(1)}%)
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-300 mb-2">Faces Detected</h3>
                  <ul className="space-y-2">
                    {detectionResult.faces.map((face: any, idx: number) => (
                      <li key={idx} className="text-gray-400">
                        {face.name}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {detectionResult.annotated_image && (
                <div className="mt-4">
                  <img
                    src={detectionResult.annotated_image}
                    alt="Detection result"
                    className="w-full rounded-lg"
                  />
                </div>
              )}
            </Card>
          </motion.div>
        )}

        {/* Known Faces */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6"
        >
          <Card className="p-6 bg-slate-900 border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Known Faces ({knownFaces.length})</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {knownFaces.map((name, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-800 rounded-lg flex items-center justify-between"
                >
                  <span className="text-white">{name}</span>
                  <Button
                    onClick={() => deletePerson(name)}
                    variant="destructive"
                    size="sm"
                  >
                    ✕
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
