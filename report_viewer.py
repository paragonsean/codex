#!/usr/bin/env python3
"""
report_viewer.py

Simple utility to view generated reports and optionally convert to PDF.
"""

import argparse
import subprocess
import sys
import webbrowser
from pathlib import Path


def open_html_report(filepath: str):
    """Open HTML report in default browser."""
    try:
        webbrowser.open(f'file://{Path(filepath).absolute()}')
        print(f"🌐 Opening report in browser: {filepath}")
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"💡 You can manually open: file://{Path(filepath).absolute()}")


def convert_to_pdf(html_path: str, pdf_path: str):
    """Convert HTML to PDF using weasyprint (if available)."""
    try:
        import weasyprint
        from weasyprint import HTML, CSS
        
        html = HTML(filename=html_path)
        html.write_pdf(pdf_path)
        print(f"📄 PDF saved: {pdf_path}")
        return True
    except ImportError:
        print("❌ WeasyPrint not installed. Install with: pip install weasyprint")
        return False
    except Exception as e:
        print(f"❌ Error converting to PDF: {e}")
        return False


def list_reports(directory: str = "reports"):
    """List all available reports."""
    reports_dir = Path(directory)
    if not reports_dir.exists():
        print(f"❌ Reports directory not found: {directory}")
        return
    
    html_files = list(reports_dir.glob("*.html"))
    md_files = list(reports_dir.glob("*.md"))
    
    print(f"📁 Reports in {directory}:")
    print("\n📄 HTML Reports:")
    for f in sorted(html_files, key=lambda x: x.stat().st_mtime, reverse=True):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")
    
    print("\n📝 Markdown Reports:")
    for f in sorted(md_files, key=lambda x: x.stat().st_mtime, reverse=True):
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="View and convert stock analysis reports")
    parser.add_argument("--list", action="store_true", help="List available reports")
    parser.add_argument("--open", type=str, help="Open HTML report file")
    parser.add_argument("--convert-pdf", type=str, help="Convert HTML to PDF")
    parser.add_argument("--output", type=str, help="Output file for PDF conversion")
    parser.add_argument("--dir", type=str, default="reports", help="Reports directory")
    
    args = parser.parse_args()
    
    if args.list:
        list_reports(args.dir)
    elif args.open:
        filepath = Path(args.dir) / args.open if not Path(args.open).is_absolute() else args.open
        if filepath.exists():
            open_html_report(str(filepath))
        else:
            print(f"❌ File not found: {filepath}")
    elif args.convert_pdf:
        html_path = Path(args.dir) / args.convert_pdf if not Path(args.convert_pdf).is_absolute() else args.convert_pdf
        if not html_path.exists():
            print(f"❌ HTML file not found: {html_path}")
            return
        
        if args.output:
            pdf_path = args.output
        else:
            pdf_path = html_path.with_suffix('.pdf')
        
        convert_to_pdf(str(html_path), pdf_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
