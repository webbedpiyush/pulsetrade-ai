"""
Kafka Consumer -> Technical Analysis -> Gemini AI Trigger.

Consumes trades from Kafka, calculates indicators, and triggers AI analysis.
"""
import asyncio
import time
from typing import Dict
from ddtrace import tracer
from google import genai
from google.genai import types

from app.core.kafka import get_consumer, TOPIC_CRYPTO_TRADES
from app.core.config import get_settings
from app.models.trade import TradeEvent, AlertEvent
from app.indicators.rsi import RSICalculator
from app.indicators.volume import VolumeSpikeDetector
from app.indicators.price import PriceChangeDetector, LevelCrossDetector


# Trigger thresholds (adjusted for 60-second RSI for professional demo look)
RSI_OVERBOUGHT = 70  # More achievable than 80 with 60s period
RSI_OVERSOLD = 30    # More achievable than 20 with 60s period
VOLUME_SPIKE_THRESHOLD = 5.0

# Cooldown (5 minutes per symbol per trigger type)
COOLDOWN_SECONDS = 300


class MarketAnalyzer:
    """
    Analyzes market data and triggers AI insights.
    """
    
    def __init__(self):
        self.consumer = get_consumer()
        self.rsi = RSICalculator(period=60)  # 1-Minute RSI (60 1-second candles)
        self.volume = VolumeSpikeDetector(window_size=30)  # 30-second rolling window
        
        # New Detectors
        self.whale_detector = PriceChangeDetector(window_seconds=60, threshold_percent=1.0)
        self.level_detector = LevelCrossDetector(levels=[
            68000, 69000, 70000,  # BTC Levels
            95000, 96000, 97000,  # Just in case
            98000, 99000, 100000 
        ])
        self.running = False
        
        # Cooldown tracker: {symbol_type: last_trigger_time}
        self.cooldowns: Dict[str, float] = {}
        
        # AI client
        settings = get_settings()
        self.ai_client = genai.Client(api_key=settings.google_api_key)
        
        # Callbacks (set by main.py)
        self.on_alert = None
        self.on_analysis = None
        
        self.trades_processed = 0
        self.alerts_triggered = 0
        self.alerts_skipped = 0
        
        # Callback to check allowed connections (returns bool)
        self.connection_check_callback = None
        
    async def start(self):
        """Start the analyzer (runs forever)."""
        self.running = True
        self.consumer.subscribe([TOPIC_CRYPTO_TRADES])
        print("[Analyzer] Started, consuming from", TOPIC_CRYPTO_TRADES)
        
        while self.running:
            # Poll Kafka (blocking but with timeout)
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                await asyncio.sleep(0.01)  # Yield to other tasks
                continue
                
            if msg.error():
                print(f"[Analyzer] Kafka error: {msg.error()}")
                continue
                
            # Process trade
            trade = TradeEvent.from_kafka_bytes(msg.value())
            await self._process_trade(trade)
            
    async def _process_trade(self, trade: TradeEvent):
        """Process a single trade event."""
        self.trades_processed += 1
        
        # Update indicators with timestamp for time-based aggregation
        # These return results only when a 1-second candle completes
        rsi_result = self.rsi.update(trade.symbol, trade.price, trade.time)
        volume_result = self.volume.update(trade.symbol, trade.volume, trade.time)
        whale_result = self.whale_detector.update(trade.symbol, trade.price, trade.time)
        level_result = self.level_detector.update(trade.symbol, trade.price)
        
        # Check triggers (only fires when 1-second candles complete)
        if rsi_result:
            if rsi_result.is_overbought:
                await self._maybe_trigger(
                    trade, "RSI_HIGH", rsi_result.rsi,
                    f"{trade.symbol} RSI hit {rsi_result.rsi} - extremely overbought!"
                )
            elif rsi_result.is_oversold:
                await self._maybe_trigger(
                    trade, "RSI_LOW", rsi_result.rsi,
                    f"{trade.symbol} RSI dropped to {rsi_result.rsi} - oversold territory!"
                )
                
        if volume_result and volume_result.is_spike:
            await self._maybe_trigger(
                trade, "VOLUME_SPIKE", volume_result.spike_multiplier,
                f"{trade.symbol} volume spike {volume_result.spike_multiplier}x!"
            )
            
        # Check Whale Alert
        if whale_result and whale_result.is_whale_move:
            direction = "surged" if whale_result.change_percent > 0 else "dumped"
            await self._maybe_trigger(
                trade, "WHALE_ALERT", whale_result.change_percent,
                f"{trade.symbol} {direction} {whale_result.change_percent}% in {whale_result.time_window_sec}s!"
            )
            
        # Check Psychological Level
        if level_result:
            await self._maybe_trigger(
                trade, "PSYCH_LEVEL", float(level_result.level),
                f"{trade.symbol} crossed ${level_result.level} {level_result.direction}!"
            )
            
    async def _maybe_trigger(
        self, 
        trade: TradeEvent, 
        trigger_type: str, 
        trigger_value: float,
        message: str
    ):
        """Trigger alert if not in cooldown."""
        key = f"{trade.symbol}_{trigger_type}"
        now = time.time()
        
        # Check cooldown
        last_time = self.cooldowns.get(key, 0)
        if now - last_time < COOLDOWN_SECONDS:
            return  # Still in cooldown
            
        # Set cooldown
        self.cooldowns[key] = now
        self.alerts_triggered += 1
        
        print(f"[Analyzer] ALERT: {message}")
        
        # Create alert event
        alert = AlertEvent(
            symbol=trade.symbol,
            price=trade.price,
            trigger_type=trigger_type,
            trigger_value=trigger_value,
            message=message,
            time=trade.time,
        )
        
        # Notify callback
        if self.on_alert:
            await self.on_alert(alert)
            
        # Check if we should run expensive AI (Smart Standby)
        if self.connection_check_callback:
            has_audience = self.connection_check_callback()
            if not has_audience:
                self.alerts_skipped += 1
                if self.alerts_skipped % 10 == 0:  # Log every 10th skip to not spam
                    print(f"[Analyzer] Skipping AI generation - No active clients (Total Skipped: {self.alerts_skipped})")
                return

        # Generate AI analysis
        await self._generate_ai_analysis(alert)
        
    async def _generate_ai_analysis(self, alert: AlertEvent):
        """Generate AI analysis using Gemini."""
        prompt = f"""
        You are a crypto market commentator. Be concise and exciting.
        
        Event: {alert.trigger_type} triggered for {alert.symbol}
        Price: ${alert.price:,.2f}
        Trigger Value: {alert.trigger_value}
        
        Give a 1-sentence market insight. Is this a pump or trap?
        """
        
        with tracer.trace("gemini.generate", service="pulsetrade-analyzer") as span:
            span.set_tag("symbol", alert.symbol)
            span.set_tag("trigger_type", alert.trigger_type)
            
            try:
                response = self.ai_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=100,
                    )
                )
                analysis_text = response.text
                print(f"[Analyzer] Gemini: {analysis_text}")
                
                if self.on_analysis:
                    await self.on_analysis(alert.symbol, analysis_text)
                    
            except Exception as e:
                print(f"[Analyzer] Gemini error: {e}")
                
    def stop(self):
        """Stop the analyzer."""
        self.running = False
        self.consumer.close()
        print("[Analyzer] Stopped")


# Singleton
_analyzer: MarketAnalyzer | None = None


def get_analyzer() -> MarketAnalyzer:
    """Get singleton analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = MarketAnalyzer()
    return _analyzer
