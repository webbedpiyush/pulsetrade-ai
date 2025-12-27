"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Activity, Mic, Zap, BarChart2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// --- Crypto Edition Landing Page ---

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-400 flex items-center justify-center text-white font-bold text-lg">
              P
            </div>
            <span className="font-bold text-xl">PulseTrade AI</span>
            <Badge variant="secondary" className="ml-2">Crypto Edition</Badge>
          </div>

          <Link href="/dashboard">
            <Button className="bg-emerald-600 hover:bg-emerald-500">
              Launch Dashboard
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge className="mb-4 bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
              Hackathon Project
            </Badge>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white via-emerald-200 to-cyan-400 bg-clip-text text-transparent">
              Real-Time Crypto
              <br />
              Voice Intelligence
            </h1>

            <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
              Stream Binance trades through Kafka, analyze with Gemini AI,
              and hear market insights through ElevenLabs voice synthesis.
            </p>

            <div className="flex gap-4 justify-center">
              <Link href="/dashboard">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-500 text-lg px-8">
                  Open Dashboard
                  <ArrowRight className="ml-2" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 border-t border-white/5">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Powered By</h2>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { name: "Binance", desc: "WebSocket Streaming", icon: Activity },
              { name: "Confluent", desc: "Kafka Pipeline", icon: Zap },
              { name: "Gemini", desc: "AI Analysis", icon: BarChart2 },
              { name: "ElevenLabs", desc: "Voice Synthesis", icon: Mic },
            ].map((tech) => (
              <div
                key={tech.name}
                className="p-6 rounded-xl bg-slate-900 border border-slate-800 text-center"
              >
                <tech.icon className="w-8 h-8 mx-auto mb-3 text-emerald-400" />
                <h3 className="font-semibold mb-1">{tech.name}</h3>
                <p className="text-sm text-slate-500">{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 text-center text-slate-500 text-sm">
        Built for hackathon by @webbedpiyush
      </footer>
    </main>
  );
}
