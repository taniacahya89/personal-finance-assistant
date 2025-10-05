# finance_calculator.py
from datetime import datetime, timedelta
from typing import Dict, List

# Expense categories mapping
EXPENSE_CATEGORIES = {
    "Kebutuhan (Needs)": [
        "Makanan & Minuman",
        "Transportasi",
        "Tagihan (Listrik, Air, Internet)",
        "Sewa/Cicilan Rumah",
        "Kesehatan",
        "Pendidikan"
    ],
    "Keinginan (Wants)": [
        "Hiburan",
        "Belanja (Fashion, Gadget)",
        "Makan di Luar (Restaurant)",
        "Traveling",
        "Hobi"
    ],
    "Lainnya": [
        "Lainnya"
    ]
}

# Flatten all categories for dropdown
ALL_CATEGORIES = []
for group, cats in EXPENSE_CATEGORIES.items():
    ALL_CATEGORIES.extend(cats)

def categorize_expense_type(category: str) -> str:
    """Determine if expense is Needs, Wants, or Other"""
    for expense_type, categories in EXPENSE_CATEGORIES.items():
        if category in categories:
            if "Kebutuhan" in expense_type:
                return "Needs"
            elif "Keinginan" in expense_type:
                return "Wants"
            else:
                return "Other"
    return "Other"

def calculate_budget_503020(monthly_income: float) -> Dict[str, float]:
    """Calculate 50/30/20 budget rule"""
    return {
        "needs": monthly_income * 0.50,
        "wants": monthly_income * 0.30,
        "savings": monthly_income * 0.20
    }

def analyze_spending(expenses: List[Dict], monthly_income: float) -> Dict:
    """Analyze spending patterns and compare with 50/30/20 rule"""
    total_expenses = sum(exp['amount'] for exp in expenses)
    
    # Categorize expenses
    needs_total = 0
    wants_total = 0
    other_total = 0
    
    category_breakdown = {}
    
    for exp in expenses:
        amount = exp['amount']
        category = exp['category']
        
        # Add to category breakdown
        if category in category_breakdown:
            category_breakdown[category] += amount
        else:
            category_breakdown[category] = amount
        
        # Categorize as needs/wants
        exp_type = categorize_expense_type(category)
        if exp_type == "Needs":
            needs_total += amount
        elif exp_type == "Wants":
            wants_total += amount
        else:
            other_total += amount
    
    # Calculate ideal budget
    ideal_budget = calculate_budget_503020(monthly_income)
    
    # Calculate savings
    actual_savings = monthly_income - total_expenses
    
    # Calculate percentages
    needs_percentage = (needs_total / monthly_income * 100) if monthly_income > 0 else 0
    wants_percentage = (wants_total / monthly_income * 100) if monthly_income > 0 else 0
    savings_percentage = (actual_savings / monthly_income * 100) if monthly_income > 0 else 0
    
    return {
        "total_expenses": total_expenses,
        "needs_total": needs_total,
        "wants_total": wants_total,
        "other_total": other_total,
        "actual_savings": actual_savings,
        "needs_percentage": needs_percentage,
        "wants_percentage": wants_percentage,
        "savings_percentage": savings_percentage,
        "ideal_budget": ideal_budget,
        "category_breakdown": category_breakdown,
        "needs_difference": needs_total - ideal_budget["needs"],
        "wants_difference": wants_total - ideal_budget["wants"],
        "savings_difference": actual_savings - ideal_budget["savings"]
    }

def calculate_savings_timeline(current_amount: float, target_amount: float, monthly_saving: float) -> Dict:
    """Calculate how long it takes to reach savings goal"""
    if monthly_saving <= 0:
        return {
            "months_needed": float('inf'),
            "estimated_completion": "Never (no savings)",
            "is_achievable": False
        }
    
    remaining = target_amount - current_amount
    if remaining <= 0:
        return {
            "months_needed": 0,
            "estimated_completion": "Goal already achieved!",
            "is_achievable": True
        }
    
    months_needed = remaining / monthly_saving
    completion_date = datetime.now() + timedelta(days=int(months_needed * 30))
    
    return {
        "months_needed": round(months_needed, 1),
        "estimated_completion": completion_date.strftime("%B %Y"),
        "is_achievable": True,
        "remaining_amount": remaining
    }

def get_financial_health_score(analysis: Dict) -> Dict:
    """Calculate financial health score (0-100)"""
    score = 0
    
    # Savings rate (max 40 points)
    if analysis['savings_percentage'] >= 20:
        score += 40
    elif analysis['savings_percentage'] >= 10:
        score += 30
    elif analysis['savings_percentage'] >= 5:
        score += 20
    else:
        score += 10
    
    # Budget adherence (max 30 points)
    needs_adherence = max(0, 30 - abs(analysis['needs_percentage'] - 50) / 2)
    score += needs_adherence
    
    # Expense control (max 30 points)
    expense_ratio = analysis['total_expenses'] / (analysis['total_expenses'] + analysis['actual_savings'])
    if expense_ratio <= 0.7:
        score += 30
    elif expense_ratio <= 0.8:
        score += 20
    elif expense_ratio <= 0.9:
        score += 10
    
    # Determine grade
    if score >= 80:
        grade = "A - Excellent!"
        status = "🟢"
    elif score >= 60:
        grade = "B - Good"
        status = "🟡"
    elif score >= 40:
        grade = "C - Fair"
        status = "🟠"
    else:
        grade = "D - Needs Improvement"
        status = "🔴"
    
    return {
        "score": round(score),
        "grade": grade,
        "status": status
    }

def format_currency(amount: float) -> str:
    """Format number as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def get_financial_tips(analysis: Dict) -> List[str]:
    """Generate personalized financial tips based on spending analysis"""
    tips = []
    
    if analysis['savings_percentage'] < 10:
        tips.append("💡 **Tip Tabungan**: Saving rate kamu di bawah 10%. Coba targetkan minimal 10-20% dari penghasilan untuk masa depan yang lebih aman.")
    
    if analysis['needs_difference'] > 0:
        tips.append(f"⚠️ **Pengeluaran Kebutuhan**: Over budget {format_currency(analysis['needs_difference'])}. Review tagihan bulanan dan cari alternatif lebih hemat.")
    
    if analysis['wants_difference'] > 0:
        tips.append(f"🎯 **Pengeluaran Keinginan**: Over budget {format_currency(analysis['wants_difference'])}. Pertimbangkan mengurangi hiburan atau belanja yang tidak urgent.")
    
    if analysis['savings_percentage'] > 30:
        tips.append("✨ **Excellent!**: Saving rate kamu sangat baik! Pertimbangkan untuk mulai investasi agar uang bekerja untuk kamu.")
    
    # Category-specific tips
    if "Makan di Luar (Restaurant)" in analysis['category_breakdown']:
        restaurant_spend = analysis['category_breakdown']["Makan di Luar (Restaurant)"]
        if restaurant_spend > 1000000:  # More than 1 million
            tips.append(f"🍽️ **Food Spending**: Pengeluaran makan di luar {format_currency(restaurant_spend)}. Meal prep bisa save hingga 50%!")
    
    if not tips:
        tips.append("👏 **Great Job!**: Financial management kamu sudah bagus! Keep up the good work!")
    
    return tips