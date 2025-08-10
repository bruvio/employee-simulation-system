#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import argparse
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

# Import our simulation modules
from employee_population_simulator import EmployeePopulationGenerator
from performance_review_system import PerformanceReviewSystem
from review_cycle_simulator import ReviewCycleSimulator
from visualization_generator import VisualizationGenerator
from data_export_system import DataExportSystem
from employee_story_tracker import EmployeeStoryTracker
from smart_logging_manager import SmartLoggingManager, get_smart_logger
from file_optimization_manager import FileOptimizationManager
from interactive_dashboard_generator import InteractiveDashboardGenerator
from advanced_story_export_system import AdvancedStoryExportSystem
from performance_optimization_manager import PerformanceOptimizationManager

class EmployeeSimulationOrchestrator:
    """
    Main orchestrator for the complete employee population simulation system.
    Coordinates all phases of the simulation pipeline.
    """
    
    def __init__(self, config=None):
        self.config = config or self._get_default_config()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.artifacts_dir = Path("artifacts")
        self.images_dir = Path("images")
        
        # Initialize smart logging manager
        log_level = self.config.get('log_level', 'INFO')
        enable_progress = self.config.get('enable_progress_bar', True)
        self.smart_logger = SmartLoggingManager(
            log_level=log_level,
            enable_progress_indicators=enable_progress,
            log_file_path=f"artifacts/simulation_log_{self.timestamp}.log" if self.config.get('enable_file_logging', False) else None,
            suppress_noisy_libraries=True
        )
        self.logger = self.smart_logger.get_logger("EmployeeSimulationOrchestrator")
        
        # Initialize performance optimization manager
        self.performance_manager = PerformanceOptimizationManager(smart_logger=self.smart_logger)
        
        # Apply performance optimizations based on population size
        population_size = self.config.get('population_size', 1000)
        enable_story_tracking = self.config.get('enable_story_tracking', False)
        self.performance_optimizations = self.performance_manager.apply_performance_optimizations(
            population_size=population_size,
            enable_story_tracking=enable_story_tracking
        )
        
        # Initialize file optimization manager
        self.file_manager = FileOptimizationManager(
            base_output_dir=str(self.artifacts_dir),
            base_images_dir=str(self.images_dir)
        )
        
        # Initialize story tracker if enabled
        self.story_tracker = None
        if self.config.get('enable_story_tracking', False):
            self.story_tracker = EmployeeStoryTracker()
            self.smart_logger.log_info("Story tracking enabled")
        
        # Create structured run directory
        self.run_directories = self.file_manager.create_run_directory(
            run_id=self.timestamp,
            enable_story_tracking=self.config.get('enable_story_tracking', False)
        )
        
        # Set convenience references for backward compatibility
        self.run_output_dir = self.run_directories['run_root']
        self.run_images_dir = self.run_directories['images_root']
        
        self.smart_logger.log_success(f"Initialized employee simulation orchestrator with timestamp: {self.timestamp}")
    
    def _get_default_config(self):
        """Get default simulation configuration"""
        return {
            'population_size': 1000,
            'random_seed': 42,
            'max_cycles': 15,
            'convergence_threshold': 0.001,
            'export_formats': ['csv', 'excel', 'json'],
            'generate_visualizations': True,
            'export_individual_files': True,
            'export_comprehensive_report': True,
            
            # Story tracking options
            'enable_story_tracking': False,
            'tracked_employee_count': 20,  # Max employees per category
            'story_categories': ['gender_gap', 'above_range', 'high_performer'],
            'story_export_formats': ['json', 'csv', 'excel', 'markdown'],  # Available: json, csv, excel, xml, markdown
            
            # Logging options
            'log_level': 'INFO',  # ERROR, WARNING, INFO, DEBUG
            'enable_progress_bar': True,
            'enable_file_logging': False,
            'generate_summary_report': True,
            
            # Visualization options
            'generate_interactive_dashboard': False,
            'create_individual_story_charts': False,
            'export_story_data': True
        }
    
    def run_complete_simulation(self):
        """
        Run the complete end-to-end employee simulation pipeline
        
        Returns:
            dict: Results and file paths from the simulation
        """
        self.smart_logger.log_info("Starting complete employee simulation pipeline")
        
        results = {
            'simulation_config': self.config,
            'timestamp': self.timestamp,
            'files_generated': {},
            'validation_results': {},
            'summary_metrics': {}
        }
        
        try:
            # Phase 1: Generate Employee Population
            self.smart_logger.start_phase("Phase 1: Generate Employee Population", 4)
            population_generator = EmployeePopulationGenerator(
                population_size=self.config['population_size'],
                random_seed=self.config['random_seed'],
                level_distribution=self.config.get('level_distribution'),
                gender_pay_gap_percent=self.config.get('gender_pay_gap_percent'),
                salary_constraints=self.config.get('salary_constraints')
            )
            
            population_data = population_generator.generate_population()
            population_filename = f"employee_population_{self.timestamp}.json"
            population_filepath = self.artifacts_dir / population_filename
            
            # Save population data
            with open(population_filepath, 'w') as f:
                json.dump(population_data, f, indent=2, default=str)
            
            results['files_generated']['population'] = str(population_filepath)
            results['summary_metrics']['population_size'] = len(population_data)
            
            # Validate population constraints
            validation_results = self._validate_population(population_data)
            results['validation_results']['population'] = validation_results
            results['population_data'] = population_data  # Add population data to results
            
            self.smart_logger.log_info(f"Phase 1 completed: {len(population_data)} employees generated")
            
            # Phase 2: Initialize Performance Review System
            self.smart_logger.log_info("Phase 2: Initializing performance review system")
            review_system = PerformanceReviewSystem(random_seed=self.config['random_seed'])
            
            # Validate review system
            review_validation = review_system.validate_uplift_calculations()
            results['validation_results']['review_system'] = review_validation
            
            self.smart_logger.log_info("Phase 2 completed: Performance review system validated")
            
            # Phase 3: Run Multi-Cycle Simulation
            self.smart_logger.log_info("Phase 3: Running multi-cycle simulation")
            cycle_simulator = ReviewCycleSimulator(
                initial_population=population_data,
                random_seed=self.config['random_seed']
            )
            
            inequality_progression = cycle_simulator.simulate_multiple_cycles(
                num_cycles=self.config['max_cycles']
            )
            
            # Convert to expected format
            simulation_results = {
                'inequality_metrics': pd.DataFrame(inequality_progression),
                'converged': len(inequality_progression) < self.config['max_cycles'] + 1
            }
            simulation_filename = f"simulation_results_{self.timestamp}.json"
            simulation_filepath = self.artifacts_dir / simulation_filename
            
            # Save simulation results (with DataFrame conversion)
            serializable_results = self._make_serializable(simulation_results)
            with open(simulation_filepath, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            results['files_generated']['simulation'] = str(simulation_filepath)
            if isinstance(simulation_results, dict):
                inequality_df = simulation_results.get('inequality_metrics', pd.DataFrame())
                convergence_achieved = simulation_results.get('converged', False)
            else:
                # simulation_results is the DataFrame directly
                inequality_df = simulation_results
                convergence_achieved = False
            
            results['summary_metrics'].update({
                'cycles_completed': len(inequality_df) - 1 if not inequality_df.empty else 0,
                'final_gini_coefficient': float(inequality_df.iloc[-1]['gini_coefficient']) if not inequality_df.empty else 'N/A',
                'convergence_achieved': convergence_achieved
            })
            
            self.smart_logger.log_info(f"Phase 3 completed: {results['summary_metrics']['cycles_completed']} cycles simulated")
            
            # Phase 4: Generate Visualizations
            if self.config['generate_visualizations']:
                self.smart_logger.log_info("Phase 4: Generating visualizations")
                
                # Generate all visualization types  
                viz_generator = VisualizationGenerator(
                    population_data=population_data,
                    inequality_progression=simulation_results.get('inequality_metrics', pd.DataFrame()).to_dict('records') if isinstance(simulation_results, dict) else simulation_results.to_dict('records')
                )
                viz_files = viz_generator.generate_complete_analysis()
                
                results['files_generated']['visualizations'] = viz_files
                self.smart_logger.log_info(f"Phase 4 completed: {len(viz_files)} visualization files generated")
            
            # Phase 5: Export Data
            self.smart_logger.log_info("Phase 5: Exporting data")
            exporter = DataExportSystem(output_dir=str(self.artifacts_dir))
            
            export_files = {}
            
            # Export individual datasets if requested
            if self.config['export_individual_files']:
                # Population data
                pop_exports = exporter.export_employee_population(
                    population_data, format_types=self.config['export_formats']
                )
                export_files['population'] = {str(k): str(v) for k, v in pop_exports.items()}
                
                # Simulation results
                sim_exports = exporter.export_simulation_results(
                    simulation_results, format_types=self.config['export_formats']
                )
                export_files['simulation'] = {str(k): str(v) for k, v in sim_exports.items()}
            
            # Comprehensive analysis report
            if self.config['export_comprehensive_report']:
                analysis_exports = exporter.export_analysis_report(
                    population_data, simulation_results, format_types=self.config['export_formats']
                )
                export_files['comprehensive_analysis'] = {str(k): str(v) for k, v in analysis_exports.items()}
            
            results['files_generated']['exports'] = export_files
            self.smart_logger.log_info("Phase 5 completed: Data export finished")
            
            # Generate final summary  
            try:
                final_summary = self._generate_final_summary(results)
                results['final_summary'] = final_summary
            except Exception as e:
                self.smart_logger.log_error("Error generating final summary", e)
                results['final_summary'] = {'error': str(e)}
            
            # Generate comprehensive execution summary with file organization
            self._generate_comprehensive_summary(results)
            
            # Print execution summary
            self.smart_logger.print_execution_summary()
            
            # Export execution summary if enabled
            if self.config.get('generate_summary_report', True):
                summary_path = str(self.run_directories['reports'] / "execution_summary.json")
                self.smart_logger.export_summary(summary_path)
                results['files_generated']['execution_summary'] = summary_path
                
                # Generate comprehensive run index
                index_path = self.file_manager.generate_run_index()
                results['files_generated']['run_index'] = index_path
                
                # Generate performance analysis report
                performance_summary = self.performance_manager.get_performance_summary()
                performance_path = str(self.run_directories['reports'] / "performance_analysis.json")
                with open(performance_path, 'w') as f:
                    json.dump(performance_summary, f, indent=2, default=str)
                results['files_generated']['performance_analysis'] = performance_path
                
                # Log performance insights
                peak_memory = performance_summary['performance_metrics']['peak_memory_usage_mb']
                total_time = performance_summary['performance_metrics']['total_execution_time_seconds']
                optimizations = len(performance_summary['optimizations']['optimization_list'])
                
                self.smart_logger.log_info(f"Performance Summary: {total_time:.1f}s execution, {peak_memory:.1f}MB peak memory, {optimizations} optimizations applied")
            
            self.smart_logger.log_success("Complete simulation pipeline finished successfully")
            return results
            
        except Exception as e:
            self.smart_logger.log_error(f"Simulation pipeline failed: {e}")
            results['error'] = str(e)
            raise
    
    def run_quick_validation(self):
        """
        Run a quick validation of all system components without full simulation
        
        Returns:
            dict: Validation results
        """
        self.smart_logger.log_info("Running quick validation of all system components")
        
        validation_results = {}
        
        try:
            # Test population generation
            pop_gen = EmployeePopulationGenerator(population_size=100, random_seed=42)
            small_population = pop_gen.generate_population()
            pop_validation = self._validate_population(small_population)
            validation_results['population_generator'] = {
                'status': 'PASS' if pop_validation['median_constraint_met'] else 'FAIL',
                'details': pop_validation
            }
            
            # Test performance review system
            review_system = PerformanceReviewSystem(random_seed=42)
            review_validation = review_system.validate_uplift_calculations()
            validation_results['review_system'] = {
                'status': 'PASS' if review_validation['all_tests_passed'] else 'FAIL',
                'details': review_validation
            }
            
            # Test cycle simulator with minimal data
            try:
                cycle_simulator = ReviewCycleSimulator(
                    initial_population=small_population,
                    random_seed=42
                )
                mini_simulation = cycle_simulator.simulate_multiple_cycles(num_cycles=2)
                validation_results['cycle_simulator'] = {
                    'status': 'PASS' if len(mini_simulation) > 1 else 'FAIL',
                    'details': f"Completed {len(mini_simulation) - 1} cycles"
                }
            except Exception as e:
                validation_results['cycle_simulator'] = {
                    'status': 'FAIL',
                    'details': f"Error: {str(e)}"
                }
            
            # Test visualization generator
            viz_generator = VisualizationGenerator()
            validation_results['visualization_generator'] = {
                'status': 'PASS',
                'details': 'Visualization generator initialized successfully'
            }
            
            # Test data export system
            exporter = DataExportSystem()
            validation_results['data_export_system'] = {
                'status': 'PASS',
                'details': 'Data export system initialized successfully'
            }
            
            overall_status = 'PASS' if all(
                result['status'] == 'PASS' for result in validation_results.values()
            ) else 'FAIL'
            
            validation_results['overall'] = {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'components_tested': len(validation_results) - 1
            }
            
            self.smart_logger.log_info(f"Quick validation completed: {overall_status}")
            return validation_results
            
        except Exception as e:
            self.smart_logger.log_error(f"Quick validation failed: {e}")
            validation_results['overall'] = {
                'status': 'FAIL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return validation_results
    
    def _validate_population(self, population_data):
        """Validate population meets all constraints"""
        df = pd.DataFrame(population_data)
        
        # Check senior engineer median constraint
        senior_salaries = df[df['level'].isin([4, 5, 6])]['salary']
        median_salary = senior_salaries.median()
        target_median = 90108.0
        median_tolerance = 50.0
        
        validation = {
            'total_employees': len(population_data),
            'senior_engineers': len(senior_salaries),
            'senior_median_salary': median_salary,
            'target_median': target_median,
            'median_difference': abs(median_salary - target_median),
            'median_constraint_met': abs(median_salary - target_median) <= median_tolerance,
            'gender_distribution': df['gender'].value_counts().to_dict(),
            'level_distribution': df['level'].value_counts().sort_index().to_dict()
        }
        
        return validation
    
    def _make_serializable(self, obj):
        """Convert DataFrames and other non-serializable objects for JSON export"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj
    
    def _generate_final_summary(self, results):
        """Generate final summary of simulation results"""
        summary = {
            'simulation_timestamp': self.timestamp,
            'configuration': self.config,
            'population_size': results['summary_metrics'].get('population_size', 'N/A'),
            'cycles_completed': results['summary_metrics'].get('cycles_completed', 'N/A'),
            'final_gini_coefficient': results['summary_metrics'].get('final_gini_coefficient', 'N/A'),
            'convergence_achieved': results['summary_metrics'].get('convergence_achieved', 'N/A'),
            'validation_status': {
                'population': results['validation_results'].get('population', {}).get('median_constraint_met', False),
                'review_system': results['validation_results'].get('review_system', {}).get('all_tests_passed', False)
            },
            'total_files_generated': sum(
                len(files) if isinstance(files, (list, dict)) else 1 
                for files in results['files_generated'].values()
            )
        }
        
        return summary
    
    def _generate_comprehensive_summary(self, results):
        """Generate comprehensive summary with file organization and progress tracking"""
        try:
            # Organize population files
            if 'population_size' in results.get('summary_metrics', {}):
                population_files = self.file_manager.organize_population_files(
                    population_data=[]  # Will be populated in actual runs
                )
                if 'file_organization' not in results:
                    results['file_organization'] = {}
                results['file_organization']['population_files'] = population_files
            
            # Get file manager summary
            file_summary = self.file_manager.get_run_summary()
            results['file_organization']['directory_summary'] = file_summary
            
            # Clean up temporary files
            cleaned_files = self.file_manager.cleanup_temporary_files()
            if cleaned_files > 0:
                self.smart_logger.log_info(f"Cleaned up {cleaned_files} temporary files")
                results['file_organization']['temp_files_cleaned'] = cleaned_files
            
            self.smart_logger.log_success("Comprehensive summary generated")
            
        except Exception as e:
            self.smart_logger.log_error("Failed to generate comprehensive summary", e)
    
    def run_with_story_tracking(self):
        """
        Run simulation with employee story tracking enabled
        
        Returns:
            dict: Results including employee stories and enhanced metrics
        """
        if not self.story_tracker:
            self.smart_logger.log_warning("Story tracking not enabled - falling back to standard simulation")
            return self.run_complete_simulation()
        
        self.smart_logger.log_info("Starting complete simulation with employee story tracking")
        
        results = {
            'simulation_config': self.config,
            'timestamp': self.timestamp,
            'files_generated': {},
            'validation_results': {},
            'summary_metrics': {},
            'employee_stories': {}
        }
        
        try:
            # Phase 1: Generate Employee Population
            self.smart_logger.log_info("Phase 1: Generating employee population")
            population_generator = EmployeePopulationGenerator(
                population_size=self.config['population_size'],
                random_seed=self.config['random_seed'],
                level_distribution=self.config.get('level_distribution'),
                gender_pay_gap_percent=self.config.get('gender_pay_gap_percent'),
                salary_constraints=self.config.get('salary_constraints')
            )
            
            population_data = population_generator.generate_population()
            
            # Add initial cycle data to story tracker
            self.story_tracker.add_cycle_data(0, population_data)
            
            # Save population data
            if hasattr(self, 'run_output_dir'):
                population_filepath = self.run_output_dir / "population_data" / "employee_population.json"
            else:
                population_filepath = self.artifacts_dir / f"employee_population_{self.timestamp}.json"
            
            with open(population_filepath, 'w') as f:
                json.dump(population_data, f, indent=2, default=str)
            
            results['files_generated']['population'] = str(population_filepath)
            results['summary_metrics']['population_size'] = len(population_data)
            
            # Validate population constraints
            validation_results = self._validate_population(population_data)
            results['validation_results']['population'] = validation_results
            results['population_data'] = population_data  # Add population data to results
            
            self.smart_logger.log_info(f"Phase 1 completed: {len(population_data)} employees generated")
            
            # Phase 2: Initialize Performance Review System
            self.smart_logger.log_info("Phase 2: Initializing performance review system")
            review_system = PerformanceReviewSystem(random_seed=self.config['random_seed'])
            
            review_validation = review_system.validate_uplift_calculations()
            results['validation_results']['review_system'] = review_validation
            
            self.smart_logger.log_info("Phase 2 completed: Performance review system validated")
            
            # Phase 3: Run Multi-Cycle Simulation with Story Tracking
            self.smart_logger.log_info("Phase 3: Running multi-cycle simulation with story tracking")
            cycle_simulator = ReviewCycleSimulator(
                initial_population=population_data,
                random_seed=self.config['random_seed']
            )
            
            inequality_progression = cycle_simulator.simulate_multiple_cycles(
                num_cycles=self.config['max_cycles']
            )
            
            # Capture cycle data for story tracking
            for cycle_num in range(1, len(inequality_progression)):
                cycle_population = cycle_simulator.population
                self.story_tracker.add_cycle_data(cycle_num, cycle_population)
            
            # Identify tracked employees with performance optimization
            self.performance_manager.monitor_memory_usage("before_story_identification")
            
            # Use optimized story identification for large populations
            if len(population_data) > 1000:
                tracked_employees = self.performance_manager.optimize_story_identification(
                    population_data=population_data,
                    max_per_category=self.config['tracked_employee_count']
                )
            else:
                tracked_employees = self.story_tracker.identify_tracked_employees(
                    max_per_category=self.config['tracked_employee_count']
                )
            
            self.performance_manager.monitor_memory_usage("after_story_identification")
            
            # Generate employee stories
            employee_stories = {}
            for category, employee_ids in tracked_employees.items():
                category_stories = []
                for emp_id in employee_ids:
                    story = self.story_tracker.generate_employee_story(emp_id, category)
                    if story:
                        category_stories.append(story)
                employee_stories[category] = category_stories
            
            results['employee_stories'] = employee_stories
            
            # Advanced story export if requested
            if self.config['export_story_data']:
                self.smart_logger.start_phase("Advanced Story Export", 4)
                
                # Initialize advanced export system
                export_system = AdvancedStoryExportSystem(
                    output_base_dir=str(self.run_directories['employee_stories']),
                    smart_logger=self.smart_logger
                )
                
                # Get cycle timeline data
                timeline_df = self.story_tracker.create_story_timeline()
                
                # Export comprehensive story data in multiple formats
                story_export_formats = self.config.get('story_export_formats', ['json', 'csv', 'excel', 'markdown'])
                story_exports = export_system.export_employee_stories_comprehensive(
                    employee_stories=employee_stories,
                    population_data=population_data,
                    cycle_data=timeline_df if not timeline_df.empty else None,
                    formats=story_export_formats
                )
                
                self.smart_logger.update_progress(f"Stories exported in {len(story_exports)} formats")
                results['files_generated']['story_exports'] = story_exports
                
                # Export comparative analysis
                comparative_analysis_file = export_system.export_comparative_analysis(
                    employee_stories=employee_stories,
                    population_data=population_data,
                    output_format='json'
                )
                results['files_generated']['comparative_analysis'] = comparative_analysis_file
                self.smart_logger.update_progress("Comparative analysis exported")
                
                # Save basic story data for backward compatibility
                story_data = self.story_tracker.export_stories_to_dict()
                for category in story_data['categories']:
                    story_filepath = self.run_directories['employee_stories'] / f"{category}_basic.json"
                    with open(story_filepath, 'w') as f:
                        json.dump(story_data['categories'][category], f, indent=2, default=str)
                
                self.smart_logger.update_progress("Basic story data saved")
                
                # Save comprehensive story timeline
                if not timeline_df.empty:
                    timeline_filepath = self.run_directories['population_data'] / "cycle_progressions.csv"
                    timeline_df.to_csv(timeline_filepath, index=False)
                    results['files_generated']['story_timeline'] = str(timeline_filepath)
                    self.smart_logger.update_progress("Story timeline exported")
                
                self.smart_logger.complete_phase("Advanced Story Export")
                self.smart_logger.log_success(f"Advanced story export completed: {len(story_exports) + 1} file types generated")
            
            # Convert simulation results to expected format
            simulation_results = {
                'inequality_metrics': pd.DataFrame(inequality_progression),
                'converged': len(inequality_progression) < self.config['max_cycles'] + 1
            }
            
            simulation_filename = f"simulation_results_{self.timestamp}.json"
            simulation_filepath = self.artifacts_dir / simulation_filename
            
            serializable_results = self._make_serializable(simulation_results)
            with open(simulation_filepath, 'w') as f:
                json.dump(serializable_results, f, indent=2, default=str)
            
            results['files_generated']['simulation'] = str(simulation_filepath)
            
            inequality_df = simulation_results.get('inequality_metrics', pd.DataFrame())
            convergence_achieved = simulation_results.get('converged', False)
            
            results['summary_metrics'].update({
                'cycles_completed': len(inequality_df) - 1 if not inequality_df.empty else 0,
                'final_gini_coefficient': float(inequality_df.iloc[-1]['gini_coefficient']) if not inequality_df.empty else 'N/A',
                'convergence_achieved': convergence_achieved,
                'total_tracked_employees': sum(len(stories) for stories in employee_stories.values())
            })
            
            self.smart_logger.log_info(f"Phase 3 completed: {results['summary_metrics']['cycles_completed']} cycles simulated with {results['summary_metrics']['total_tracked_employees']} employees tracked")
            
            # Phase 4: Generate Enhanced Visualizations & Interactive Dashboard
            if self.config['generate_visualizations'] or self.config['generate_interactive_dashboard']:
                self.smart_logger.start_phase("Phase 4: Generate Enhanced Visualizations", 3)
                
                viz_generator = VisualizationGenerator(
                    population_data=population_data,
                    inequality_progression=simulation_results.get('inequality_metrics', pd.DataFrame()).to_dict('records'),
                    story_tracker=self.story_tracker
                )
                viz_files = viz_generator.generate_complete_analysis()
                self.smart_logger.update_progress("Standard visualizations generated")
                
                # Generate interactive dashboard if requested
                if self.config['generate_interactive_dashboard']:
                    dashboard_generator = InteractiveDashboardGenerator(
                        story_tracker=self.story_tracker,
                        smart_logger=self.smart_logger
                    )
                    
                    # Get cycle progression data for timeline
                    cycle_timeline = None
                    if hasattr(self, 'story_tracker') and self.story_tracker:
                        cycle_timeline = self.story_tracker.create_story_timeline()
                    
                    # Generate comprehensive dashboard
                    dashboard_path = self.run_images_dir / "comprehensive_employee_dashboard.html"
                    dashboard_file = dashboard_generator.generate_comprehensive_dashboard(
                        population_data=population_data,
                        tracked_employees=employee_stories,
                        cycle_data=cycle_timeline,
                        output_path=str(dashboard_path)
                    )
                    
                    results['files_generated']['interactive_dashboard'] = dashboard_file
                    self.smart_logger.update_progress("Interactive dashboard generated")
                
                # Generate story-aware visualizations if requested
                if self.config['create_individual_story_charts']:
                    story_viz_files = self._generate_individual_story_charts(employee_stories)
                    if story_viz_files:
                        results['files_generated']['story_visualizations'] = story_viz_files
                        self.smart_logger.update_progress("Individual story charts generated")
                
                results['files_generated']['visualizations'] = viz_files
                total_viz_count = len(viz_files)
                if 'interactive_dashboard' in results['files_generated']:
                    total_viz_count += 1
                if 'story_visualizations' in results['files_generated']:
                    total_viz_count += len(results['files_generated']['story_visualizations'])
                
                self.smart_logger.complete_phase("Phase 4: Generate Enhanced Visualizations")
                self.smart_logger.log_success(f"Phase 4 completed: {total_viz_count} visualization components generated")
            
            # Phase 5: Export Data
            self.smart_logger.log_info("Phase 5: Exporting data")
            exporter = DataExportSystem(output_dir=str(self.artifacts_dir))
            
            export_files = {}
            
            if self.config['export_individual_files']:
                pop_exports = exporter.export_employee_population(
                    population_data, format_types=self.config['export_formats']
                )
                export_files['population'] = {str(k): str(v) for k, v in pop_exports.items()}
                
                sim_exports = exporter.export_simulation_results(
                    simulation_results, format_types=self.config['export_formats']
                )
                export_files['simulation'] = {str(k): str(v) for k, v in sim_exports.items()}
            
            if self.config['export_comprehensive_report']:
                analysis_exports = exporter.export_analysis_report(
                    population_data, simulation_results, format_types=self.config['export_formats']
                )
                export_files['comprehensive_analysis'] = {str(k): str(v) for k, v in analysis_exports.items()}
            
            results['files_generated']['exports'] = export_files
            
            # Generate summary report
            if self.config['generate_summary_report']:
                summary_report = self.generate_story_report(employee_stories)
                if hasattr(self, 'run_output_dir'):
                    summary_filepath = self.run_output_dir / "summary_report.md"
                else:
                    summary_filepath = self.artifacts_dir / f"summary_report_{self.timestamp}.md"
                
                with open(summary_filepath, 'w') as f:
                    f.write(summary_report)
                
                results['files_generated']['summary_report'] = str(summary_filepath)
            
            self.smart_logger.log_info("Phase 5 completed: Data export and reporting finished")
            
            # Generate final summary
            try:
                final_summary = self._generate_final_summary(results)
                results['final_summary'] = final_summary
            except Exception as e:
                self.smart_logger.log_error(f"Error generating final summary: {e}")
                results['final_summary'] = {'error': str(e)}
            
            self.smart_logger.log_info("Complete simulation with story tracking finished successfully")
            return results
            
        except Exception as e:
            self.smart_logger.log_error(f"Story tracking simulation failed: {e}")
            results['error'] = str(e)
            raise
    
    def generate_story_report(self, employee_stories):
        """Generate markdown report of employee stories"""
        if not employee_stories:
            return "# Employee Story Report\n\nNo employee stories available."
        
        report_lines = [
            "# Employee Story Report",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Simulation Timestamp: {self.timestamp}",
            "",
            "## Executive Summary",
            ""
        ]
        
        total_tracked = sum(len(stories) for stories in employee_stories.values())
        report_lines.append(f"Total employees tracked: **{total_tracked}**")
        report_lines.append("")
        
        for category, stories in employee_stories.items():
            if not stories:
                continue
                
            category_title = category.replace('_', ' ').title()
            report_lines.extend([
                f"### {category_title} ({len(stories)} employees)",
                ""
            ])
            
            for story in stories:
                report_lines.extend([
                    f"#### Employee {story.employee_id}",
                    "",
                    f"**Category:** {story.category}",
                    f"**Salary Growth:** {story.total_growth_percent:+.1f}% (£{story.initial_salary:,.0f} → £{story.current_salary:,.0f})",
                    "",
                    f"**Story:** {story.story_summary}",
                    "",
                    "**Key Events:**"
                ])
                
                if story.key_events:
                    for event in story.key_events:
                        report_lines.append(f"- {event}")
                else:
                    report_lines.append("- No significant events recorded")
                
                report_lines.extend(["", "**Recommendations:**"])
                for rec in story.recommendations:
                    report_lines.append(f"- {rec}")
                
                report_lines.extend(["", "---", ""])
        
        return "\n".join(report_lines)
    
    def export_interactive_dashboard(self, output_path: str = None):
        """Export interactive HTML dashboard"""
        if not self.story_tracker:
            self.smart_logger.log_warning("Story tracking not enabled - cannot export interactive dashboard")
            return None
        
        if output_path is None:
            if hasattr(self, 'run_images_dir'):
                output_path = self.run_images_dir / "employee_stories_dashboard.html"
            else:
                output_path = self.images_dir / f"employee_stories_dashboard_{self.timestamp}.html"
        
        # TODO: This will be fully implemented in Phase 4 of the PRP
        # For now, return a placeholder
        self.smart_logger.log_info(f"Interactive dashboard export planned for: {output_path}")
        return str(output_path)
    
    def get_tracked_employee_summary(self):
        """Get summary statistics of tracked employees"""
        if not self.story_tracker:
            return {'error': 'Story tracking not enabled'}
        
        return self.story_tracker.get_tracked_employee_summary()
    
    def _generate_individual_story_charts(self, employee_stories: Dict[str, List]) -> List[str]:
        """Generate individual story charts for each category"""
        story_viz_files = []
        
        if not employee_stories:
            return story_viz_files
        
        try:
            dashboard_generator = InteractiveDashboardGenerator(
                story_tracker=self.story_tracker,
                smart_logger=self.smart_logger
            )
            
            for category, stories in employee_stories.items():
                if stories:
                    # Create category-specific dashboard
                    category_dashboard_path = self.run_images_dir / f"{category}_story_dashboard.html"
                    category_tracked = {category: stories}
                    
                    dashboard_file = dashboard_generator.generate_comprehensive_dashboard(
                        population_data=[],  # Simplified for category-specific view
                        tracked_employees=category_tracked,
                        cycle_data=None,
                        output_path=str(category_dashboard_path)
                    )
                    
                    story_viz_files.append(dashboard_file)
            
            return story_viz_files
            
        except Exception as e:
            self.smart_logger.log_error(f"Failed to generate individual story charts: {e}")
            return []

def main():
    """Command-line interface for the simulation orchestrator"""
    parser = argparse.ArgumentParser(description="Employee Population Simulation Orchestrator")
    parser.add_argument('--mode', choices=['full', 'quick-validation', 'story-validation'], default='full',
                       help='Simulation mode to run')
    parser.add_argument('--config', help='Path to JSON configuration file')
    parser.add_argument('--population-size', type=int, default=1000,
                       help='Number of employees to generate')
    parser.add_argument('--max-cycles', type=int, default=15,
                       help='Maximum number of review cycles to simulate')
    parser.add_argument('--random-seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization generation')
    parser.add_argument('--export-formats', nargs='+', choices=['csv', 'excel', 'json'],
                       default=['csv', 'excel', 'json'], help='Export formats')
    
    # Story tracking arguments
    parser.add_argument('--enable-stories', action='store_true',
                       help='Enable employee story tracking')
    parser.add_argument('--generate-stories', action='store_true',
                       help='Generate individual employee stories (implies --enable-stories)')
    parser.add_argument('--interactive-viz', action='store_true',
                       help='Generate interactive visualizations')
    parser.add_argument('--log-level', choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO',
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            self.smart_logger.log_info(f"Loaded configuration from {args.config}")
        except Exception as e:
            self.smart_logger.log_error(f"Failed to load configuration: {e}")
            sys.exit(1)
    else:
        # Use command-line arguments to build config
        config = {
            'population_size': args.population_size,
            'random_seed': args.random_seed,
            'max_cycles': args.max_cycles,
            'convergence_threshold': 0.001,
            'export_formats': args.export_formats,
            'generate_visualizations': not args.no_viz,
            'export_individual_files': True,
            'export_comprehensive_report': True,
            
            # Story tracking configuration from CLI
            'enable_story_tracking': args.enable_stories or args.generate_stories,
            'generate_interactive_dashboard': args.interactive_viz,
            'create_individual_story_charts': args.generate_stories,
            'log_level': args.log_level
        }
    
    # Initialize orchestrator
    orchestrator = EmployeeSimulationOrchestrator(config=config)
    
    try:
        if args.mode == 'quick-validation':
            # Run quick validation
            validation_results = orchestrator.run_quick_validation()
            print("\n=== QUICK VALIDATION RESULTS ===")
            print(json.dumps(validation_results, indent=2, default=str))
            
            if validation_results['overall']['status'] == 'FAIL':
                sys.exit(1)
        
        elif args.mode == 'story-validation':
            # Run story tracking validation with small population
            print("\n=== STORY TRACKING VALIDATION ===")
            validation_config = config.copy()
            validation_config.update({
                'population_size': 100,
                'max_cycles': 3,
                'enable_story_tracking': True,
                'export_story_data': True,
                'generate_summary_report': True,
                'tracked_employee_count': 10,  # Max employees per category
                'story_categories': ['gender_gap', 'above_range', 'high_performer']
            })
            
            validation_orchestrator = EmployeeSimulationOrchestrator(config=validation_config)
            results = validation_orchestrator.run_with_story_tracking()
            
            # Validate story tracking results
            story_validation = {
                'total_tracked_employees': results['summary_metrics'].get('total_tracked_employees', 0),
                'categories_found': len(results.get('employee_stories', {})),
                'story_files_generated': 'employee_stories' in results.get('files_generated', {}),
                'summary_report_generated': 'summary_report' in results.get('files_generated', {})
            }
            
            validation_passed = (
                story_validation['total_tracked_employees'] >= 5 and
                story_validation['categories_found'] >= 1 and
                story_validation['story_files_generated'] and
                story_validation['summary_report_generated']
            )
            
            print(f"Total tracked employees: {story_validation['total_tracked_employees']}")
            print(f"Categories found: {story_validation['categories_found']}")
            print(f"Story files generated: {story_validation['story_files_generated']}")
            print(f"Summary report generated: {story_validation['summary_report_generated']}")
            print(f"\nValidation: {'✓ PASS' if validation_passed else '✗ FAIL'}")
            
            if not validation_passed:
                sys.exit(1)
        
        else:
            # Run complete simulation (with or without story tracking)
            if config.get('enable_story_tracking', False):
                results = orchestrator.run_with_story_tracking()
            else:
                results = orchestrator.run_complete_simulation()
            
            print("\n=== SIMULATION COMPLETED SUCCESSFULLY ===")
            print(f"Timestamp: {results['timestamp']}")
            print(f"Population Size: {results['summary_metrics']['population_size']}")
            print(f"Cycles Completed: {results['summary_metrics']['cycles_completed']}")
            print(f"Final Gini Coefficient: {results['summary_metrics']['final_gini_coefficient']}")
            print(f"Convergence Achieved: {results['summary_metrics']['convergence_achieved']}")
            
            print("\n=== FILES GENERATED ===")
            for category, files in results['files_generated'].items():
                if isinstance(files, dict):
                    print(f"{category.upper()}:")
                    for subcategory, subfiles in files.items():
                        if isinstance(subfiles, dict):
                            for format_type, filepath in subfiles.items():
                                print(f"  {subcategory} ({format_type}): {filepath}")
                        else:
                            print(f"  {subcategory}: {subfiles}")
                else:
                    print(f"{category.upper()}: {files}")
            
            print("\n=== VALIDATION STATUS ===")
            if 'final_summary' in results and 'validation_status' in results['final_summary']:
                for component, status in results['final_summary']['validation_status'].items():
                    status_str = "✓ PASS" if status else "✗ FAIL"
                    print(f"{component.title()}: {status_str}")
            else:
                validation_status = results.get('validation_results', {})
                for component, result in validation_status.items():
                    if isinstance(result, dict) and 'median_constraint_met' in result:
                        status_str = "✓ PASS" if result['median_constraint_met'] else "✗ FAIL"
                        print(f"{component.title()}: {status_str}")
                    elif isinstance(result, dict) and 'all_tests_passed' in result:
                        status_str = "✓ PASS" if result['all_tests_passed'] else "✗ FAIL"
                        print(f"{component.title()}: {status_str}")
            
    except Exception as e:
        self.smart_logger.log_error(f"Orchestrator failed: {e}")
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()