from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
import numpy as np

@dataclass
class FairValueGap:
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    high_price: float
    low_price: float
    type: str  # 'bullish' or 'bearish'
    volume: float
    is_active: bool = True

class FairValueGaps:
    def __init__(self, min_gap_size: float = 0.001):
        self.min_gap_size = min_gap_size
        self.gaps: List[FairValueGap] = []
        
    def detect_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect fair value gaps in price data"""
        df = df.copy()
        df['bull_fvg'] = False
        df['bear_fvg'] = False
        
        for i in range(2, len(df)):
            # Bullish FVG
            if df['low'].iloc[i] > df['high'].iloc[i-1]:
                gap_size = df['low'].iloc[i] - df['high'].iloc[i-1]
                if gap_size >= self.min_gap_size:
                    df.loc[df.index[i], 'bull_fvg'] = True
                    self.gaps.append(FairValueGap(
                        start_time=df.index[i-1],
                        end_time=df.index[i],
                        high_price=df['low'].iloc[i],
                        low_price=df['high'].iloc[i-1],
                        type='bullish',
                        volume=df['volume'].iloc[i]
                    ))
                    
            # Bearish FVG
            if df['high'].iloc[i] < df['low'].iloc[i-1]:
                gap_size = df['low'].iloc[i-1] - df['high'].iloc[i]
                if gap_size >= self.min_gap_size:
                    df.loc[df.index[i], 'bear_fvg'] = True
                    self.gaps.append(FairValueGap(
                        start_time=df.index[i-1],
                        end_time=df.index[i],
                        high_price=df['low'].iloc[i-1],
                        low_price=df['high'].iloc[i],
                        type='bearish',
                        volume=df['volume'].iloc[i]
                    ))
                    
        return df
    
    def update_gaps(self, current_price: float):
        """Update status of existing gaps"""
        for gap in self.gaps:
            if not gap.is_active:
                continue
                
            if gap.type == 'bullish' and current_price <= gap.low_price:
                gap.is_active = False
            elif gap.type == 'bearish' and current_price >= gap.high_price:
                gap.is_active = False
                
    def get_active_gaps(self) -> List[FairValueGap]:
        """Get list of currently active gaps"""
        return [gap for gap in self.gaps if gap.is_active]