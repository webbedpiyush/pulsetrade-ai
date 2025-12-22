import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/prisma";

// Valid NIFTY 50 symbols
const VALID_SYMBOLS = [
    "NSE:ADANIENT", "NSE:ADANIPORTS", "NSE:APOLLOHOSP", "NSE:ASIANPAINT", "NSE:AXISBANK",
    "NSE:BAJAJ-AUTO", "NSE:BAJFINANCE", "NSE:BAJAJFINSV", "NSE:BEL", "NSE:BPCL",
    "NSE:BHARTIARTL", "NSE:BRITANNIA", "NSE:CIPLA", "NSE:COALINDIA", "NSE:DRREDDY",
    "NSE:EICHERMOT", "NSE:GRASIM", "NSE:HCLTECH", "NSE:HDFCBANK", "NSE:HDFCLIFE",
    "NSE:HEROMOTOCO", "NSE:HINDALCO", "NSE:HINDUNILVR", "NSE:ICICIBANK", "NSE:ITC",
    "NSE:INDUSINDBK", "NSE:INFY", "NSE:JSWSTEEL", "NSE:KOTAKBANK", "NSE:LT",
    "NSE:M&M", "NSE:MARUTI", "NSE:NESTLEIND", "NSE:NTPC", "NSE:ONGC",
    "NSE:POWERGRID", "NSE:RELIANCE", "NSE:SBILIFE", "NSE:SHRIRAMFIN", "NSE:SBIN",
    "NSE:SUNPHARMA", "NSE:TCS", "NSE:TATACONSUM", "NSE:TATAMOTORS", "NSE:TATASTEEL",
    "NSE:TECHM", "NSE:TITAN", "NSE:TRENT", "NSE:ULTRACEMCO", "NSE:WIPRO",
];

interface RouteParams {
    params: Promise<{ id: string }>;
}

// GET /api/portfolio/[id]/stocks - List available stocks
export async function GET(request: Request, { params }: RouteParams) {
    try {
        const { userId } = await auth();

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        return NextResponse.json({ availableSymbols: VALID_SYMBOLS });
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch stocks" }, { status: 500 });
    }
}

// POST /api/portfolio/[id]/stocks - Add stock to portfolio
export async function POST(request: Request, { params }: RouteParams) {
    try {
        const { userId } = await auth();
        const { id } = await params;

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { symbol, alertEnabled = true } = await request.json();

        if (!symbol) {
            return NextResponse.json({ error: "Symbol is required" }, { status: 400 });
        }

        // Validate symbol
        if (!VALID_SYMBOLS.includes(symbol)) {
            return NextResponse.json({ error: "Invalid symbol" }, { status: 400 });
        }

        // Verify portfolio ownership
        const portfolio = await prisma.portfolio.findFirst({
            where: { id, userId },
        });

        if (!portfolio) {
            return NextResponse.json({ error: "Portfolio not found" }, { status: 404 });
        }

        // Add stock (upsert to handle duplicates)
        const stock = await prisma.stock.upsert({
            where: {
                portfolioId_symbol: { portfolioId: id, symbol },
            },
            update: { alertEnabled },
            create: {
                portfolioId: id,
                symbol,
                alertEnabled,
            },
        });

        return NextResponse.json(stock, { status: 201 });
    } catch (error) {
        console.error("Stock POST error:", error);
        return NextResponse.json({ error: "Failed to add stock" }, { status: 500 });
    }
}

// DELETE /api/portfolio/[id]/stocks - Remove stock from portfolio
export async function DELETE(request: Request, { params }: RouteParams) {
    try {
        const { userId } = await auth();
        const { id } = await params;

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { symbol } = await request.json();

        // Verify portfolio ownership
        const portfolio = await prisma.portfolio.findFirst({
            where: { id, userId },
        });

        if (!portfolio) {
            return NextResponse.json({ error: "Portfolio not found" }, { status: 404 });
        }

        await prisma.stock.deleteMany({
            where: { portfolioId: id, symbol },
        });

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error("Stock DELETE error:", error);
        return NextResponse.json({ error: "Failed to remove stock" }, { status: 500 });
    }
}
