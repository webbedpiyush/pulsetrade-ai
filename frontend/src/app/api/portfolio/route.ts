import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/prisma";

// GET /api/portfolio - List user's portfolios
export async function GET() {
    try {
        const { userId } = await auth();

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const portfolios = await prisma.portfolio.findMany({
            where: { userId },
            include: {
                stocks: true,
            },
            orderBy: { createdAt: "desc" },
        });

        return NextResponse.json(portfolios);
    } catch (error) {
        console.error("Portfolio GET error:", error);
        return NextResponse.json({ error: "Failed to fetch portfolios" }, { status: 500 });
    }
}

// POST /api/portfolio - Create new portfolio
export async function POST(request: Request) {
    try {
        const { userId } = await auth();

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { name } = await request.json();

        if (!name) {
            return NextResponse.json({ error: "Name is required" }, { status: 400 });
        }

        const portfolio = await prisma.portfolio.create({
            data: {
                userId,
                name,
            },
            include: {
                stocks: true,
            },
        });

        return NextResponse.json(portfolio, { status: 201 });
    } catch (error) {
        console.error("Portfolio POST error:", error);
        return NextResponse.json({ error: "Failed to create portfolio" }, { status: 500 });
    }
}
