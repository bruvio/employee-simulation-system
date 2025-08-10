#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
🏢 Employee Simulation Explorer
===============================

A comprehensive tool for generating and analyzing employee populations with 
story tracking. Designed to find specific employee cases like:
- Level 5, £80,692.50, Exceeding performance

Run this script to:
1. Generate realistic employee population
2. Track interesting employee stories
3. Display human-readable analysis with narratives
4. Show population distribution graphs
"""

import sys
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Optional seaborn import
try:
    import seaborn as sns
    sns.set_palette("husl")
except ImportError:
    sns = None

# Try to import the orchestrator
try:
    from employee_simulation_orchestrator import EmployeeSimulationOrchestrator
except ImportError:
    print("❌ Could not import EmployeeSimulationOrchestrator")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

class EmployeeStoryExplorer:
    """Interactive employee story explorer with human-readable output"""
    
    def __init__(self):
        self.population_data = []
        self.tracked_stories = {}
        self.results = {}
        
    def run_simulation(self, population_size=1000, random_seed=42, target_salary=80692.50, target_level=5, level_distribution=None, gender_pay_gap_percent=None, salary_constraints=None):
        """Run employee simulation and return human-readable analysis"""
        
        print("🏢 EMPLOYEE SIMULATION & STORY EXPLORER")
        print("=" * 60)
        print(f"🎯 Looking for employees similar to:")
        print(f"   Level: {target_level}")
        print(f"   Salary: £{target_salary:,.2f}")
        print(f"   Performance: High/Exceeding")
        print()
        
        # Configure simulation for clean output
        config = {
            'population_size': population_size,
            'random_seed': random_seed,
            'max_cycles': 3,
            'level_distribution': level_distribution,
            'gender_pay_gap_percent': gender_pay_gap_percent,
            'salary_constraints': salary_constraints,
            
            # Story tracking enabled
            'enable_story_tracking': True,
            'tracked_employee_count': 20,
            'export_story_data': False,  # No file exports
            
            # Disable all file generation for clean output
            'generate_interactive_dashboard': False,
            'create_individual_story_charts': False,
            'export_formats': [],  # No exports
            'story_export_formats': [],
            'generate_visualizations': False,
            'export_individual_files': False,
            'export_comprehensive_report': False,
            'generate_summary_report': False,
            
            # Minimal logging
            'log_level': 'WARNING',  # Reduce noise
            'enable_progress_bar': False,
        }
        
        try:
            print("🔄 Generating employee population and running simulation...")
            orchestrator = EmployeeSimulationOrchestrator(config=config)
            
            # Get results - handle the orchestrator's return format
            raw_results = orchestrator.run_with_story_tracking()
            
            # Extract data safely regardless of return type
            if isinstance(raw_results, tuple):
                # If it returns a tuple, take the first element
                self.results = raw_results[0] if raw_results else {}
            else:
                self.results = raw_results or {}
            
            # Get population data from file if not in results
            self.population_data = self.results.get('population_data', [])
            
            if not self.population_data:
                # Try to load from generated files
                files = self.results.get('files_generated', {})
                pop_file = files.get('population')
                if pop_file and Path(pop_file).exists():
                    import json
                    with open(pop_file, 'r') as f:
                        self.population_data = json.load(f)
            
            # Get tracked stories
            self.tracked_stories = self.results.get('employee_stories', {})
            
            print("✅ Simulation completed successfully!")
            print()
            
            # Generate analysis
            self._analyze_population(target_salary, target_level)
            self._analyze_tracked_stories()
            self._create_visualizations()
            
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _analyze_population(self, target_salary, target_level):
        """Analyze the generated population with human narrative"""
        
        if not self.population_data:
            print("❌ No population data available for analysis")
            return
        
        df = pd.DataFrame(self.population_data)
        
        print("📊 POPULATION ANALYSIS")
        print("-" * 40)
        print(f"Generated {len(df)} employees across {df['level'].nunique()} levels")
        print()
        
        # Level distribution
        print("👥 Level Distribution:")
        level_dist = df['level'].value_counts().sort_index()
        for level, count in level_dist.items():
            pct = (count / len(df)) * 100
            print(f"   Level {level}: {count:,} employees ({pct:.1f}%)")
        print()
        
        # Target level analysis
        target_employees = df[df['level'] == target_level]
        print(f"🎯 Level {target_level} Employee Analysis:")
        print(f"   Total Level {target_level} employees: {len(target_employees)}")
        
        if len(target_employees) > 0:
            # Salary analysis
            salaries = target_employees['salary']
            print(f"   Salary range: £{salaries.min():,.0f} - £{salaries.max():,.0f}")
            print(f"   Average salary: £{salaries.mean():,.0f}")
            print(f"   Median salary: £{salaries.median():,.0f}")
            
            # Target salary comparison
            diff_from_avg = target_salary - salaries.mean()
            pct_diff = (diff_from_avg / salaries.mean()) * 100
            print(f"   Target £{target_salary:,.0f} vs average: {pct_diff:+.1f}% ({diff_from_avg:+,.0f})")
            print()
            
            # Performance distribution
            print(f"   Performance Distribution:")
            perf_dist = target_employees['performance_rating'].value_counts()
            for perf, count in perf_dist.items():
                pct = (count / len(target_employees)) * 100
                print(f"     {perf}: {count} ({pct:.1f}%)")
            print()
            
            # Find closest matches
            target_employees_copy = target_employees.copy()
            target_employees_copy['salary_diff'] = abs(target_employees_copy['salary'] - target_salary)
            closest_matches = target_employees_copy.nsmallest(5, 'salary_diff')
            
            print(f"💎 Closest Matches to Level {target_level}, £{target_salary:,.0f}:")
            for i, (_, emp) in enumerate(closest_matches.iterrows(), 1):
                diff = emp['salary_diff']
                print(f"   {i}. Employee {emp['employee_id']}:")
                print(f"      Salary: £{emp['salary']:,.0f} (±£{diff:.0f})")
                print(f"      Performance: {emp['performance_rating']}")
                print(f"      Gender: {emp['gender']}")
                
                # Check if tracked
                is_tracked = self._is_employee_tracked(emp['employee_id'])
                if is_tracked:
                    print(f"      📚 TRACKED: {is_tracked}")
                print()
        
        # Gender analysis
        print("⚖️ Gender Pay Analysis:")
        gender_stats = df.groupby('gender')['salary'].agg(['mean', 'median', 'count'])
        for gender, stats in gender_stats.iterrows():
            print(f"   {gender}: {stats['count']} employees, avg £{stats['mean']:,.0f}, median £{stats['median']:,.0f}")
        
        if len(gender_stats) >= 2:
            gap = abs(gender_stats['median'].iloc[0] - gender_stats['median'].iloc[1])
            higher_gender = gender_stats['median'].idxmax()
            gap_pct = (gap / gender_stats['median'].max()) * 100
            print(f"   Gender pay gap: £{gap:.0f} ({gap_pct:.1f}%) favoring {higher_gender}")
        print()
    
    def _is_employee_tracked(self, employee_id):
        """Check if an employee is being tracked and return category"""
        for category, stories in self.tracked_stories.items():
            for story in stories:
                story_emp_id = getattr(story, 'employee_id', None) or story.get('employee_id')
                if story_emp_id == employee_id:
                    return category.replace('_', ' ').title()
        return None
    
    def _analyze_tracked_stories(self):
        """Analyze tracked employee stories with narrative"""
        
        if not self.tracked_stories:
            print("📚 No employee stories tracked")
            return
        
        total_tracked = sum(len(stories) for stories in self.tracked_stories.values())
        print("📚 TRACKED EMPLOYEE STORIES")
        print("-" * 40)
        print(f"Identified {total_tracked} employees across {len(self.tracked_stories)} categories:")
        print()
        
        for category, stories in self.tracked_stories.items():
            if not stories:
                continue
                
            category_name = category.replace('_', ' ').title()
            print(f"🏷️ {category_name} ({len(stories)} employees):")
            
            # Category description
            descriptions = {
                'high_performer': 'Top performers with exceptional ratings or salaries',
                'above_range': 'Employees with salaries significantly above their level average',
                'gender_gap_affected': 'Employees in groups with notable gender pay disparities'
            }
            
            desc = descriptions.get(category, 'Employees meeting specific tracking criteria')
            print(f"   📝 {desc}")
            
            # Show a few examples
            for i, story in enumerate(stories[:3], 1):
                if hasattr(story, '__dict__'):
                    story_data = story.__dict__
                else:
                    story_data = story
                
                emp_id = story_data.get('employee_id', 'Unknown')
                current_salary = story_data.get('current_salary', 0)
                
                # Find employee in population for more details
                if self.population_data:
                    emp_detail = next((emp for emp in self.population_data if emp['employee_id'] == emp_id), {})
                    level = emp_detail.get('level', 'Unknown')
                    performance = emp_detail.get('performance_rating', 'Unknown')
                    gender = emp_detail.get('gender', 'Unknown')
                    
                    print(f"   {i}. Employee {emp_id}: Level {level}, £{current_salary:,.0f}, {performance}, {gender}")
            
            if len(stories) > 3:
                print(f"   ... and {len(stories) - 3} more employees")
            print()
    
    def _create_visualizations(self):
        """Create population distribution visualizations"""
        
        if not self.population_data:
            print("📊 No data available for visualizations")
            return
        
        print("📊 POPULATION VISUALIZATIONS")
        print("-" * 40)
        
        df = pd.DataFrame(self.population_data)
        
        # Set up the plotting style
        plt.style.use('default')
        if sns:
            sns.set_palette("husl")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Employee Population Analysis', fontsize=16, fontweight='bold')
        
        # 1. Salary distribution by level
        if sns:
            sns.boxplot(data=df, x='level', y='salary', ax=axes[0,0])
        else:
            # Fallback to matplotlib boxplot
            level_groups = [group['salary'].values for name, group in df.groupby('level')]
            bp = axes[0,0].boxplot(level_groups)
            axes[0,0].set_xticks(range(1, len(sorted(df['level'].unique())) + 1))
            axes[0,0].set_xticklabels(sorted(df['level'].unique()))
        axes[0,0].set_title('Salary Distribution by Level')
        axes[0,0].set_ylabel('Salary (£)')
        axes[0,0].set_xlabel('Level')
        axes[0,0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}K'))
        
        # 2. Performance rating distribution
        perf_counts = df['performance_rating'].value_counts()
        axes[0,1].pie(perf_counts.values, labels=perf_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0,1].set_title('Performance Rating Distribution')
        
        # 3. Salary vs Performance
        perf_order = ['Not met', 'Partially met', 'Achieving', 'High Performing', 'Exceeding']
        perf_numeric = df['performance_rating'].map({perf: i for i, perf in enumerate(perf_order)})
        
        scatter = axes[1,0].scatter(perf_numeric, df['salary'], 
                                  c=df['level'], cmap='viridis', alpha=0.6)
        axes[1,0].set_title('Salary vs Performance Rating')
        axes[1,0].set_xlabel('Performance Rating')
        axes[1,0].set_ylabel('Salary (£)')
        axes[1,0].set_xticks(range(len(perf_order)))
        axes[1,0].set_xticklabels(perf_order, rotation=45)
        axes[1,0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x/1000:.0f}K'))
        
        cbar = plt.colorbar(scatter, ax=axes[1,0])
        cbar.set_label('Level')
        
        # 4. Gender distribution by level
        gender_level = pd.crosstab(df['level'], df['gender'])
        gender_level.plot(kind='bar', ax=axes[1,1], stacked=True)
        axes[1,1].set_title('Gender Distribution by Level')
        axes[1,1].set_xlabel('Level')
        axes[1,1].set_ylabel('Number of Employees')
        axes[1,1].legend(title='Gender')
        axes[1,1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = Path('employee_population_analysis.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📈 Population analysis chart saved as: {plot_path}")
        print()
        
        # Print key insights
        print("🔍 KEY INSIGHTS:")
        
        # Salary insight
        salary_by_level = df.groupby('level')['salary'].mean()
        highest_paid_level = salary_by_level.idxmax()
        print(f"• Highest average salary: Level {highest_paid_level} (£{salary_by_level.max():,.0f})")
        
        # Performance insight
        exceeding_count = len(df[df['performance_rating'] == 'Exceeding'])
        exceeding_pct = (exceeding_count / len(df)) * 100
        print(f"• Exceeding performers: {exceeding_count} employees ({exceeding_pct:.1f}%)")
        
        # Gender insight
        gender_counts = df['gender'].value_counts()
        male_pct = (gender_counts.get('Male', 0) / len(df)) * 100
        print(f"• Gender split: {male_pct:.1f}% Male, {100-male_pct:.1f}% Female")
        
        # Tracked insight
        if self.tracked_stories:
            total_tracked = sum(len(stories) for stories in self.tracked_stories.values())
            tracked_pct = (total_tracked / len(df)) * 100
            print(f"• Story tracking: {total_tracked} employees ({tracked_pct:.1f}%) identified as interesting cases")


def main():
    """Main execution function"""
    
    explorer = EmployeeStoryExplorer()
    
    # Run with different scenarios
    scenarios = [
        {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5},
        # Example with level skewing - more Level 3 employees
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5, 
        #  'level_distribution': [0.20, 0.20, 0.35, 0.10, 0.10, 0.05]},  # 35% Level 3 vs 20% default
        
        # Example with 2024 UK gender pay gap simulation
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5,
        #  'gender_pay_gap_percent': 15.8},  # 2024 UK average
        
        # Combined example: level skewing + gender pay gap
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5,
        #  'level_distribution': [0.20, 0.20, 0.35, 0.10, 0.10, 0.05],
        #  'gender_pay_gap_percent': 15.8},
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: Population {scenario['population_size']:,}, Seed {scenario['random_seed']}")
        print(f"{'='*60}")
        
        success = explorer.run_simulation(**scenario)
        
        if not success:
            print(f"❌ Scenario {i} failed")
            continue
        
        # Create markdown report
        create_markdown_report(explorer, scenario)
        
        # Option to continue or exit
        if i < len(scenarios):
            response = input("\n🤔 Try another scenario? (y/n): ").strip().lower()
            if response != 'y':
                break
    
    print("\n🎉 Employee Story Exploration Complete!")
    print("📝 Check 'employee_analysis_report.md' for detailed narrative analysis")
    print("📊 Check 'employee_population_analysis.png' for population visualizations")


def create_markdown_report(explorer, scenario):
    """Create a markdown report with narrative analysis"""
    
    report_path = Path('employee_analysis_report.md')
    
    with open(report_path, 'w') as f:
        f.write("# Employee Population Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"This analysis examines a simulated employee population of {scenario['population_size']:,} employees "
                f"generated with random seed {scenario['random_seed']}. The simulation focuses on identifying "
                f"employees with profiles similar to: **Level {scenario['target_level']}, £{scenario['target_salary']:,.0f} salary, "
                f"with high performance ratings**.\n\n")
        
        if explorer.population_data:
            df = pd.DataFrame(explorer.population_data)
            
            f.write("## Key Findings\n\n")
            
            # Population overview
            f.write(f"### Population Overview\n")
            f.write(f"- **Total Employees**: {len(df):,}\n")
            f.write(f"- **Organizational Levels**: {df['level'].nunique()}\n")
            f.write(f"- **Salary Range**: £{df['salary'].min():,.0f} - £{df['salary'].max():,.0f}\n")
            f.write(f"- **Average Salary**: £{df['salary'].mean():,.0f}\n\n")
            
            # Target level analysis
            target_employees = df[df['level'] == scenario['target_level']]
            if len(target_employees) > 0:
                f.write(f"### Level {scenario['target_level']} Analysis\n")
                f.write(f"- **Population**: {len(target_employees)} employees ({len(target_employees)/len(df)*100:.1f}% of total)\n")
                f.write(f"- **Salary Range**: £{target_employees['salary'].min():,.0f} - £{target_employees['salary'].max():,.0f}\n")
                f.write(f"- **Average Salary**: £{target_employees['salary'].mean():,.0f}\n")
                
                # Performance breakdown
                perf_dist = target_employees['performance_rating'].value_counts()
                f.write(f"- **Performance Distribution**:\n")
                for perf, count in perf_dist.items():
                    pct = (count / len(target_employees)) * 100
                    f.write(f"  - {perf}: {count} employees ({pct:.1f}%)\n")
                f.write("\n")
        
        # Story tracking results
        if explorer.tracked_stories:
            f.write("## Story Tracking Results\n\n")
            f.write("The system identified several employees with interesting career patterns:\n\n")
            
            for category, stories in explorer.tracked_stories.items():
                if stories:
                    category_name = category.replace('_', ' ').title()
                    f.write(f"### {category_name}\n")
                    f.write(f"Identified **{len(stories)} employees** in this category.\n\n")
        
        f.write("## Methodology\n\n")
        f.write("This analysis uses a sophisticated employee simulation system that:\n")
        f.write("1. Generates realistic employee populations with appropriate salary distributions\n")
        f.write("2. Applies performance review cycles with career progression\n")
        f.write("3. Identifies employees with interesting patterns (high performers, outliers, etc.)\n")
        f.write("4. Tracks individual employee stories across multiple review cycles\n\n")
        
        f.write("## Visualizations\n\n")
        f.write("See `employee_population_analysis.png` for comprehensive visual analysis including:\n")
        f.write("- Salary distribution by organizational level\n")
        f.write("- Performance rating distribution\n")
        f.write("- Correlation between salary and performance\n")
        f.write("- Gender distribution across levels\n\n")
        
        f.write("---\n")
        f.write("*Report generated by Employee Story Explorer*\n")
    
    print(f"📝 Detailed analysis report saved as: {report_path}")


if __name__ == "__main__":
    main()