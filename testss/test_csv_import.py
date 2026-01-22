#!/usr/bin/env python3
"""
test_csv_import.py

Test the CSV import functionality for the interactive menu.
"""

import csv
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_csv_import():
    """Test CSV import functionality."""
    print("📥 Testing CSV Import Functionality")
    print("=" * 40)
    
    # Check if sample CSV exists
    csv_file = "sample_portfolio.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Sample CSV file not found: {csv_file}")
        return
    
    print(f"📄 Reading from: {csv_file}")
    
    try:
        # Read CSV file
        imported_positions = []
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            
            # Check required columns
            required_columns = ['ticker', 'num_shares', 'cost_per_share']
            if not all(col in reader.fieldnames for col in required_columns):
                print(f"❌ CSV must contain columns: {', '.join(required_columns)}")
                print(f"Found columns: {', '.join(reader.fieldnames)}")
                return
            
            print(f"✅ CSV columns validated: {', '.join(reader.fieldnames)}")
            
            # Process each row
            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    ticker = row['ticker'].strip().upper()
                    if not ticker:
                        print(f"⚠️  Row {row_num}: Empty ticker")
                        continue
                    
                    shares = float(row['num_shares'])
                    if shares <= 0:
                        print(f"⚠️  Row {row_num}: Invalid shares ({shares})")
                        continue
                    
                    cost_per_share = float(row['cost_per_share'])
                    if cost_per_share <= 0:
                        print(f"⚠️  Row {row_num}: Invalid cost per share ({cost_per_share})")
                        continue
                    
                    purchase_date = row.get('purchase_date', '').strip()
                    notes = row.get('notes', '').strip()
                    
                    position = {
                        'ticker': ticker,
                        'shares': shares,
                        'cost_basis': cost_per_share,
                        'purchase_date': purchase_date,
                        'notes': notes
                    }
                    
                    imported_positions.append(position)
                    print(f"  ✅ Row {row_num-1}: {ticker} - {shares} shares @ ${cost_per_share}")
                    
                except ValueError as e:
                    print(f"⚠️  Row {row_num}: Invalid data - {e}")
                except Exception as e:
                    print(f"⚠️  Row {row_num}: Error - {e}")
        
        if imported_positions:
            # Create portfolio structure
            portfolio = {
                'portfolio_name': 'Imported Portfolio',
                'positions': imported_positions
            }
            
            # Save to JSON file
            output_file = "test_imported_portfolio.json"
            with open(output_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
            
            print(f"\n📊 Import Summary:")
            print(f"  • Total positions imported: {len(imported_positions)}")
            print(f"  • Portfolio saved to: {output_file}")
            
            # Calculate portfolio stats
            total_value = sum(pos['shares'] * pos['cost_basis'] for pos in imported_positions)
            print(f"  • Total portfolio value: ${total_value:,.2f}")
            
            print(f"\n📋 Imported Positions:")
            for pos in imported_positions:
                position_value = pos['shares'] * pos['cost_basis']
                print(f"  • {pos['ticker']}: {pos['shares']} shares @ ${pos['cost_basis']:.2f} = ${position_value:,.2f}")
                if pos.get('purchase_date'):
                    print(f"    📅 Purchased: {pos['purchase_date']}")
                if pos.get('notes'):
                    print(f"    📝 Notes: {pos['notes']}")
            
            print(f"\n✅ CSV import test completed successfully!")
            
        else:
            print("❌ No valid positions found in CSV")
            
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        import traceback
        traceback.print_exc()

def test_csv_export():
    """Test CSV export functionality."""
    print("\n📤 Testing CSV Export Functionality")
    print("=" * 40)
    
    # Create sample portfolio data
    portfolio = {
        'portfolio_name': 'Test Portfolio',
        'positions': [
            {
                'ticker': 'AAPL',
                'shares': 100,
                'cost_basis': 150.25,
                'purchase_date': '2023-01-15',
                'notes': 'Core position'
            },
            {
                'ticker': 'MSFT',
                'shares': 50,
                'cost_basis': 250.50,
                'purchase_date': '2023-02-20',
                'notes': 'Cloud exposure'
            }
        ]
    }
    
    try:
        # Export to CSV
        output_file = "test_portfolio_export.csv"
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['ticker', 'num_shares', 'cost_per_share', 'purchase_date', 'notes']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for pos in portfolio['positions']:
                row = {
                    'ticker': pos['ticker'],
                    'num_shares': pos['shares'],
                    'cost_per_share': pos['cost_basis'],
                    'purchase_date': pos.get('purchase_date', ''),
                    'notes': pos.get('notes', '')
                }
                writer.writerow(row)
        
        print(f"✅ Portfolio exported to: {output_file}")
        print(f"📊 Exported {len(portfolio['positions'])} positions")
        
        # Verify export
        with open(output_file, 'r') as f:
            content = f.read()
            print(f"\n📄 Exported CSV content:")
            print(content)
        
        print(f"\n✅ CSV export test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_csv_import()
    test_csv_export()
