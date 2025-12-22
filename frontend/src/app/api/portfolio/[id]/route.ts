import { NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import prisma from "@/lib/prisma";

interface RouteParams {
    params: Promise<{ id: string }>;
}

// GET /api/portfolio/[id] - Get portfolio with stocks
export async function GET(request: Request, { params }: RouteParams) {
    try {
        const { userId } = await auth();
        const { id } = await params;

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const portfolio = await prisma.portfolio.findFirst({
            where: { id, userId },
            include: { stocks: true },
        });

        if (!portfolio) {
            return NextResponse.json({ error: "Not found" }, { status: 404 });
        }

        return NextResponse.json(portfolio);
    } catch (error) {
        console.error("Portfolio GET error:", error);
        return NextResponse.json({ error: "Failed to fetch portfolio" }, { status: 500 });
    }
}

// DELETE /api/portfolio/[id] - Delete portfolio
export async function DELETE(request: Request, { params }: RouteParams) {
    try {
        const { userId } = await auth();
        const { id } = await params;

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        // Verify ownership
        const portfolio = await prisma.portfolio.findFirst({
            where: { id, userId },
        });

        if (!portfolio) {
            return NextResponse.json({ error: "Not found" }, { status: 404 });
        }

        await prisma.portfolio.delete({ where: { id } });

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error("Portfolio DELETE error:", error);
        return NextResponse.json({ error: "Failed to delete portfolio" }, { status: 500 });
    }
}
