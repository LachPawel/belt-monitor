#!/usr/bin/env python3
"""
Belt Monitor - CLI Entry Point
Analyze conveyor belt videos/images from command line
"""
import argparse
import json
import sys
from pathlib import Path

from app.belt_analyzer import BeltAnalyzer
from app.report_generator import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Conveyor Belt Width Monitor - Analyze belt width from video/images"
    )
    parser.add_argument("input", help="Input video or image file")
    parser.add_argument("-o", "--output", default="reports", help="Output directory")
    parser.add_argument("--min-width", type=float, default=100.0, help="Min belt width threshold (px)")
    parser.add_argument("--max-width", type=float, default=2000.0, help="Max belt width threshold (px)")
    parser.add_argument("--seam-threshold", type=float, default=0.3, help="Seam detection sensitivity")
    parser.add_argument("--sample-rate", type=int, default=1, help="Process every Nth frame")
    parser.add_argument("--roi", nargs=4, type=int, metavar=('X', 'Y', 'W', 'H'), help="Region of interest")
    parser.add_argument("--format", choices=["all", "excel", "csv", "json"], default="all", help="Output format")
    parser.add_argument("--json-stdout", action="store_true", help="Output JSON to stdout")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Configure analyzer
    roi = tuple(args.roi) if args.roi else None
    analyzer = BeltAnalyzer(
        min_width_threshold=args.min_width,
        max_width_threshold=args.max_width,
        seam_detection_threshold=args.seam_threshold,
        roi=roi
    )
    
    # Run analysis
    print(f"Analyzing: {input_path}")
    
    if input_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
        result = analyzer.analyze_image(str(input_path))
    else:
        result = analyzer.analyze_video(str(input_path), sample_rate=args.sample_rate)
    
    # Output results
    if args.json_stdout:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        # Generate reports
        generator = ReportGenerator(args.output)
        base_name = input_path.stem
        
        if args.format == "all":
            paths = generator.generate_all(result, base_name)
            print(f"Reports generated:")
            for fmt, path in paths.items():
                print(f"  {fmt}: {path}")
        elif args.format == "excel":
            path = generator.generate_excel(result, f"{base_name}.xlsx")
            print(f"Excel report: {path}")
        elif args.format == "csv":
            path = generator.generate_csv(result, f"{base_name}.csv")
            print(f"CSV report: {path}")
        elif args.format == "json":
            path = generator.generate_json(result, f"{base_name}.json")
            print(f"JSON report: {path}")
    
    # Print summary
    print(f"\nAnalysis Summary:")
    print(f"  Total frames: {result.total_frames}")
    print(f"  Segments detected: {len(result.segments)}")
    print(f"  Alerts: {len(result.alerts)}")
    
    if result.segments:
        print(f"\nSegment Details:")
        for seg in result.segments:
            print(f"  Segment {seg.segment_id}: "
                  f"min={seg.min_width:.1f}px, max={seg.max_width:.1f}px, avg={seg.avg_width:.1f}px")


if __name__ == "__main__":
    main()
