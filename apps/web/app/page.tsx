"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-4xl w-full"
      >
        <Card className="p-12 bg-white/10 backdrop-blur-lg border-white/20">
          <h1 className="text-6xl font-bold text-white mb-4 text-center">
            Vision-Mate
          </h1>
          <p className="text-xl text-gray-300 mb-8 text-center">
            Your intelligent vision assistant powered by AI
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <FeatureCard
              title="Object Detection"
              description="Real-time YOLO-powered object recognition"
              icon="🔍"
            />
            <FeatureCard
              title="Face Recognition"
              description="Identify and remember people instantly"
              icon="👤"
            />
            <FeatureCard
              title="Voice Control"
              description="Hands-free operation with natural speech"
              icon="🎤"
            />
          </div>

          <div className="flex justify-center">
            <Button
              onClick={() => router.push("/dashboard")}
              className="text-lg px-8 py-6 bg-purple-600 hover:bg-purple-700"
              size="lg"
            >
              Launch Dashboard
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}

function FeatureCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="p-6 bg-white/5 rounded-lg border border-white/10"
    >
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </motion.div>
  );
}
