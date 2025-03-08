import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import os
from datetime import datetime

# Set matplotlib to use a non-GUI backend
matplotlib.use('Agg')

class ChartService:
    @staticmethod
    def generate_depreciation_chart(vehicle1, vehicle2, comparison):
        """Generate a chart showing vehicle depreciation over time"""
        # Create figure and axis
        plt.figure(figsize=(10, 6))
        
        # Extract data
        years = list(range(len(comparison['vehicle1']['yearly_values']) + 1))
        
        # Vehicle 1 values (starting with initial price)
        v1_values = [comparison['vehicle1']['initial_price']]
        v1_values.extend([year_data['end_value'] for year_data in comparison['vehicle1']['yearly_values']])
        
        # Vehicle 2 values (starting with initial price)
        v2_values = [comparison['vehicle2']['initial_price']]
        v2_values.extend([year_data['end_value'] for year_data in comparison['vehicle2']['yearly_values']])
        
        # Plot data
        plt.plot(years, v1_values, 'b-', linewidth=2.5, label=f"{vehicle1.make} {vehicle1.model}")
        plt.plot(years, v2_values, 'r-', linewidth=2.5, label=f"{vehicle2.make} {vehicle2.model}")
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value ($)')
        plt.title('Vehicle Value Over Time (Dollars)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"
    
    @staticmethod
    def generate_retention_chart(vehicle1, vehicle2, comparison):
        """Generate a chart showing value retention percentage"""
        # Create figure and axis
        plt.figure(figsize=(10, 6))
        
        # Extract data
        years = list(range(len(comparison['vehicle1']['yearly_values']) + 1))
        
        # Calculate retention percentages
        v1_initial = comparison['vehicle1']['initial_price']
        v2_initial = comparison['vehicle2']['initial_price']
        
        # Start with 100% retention
        v1_retention = [100]
        v1_values = [comparison['vehicle1']['initial_price']]
        v1_values.extend([year_data['end_value'] for year_data in comparison['vehicle1']['yearly_values']])
        for value in v1_values[1:]:
            v1_retention.append((value / v1_initial) * 100)
        
        v2_retention = [100]
        v2_values = [comparison['vehicle2']['initial_price']]
        v2_values.extend([year_data['end_value'] for year_data in comparison['vehicle2']['yearly_values']])
        for value in v2_values[1:]:
            v2_retention.append((value / v2_initial) * 100)
        
        # Debug output
        print("Vehicle 1 retention:", v1_retention)
        print("Vehicle 2 retention:", v2_retention)
        
        # Plot data with different styles to ensure visibility
        plt.plot(years, v1_retention, 'b-', linewidth=2.5, label=f"{vehicle1.make} {vehicle1.model}")
        plt.plot(years, v2_retention, 'r--', linewidth=2.5, label=f"{vehicle2.make} {vehicle2.model}")
        
        # Set y-axis limits to ensure both lines are visible
        plt.ylim(0, 105)  # Set y-axis from 0% to 105%
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value Retained (%)')
        plt.title('Value Retention Percentage')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as percentage
        plt.gca().yaxis.set_major_formatter('{x:.0f}%')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def generate_single_vehicle_chart(vehicle, depreciation_data):
        """Generate a chart showing vehicle depreciation over time for a single vehicle"""
        # Create figure and axis
        plt.figure(figsize=(10, 6))
        
        # Extract data
        years = list(range(len(depreciation_data['yearly_values']) + 1))
        
        # Vehicle values (starting with initial price)
        values = [depreciation_data['initial_price']]
        values.extend([year_data['end_value'] for year_data in depreciation_data['yearly_values']])
        
        # Plot data
        plt.plot(years, values, 'b-', linewidth=2.5, label=f"{vehicle.make} {vehicle.model}")
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value ($)')
        plt.title('Vehicle Value Over Time (Dollars)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def generate_single_vehicle_retention_chart(vehicle, depreciation_data):
        """Generate a chart showing value retention percentage for a single vehicle"""
        # Create figure and axis
        plt.figure(figsize=(10, 6))
        
        # Extract data
        years = list(range(len(depreciation_data['yearly_values']) + 1))
        
        # Calculate retention percentages
        initial = depreciation_data['initial_price']
        
        # Start with 100% retention
        retention = [100]
        values = [depreciation_data['initial_price']]
        values.extend([year_data['end_value'] for year_data in depreciation_data['yearly_values']])
        for value in values[1:]:
            retention.append((value / initial) * 100)
        
        # Plot data
        plt.plot(years, retention, 'b-', linewidth=2.5, label=f"{vehicle.make} {vehicle.model}")
        
        # Set y-axis limits
        plt.ylim(0, 105)  # Set y-axis from 0% to 105%
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value Retained (%)')
        plt.title('Value Retention Percentage')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as percentage
        plt.gca().yaxis.set_major_formatter('{x:.0f}%')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def generate_multi_vehicle_chart(vehicles, depreciation_data_list):
        """Generate a chart showing vehicle depreciation over time for multiple vehicles"""
        # Create figure and axis
        plt.figure(figsize=(12, 7))
        
        # Define a list of colors for the lines
        colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
        
        # Extract data for each vehicle
        for i, (vehicle, depreciation_data) in enumerate(zip(vehicles, depreciation_data_list)):
            # Extract years
            years = list(range(len(depreciation_data['yearly_values']) + 1))
            
            # Vehicle values (starting with initial price)
            values = [depreciation_data['initial_price']]
            values.extend([year_data['end_value'] for year_data in depreciation_data['yearly_values']])
            
            # Plot data with a different color
            color_index = i % len(colors)
            plt.plot(years, values, f'{colors[color_index]}-', linewidth=2.5, 
                     label=f"{vehicle.make} {vehicle.model} ({vehicle.year})")
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value ($)')
        plt.title('Vehicle Value Over Time (Dollars)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as currency
        plt.gca().yaxis.set_major_formatter('${x:,.0f}')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def generate_multi_vehicle_retention_chart(vehicles, depreciation_data_list):
        """Generate a chart showing value retention percentage for multiple vehicles"""
        # Create figure and axis
        plt.figure(figsize=(12, 7))
        
        # Define a list of colors and line styles for the lines
        colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
        line_styles = ['-', '--', '-.', ':']
        
        # Extract data for each vehicle
        for i, (vehicle, depreciation_data) in enumerate(zip(vehicles, depreciation_data_list)):
            # Extract years
            years = list(range(len(depreciation_data['yearly_values']) + 1))
            
            # Calculate retention percentages
            initial = depreciation_data['initial_price']
            
            # Start with 100% retention
            retention = [100]
            values = [depreciation_data['initial_price']]
            values.extend([year_data['end_value'] for year_data in depreciation_data['yearly_values']])
            for value in values[1:]:
                retention.append((value / initial) * 100)
            
            # Plot data with a different color and line style
            color_index = i % len(colors)
            style_index = i % len(line_styles)
            plt.plot(years, retention, f'{colors[color_index]}{line_styles[style_index]}', 
                     linewidth=2.5, label=f"{vehicle.make} {vehicle.model} ({vehicle.year})")
        
        # Set y-axis limits
        plt.ylim(0, 105)  # Set y-axis from 0% to 105%
        
        # Add labels and title
        plt.xlabel('Years')
        plt.ylabel('Value Retained (%)')
        plt.title('Value Retention Percentage')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format y-axis as percentage
        plt.gca().yaxis.set_major_formatter('{x:.0f}%')
        
        # Save to memory
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        
        # Encode as base64 for HTML embedding
        encoded = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{encoded}"
