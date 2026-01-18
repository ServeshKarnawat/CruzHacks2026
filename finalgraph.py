import pandas as pd
import plotly.express as px

#  Range of Motion plotting
def plot_rom(df):
    df_cleaned = df[df['Rep_Count'] > 0]

    # 3. Create the Plotly figure
    fig = px.line(
        df_cleaned, 
        x='Timestamp', 
        y='Flex_Value', 
        color='Rep_Count',
        title='Range of Motion Colorized by Detected Repetitions',
        labels={'Flex_Value': 'Flex Value', 'Rep_Count': 'Repetition #'},

    )

    fig.update_layout(
        title_font_size=50,      # Increases font size
        title_font_family="Arial", # Optional: change font
    )

    # Optional: Improve layout
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(xaxis_title="Time", yaxis_title="Flex Value")

    # 4. Show the plot
    fig.show()
    fig.write_html('templates/rom.html')

# Steadiness plotting
def plot_steady(df):
    intensity_mean = df['Intensity'].mean()
    df['Intensity_Avg'] = intensity_mean
    y_min = df['Intensity'].min() * 1
    y_max = df['Intensity'].max() * 5

    df['Magnitude'] = df['Intensity']   


    fig = px.line(
        df,
        x='Timestamp',
        y='Magnitude',
        title='Steadiness',
        template='plotly_white',
    )

    # add constant
    fig.add_hline(
        y=intensity_mean,
    )
    fig.update_yaxes(range=[0, 0.4])

    fig.update_layout(
        title_font_size=50,      # Increases font size
        title_font_family="Arial", # Optional: change font
    )

    fig.show()
    fig.write_html('templates/steady.html')
