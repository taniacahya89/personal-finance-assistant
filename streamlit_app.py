# streamlit_app.py - Fixed Complete Version
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from google import genai
from finance_db import *
from finance_calculator import *

# Page config
st.set_page_config(
    page_title="Personal Finance Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2d3748;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar text colors - more specific */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Input fields in sidebar - BLACK text */
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox select {
        color: #2d3748 !important;
        background: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #718096 !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: white !important;
        font-weight: 600;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.6rem;
        transition: all 0.3s ease;
        color: #2d3748 !important;
        background: white !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-radius: 10px;
        font-weight: 600;
        padding: 1rem;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 12px;
        border-radius: 10px;
    }
            
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem !important;
        }
        
        h1 {
            font-size: 2rem !important;
        }
        
        [data-testid="stMetric"] {
            padding: 1rem !important;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        
        /* Stack columns on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
</style>

""", unsafe_allow_html=True)

# Initialize database
init_database()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    google_api_key = st.text_input("🔑 Google AI API Key", type="password", key="api_key")
    
    st.markdown("---")
    
    st.markdown("### 📊 Navigation")
    page = st.radio(
        "Choose View",
        ["🏠 Dashboard", "➕ Add Expense", "📜 Expenses History", "📝 Budget Planner", "🎯 Savings Goals", "💬 Chat Assistant"],
        label_visibility="collapsed"
    )
    
    page = page.split(" ", 1)[1]
    
    st.markdown("---")
    
    st.markdown("### 👤 Your Profile")
    
    profile = get_user_profile()
    
    if profile:
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <p style='margin: 0;'><strong>Name:</strong> {profile['name']}</p>
            <p style='margin: 0.5rem 0 0 0;'><strong>Income:</strong> {format_currency(profile['monthly_income'])}</p>
            <p style='margin: 0.5rem 0 0 0;'><strong>Status:</strong> {profile['status']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.edit_profile = True
    else:
        st.info("Please setup your profile first")
        st.session_state.edit_profile = True
    
    if st.session_state.get('edit_profile', False):
        with st.form("profile_form"):
            st.markdown("#### Setup Profile")
            name = st.text_input("Full Name", value=profile['name'] if profile else "")
            income = st.number_input("Monthly Income (Rp)", min_value=0, value=int(profile['monthly_income']) if profile else 5000000, step=100000)
            status = st.selectbox("Status", ["Single", "Married", "Married with Kids"], index=["Single", "Married", "Married with Kids"].index(profile['status']) if profile else 0)
            dependents = st.number_input("Dependents", min_value=0, value=profile['dependents'] if profile else 0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save", use_container_width=True):
                    save_user_profile(name, income, status, dependents)
                    st.session_state.edit_profile = False
                    st.success("Profile saved!")
                    st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_profile = False
                    st.rerun()
    
    st.markdown("---")
    
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.pop("messages", None)
        st.session_state.pop("chat", None)
        st.rerun()

# Check profile
profile = get_user_profile()
if not profile and page != "Dashboard":
    st.warning("⚠️ Please setup your profile in the sidebar first!")
    st.stop()

# API initialization for chat
if google_api_key and page == "Chat Assistant":
    if ("genai_client" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
        try:
            st.session_state.genai_client = genai.Client(api_key=google_api_key)
            st.session_state._last_key = google_api_key
            st.session_state.pop("chat", None)
            st.session_state.pop("messages", None)
        except Exception as e:
            st.error(f"Invalid API Key: {e}")
            st.stop()
    
    if "chat" not in st.session_state:
        st.session_state.chat = st.session_state.genai_client.chats.create(model="gemini-2.5-flash")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

# ==================== DASHBOARD ====================
if page == "Dashboard":
    st.title("💰 Personal Finance Dashboard")
    
    if not profile:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 2rem; border-radius: 15px; text-align: center;'>
            <h2 style='color: white; margin: 0;'>👋 Welcome!</h2>
            <p style='margin-top: 1rem;'>Please setup your profile in the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    st.caption(f"Hello, **{profile['name']}**! Here's your financial overview.")
    
    expenses = get_expenses()
    
    if not expenses:
        st.info("📝 No expenses recorded yet. Start by adding your first expense!")
        st.stop()
    
    analysis = analyze_spending(expenses, profile['monthly_income'])
    health_score = get_financial_health_score(analysis)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Monthly Income", format_currency(profile['monthly_income']))
    
    with col2:
        st.metric("💸 Total Expenses", format_currency(analysis['total_expenses']))
    
    with col3:
        st.metric("💰 Current Savings", format_currency(analysis['actual_savings']), delta=f"{analysis['savings_percentage']:.1f}%")
    
    with col4:
        st.metric(f"{health_score['status']} Health Score", f"{health_score['score']}/100", delta=health_score['grade'])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Expense Breakdown")
        if analysis['category_breakdown']:
            df_category = pd.DataFrame([{"Category": k, "Amount": v} for k, v in analysis['category_breakdown'].items()])
            fig = px.pie(df_category, values='Amount', names='Category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(font=dict(family="Inter"), height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Budget vs Actual")
        df_budget = pd.DataFrame({
            'Category': ['Needs', 'Wants', 'Savings'],
            'Ideal': [analysis['ideal_budget']['needs'], analysis['ideal_budget']['wants'], analysis['ideal_budget']['savings']],
            'Actual': [analysis['needs_total'], analysis['wants_total'], analysis['actual_savings']]
        })
        fig = go.Figure(data=[
            go.Bar(name='Ideal', x=df_budget['Category'], y=df_budget['Ideal'], marker_color='#a8dadc'),
            go.Bar(name='Actual', x=df_budget['Category'], y=df_budget['Actual'], marker_color='#457b9d')
        ])
        fig.update_layout(barmode='group', font=dict(family="Inter"), height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("💡 Personalized Financial Tips")
    tips = get_financial_tips(analysis)
    for tip in tips:
        st.info(tip)

# ==================== ADD EXPENSE ====================
elif page == "Add Expense":
    st.title("💸 Add New Expense")
    
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input("📅 Date", value=date.today())
            category = st.selectbox("🏷️ Category", ALL_CATEGORIES)
        
        with col2:
            amount = st.number_input("💵 Amount (Rp)", min_value=0, step=1000)
            note = st.text_input("📝 Note (optional)")
        
        submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)
        
        if submitted:
            if amount > 0:
                add_expense(expense_date.isoformat(), category, amount, note)
                st.success(f"✅ Expense added: {format_currency(amount)} for {category}")
                st.balloons()
            else:
                st.error("❌ Amount must be greater than 0")

# ==================== EXPENSES HISTORY ====================
elif page == "Expenses History":
    st.title("📋 Expenses History")
    
    expenses = get_expenses()
    
    if not expenses:
        st.info("No expenses recorded yet.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("🏷️ Filter by Category", ["All"] + ALL_CATEGORIES)
        with col2:
            filter_month = st.selectbox("📅 Filter by Month", ["All", "This Month", "Last Month"])
        
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        if filter_category != "All":
            df = df[df['category'] == filter_category]
        
        if filter_month == "This Month":
            start_of_month = datetime.now().replace(day=1)
            df = df[df['date'] >= start_of_month]
        elif filter_month == "Last Month":
            start_last_month = (datetime.now().replace(day=1) - relativedelta(months=1))
            end_last_month = datetime.now().replace(day=1)
            df = df[(df['date'] >= start_last_month) & (df['date'] < end_last_month)]
        
        st.markdown(f"### Total: **{format_currency(df['amount'].sum())}**")
        st.divider()
        
        for idx, row in df.iterrows():
            with st.expander(f"📅 {row['date'].strftime('%Y-%m-%d')} | {row['category']} | {format_currency(row['amount'])}"):
                st.markdown(f"**Note:** {row['note'] if row['note'] else '_No note_'}")
                if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                    delete_expense(row['id'])
                    st.success("Expense deleted!")
                    st.rerun()

# ==================== BUDGET PLANNER ====================
elif page == "Budget Planner":
    st.title("📝 Budget Planner (50/30/20)")
    
    expenses = get_expenses()
    if not expenses:
        st.info("Add expenses first to see budget analysis")
    else:
        analysis = analyze_spending(expenses, profile['monthly_income'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏠 Needs (50%)", format_currency(analysis['ideal_budget']['needs']), 
                     delta=format_currency(analysis['needs_difference']) if analysis['needs_difference'] != 0 else None, delta_color="inverse")
            # Fix: ensure progress is between 0 and 1
            needs_progress = max(0, min(analysis['needs_total'] / analysis['ideal_budget']['needs'], 1.0))
            st.progress(needs_progress)
            st.caption(f"Actual: {format_currency(analysis['needs_total'])}")
        
        with col2:
            st.metric("🎉 Wants (30%)", format_currency(analysis['ideal_budget']['wants']),
                     delta=format_currency(analysis['wants_difference']) if analysis['wants_difference'] != 0 else None, delta_color="inverse")
            # Fix: ensure progress is between 0 and 1
            wants_progress = max(0, min(analysis['wants_total'] / analysis['ideal_budget']['wants'], 1.0))
            st.progress(wants_progress)
            st.caption(f"Actual: {format_currency(analysis['wants_total'])}")
        
        with col3:
            st.metric("💎 Savings (20%)", format_currency(analysis['ideal_budget']['savings']),
                     delta=format_currency(analysis['savings_difference']) if analysis['savings_difference'] != 0 else None)
            # Fix: handle negative savings (deficit)
            if analysis['ideal_budget']['savings'] > 0:
                savings_progress = max(0, min(analysis['actual_savings'] / analysis['ideal_budget']['savings'], 1.0))
            else:
                savings_progress = 0
            st.progress(savings_progress)
            st.caption(f"Actual: {format_currency(analysis['actual_savings'])}")
            
            # Show warning if deficit
            if analysis['actual_savings'] < 0:
                st.warning("⚠️ Deficit detected! Expenses exceed income.")

# ==================== SAVINGS GOALS ====================
elif page == "Savings Goals":
    st.title("🎯 Savings Goals")
    
    with st.expander("➕ Add New Goal"):
        with st.form("goal_form"):
            col1, col2 = st.columns(2)
            with col1:
                goal_name = st.text_input("Goal Name", placeholder="e.g., Beli Motor")
                target_amount = st.number_input("Target Amount (Rp)", min_value=0, step=100000)
            with col2:
                deadline = st.date_input("Target Date (optional)")
            
            if st.form_submit_button("➕ Add Goal", use_container_width=True):
                if goal_name and target_amount > 0:
                    add_savings_goal(goal_name, target_amount, deadline.isoformat())
                    st.success(f"Goal '{goal_name}' added!")
                    st.rerun()
    
    st.divider()
    
    goals = get_savings_goals()
    expenses = get_expenses()
    
    if not goals:
        st.info("No savings goals yet. Add your first goal above!")
    elif not expenses:
        st.warning("Add expenses first to calculate savings timeline")
    else:
        analysis = analyze_spending(expenses, profile['monthly_income'])
        
        for goal in goals:
            st.subheader(f"🎯 {goal['goal_name']}")
            progress_pct = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.progress(min(progress_pct / 100, 1.0))
                st.markdown(f"**Progress:** {format_currency(goal['current_amount'])} / {format_currency(goal['target_amount'])} ({progress_pct:.1f}%)")
                
                timeline = calculate_savings_timeline(goal['current_amount'], goal['target_amount'], analysis['actual_savings'])
                if timeline['is_achievable']:
                    st.markdown(f"**📅 Estimated completion:** {timeline['estimated_completion']}")
            
            with col2:
                new_amount = st.number_input("Update (Rp)", min_value=0.0, value=float(goal['current_amount']), step=10000.0, key=f"goal_{goal['id']}")
                if st.button("💾", key=f"update_{goal['id']}", use_container_width=True):
                    update_goal_progress(goal['id'], new_amount)
                    st.success("Updated!")
                    st.rerun()
            
            st.divider()

# ==================== CHAT ASSISTANT ====================
elif page == "Chat Assistant":
    st.title("💬 AI Finance Assistant")
    st.caption("Ask me anything about personal finance!")
    
    if not google_api_key:
        st.info("🔑 Please add your Google AI API key in the sidebar to start chatting.")
        st.stop()
    
    expenses = get_expenses()
    goals = get_savings_goals()
    
    if expenses:
        analysis = analyze_spending(expenses, profile['monthly_income'])
        
        context = f"""
User Profile:
- Name: {profile['name']}
- Monthly Income: {format_currency(profile['monthly_income'])}
- Status: {profile['status']}

Financial Summary:
- Total Expenses: {format_currency(analysis['total_expenses'])}
- Current Savings: {format_currency(analysis['actual_savings'])}
- Savings Rate: {analysis['savings_percentage']:.1f}%
- Needs Spending: {format_currency(analysis['needs_total'])} ({analysis['needs_percentage']:.1f}%)
- Wants Spending: {format_currency(analysis['wants_total'])} ({analysis['wants_percentage']:.1f}%)

Top Expense Categories:
"""
        for cat, amt in sorted(analysis['category_breakdown'].items(), key=lambda x: x[1], reverse=True)[:3]:
            context += f"- {cat}: {format_currency(amt)}\n"
        
        if goals:
            context += "\nSavings Goals:\n"
            for goal in goals:
                context += f"- {goal['goal_name']}: {format_currency(goal['current_amount'])} / {format_currency(goal['target_amount'])}\n"
        
        if len(st.session_state.messages) == 0:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Halo {profile['name']}! Saya assistant keuangan pribadi kamu. Saya sudah lihat data keuangan kamu dan siap membantu. Ada yang ingin ditanyakan?"
            })
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Tanya sesuatu tentang keuangan kamu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        try:
            full_prompt = prompt
            if expenses:
                full_prompt = f"[User's financial context: {context}]\n\nUser question: {prompt}"
            
            response = st.session_state.chat.send_message(full_prompt)
            answer = response.text if hasattr(response, "text") else str(response)
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Footer
st.divider()
st.markdown("<div style='text-align: center; color: #718096;'>Personal Finance Assistant | Powered by Gemini AI</div>", unsafe_allow_html=True)