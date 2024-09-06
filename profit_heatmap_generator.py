import pandas as pd
import plotly.graph_objects as go


class ProfitHeatmapGenerator:
    def __init__(self, rental_properties, occupancy_rates, percentage_changes):
        self.rental_properties = rental_properties
        self.occupancy_rates = occupancy_rates
        self.percentage_changes = percentage_changes

    def calculate_profits(self):
        # Collect results
        results = []
        for occupancy in self.occupancy_rates:
            for change in self.percentage_changes:
                total_profit = 0
                for rental in self.rental_properties:
                    new_room_rate = rental.base_room_rate * (1 + change)
                    profit = rental.calculate_yearly_profit(occupancy, new_room_rate)
                    total_profit += profit
                results.append({
                    'Occupancy Rate': round(occupancy, 2),
                    'Percentage Change in Room Rate': round(change, 2),
                    'Cumulative Profit': round(total_profit, 2)
                })
        return pd.DataFrame(results)

    def create_heatmap(self, df):
        pivot_table = df.pivot(index='Percentage Change in Room Rate', columns='Occupancy Rate',
                               values='Cumulative Profit')
        text_matrix = pivot_table.map(lambda z: f"€{z:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        abs_max = max(abs(pivot_table.min().min()), abs(pivot_table.max().max()))
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot_table.values,
                x=self.occupancy_rates,
                y=self.percentage_changes,
                colorscale=['red', 'white', 'green'],
                zmin=-abs_max,
                zmax=abs_max,
                zmid=0,
                hoverinfo='z',
                showscale=True
            )
        )

        annotations = []
        for i, percentage_change in enumerate(self.percentage_changes):
            for j, occupancy_rate in enumerate(self.occupancy_rates):
                value = pivot_table.iloc[i, j]
                text_color = 'red' if value < 0 else 'black'
                annotations.append(
                    dict(
                        x=occupancy_rate,
                        y=percentage_change,
                        text=text_matrix.iloc[i, j],
                        showarrow=False,
                        font=dict(color=text_color, size=12),
                        xanchor='center',
                        yanchor='middle'
                    )
                )

        fig.update_layout(
            title='Impact of Room Rate Changes on Cumulative Profit (€)',
            xaxis_title='Occupancy Rate',
            yaxis_title='Percentage Change in Room Rate',
            xaxis=dict(tickmode='array', tickvals=self.occupancy_rates, ticktext=[f'{x:.1f}'
                                                                                  for x in self.occupancy_rates]),
            yaxis=dict(tickmode='array', tickvals=self.percentage_changes,
                       ticktext=[f'{x:.1f}' for x in self.percentage_changes]),
            annotations=annotations
        )

        fig.show()
