import pandas as pd
from market_structure import MarketStructure
from fair_value_gaps import FairValueGaps
from liquidity_analysis import LiquidityAnalysis

def analyze_market(df: pd.DataFrame):
    """
    Analyze market structure, fair value gaps and liquidity levels
    
    Args:
        df: DataFrame with OHLCV data
    """
    # Initialize analyzers
    ms = MarketStructure()
    fvg = FairValueGaps()
    liq = LiquidityAnalysis()
    
    # Detect market structure
    df = ms.detect_fractals(df)
    df = ms.identify_structure_breaks(df)
    
    # Detect fair value gaps
    df = fvg.detect_gaps(df)
    
    # Detect liquidity levels
    df = liq.detect_liquidity_levels(df)
    
    return df, ms, fvg, liq

def main():
    # Load your price data here
    # df = pd.read_csv('your_data.csv')
    
    # Analyze market
    df, ms, fvg, liq = analyze_market(df)
    
    # Get active signals
    active_gaps = fvg.get_active_gaps()
    significant_levels = liq.get_significant_levels()
    
    # Print analysis results
    print("Active Fair Value Gaps:")
    for gap in active_gaps:
        print(f"{gap.type.title()} FVG at {gap.low_price:.2f}-{gap.high_price:.2f}")
        
    print("\nSignificant Liquidity Levels:")
    for level in significant_levels:
        print(f"{level.type.title()} liquidity at {level.price:.2f} ({level.count} touches)")

if __name__ == "__main__":
    main()