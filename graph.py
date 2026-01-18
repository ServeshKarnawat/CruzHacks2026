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
        title='Range of Motion',
        labels={'Flex_Value': 'Flex Value', 'Rep_Count': 'Repetition #'},

    )

    fig.update_layout(
        title_font_size=20,      # Increases font size
        title_font_family="Arial", # Optional: change font
        xaxis_title="Time", 
        yaxis_title="Flex Value",
        margin=dict(l=20, r=12, t=60, b=12), # Increased top margin (t) for title space

        paper_bgcolor='rgba(255, 255, 255,0.50)', # Outer background (margins)
        plot_bgcolor='rgba(0,0,0,0)',  # Inner plot area background
        
    )

    fig.update_xaxes(
        tickfont=dict(size=5),      # Smaller font
        title_font=dict(size=10),    # Smaller axis title
        tickangle=45                 # Keeps labels readable but compact
    )
    
    # Optional: Improve layout
    fig.update_traces(marker=dict(size=8))

    # 4. Show the plot
    #fig.show()
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
    fig.update_yaxes(
        range=[0, 0.3],
        tickfont=dict(size=5),
        title_font=dict(size=10)
    )

    fig.update_xaxes(
        tickfont=dict(size=5),      # Smaller font
        title_font=dict(size=10),    # Smaller axis title
        tickangle=45,              # Keeps labels readable but compact
    )

    fig.update_layout(
        title={
            'text': 'Steadiness',
            'y': 0.9,          # Sets the vertical position (0 to 1)
            'x': 0.5,          # Sets the horizontal position (0 to 1)
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=20,
        title_font_family="Arial",
        margin=dict(l=20, r=20, t=60, b=20), # Increased top margin (t) for title space
        autosize=True,

        paper_bgcolor='rgba(255, 255, 255,0.50)', # Outer background (margins)

        plot_bgcolor='rgba(0,0,0,0)',  # Inner plot area background
    )
    #fig.show()
    fig.write_html('templates/steady.html')

df = pd.read_csv('arm_stability_data_good.csv')
plot_rom(df)
plot_steady(df)
