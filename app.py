import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(page_title="Lin's Training Dashboard", layout="wide")
st.title("Lin's Training Dashboard")

# Load and prepare data
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('data/training-data.csv')
        required_columns = ['ID', 'Exercise', 'Reps', 'Load', 'Weight_Used', 'Good', 'Timestamp']
        if not all(col in data.columns for col in required_columns):
            st.error("Missing required columns in the data")
            st.stop()
        data = data.dropna(subset=['Exercise', 'Reps', 'Load', 'Weight_Used', 'Good'])
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

data = load_data()

# Create tabs for S, B, D exercises
tab_s, tab_b, tab_d = st.tabs(["SQUAT", "BENCH", "DEADLIFT"])

def get_rep_range(reps):
    if reps == 1:
        return "1 Rep"
    elif reps <= 3:
        return "2-3 Reps"
    else:
        return "4+ Reps"

def get_load_range(load):
    if load <= 6:
        return "5-6"
    elif load == 7:
        return "7"
    else:
        return "8-9"

def create_exercise_plots(exercise_data, exercise_name):
    # Add rep range and load range categories to data
    exercise_data['Rep_Range'] = exercise_data['Reps'].apply(get_rep_range)
    exercise_data['Load_Range'] = exercise_data['Load'].apply(get_load_range)
    
    # Define ranges order
    rep_ranges = ["1 Rep", "2-3 Reps", "4+ Reps"]
    load_ranges = ["5-6", "7", "8-9"]
    
    # Create plots for each rep range
    for rep_range in rep_ranges:
        rep_range_data = exercise_data[exercise_data['Rep_Range'] == rep_range]
        
        if len(rep_range_data) > 0:
            st.subheader(f"{rep_range}")
            
            # Create plots for each load range within the rep range
            for load_range in load_ranges:
                range_data = rep_range_data[rep_range_data['Load_Range'] == load_range]
                
                if len(range_data) > 0:
                    # Sort by ID and create sequence
                    range_data = range_data.sort_values('ID').reset_index(drop=True)
                    range_data['Sequence'] = range(1, len(range_data) + 1)
                    
                    # Create figure with single trendline
                    fig = go.Figure()
                    
                    # Add the line and points
                    fig.add_trace(go.Scatter(
                        x=range_data['Sequence'],
                        y=range_data['Weight_Used'],
                        mode='lines+markers+text',
                        showlegend=False,
                        line=dict(color='blue'),
                        marker=dict(
                            color=range_data['Good'].apply(lambda x: 'red' if x == 'n' else 'blue'),
                            size=8
                        ),
                        text=range_data['Timestamp'],
                        textposition="top right",
                        textfont=dict(size=10),
                        hovertemplate=(
                            "ID: %{customdata[0]}<br>" +
                            "Reps: %{customdata[1]}<br>" +
                            "RPE: %{customdata[2]}<br>" +
                            "Weight: %{y} kg<br>" +
                            "Good: %{customdata[3]}" +
                            "<extra></extra>"
                        ),
                        customdata=range_data[['ID', 'Reps', 'Load', 'Good']].values
                    ))
                    
                    fig.update_layout(
                        title=f"RPE {load_range}",
                        xaxis_title="Sequence",
                        yaxis_title="Weight Used (kg)",
                        showlegend=False,
                        height=400,
                        xaxis=dict(
                            tickmode='linear',
                            tick0=1,
                            dtick=1,
                            tickformat='d'
                        ),
                        margin=dict(t=50, r=50)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

# S tab content
with tab_s:
    s_data = data[data["Exercise"] == "S"]
    create_exercise_plots(s_data, "S")

# B tab content
with tab_b:
    b_data = data[data["Exercise"] == "B"]
    create_exercise_plots(b_data, "B")

# D tab content
with tab_d:
    d_data = data[data["Exercise"] == "D"]
    create_exercise_plots(d_data, "D")
