import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
from datetime import datetime
from time_analysis import TimeAnalyzer
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Time Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create data directory if it doesn't exist
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

def get_existing_files():
    """Get list of existing files in data directory"""
    if DATA_DIR.exists():
        return [f.name for f in DATA_DIR.iterdir() if f.suffix in ['.xlsx', '.csv', '.xls']]
    return []

def save_uploaded_file(uploaded_file):
    """Save uploaded file to data directory"""
    file_path = DATA_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def get_llm_summary(stats, base_url=None, model=None, api_key=None):
    """Generate LLM-based summary of time analysis using OpenAI-compatible API"""
    # Use environment variables as fallback
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return None

    try:
        from openai import OpenAI

        # Initialize OpenAI client with custom base URL
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        # Prepare context for LLM
        context = f"""
        Time Analysis Summary:

        Total Hours by Activity Type:
        {json.dumps(stats.get('total_hours', {}), indent=2)}

        Monthly Averages:
        {json.dumps(stats.get('monthly_averages', {}), indent=2)}

        Top Activities:
        {json.dumps(stats.get('top_activities', {}), indent=2)}
        """

        # Create chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a time management coach analyzing someone's time tracking data. Provide insightful analysis and actionable recommendations."},
                {"role": "user", "content": f"Please analyze this time tracking data and provide insights:\n{context}"}
            ],
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        st.warning(f"LLM analysis failed: {str(e)}")
        return None

# Main UI
st.title("📊 Time Analysis Dashboard")
st.markdown("Upload and analyze your time tracking data with visualizations and AI insights")

# Sidebar for file management and settings
with st.sidebar:
    st.header("⚙️ Settings")

    # File Upload Section
    st.subheader("1️⃣ Upload Files")
    uploaded_files = st.file_uploader(
        "Upload Excel/CSV files",
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload your time tracking files to the data folder"
    )

    if uploaded_files:
        if st.button("💾 Save Uploaded Files"):
            with st.spinner("Saving files..."):
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file)
                    st.success(f"✅ Saved: {uploaded_file.name}")

    st.divider()

    # File Selection Section
    st.subheader("2️⃣ Select File to Analyze")
    existing_files = get_existing_files()

    if existing_files:
        # Selection mode
        analysis_mode = st.radio(
            "Analysis Mode",
            options=["📄 Single Week", "📅 Monthly", "📆 Yearly"],
            help="Choose the scope of your analysis:\n- Single Week: Analyze one specific week\n- Monthly: Analyze all weeks in a specific month\n- Yearly: Analyze the entire year"
        )

        selected_file = st.selectbox(
            "Choose a file",
            options=existing_files,
            help="Select a file from the data folder to analyze"
        )

        year = st.number_input(
            "Year",
            min_value=2020,
            max_value=2030,
            value=2024,
            help="Year of the time tracking data"
        )

        # Show additional options based on mode
        selected_month = None
        selected_week = None

        if analysis_mode == "📄 Single Week":
            col1, col2 = st.columns(2)
            with col1:
                selected_month = st.number_input(
                    "Month",
                    min_value=1,
                    max_value=12,
                    value=1,
                    help="Month number (1-12)"
                )
            with col2:
                selected_week = st.number_input(
                    "Week",
                    min_value=1,
                    max_value=5,
                    value=1,
                    help="Week number in the month"
                )
        elif analysis_mode == "📅 Monthly":
            selected_month = st.number_input(
                "Month",
                min_value=1,
                max_value=12,
                value=1,
                help="Month number (1-12)"
            )

        if st.button("🔍 Analyze", type="primary"):
            with st.spinner("Analyzing data..."):
                try:
                    file_path = DATA_DIR / selected_file
                    st.session_state.analyzer = TimeAnalyzer(str(file_path), year=year)
                    st.session_state.analyzer.load_data()
                    st.session_state.analyzer.process_data()

                    # Filter data based on selected mode
                    if analysis_mode == "📄 Single Week" and selected_month and selected_week:
                        st.session_state.analyzer.processed_data = st.session_state.analyzer.processed_data[
                            (st.session_state.analyzer.processed_data['Month'] == selected_month) &
                            (st.session_state.analyzer.processed_data['Week'] == selected_week)
                        ]
                        st.info(f"📊 Analyzing: Month {selected_month}, Week {selected_week}")
                    elif analysis_mode == "📅 Monthly" and selected_month:
                        st.session_state.analyzer.processed_data = st.session_state.analyzer.processed_data[
                            st.session_state.analyzer.processed_data['Month'] == selected_month
                        ]
                        st.info(f"📊 Analyzing: All weeks in Month {selected_month}")
                    else:
                        st.info(f"📊 Analyzing: Entire year {year}")

                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.analysis_complete = False
    else:
        st.info("📁 No files found. Upload files above to get started.")

    st.divider()

    # LLM Configuration Section
    st.subheader("3️⃣ LLM Configuration")
    st.markdown("Configure OpenAI-compatible LLM providers (OpenAI, Qwen, etc.)")

    # Base URL for OpenAI-compatible APIs
    base_url = st.text_input(
        "API Base URL",
        value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        help="API endpoint URL. Use default for OpenAI, or custom URL for other providers (e.g., Qwen, local models)"
    )

    # Model selection
    model_options = [
        # OpenAI models
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        # Qwen models
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen2.5-72b-instruct",
        "qwen2.5-32b-instruct",
        "qwen2.5-14b-instruct",
        "qwen2.5-7b-instruct",
        # Other
        "custom"
    ]

    selected_model = st.selectbox(
        "Model",
        options=model_options,
        index=0,
        help="Select the LLM model to use for analysis"
    )

    # Allow custom model input
    if selected_model == "custom":
        selected_model = st.text_input(
            "Custom Model Name",
            value="",
            help="Enter the exact model name/ID"
        )

    # API Key
    api_key = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Enter your API key"
    )

    if st.button("💾 Save LLM Configuration to .env"):
        env_content = f"""# LLM Configuration for Time Analysis
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OPENAI_API_KEY={api_key}
OPENAI_BASE_URL={base_url}
OPENAI_MODEL={selected_model}
"""
        with open(".env", "w") as f:
            f.write(env_content)
        st.success("✅ LLM configuration saved to .env file")
        st.info("🔄 Restart the app to load new configuration")

    st.divider()

    # Info section
    st.subheader("ℹ️ Activity Types")
    st.markdown("""
    - **R**: Rest
    - **P**: Procrastination
    - **G**: Guilt-free Play
    - **M**: Mandatory Work
    - **W**: Productive Work
    """)

# Main content area
if st.session_state.analysis_complete and st.session_state.analyzer:
    analyzer = st.session_state.analyzer

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Visualizations", "📋 Statistics", "🤖 AI Insights"])

    with tab1:
        st.header("Overview")

        # Generate stats
        stats = analyzer.get_activity_stats()

        # Display key metrics
        col1, col2, col3 = st.columns(3)

        total_hours = sum(stats['total_hours'].values())
        most_common = max(stats['total_hours'].items(), key=lambda x: x[1])

        with col1:
            st.metric("Total Hours Tracked", f"{total_hours:.1f}h")

        with col2:
            st.metric("Most Common Activity", most_common[0])

        with col3:
            st.metric("Hours in Most Common", f"{most_common[1]:.1f}h")

        st.divider()

        # Display activity breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Activity Type Distribution")
            df_activity = pd.DataFrame(
                list(stats['total_hours'].items()),
                columns=['Activity Type', 'Hours']
            )
            st.dataframe(df_activity, use_container_width=True)

        with col2:
            st.subheader("Monthly Averages")
            df_monthly = pd.DataFrame(
                list(stats['monthly_averages'].items()),
                columns=['Activity Type', 'Hours/Month']
            )
            st.dataframe(df_monthly, use_container_width=True)

    with tab2:
        st.header("Visualizations")

        # Overall distribution pie chart
        st.subheader("Overall Time Distribution")
        fig_overall = analyzer.plot_weekly_summary()
        st.plotly_chart(fig_overall, use_container_width=True)

        # Monthly distribution
        st.subheader("Monthly Time Distribution")
        fig_monthly = analyzer.plot_monthly_distribution()
        st.plotly_chart(fig_monthly, use_container_width=True)

        # Weekly distribution
        st.subheader("Weekly Time Distribution")
        fig_weekly = analyzer.plot_weekly_distribution()
        st.plotly_chart(fig_weekly, use_container_width=True)

        # Daily distribution
        st.subheader("Time Distribution by Day of Week")
        fig_daily = analyzer.plot_daily_distribution()
        st.plotly_chart(fig_daily, use_container_width=True)

    with tab3:
        st.header("Detailed Statistics")

        # Generate report
        report = analyzer.generate_report()
        st.text(report)

        st.divider()

        # Top activities
        st.subheader("Top 10 Specific Activities")
        df_top = pd.DataFrame(
            list(stats['top_activities'].items()),
            columns=['Activity', 'Hours']
        )
        st.dataframe(df_top, use_container_width=True)

        # Download options
        st.divider()
        st.subheader("Download Reports")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Download Text Report"):
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"time_analysis_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

        with col2:
            if st.button("📥 Generate Detailed Stats CSV"):
                with st.spinner("Generating detailed statistics..."):
                    analyzer.generate_detailed_stats()
                    st.success("✅ Detailed statistics saved to time_analysis_output/detailed_stats/")

    with tab4:
        st.header("AI-Powered Insights")

        if not os.getenv("OPENAI_API_KEY"):
            st.warning("⚠️ No API key configured. Please add your API key in the sidebar to enable AI insights.")
            st.info("💡 The AI can provide personalized insights and recommendations based on your time tracking data.")
        else:
            # Show current configuration
            current_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            current_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            st.info(f"**Current Configuration:**\n- Base URL: `{current_base_url}`\n- Model: `{current_model}`")

            if st.button("🤖 Generate AI Insights", type="primary"):
                with st.spinner("Generating AI insights..."):
                    stats = analyzer.get_activity_stats()
                    insights = get_llm_summary(stats)

                    if insights:
                        st.markdown("### AI Analysis")
                        st.markdown(insights)
                    else:
                        st.error("Failed to generate AI insights. Check your API configuration and try again.")

else:
    # Welcome screen
    st.info("👈 Please upload and select a file from the sidebar to begin analysis")

    # Show example of what the data should look like
    st.subheader("Expected Data Format")
    st.markdown("""
    Your Excel/CSV file should contain sheets named in the format `month.week` (e.g., `1.1`, `1.2`, etc.)

    Each sheet should have columns for Time and days of the week, with activities coded as:
    - `R: Rest activity`
    - `P: Procrastination activity`
    - `G: Guilt-free play activity`
    - `M: Mandatory work activity`
    - `W: Productive work activity`

    Example:
    ```
    Time     | Sunday | Monday      | Tuesday     | ...
    08:00    | R:     | W: Planning | W: Planning | ...
    08:30    | R:     | W: Coding   | W: Coding   | ...
    ```
    """)

    # Show existing files
    existing_files = get_existing_files()
    if existing_files:
        st.subheader("Files in Data Folder")
        for file in existing_files:
            st.write(f"📄 {file}")
