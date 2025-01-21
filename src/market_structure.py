from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
import numpy as np

@dataclass
class Structure:
    time: pd.Timestamp
    price: float
    type: str  # 'bullish' or 'bearish'
    label: str  # 'BOS' or 'CHoCH'

class MarketStructure:
    def __init__(self, length: int = 5):
        self.length = length
        self.structures: List[Structure] = []
        
    def detect_fractals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect bullish and bearish fractals in price data"""
        df = df.copy()
        p = self.length // 2
        
        # Calculate directional movement
        df['dh'] = df['high'].diff().apply(np.sign).rolling(p).sum()
        df['dl'] = df['low'].diff().apply(np.sign).rolling(p).sum()
        
        # Detect fractals
        df['bull_fractal'] = (df['dh'] == -p) & (df['dh'].shift(p) == p) & \
            (df['high'].shift(p) == df['high'].rolling(self.length).max())
            
        df['bear_fractal'] = (df['dl'] == p) & (df['dl'].shift(p) == -p) & \
            (df['low'].shift(p) == df['low'].rolling(self.length).min())
            
        return df
    
    def identify_structure_breaks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify Changes of Character (CHoCH) and Breaks of Structure (BOS)"""
        df = df.copy()
        df['structure'] = None
        df['structure_label'] = None
        
        # Track market state
        trend = 0  # -1: bearish, 0: undefined, 1: bullish
        
        for i in range(self.length, len(df)):
            if df['bull_fractal'].iloc[i] and trend <= 0:
                # Potential bullish structure
                prev_high = df['high'].iloc[i-self.length:i].max()
                if df['close'].iloc[i] > prev_high:
                    df.loc[df.index[i], 'structure'] = 'bullish'
                    df.loc[df.index[i], 'structure_label'] = 'CHoCH' if trend == -1 else 'BOS'
                    trend = 1
                    
            elif df['bear_fractal'].iloc[i] and trend >= 0:
                # Potential bearish structure
                prev_low = df['low'].iloc[i-self.length:i].min()
                if df['close'].iloc[i] < prev_low:
                    df.loc[df.index[i], 'structure'] = 'bearish'
                    df.loc[df.index[i], 'structure_label'] = 'CHoCH' if trend == 1 else 'BOS'
                    trend = -1
                    
        return df