"use client";
// forcing rebuild

import Link from "next/link";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowRight, BarChart2, Brain, Radio, Shield, Zap, Play, CheckCircle2, TrendingUp, Mic, Globe, Activity } from "lucide-react";
import { SignInButton, SignedIn, SignedOut } from "@clerk/nextjs";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

// --- Components ---

function FloatingNavbar() {
  return (
    <div className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4">
      <nav className="bg-slate-900/40 backdrop-blur-md border border-white/10 rounded-full px-6 py-3 flex items-center gap-8 shadow-2xl shadow-brand-900/20">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-500 to-cyan-400 flex items-center justify-center text-white font-serif font-bold text-lg">P</div>
          <span className="font-serif font-bold text-white tracking-tight hidden sm:block">PulseTrade AI</span>
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-1 bg-white/5 rounded-full px-2 py-1 border border-white/5">
          <Link href="#features" className="px-4 py-1.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-full transition-all">Features</Link>
          <Link href="#how-it-works" className="px-4 py-1.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-full transition-all">How it works</Link>
          <Link href="#pricing" className="px-4 py-1.5 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-full transition-all">Pricing</Link>
        </div>

        <div className="flex items-center gap-3">
          <SignedIn>
            <Link href="/dashboard">
              <Button variant="secondary" size="sm" className="rounded-full bg-white text-slate-900 hover:bg-slate-200 font-medium">Dashboard</Button>
            </Link>
          </SignedIn>
          <SignedOut>
            <Link href="/sign-in" className="text-sm font-medium text-slate-400 hover:text-white hidden sm:block">Login</Link>
            <Link href="/sign-up">
              <Button size="sm" className="rounded-full bg-brand-600 hover:bg-brand-500 text-white border border-brand-400/20 shadow-[0_0_15px_-3px_rgba(14,165,233,0.4)]">
                Get Started
              </Button>
            </Link>
          </SignedOut>
        </div>
      </nav>
    </div>
  );
}

function Marquee({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative w-full overflow-hidden mask-gradient-x border-y border-white/5 bg-white/[0.02]">
      <div className="flex w-max animate-marquee gap-16 items-center py-8">
        {children}
        {children}
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description, delay = 0 }: { icon: React.ReactNode, title: string, description: string, delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="h-full bg-slate-900/40 border-white/10 p-6 hover:bg-slate-800/40 transition-colors group relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="w-12 h-12 rounded-xl bg-slate-800/50 flex items-center justify-center mb-4 text-brand-400 group-hover:scale-110 transition-transform">
          {icon}
        </div>
        <h3 className="text-xl font-serif font-medium text-white mb-2">{title}</h3>
        <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
      </Card>
    </motion.div>
  );
}

function BeamBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
      <div className="absolute -top-[20%] left-[20%] w-[60%] h-[60%] bg-brand-900/20 blur-[150px] rounded-full mix-blend-screen animate-pulse-slow" />
      <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] bg-cyan-900/20 blur-[120px] rounded-full mix-blend-screen" />

      <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-brand-500/10 to-transparent animate-beam" />
      <div className="absolute top-0 right-1/4 w-px h-full bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent animate-beam [animation-delay:2s]" />

      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />
    </div>
  );
}

// --- Main Page ---

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 selection:bg-brand-500/30 overflow-x-hidden font-sans">
      <FloatingNavbar />

      {/* Hero Section */}
      <section className="relative pt-40 pb-20 md:pt-52 md:pb-32 overflow-hidden min-h-screen flex flex-col items-center text-center px-4">
        <BeamBackground />

        <motion.div style={{ opacity }} className="max-w-4xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-semibold tracking-wide uppercase mb-8 backdrop-blur-md"
          >
            <Zap className="w-3 h-3 fill-current" />
            Real-time Market Intelligence
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl md:text-7xl font-serif font-medium tracking-tight mb-8 leading-[1.1] text-white"
          >
            Trade at the Speed of <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-300 via-cyan-300 to-brand-300 italic">AI Intuition.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto font-light leading-relaxed"
          >
            PulseTrade AI combines <strong>Gemini 2.5</strong> multimodal analysis with <strong>ElevenLabs</strong> voice synthesis to give you a superhuman edge in the <strong>NIFTY 50</strong>.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link href="/sign-up">
              <Button size="lg" className="rounded-full bg-brand-600 hover:bg-brand-500 text-white px-8 h-12 text-base shadow-[0_0_20px_-5px_rgba(14,165,233,0.5)]">
                Start Trading Free <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <Link href="#demo">
              <Button variant="outline" size="lg" className="rounded-full border-slate-700 text-slate-300 hover:text-white hover:bg-white/5 h-12 px-8">
                <Play className="mr-2 w-4 h-4" /> Live Demo
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Social Proof */}
      <div className="py-12 border-t border-white/5 bg-white/[0.01]">
        <div className="text-center mb-6 text-xs font-semibold text-slate-600 uppercase tracking-widest">Powered By Industry Leaders</div>
        <Marquee>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><Brain className="w-6 h-6" /> Gemini 2.5</div>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><Mic className="w-6 h-6" /> ElevenLabs</div>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><Globe className="w-6 h-6" /> NSE India</div>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><TrendingUp className="w-6 h-6" /> TradingView</div>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><Zap className="w-6 h-6" /> WebSocket</div>
          <div className="flex items-center gap-2 text-slate-500 font-sans font-semibold text-xl opacity-60"><Shield className="w-6 h-6" /> Next.js 14</div>
        </Marquee>
      </div>

      {/* Features Grid */}
      <section id="features" className="py-24 relative bg-[#020617]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <Badge variant="outline" className="mb-4 border-brand-500/30 text-brand-300 bg-brand-500/5">Features 2.0</Badge>
            <h2 className="text-3xl md:text-5xl font-serif font-medium mb-6 text-white">
              The Unfair Advantage
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto text-lg font-light">
              Why read charts when your AI assistant can watch them for you?
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon={<Brain className="w-6 h-6" />}
              title="Gemini 2.5 Intelligence"
              description="Multimodal analysis that understands market context, pattern recognition, and sentiment - updated every second."
            />
            <FeatureCard
              delay={0.1}
              icon={<Radio className="w-6 h-6" />}
              title="ElevenLabs Voice Alerts"
              description="Hear the market. Realistic voice synthesis announces breakouts, reversals, and volume spikes instantly."
            />
            <FeatureCard
              delay={0.2}
              icon={<Activity className="w-6 h-6" />}
              title="NIFTY 50 Live"
              description="Full coverage of India's top 50 stocks with real-time data ingestion and minimal latency."
            />
            <FeatureCard
              delay={0.3}
              icon={<BarChart2 className="w-6 h-6" />}
              title="Technical Vision"
              description="Auto-calculation of SMA, VWAP, RSI, and Bollinger Bands. The AI sees every crossover."
            />
            <FeatureCard
              delay={0.4}
              icon={<Shield className="w-6 h-6" />}
              title="Secure Portfolios"
              description="Personalized watchlists with encrypted user data. Only receive intelligence on stocks you own."
            />
            <FeatureCard
              delay={0.5}
              icon={<Zap className="w-6 h-6" />}
              title="75ms Latency"
              description="Built on a high-performance WebSocket architecture. Be faster than the institutional algos."
            />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 bg-slate-950 border-t border-white/5 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-brand-900/10 to-transparent pointer-events-none" />

        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <h2 className="text-4xl md:text-6xl font-serif text-white mb-8 tracking-tight">
            Ready to upgrade your <br />
            <span className="text-brand-300 italic">trading desk?</span>
          </h2>

          <p className="text-slate-400 mb-12 text-lg">
            Join hundreds of traders using AI to navigate the NIFTY 50.
          </p>

          <Link href="/sign-up">
            <Button size="lg" className="rounded-full bg-white text-slate-950 hover:bg-slate-200 px-10 h-14 text-lg font-bold shadow-2xl shadow-brand-500/20 hover:scale-105 transition-transform">
              Get PulseTrade AI
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5 bg-[#020617]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-slate-500 text-sm gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-white text-xs font-serif font-bold">P</div>
            <span>© 2024 PulseTrade AI</span>
          </div>
          <div className="flex gap-6">
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
