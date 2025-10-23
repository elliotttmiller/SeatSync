#!/bin/bash
# SeatSync Streamlit Development App Runner

echo "🎫 Starting SeatSync Development Dashboard..."
echo "=============================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit plotly
fi

# Check if backend dependencies are installed
echo "📦 Checking backend dependencies..."
pip install -q -r backend/requirements.txt

echo ""
echo "🚀 Launching Streamlit app..."
echo "=============================================="
echo "Access the dashboard at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Run streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address localhost
