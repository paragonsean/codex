# 🎯 Interactive Menu System - CSV Import Guide

## ✅ CSV Import Functionality Added

The interactive menu now supports importing portfolios from CSV files with the following format:

### **📄 CSV Format:**
```csv
ticker,num_shares,cost_per_share,purchase_date,notes
AAPL,100,150.25,2023-01-15,Core position
MSFT,50,250.50,2023-02-20,Cloud exposure
GOOGL,25,2800.00,2023-03-10,Search dominance
NVDA,75,450.75,2023-04-05,AI play
TSLA,30,200.00,2023-05-12,Growth stock
BRK.B,10,350.00,2023-06-08,Value holding
```

### **🔧 Required Columns:**
- **ticker**: Stock symbol (e.g., AAPL, MSFT)
- **num_shares**: Number of shares (e.g., 100, 50.5)
- **cost_per_share**: Price paid per share (e.g., 150.25, 2800.00)

### **📋 Optional Columns:**
- **purchase_date**: Date of purchase (e.g., 2023-01-15)
- **notes**: Any notes about the position

### **🚀 How to Use:**

#### **1. Run the Interactive Menu:**
```bash
python interactive_menu.py
```

#### **2. Select Portfolio Management:**
```
1️⃣  📚 Manage Portfolio
```

#### **3. Import from CSV:**
```
7️⃣  📥 Import Portfolio from CSV
```

#### **4. Enter CSV File Path:**
```
Enter CSV file path: tests/fixtures/sample_portfolio.csv
```

### **✅ Features:**

#### **📥 Import Features:**
- **Validation**: Checks for required columns and valid data
- **Duplicate Handling**: Asks what to do with existing tickers (replace/skip/cancel)
- **Error Reporting**: Shows which rows were skipped and why
- **Data Validation**: Ensures shares and cost are positive numbers

#### **📤 Export Features:**
- **Complete Export**: Exports all portfolio data to CSV
- **Standard Format**: Uses the same format as import
- **Custom Path**: Choose your own file name and location

### **📊 Test Results:**
```
📥 Testing CSV Import Functionality
=====================================
📄 Reading from: sample_portfolio.csv
✅ CSV columns validated: ticker, num_shares, cost_per_share, purchase_date, notes
✅ Row 1: AAPL - 100.0 shares @ $150.25
✅ Row 2: MSFT - 50.0 shares @ $250.50
✅ Row 3: GOOGL - 25.0 shares @ $2800.00
✅ Row 4: NVDA - 75.0 shares @ $450.75
✅ Row 5: TSLA - 30.0 shares @ $200.00
✅ Row 6: BRK.B - 10.0 shares @ $350.00

📊 Import Summary:
  • Total positions imported: 6
  • Portfolio saved to: test_imported_portfolio.json
  • Total portfolio value: $140,856.25
```

### **🔍 Error Handling:**
- **Missing File**: Clear error if CSV file doesn't exist
- **Invalid Format**: Shows required vs found columns
- **Data Validation**: Catches invalid numbers and empty fields
- **Duplicate Detection**: Handles existing tickers gracefully

### **💡 Tips:**
1. **Use Headers**: Always include the header row in your CSV
2. **Check Format**: Ensure ticker symbols are valid (e.g., BRK.B not BRK-B)
3. **Validate Data**: Check that shares and prices are positive numbers
4. **Backup First**: Export current portfolio before importing new data

### **📁 Files Created:**
- `tests/fixtures/sample_portfolio.csv` - Example CSV file
- `test_imported_portfolio.json` - Test import result
- `test_portfolio_export.csv` - Test export result

### **🎯 Complete Menu Options:**

#### **Portfolio Management:**
1. ➕ Add Stock to Portfolio
2. ➖ Remove Stock from Portfolio
3. ✏️ Edit Position
4. 📋 View Portfolio
5. 📁 Load Portfolio from File
6. 💾 Save Portfolio to File
7. 📥 **Import Portfolio from CSV** ← NEW
8. 📤 **Export Portfolio to CSV** ← NEW
9. 🔙 Back to Main Menu

The CSV import/export functionality makes it easy to:
- **Import existing portfolios** from spreadsheets
- **Backup portfolio data** in standard CSV format
- **Share portfolios** with other users
- **Migrate from other systems** that export CSV data

🚀 **Ready to use!**
