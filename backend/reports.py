from fpdf import FPDF
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_agg import FigureCanvasAgg
import datetime
import json
import tempfile
import os
from collections import defaultdict
import numpy as np
from config import db, RESOURCES_COLLECTION

class CampusAssetsPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Professional layout constants
        self.MARGIN_LEFT = 20
        self.MARGIN_RIGHT = 20
        self.MARGIN_TOP = 25
        self.MARGIN_BOTTOM = 25
        self.PAGE_WIDTH = 210  # A4
        self.PAGE_HEIGHT = 297  # A4
        self.EFFECTIVE_WIDTH = self.PAGE_WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        
        # Set margins and auto page break
        self.set_margins(self.MARGIN_LEFT, self.MARGIN_TOP, self.MARGIN_RIGHT)
        self.set_auto_page_break(auto=True, margin=self.MARGIN_BOTTOM)
        
        # Color palette
        self.COLOR_PRIMARY = (52, 73, 94)     # Dark blue-gray
        self.COLOR_SECONDARY = (41, 128, 185)  # Blue
        self.COLOR_ACCENT = (231, 76, 60)      # Red
        self.COLOR_SUCCESS = (46, 204, 113)    # Green
        self.COLOR_TEXT = (44, 62, 80)         # Dark gray
        self.COLOR_LIGHT = (236, 240, 241)     # Light gray

    def header(self):
        """Professional header with consistent styling"""
        # Company/System title
        self.set_font('Arial', 'B', 18)
        self.set_text_color(*self.COLOR_PRIMARY)
        self.cell(0, 12, 'CAMPUS ASSETS MANAGEMENT SYSTEM', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', '', 11)
        self.set_text_color(*self.COLOR_TEXT)
        self.cell(0, 6, 'Comprehensive Assets Analysis Report', 0, 1, 'C')
        
        # Professional line
        self.set_draw_color(*self.COLOR_SECONDARY)
        self.set_line_width(0.5)
        self.line(self.MARGIN_LEFT, self.get_y() + 2, 
                 self.MARGIN_LEFT + self.EFFECTIVE_WIDTH, self.get_y() + 2)
        self.ln(8)

    def footer(self):
        """Professional footer"""
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.set_text_color(127, 140, 141)
        footer_text = f'Page {self.page_no()} | Generated: {datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")}'
        self.cell(0, 10, footer_text, 0, 0, 'C')

    def section_title(self, title, icon=""):
        """Add section title with professional styling"""
        self.ln(8)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.COLOR_PRIMARY)
        display_title = f'{icon} {title}' if icon else title
        self.cell(0, 10, display_title.upper(), 0, 1, 'L')
        
        # Underline
        self.set_draw_color(*self.COLOR_PRIMARY)
        self.set_line_width(0.3)
        self.line(self.MARGIN_LEFT, self.get_y(), 
                 self.MARGIN_LEFT + self.EFFECTIVE_WIDTH, self.get_y())
        self.ln(6)

    def subsection_title(self, title):
        """Add subsection title"""
        self.ln(4)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*self.COLOR_TEXT)
        self.cell(0, 7, title, 0, 1, 'L')
        self.ln(2)

    def content_text(self, text, indent=0):
        """Add content text with proper wrapping"""
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.COLOR_TEXT)
        
        # Handle multiline text
        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                self.ln(4)
                continue
                
            # Calculate available width
            available_width = self.EFFECTIVE_WIDTH - indent
            
            # Check if we need to wrap text
            if self.get_string_width(line) > available_width:
                # Split text into multiple lines
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if self.get_string_width(test_line) <= available_width:
                        current_line = test_line
                    else:
                        if current_line:
                            if indent > 0:
                                self.set_x(self.MARGIN_LEFT + indent)
                            self.cell(available_width, 5, current_line, 0, 1, 'L')
                            current_line = word
                        else:
                            # Single word too long, just add it
                            if indent > 0:
                                self.set_x(self.MARGIN_LEFT + indent)
                            self.cell(available_width, 5, word, 0, 1, 'L')
                            current_line = ""
                
                # Add remaining text
                if current_line:
                    if indent > 0:
                        self.set_x(self.MARGIN_LEFT + indent)
                    self.cell(available_width, 5, current_line, 0, 1, 'L')
            else:
                # Text fits on one line
                if indent > 0:
                    self.set_x(self.MARGIN_LEFT + indent)
                self.cell(available_width, 5, line, 0, 1, 'L')

    def create_stat_grid(self, stats_data, columns=4):
        """Create responsive statistics grid"""
        if not stats_data:
            return
            
        # Calculate dimensions
        box_width = self.EFFECTIVE_WIDTH / columns
        box_height = 28
        padding = 2
        
        # Process stats in rows
        for row_start in range(0, len(stats_data), columns):
            row_data = stats_data[row_start:row_start + columns]
            start_y = self.get_y()
            
            # Check if row fits on current page
            if start_y + box_height > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
                self.add_page()
                start_y = self.get_y()
            
            # Draw boxes for this row
            for i, (title, value) in enumerate(row_data):
                x_pos = self.MARGIN_LEFT + (i * box_width)
                self.draw_stat_box(title, value, x_pos, start_y, 
                                 box_width - padding, box_height)
            
            # Move to next row
            self.set_y(start_y + box_height + 6)

    def draw_stat_box(self, title, value, x, y, width, height):
        """Draw individual stat box with responsive text"""
        # Background
        self.set_fill_color(*self.COLOR_LIGHT)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.rect(x, y, width, height, 'DF')
        
        # Title
        self.set_xy(x + 3, y + 3)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(108, 117, 125)
        
        # Fit title in available space
        title_text = str(title)
        max_width = width - 6
        while self.get_string_width(title_text) > max_width and len(title_text) > 5:
            title_text = title_text[:-4] + '...'
        
        self.cell(max_width, 5, title_text, 0, 0, 'C')
        
        # Value
        self.set_xy(x + 3, y + 12)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*self.COLOR_SECONDARY)
        
        # Format and fit value
        value_text = str(value)
        font_size = 12
        
        # Reduce font size if needed
        while font_size > 8 and self.get_string_width(value_text) > max_width:
            font_size -= 1
            self.set_font('Arial', 'B', font_size)
        
        # Truncate if still too long
        while self.get_string_width(value_text) > max_width and len(value_text) > 5:
            if 'Rs.' in value_text and ',' in value_text:
                value_text = value_text.replace(',', '')
            else:
                value_text = value_text[:-4] + '...'
        
        self.cell(max_width, 10, value_text, 0, 0, 'C')

    def create_responsive_table(self, headers, data, column_ratios=None):
        """Create table with automatic text wrapping and page breaks"""
        if not headers or not data:
            return
            
        # Calculate column widths
        if column_ratios is None:
            column_ratios = [1.0 / len(headers)] * len(headers)
        
        # Ensure ratios sum to 1.0
        total_ratio = sum(column_ratios)
        column_ratios = [r / total_ratio for r in column_ratios]
        
        col_widths = [ratio * self.EFFECTIVE_WIDTH for ratio in column_ratios]
        
        # Draw table
        self.draw_table_header(headers, col_widths)
        self.draw_table_data(data, col_widths)

    def draw_table_header(self, headers, col_widths):
        """Draw table header with professional styling"""
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(*self.COLOR_PRIMARY)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(200, 200, 200)
        
        header_height = 8
        
        for i, header in enumerate(headers):
            # Fit header text
            header_text = str(header)
            while self.get_string_width(header_text) > col_widths[i] - 4 and len(header_text) > 3:
                header_text = header_text[:-4] + '...'
            
            self.cell(col_widths[i], header_height, header_text, 1, 0, 'C', True)
        
        self.ln()

    def draw_table_data(self, data, col_widths):
        """Draw table data with text wrapping and page management"""
        self.set_font('Arial', '', 8)
        self.set_text_color(*self.COLOR_TEXT)
        
        for row_idx, row in enumerate(data):
            # Check if we need a new page
            if self.get_y() + 20 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
                self.add_page()
            
            # Calculate row height based on content
            row_height = max(6, self.calculate_row_height(row, col_widths))
            
            # Set alternating row colors
            if row_idx % 2 == 0:
                self.set_fill_color(248, 249, 250)
            else:
                self.set_fill_color(255, 255, 255)
            
            # Draw row
            self.draw_table_row(row, col_widths, row_height)

    def calculate_row_height(self, row, col_widths):
        """Calculate required height for a table row"""
        max_lines = 1
        
        for i, cell_data in enumerate(row):
            cell_text = str(cell_data)
            available_width = col_widths[i] - 4  # Account for padding
            
            # Count lines needed for this cell
            lines_needed = self.count_text_lines(cell_text, available_width)
            max_lines = max(max_lines, lines_needed)
        
        return max_lines * 4 + 2

    def count_text_lines(self, text, max_width):
        """Count how many lines are needed for text in given width"""
        if self.get_string_width(text) <= max_width:
            return 1
        
        words = text.split()
        lines = 1
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.get_string_width(test_line) > max_width:
                lines += 1
                current_line = word
            else:
                current_line = test_line
        
        return lines

    def draw_table_row(self, row, col_widths, row_height):
        """Draw a single table row with proper text wrapping"""
        start_y = self.get_y()
        
        for i, cell_data in enumerate(row):
            cell_text = str(cell_data)
            available_width = col_widths[i] - 4
            
            # Draw cell background
            x_pos = self.get_x()
            self.rect(x_pos, start_y, col_widths[i], row_height, 'DF')
            
            # Draw text
            self.set_xy(x_pos + 2, start_y + 1)
            
            # Handle text wrapping
            if self.get_string_width(cell_text) > available_width:
                # Text needs wrapping
                words = cell_text.split()
                current_line = ""
                y_offset = 1
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if self.get_string_width(test_line) <= available_width:
                        current_line = test_line
                    else:
                        if current_line:
                            self.set_xy(x_pos + 2, start_y + y_offset)
                            self.cell(available_width, 4, current_line, 0, 0, 'L')
                            y_offset += 4
                            current_line = word
                        else:
                            # Single word too long
                            self.set_xy(x_pos + 2, start_y + y_offset)
                            self.cell(available_width, 4, word, 0, 0, 'L')
                            y_offset += 4
                            current_line = ""
                
                # Add remaining text
                if current_line:
                    self.set_xy(x_pos + 2, start_y + y_offset)
                    self.cell(available_width, 4, current_line, 0, 0, 'L')
            else:
                # Text fits in one line
                self.cell(available_width, row_height - 2, cell_text, 0, 0, 'L')
            
            # Move to next column
            self.set_xy(x_pos + col_widths[i], start_y)
        
        # Move to next row
        self.set_y(start_y + row_height)

    def add_chart_section(self, chart_path, title, height=80):
        """Add chart with proper spacing and page management"""
        # Check if chart fits on current page
        if self.get_y() + height + 15 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self.add_page()
        
        # Add chart title
        self.subsection_title(title)
        
        # Add chart image
        if os.path.exists(chart_path):
            self.image(chart_path, x=self.MARGIN_LEFT, w=self.EFFECTIVE_WIDTH, h=height)
            self.ln(height + 8)
        else:
            self.content_text(f"Chart not available: {chart_path}")

class ReportService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def generate_chart(self, chart_type, data, title, filename):
        """Generate professional charts"""
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Color palette
        colors = ['#34495e', '#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c', '#95a5a6']
        
        if chart_type == 'bar':
            labels, values = zip(*data) if data else ([], [])
            bars = ax.bar(labels, values, color=colors[:len(labels)])
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'Rs.{height:,.0f}' if height > 1000 else f'{height:.0f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            plt.xticks(rotation=45, ha='right')
            
        elif chart_type == 'pie':
            labels, values = zip(*data) if data else ([], [])
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                            colors=colors[:len(labels)], startangle=90)
            
            # Style pie chart text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
        
        # Professional styling
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='#2c3e50')
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(self.temp_dir, filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return chart_path

    def generate_comprehensive_report(self):
        """Generate the complete PDF report"""
        try:
            # Fetch data
            resources = list(db[RESOURCES_COLLECTION].find({}))
            
            if not resources:
                raise ValueError("No resources found in database")

            # Calculate statistics
            stats = self._calculate_statistics(resources)
            
            # Create PDF
            pdf = CampusAssetsPDF()

            # Build report sections
            self._add_cover_page(pdf, stats)
            self._add_executive_summary(pdf, stats)
            self._add_detailed_analytics(pdf, stats)
            self._add_department_analysis(pdf, stats)
            self._add_location_analysis(pdf, stats)
            self._add_financial_analysis(pdf, stats)
            self._add_asset_inventory(pdf, resources)
            self._add_recommendations(pdf, stats)

            # Generate output
            pdf_output = BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            return pdf_output

        except Exception as e:
            raise Exception(f"Failed to generate report: {str(e)}")

    def _calculate_statistics(self, resources):
        """Calculate comprehensive statistics"""
        stats = {
            'total_resources': len(resources),
            'total_cost': sum(float(r.get('cost', 0)) for r in resources),
            'departments': defaultdict(lambda: {'count': 0, 'cost': 0, 'items': []}),
            'locations': defaultdict(lambda: {'count': 0, 'cost': 0, 'items': []}),
            'cost_ranges': {'0-10k': 0, '10k-50k': 0, '50k-100k': 0, '100k+': 0},
            'recent_additions': 0,
            'oldest_asset': None,
            'newest_asset': None,
            'most_expensive': None,
            'least_expensive': None,
            'avg_cost': 0,
            'median_cost': 0
        }

        costs = []
        dates = []

        # Process each resource
        for resource in resources:
            cost = float(resource.get('cost', 0))
            dept = resource.get('department', 'Unknown')
            location = resource.get('location', 'Unknown')
            created_at = resource.get('created_at')

            costs.append(cost)

            # Department statistics
            stats['departments'][dept]['count'] += 1
            stats['departments'][dept]['cost'] += cost
            stats['departments'][dept]['items'].append(resource)

            # Location statistics
            stats['locations'][location]['count'] += 1
            stats['locations'][location]['cost'] += cost
            stats['locations'][location]['items'].append(resource)

            # Cost range analysis
            if cost <= 10000:
                stats['cost_ranges']['0-10k'] += 1
            elif cost <= 50000:
                stats['cost_ranges']['10k-50k'] += 1
            elif cost <= 100000:
                stats['cost_ranges']['50k-100k'] += 1
            else:
                stats['cost_ranges']['100k+'] += 1

            # Track extremes
            if not stats['most_expensive'] or cost > float(stats['most_expensive'].get('cost', 0)):
                stats['most_expensive'] = resource

            if not stats['least_expensive'] or cost < float(stats['least_expensive'].get('cost', float('inf'))):
                stats['least_expensive'] = resource

            # Date analysis
            if created_at:
                dates.append(created_at)
                if not stats['newest_asset'] or created_at > stats['newest_asset'].get('created_at'):
                    stats['newest_asset'] = resource
                if not stats['oldest_asset'] or created_at < stats['oldest_asset'].get('created_at'):
                    stats['oldest_asset'] = resource

        # Calculate derived statistics
        if costs:
            stats['avg_cost'] = sum(costs) / len(costs)
            stats['median_cost'] = sorted(costs)[len(costs)//2]

        # Recent additions
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        stats['recent_additions'] = sum(1 for d in dates if d and d >= thirty_days_ago)

        return stats

    def _add_cover_page(self, pdf, stats):
        """Professional cover page"""
        pdf.add_page()
        pdf.ln(50)
        
        # Main title
        pdf.set_font('Arial', 'B', 32)
        pdf.set_text_color(*pdf.COLOR_PRIMARY)
        pdf.cell(0, 15, 'CAMPUS ASSETS', 0, 1, 'C')
        pdf.cell(0, 15, 'ANALYSIS REPORT', 0, 1, 'C')
        pdf.ln(25)
        
        # Subtitle
        pdf.set_font('Arial', '', 16)
        pdf.set_text_color(*pdf.COLOR_TEXT)
        pdf.cell(0, 8, 'Comprehensive Overview & Strategic Insights', 0, 1, 'C')
        pdf.ln(35)
        
        # Key statistics
        cover_stats = [
            ('Total Assets', f"{stats['total_resources']:,}"),
            ('Total Value', f"Rs.{stats['total_cost']:,.0f}"),
            ('Departments', len(stats['departments'])),
            ('Locations', len(stats['locations']))
        ]
        
        pdf.create_stat_grid(cover_stats, 4)
        pdf.ln(25)
        
        # Report metadata
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(127, 140, 141)
        pdf.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
        pdf.cell(0, 6, f"Data Period: Complete Asset Database", 0, 1, 'C')
        pdf.cell(0, 6, f"Report Type: Comprehensive Analysis", 0, 1, 'C')

    def _add_executive_summary(self, pdf, stats):
        """Executive summary section"""
        pdf.add_page()
        pdf.section_title('Executive Summary')

        # Key findings
        pdf.subsection_title('Key Findings')
        
        findings = [
            f"Total of {stats['total_resources']:,} assets worth Rs.{stats['total_cost']:,.0f} under management",
            f"Average asset value: Rs.{stats['avg_cost']:,.0f}",
            f"{len(stats['departments'])} departments across {len(stats['locations'])} locations",
            f"{stats['recent_additions']} new assets added in the last 30 days"
        ]

        if stats['most_expensive']:
            findings.append(f"Most valuable asset: {stats['most_expensive'].get('description', 'N/A')} (Rs.{float(stats['most_expensive'].get('cost', 0)):,.0f})")

        top_dept = max(stats['departments'].items(), key=lambda x: x[1]['cost']) if stats['departments'] else None
        if top_dept:
            findings.append(f"Highest value department: {top_dept[0]} (Rs.{top_dept[1]['cost']:,.0f})")

        for finding in findings:
            pdf.content_text(f"- {finding}")  # Changed from • to -
        
        pdf.ln(8)

        # Distribution analysis
        pdf.subsection_title('Asset Value Distribution')
        
        distribution = [
            f"Budget assets (Rs.0-10k): {stats['cost_ranges']['0-10k']} items",
            f"Standard assets (Rs.10k-50k): {stats['cost_ranges']['10k-50k']} items",
            f"Premium assets (Rs.50k-100k): {stats['cost_ranges']['50k-100k']} items",
            f"High-value assets (Rs.100k+): {stats['cost_ranges']['100k+']} items"
        ]

        for item in distribution:
            pdf.content_text(f"- {item}")  # Changed from • to -

    def _add_detailed_analytics(self, pdf, stats):
        """Detailed analytics with charts"""
        pdf.add_page()
        pdf.section_title('Detailed Analytics')

        # Department chart
        dept_data = [(dept, data['cost']) for dept, data in sorted(stats['departments'].items(), key=lambda x: x[1]['cost'], reverse=True)]
        chart_path = self.generate_chart('bar', dept_data, 'Department-wise Asset Value Distribution', 'dept_chart.png')
        pdf.add_chart_section(chart_path, 'Department-wise Asset Value Distribution')

        # Location chart
        location_data = [(loc, data['count']) for loc, data in sorted(stats['locations'].items(), key=lambda x: x[1]['count'], reverse=True)[:8]]
        chart_path2 = self.generate_chart('pie', location_data, 'Asset Distribution by Location (Top 8)', 'location_chart.png')
        pdf.add_chart_section(chart_path2, 'Asset Distribution by Location')

    def _add_department_analysis(self, pdf, stats):
        """Department analysis section"""
        pdf.add_page()
        pdf.section_title('Department Analysis')

        # Department overview table
        pdf.subsection_title('Department Overview')
        
        headers = ['Department', 'Assets', 'Total Value', 'Avg Value', '% of Total']
        data = []
        
        sorted_depts = sorted(stats['departments'].items(), key=lambda x: x[1]['cost'], reverse=True)
        
        for dept, dept_data in sorted_depts:
            avg_value = dept_data['cost'] / dept_data['count'] if dept_data['count'] > 0 else 0
            percentage = (dept_data['cost'] / stats['total_cost'] * 100) if stats['total_cost'] > 0 else 0
            
            data.append([
                dept,
                f"{dept_data['count']}",
                f"Rs.{dept_data['cost']:,.0f}",
                f"Rs.{avg_value:,.0f}",
                f"{percentage:.1f}%"
            ])

        pdf.create_responsive_table(headers, data, [0.3, 0.15, 0.25, 0.2, 0.1])
        pdf.ln(8)

        # Detailed analysis of top departments
        pdf.subsection_title('Top 3 Departments - Detailed Analysis')
        
        for i, (dept, dept_data) in enumerate(sorted_depts[:3]):
            pdf.content_text(f"{i+1}. {dept} Department:")
            pdf.content_text(f"Total Assets: {dept_data['count']}", 10)
            pdf.content_text(f"Total Value: Rs.{dept_data['cost']:,.0f}", 10)
            pdf.content_text(f"Average Value: Rs.{dept_data['cost']/dept_data['count']:,.0f}", 10)
            
            # Top assets in department
            top_items = sorted(dept_data['items'], key=lambda x: float(x.get('cost', 0)), reverse=True)[:3]
            if top_items:
                pdf.content_text("Top assets:", 10)
                for j, item in enumerate(top_items, 1):
                    pdf.content_text(f"{j}. {item.get('description', 'N/A')} - Rs.{float(item.get('cost', 0)):,.0f}", 15)
            pdf.ln(4)

    def _add_location_analysis(self, pdf, stats):
        """Location analysis section"""
        pdf.add_page()
        pdf.section_title('Location Analysis')

        # Location overview table
        pdf.subsection_title('Location Overview')
        
        headers = ['Location', 'Assets', 'Total Value', 'Avg Value']
        data = []
        
        sorted_locations = sorted(stats['locations'].items(), key=lambda x: x[1]['cost'], reverse=True)
        
        for location, loc_data in sorted_locations[:15]:  # Top 15 locations
            avg_value = loc_data['cost'] / loc_data['count'] if loc_data['count'] > 0 else 0
            
            data.append([
                location,
                f"{loc_data['count']}",
                f"Rs.{loc_data['cost']:,.0f}",
                f"Rs.{avg_value:,.0f}"
            ])

        pdf.create_responsive_table(headers, data, [0.45, 0.15, 0.25, 0.15])

    def _add_financial_analysis(self, pdf, stats):
        """Financial analysis section"""
        pdf.add_page()
        pdf.section_title('Financial Analysis')

        # Financial overview
        pdf.subsection_title('Financial Overview')
        
        financial_stats = [
            ('Total Value', f"Rs.{stats['total_cost']:,.0f}"),
            ('Average Value', f"Rs.{stats['avg_cost']:,.0f}"),
            ('Median Value', f"Rs.{stats['median_cost']:,.0f}"),
            ('Highest Value', f"Rs.{float(stats['most_expensive'].get('cost', 0)):,.0f}")
        ]
        
        pdf.create_stat_grid(financial_stats, 4)
        pdf.ln(8)

        # Value categories
        pdf.subsection_title('Asset Value Categories')
        
        total_assets = stats['total_resources']
        categories = [
            ('Budget Assets (Rs.0-10k)', stats['cost_ranges']['0-10k'], (stats['cost_ranges']['0-10k']/total_assets*100) if total_assets > 0 else 0),
            ('Standard Assets (Rs.10k-50k)', stats['cost_ranges']['10k-50k'], (stats['cost_ranges']['10k-50k']/total_assets*100) if total_assets > 0 else 0),
            ('Premium Assets (Rs.50k-100k)', stats['cost_ranges']['50k-100k'], (stats['cost_ranges']['50k-100k']/total_assets*100) if total_assets > 0 else 0),
            ('High-Value Assets (Rs.100k+)', stats['cost_ranges']['100k+'], (stats['cost_ranges']['100k+']/total_assets*100) if total_assets > 0 else 0)
        ]

        for category, count, percentage in categories:
            pdf.content_text(f"- {category}: {count} assets ({percentage:.1f}%)")  # Changed from • to -
        
        pdf.ln(8)

        # Asset extremes
        pdf.subsection_title('Asset Value Extremes')
        
        if stats['most_expensive']:
            pdf.content_text("Most Expensive Asset:")
            pdf.content_text(f"Description: {stats['most_expensive'].get('description', 'N/A')}", 10)
            pdf.content_text(f"Value: Rs.{float(stats['most_expensive'].get('cost', 0)):,.0f}", 10)
            pdf.content_text(f"Department: {stats['most_expensive'].get('department', 'N/A')}", 10)
            pdf.content_text(f"Location: {stats['most_expensive'].get('location', 'N/A')}", 10)
            pdf.ln(4)

        if stats['least_expensive']:
            pdf.content_text("Least Expensive Asset:")
            pdf.content_text(f"Description: {stats['least_expensive'].get('description', 'N/A')}", 10)
            pdf.content_text(f"Value: Rs.{float(stats['least_expensive'].get('cost', 0)):,.0f}", 10)
            pdf.content_text(f"Department: {stats['least_expensive'].get('department', 'N/A')}", 10)

    def _add_asset_inventory(self, pdf, resources):
        """Complete asset inventory"""
        pdf.add_page()
        pdf.section_title('Complete Asset Inventory')

        sorted_resources = sorted(resources, key=lambda x: float(x.get('cost', 0)), reverse=True)

        pdf.subsection_title('All Assets (Sorted by Value)')
        
        headers = ['Description', 'Department', 'Location', 'Cost']
        data = []
        
        for resource in sorted_resources:
            description = resource.get('description', 'N/A')
            department = resource.get('department', 'N/A')
            location = resource.get('location', 'N/A')
            cost = f"Rs.{float(resource.get('cost', 0)):,.0f}"
            
            data.append([description, department, location, cost])

        pdf.create_responsive_table(headers, data, [0.45, 0.2, 0.25, 0.1])

    def _add_recommendations(self, pdf, stats):
        """Strategic recommendations section"""
        pdf.add_page()
        pdf.section_title('Strategic Recommendations')

        recommendations = []

        # High-value asset management
        if stats['cost_ranges']['100k+'] > stats['total_resources'] * 0.1:
            recommendations.append({
                'title': 'High-Value Asset Management',
                'content': f"With {stats['cost_ranges']['100k+']} high-value assets (>Rs.100k), implement enhanced security protocols, regular maintenance schedules, and insurance coverage reviews."
            })

        # Department resource distribution
        dept_values = [data['cost'] for data in stats['departments'].values()]
        if dept_values and max(dept_values) > sum(dept_values) * 0.5:
            top_dept = max(stats['departments'].items(), key=lambda x: x[1]['cost'])
            recommendations.append({
                'title': 'Department Resource Distribution',
                'content': f"{top_dept[0]} department holds {top_dept[1]['cost']/stats['total_cost']*100:.1f}% of total assets. Consider redistribution strategies for optimal resource utilization."
            })

        # Cost optimization
        if stats['avg_cost'] > 50000:
            recommendations.append({
                'title': 'Cost Optimization',
                'content': f"Average asset cost of Rs.{stats['avg_cost']:,.0f} is substantial. Review procurement policies and consider bulk purchasing agreements for better cost efficiency."
            })

        # Asset tracking enhancement
        recommendations.append({
            'title': 'Asset Tracking Enhancement',
            'content': "Implement QR code or RFID-based tracking systems for real-time asset monitoring and automated inventory management."
        })

        # Preventive maintenance
        recommendations.append({
            'title': 'Preventive Maintenance',
            'content': "Establish department-wise maintenance schedules based on asset value and usage patterns to extend asset lifespan and reduce replacement costs."
        })

        # Add recommendations to PDF
        for i, rec in enumerate(recommendations, 1):
            pdf.subsection_title(f"{i}. {rec['title']}")
            pdf.content_text(rec['content'])
            pdf.ln(4)

        # Conclusion
        pdf.ln(8)
        pdf.subsection_title('Conclusion')
        pdf.content_text(f"The campus assets management system currently oversees {stats['total_resources']:,} assets valued at Rs.{stats['total_cost']:,.0f} across {len(stats['departments'])} departments. This comprehensive analysis provides insights for strategic decision-making and operational optimization.")

    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
