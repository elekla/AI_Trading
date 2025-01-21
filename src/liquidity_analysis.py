from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
import numpy as np

@dataclass
class LiquidityLevel:
    time: pd.Timestamp
    price: float
    type: str  # 'high' or 'low'
    volume: float
    count: int  # Number of touches
    is_active: bool = True

class LiquidityAnalysis:
    def __init__(self, length: int = 14):
        self.length = length
        self.levels: List[LiquidityLevel] = []
        
    def detect_liquidity_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect liquidity levels from swing highs/lows"""
        df = df.copy()
        
        # Detect swings using pivot points
        df['swing_high'] = df['high'].rolling(self.length).apply(
            lambda x: x[len(x)//2] == max(x))
        df['swing_low'] = df['low'].rolling(self.length).apply(
            lambda x: x[len(x)//2] == min(x))
            
        # Calculate volume profile at swings
        for i in range(self.length, len(df)):
            if df['swing_high'].iloc[i]:
                volume = df['volume'].iloc[i-self.length:i+1].sum()
                count = len(df[(df['high'] >= df['high'].iloc[i] * 0.999) & 
                             (df['high'] <= df['high'].iloc[i] * 1.001)])
                
                self.levels.append(LiquidityLevel(
                    time=df.index[i],
                    price=df['high'].iloc[i],
                    type='high',
                    volume=volume,
                    count=count
                ))
                
            if df['swing_low'].iloc[i]:
                volume = df['volume'].iloc[i-self.length:i+1].sum()
                count = len(df[(df['low'] >= df['low'].iloc[i] * 0.999) & 
                             (df['low'] <= df['low'].iloc[i] * 1.001)])
                
                self.levels.append(LiquidityLevel(
                    time=df.index[i],
                    price=df['low'].iloc[i],
                    type='low', 
                    volume=volume,
                    count=count
                ))
                
        return df
    
    def get_significant_levels(self, min_touches: int = 2) -> List[LiquidityLevel]:
        """Get significant liquidity levels based on number of touches"""
        return [level for level in self.levels 
                if level.is_active and level.count >= min_touches]