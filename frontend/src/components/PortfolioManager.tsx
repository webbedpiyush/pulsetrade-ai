"use client";

/**
 * Portfolio management component.
 * Redesigned with shadcn/ui and modern aesthetics.
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Plus, Check, X, TrendingUp, Shield, PieChart, Briefcase } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Stock {
    id: string;
    symbol: string;
    alertEnabled: boolean;
}

interface Portfolio {
    id: string;
    name: string;
    stocks: Stock[];
}

const AVAILABLE_STOCKS = [
    "NSE:RELIANCE", "NSE:TCS", "NSE:INFY", "NSE:HDFCBANK", "NSE:ICICIBANK",
    "NSE:HINDUNILVR", "NSE:BHARTIARTL", "NSE:ITC", "NSE:KOTAKBANK", "NSE:LT",
    "NSE:SBIN", "NSE:AXISBANK", "NSE:BAJFINANCE", "NSE:MARUTI", "NSE:TITAN",
    "NSE:SUNPHARMA", "NSE:TATAMOTORS", "NSE:NESTLEIND", "NSE:WIPRO", "NSE:HCLTECH",
    "NSE:ADANIENT", "NSE:ADANIPORTS", "NSE:APOLLOHOSP", "NSE:ASIANPAINT", "NSE:BAJAJ-AUTO",
    "NSE:BAJAJFINSV", "NSE:BEL", "NSE:BPCL", "NSE:BRITANNIA", "NSE:CIPLA",
    "NSE:COALINDIA", "NSE:DRREDDY", "NSE:EICHERMOT", "NSE:GRASIM", "NSE:HDFCLIFE",
    "NSE:HEROMOTOCO", "NSE:HINDALCO", "NSE:INDUSINDBK", "NSE:JSWSTEEL", "NSE:M&M",
    "NSE:NTPC", "NSE:ONGC", "NSE:POWERGRID", "NSE:SBILIFE", "NSE:SHRIRAMFIN",
    "NSE:TATASTEEL", "NSE:TECHM", "NSE:TRENT", "NSE:ULTRACEMCO",
];

export function PortfolioManager() {
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
    const [newPortfolioName, setNewPortfolioName] = useState("");
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("all");

    useEffect(() => {
        fetchPortfolios();
    }, []);

    const fetchPortfolios = async () => {
        try {
            const res = await fetch("/api/portfolio");
            if (res.ok) {
                const data = await res.json();
                setPortfolios(data);
                if (data.length > 0 && !selectedPortfolio) {
                    setSelectedPortfolio(data[0]);
                }
            }
        } catch (error) {
            console.error("Failed to fetch portfolios:", error);
        } finally {
            setLoading(false);
        }
    };

    const createPortfolio = async () => {
        if (!newPortfolioName.trim()) return;

        try {
            const res = await fetch("/api/portfolio", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: newPortfolioName }),
            });

            if (res.ok) {
                const newPortfolio = await res.json();
                setPortfolios([newPortfolio, ...portfolios]);
                setSelectedPortfolio(newPortfolio);
                setNewPortfolioName("");
                setCreateDialogOpen(false);
            }
        } catch (error) {
            console.error("Failed to create portfolio:", error);
        }
    };

    const addStock = async (symbol: string) => {
        if (!selectedPortfolio) return;

        try {
            const res = await fetch(`/api/portfolio/${selectedPortfolio.id}/stocks`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbol }),
            });

            if (res.ok) {
                const updatedStocks = [...selectedPortfolio.stocks, { id: "temp", symbol, alertEnabled: true }];
                const updatedPortfolio = { ...selectedPortfolio, stocks: updatedStocks };
                setSelectedPortfolio(updatedPortfolio);
                setPortfolios(portfolios.map(p => p.id === selectedPortfolio.id ? updatedPortfolio : p));
                fetchPortfolios(); // Sync
            }
        } catch (error) {
            console.error("Failed to add stock:", error);
        }
    };

    const removeStock = async (symbol: string) => {
        if (!selectedPortfolio) return;
        try {
            await fetch(`/api/portfolio/${selectedPortfolio.id}/stocks`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ symbol }),
            });
            const updatedStocks = selectedPortfolio.stocks.filter(s => s.symbol !== symbol);
            const updatedPortfolio = { ...selectedPortfolio, stocks: updatedStocks };
            setSelectedPortfolio(updatedPortfolio);
            setPortfolios(portfolios.map(p => p.id === selectedPortfolio.id ? updatedPortfolio : p));
            fetchPortfolios();
        } catch (error) {
            console.error("Failed to remove stock:", error);
        }
    };

    const watchedSymbols = selectedPortfolio?.stocks.map((s) => s.symbol) || [];

    if (loading) {
        return (
            <Card className="bg-slate-950/50 border-white/5 animate-pulse h-[400px]">
                <CardContent className="flex items-center justify-center h-full">
                    <div className="flex flex-col items-center gap-2">
                        <Briefcase className="w-8 h-8 text-slate-600 mb-2" />
                        <p className="text-slate-500 text-sm">Loading portfolios...</p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    // Empty State with prominent Create UI
    if (portfolios.length === 0) {
        return (
            <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 overflow-hidden h-full flex flex-col justify-center items-center p-8 text-center min-h-[400px]">
                <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-dashed border-slate-700 shadow-inner">
                    <Shield className="w-8 h-8 text-slate-500" />
                </div>
                <h3 className="text-2xl font-serif text-white mb-3">No Portfolios Found</h3>
                <p className="text-slate-400 text-sm mb-8 max-w-sm leading-relaxed">
                    Create a secure watchlist to start tracking NIFTY 50 stocks and receiving personalized AI alerts.
                </p>

                <div className="w-full max-w-sm space-y-4">
                    <Input
                        value={newPortfolioName}
                        onChange={(e) => setNewPortfolioName(e.target.value)}
                        placeholder="Portfolio Name (e.g., 'Retirement Fund')"
                        className="bg-slate-900/50 border-white/10 text-white placeholder:text-slate-600 h-11"
                    />
                    <Button
                        onClick={createPortfolio}
                        className="w-full bg-brand-600 hover:bg-brand-500 text-white h-11 font-medium shadow-lg shadow-brand-900/20"
                        disabled={!newPortfolioName.trim()}
                    >
                        <Plus className="w-4 h-4 mr-2" /> Create First Portfolio
                    </Button>
                </div>
            </Card>
        );
    }

    return (
        <Card className="bg-slate-950/50 border-white/5 shadow-2xl shadow-black/50 overflow-hidden h-full flex flex-col">
            <CardHeader className="pb-4 border-b border-white/5 space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center border border-brand-500/20">
                            <PieChart className="w-4 h-4 text-brand-400" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-medium text-white">My Holdings</CardTitle>
                        </div>
                    </div>

                    <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                        <DialogTrigger asChild>
                            <Button variant="outline" size="sm" className="bg-slate-900 border-white/10 text-slate-300 hover:text-white hover:bg-slate-800 text-xs">
                                <Plus className="w-3 h-3 mr-1" /> New Portfolio
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-slate-950 border-white/10">
                            <DialogHeader>
                                <DialogTitle className="text-white">Create New Portfolio</DialogTitle>
                                <DialogDescription className="text-slate-400">Add a new collection to track separately.</DialogDescription>
                            </DialogHeader>
                            <div className="py-4">
                                <Input
                                    value={newPortfolioName}
                                    onChange={(e) => setNewPortfolioName(e.target.value)}
                                    placeholder="Portfolio Name"
                                    className="bg-slate-900 border-white/10 text-white"
                                />
                            </div>
                            <DialogFooter>
                                <Button onClick={createPortfolio} className="bg-brand-600 text-white">Create</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>

                <div className="flex items-center gap-2">
                    <Select
                        value={selectedPortfolio?.id}
                        onValueChange={(val) => {
                            const p = portfolios.find((p) => p.id === val);
                            setSelectedPortfolio(p || null);
                        }}
                    >
                        <SelectTrigger className="w-full bg-slate-900 border-white/10 text-white h-10 focus:ring-brand-500/50">
                            <SelectValue placeholder="Select Portfolio" />
                        </SelectTrigger>
                        <SelectContent className="bg-slate-900 border-white/10 text-white shadow-xl">
                            {portfolios.map((p) => (
                                <SelectItem key={p.id} value={p.id} className="focus:bg-slate-800 focus:text-white">
                                    {p.name} <span className="text-slate-500 ml-2">({p.stocks.length})</span>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </CardHeader>

            <CardContent className="p-0 flex-1 flex flex-col min-h-0">
                <Tabs defaultValue="all" className="w-full flex-1 flex flex-col" onValueChange={setActiveTab}>
                    <div className="px-4 pt-3 flex items-center justify-between">
                        <TabsList className="bg-slate-900/50 h-8 p-0.5 border border-white/5">
                            <TabsTrigger value="all" className="text-xs h-7 data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400">All Stocks</TabsTrigger>
                            <TabsTrigger value="watched" className="text-xs h-7 data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400">Watched ({watchedSymbols.length})</TabsTrigger>
                        </TabsList>
                        <Badge variant="outline" className="text-[10px] border-white/10 text-slate-500 bg-white/5">
                            {watchedSymbols.length} / {AVAILABLE_STOCKS.length} Live
                        </Badge>
                    </div>

                    <Separator className="mt-3 bg-white/5" />

                    <ScrollArea className="flex-1 w-full">
                        <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-2 pb-20">
                            {AVAILABLE_STOCKS
                                .filter(s => activeTab === 'all' || (activeTab === 'watched' && watchedSymbols.includes(s)))
                                .map((symbol) => {
                                    const isWatched = watchedSymbols.includes(symbol);
                                    const cleanSymbol = symbol.replace("NSE:", "");
                                    return (
                                        <motion.button
                                            key={symbol}
                                            onClick={() => isWatched ? removeStock(symbol) : addStock(symbol)}
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                            className={cn(
                                                "relative group flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 border text-left",
                                                isWatched
                                                    ? "bg-brand-500/10 border-brand-500/30 text-brand-300 shadow-sm"
                                                    : "bg-slate-900/40 border-white/5 text-slate-400 hover:border-white/10 hover:text-slate-200 hover:bg-slate-800"
                                            )}
                                        >
                                            <span className="truncate mr-2 font-semibold">{cleanSymbol}</span>
                                            {isWatched ? (
                                                <div className="bg-brand-500/20 p-0.5 rounded-full">
                                                    <Check className="w-3 h-3 text-brand-400" />
                                                </div>
                                            ) : (
                                                <Plus className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity text-slate-500" />
                                            )}
                                        </motion.button>
                                    );
                                })}

                            {activeTab === 'watched' && watchedSymbols.length === 0 && (
                                <div className="col-span-full py-8 text-center text-slate-500 text-sm">
                                    No stocks monitored yet. Switch to "All Stocks" to add some.
                                </div>
                            )}
                        </div>
                    </ScrollArea>
                </Tabs>
            </CardContent>
        </Card>
    );
}
