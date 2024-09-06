import pandas as pd
import numpy as np
import plotly.graph_objects as go
from rental_property import RentalProperty


def generate_heatmap_for_property(rental_property):
    # Define percentage changes and occupancy rates
    percentage_changes = np.linspace(-0.40, 0.40, 9)  # Percentage changes from -40% to +40%
    occupancies = np.linspace(0.1, 0.9, 9)  # Occupancy rates from 10% to 90%

    # Calculate room rates based on percentage changes of the baseline room rate and round to zero decimals
    adjusted_room_rates = [round(rental_property.base_room_rate * (1 + change)) for change in percentage_changes]

    # Collect results for the current property
    results = []
    for rate in adjusted_room_rates:
        row = []
        for occupancy in occupancies:
            # Calculate profit for the current property using the adjusted room rate
            profit = rental_property.calculate_yearly_profit(occupancy, rate)
            row.append(profit)
        results.append(row)

    # Create DataFrame from the results
    df = pd.DataFrame(results, columns=occupancies, index=adjusted_room_rates)  # Use absolute room rates as index

    # Create a text matrix for annotations using .map instead of .applymap
    text_matrix = df.map(lambda x: f"€{x:,.2f}")

    # Create a heatmap using plotly.graph_objects
    abs_max = max(abs(df.min().min()), abs(df.max().max()))

    fig = go.Figure(
        data=go.Heatmap(
            z=df.values,  # The actual profit values
            x=occupancies,
            y=adjusted_room_rates,  # Show rounded absolute room rates on the y-axis
            colorscale=['red', 'white', 'green'],  # Custom colorscale
            zmin=-abs_max,  # Set min for color scale as negative of abs_max
            zmax=abs_max,  # Set max for color scale as abs_max
            zmid=0,  # Center the white color around zero
            hoverinfo='z',  # Display value on hover
            showscale=True,
            text=text_matrix.values,  # Add text annotations
            texttemplate="%{text}",  # Template for showing the text
            textfont={"size": 12},  # Font size for the annotations
        )
    )

    # Customize the layout
    fig.update_layout(
        title='Yearly Profit by Room Rate Changes and Occupancy',
        xaxis_title='Calculated Occupancy (%)',
        yaxis_title='Room Rate (€)',  # Label for the y-axis showing absolute room rates
    )

    return fig.to_html(full_html=False)
