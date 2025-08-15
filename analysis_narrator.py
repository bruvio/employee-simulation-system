#!/usr/bin/env python3
"""
Analysis Narrator for Employee Simulation System.

Transforms technical analysis progress into user-friendly, business- oriented narratives.
"""


from typing import Any, Dict

# Import common utilities to boost coverage
# Removed unused imports to fix flake8 issues


class AnalysisNarrator:
    """
    Converts technical analysis steps into user-friendly business narratives.

    Replaces overwhelming technical logs with accessible progress updates that help non-technical stakeholders
    understand what the system is doing and why.
    """

    def __init__(self, scenario_config: Dict[str, Any], smart_logger=None):
        """
        Initialize analysis narrator.

        Args:
            scenario_config: Configuration for current analysis scenario
            smart_logger: Smart logging manager instance
        """
        self.config = scenario_config
        self.logger = smart_logger
        self.company_context = self._extract_company_context()

        # Narrative templates for different analysis steps
        self.narrative_templates = {
            "population_generation": self._get_population_narrative_templates(),
            "convergence_analysis": self._get_convergence_narrative_templates(),
            "intervention_analysis": self._get_intervention_narrative_templates(),
            "dashboard_generation": self._get_dashboard_narrative_templates(),
        }

    def _extract_company_context(self) -> Dict[str, Any]:
        """Extract relevant company context from configuration."""
        context = {
            "population_size": self.config.get("population_size", 200),
            "has_salary_constraints": bool(self.config.get("salary_constraints")),
            "salary_structure": self._format_salary_structure(),
            "gender_gap_target": self.config.get("gender_pay_gap_percent", 15.8),
            "scenario_name": getattr(self.config, "scenario_name", "company analysis"),
        }
        return context

    def _format_salary_structure(self) -> Dict[str, str]:
        """Format salary constraints into user-friendly ranges."""
        salary_constraints = self.config.get("salary_constraints")
        if not salary_constraints:
            return {}

        formatted = {}
        level_names = {
            1: "Level 1 (Graduates)",
            2: "Level 2 (Junior)",
            3: "Level 3 (Standard Hire)",
            4: "Level 4 (Senior)",
            5: "Level 5 (Senior)",
            6: "Level 6 (Senior)",
        }

        for level, constraints in salary_constraints.items():
            level_name = level_names.get(level, f"Level {level}")
            min_sal = constraints.get("min", 0)
            max_sal = constraints.get("max", 0)
            formatted[level] = f"{level_name}: £{min_sal:,} - £{max_sal:,}"

        return formatted

    def start_analysis_narrative(self) -> str:
        """Generate opening narrative for analysis session."""
        context = self.company_context

        salary_structure_text = ""
        if context["salary_structure"]:
            structure_lines = [f"   • {desc}" for desc in context["salary_structure"].values()]
            salary_structure_text = f"""
   Using your company's salary structure:
{chr(10).join(structure_lines)}"""

        narrative = f"""
🏢 **Analyzing {context['population_size']} employees from your organization**
{salary_structure_text}

🎯 **Focus**: Identifying salary inequality and gender pay gaps
💡 **Goal**: Provide actionable recommendations for management decisions
        """.strip()

        return narrative

    def narrate_population_generation(self, population_stats: Dict[str, Any]) -> str:
        """
        Generate narrative for population generation phase.
        """

        total_employees = population_stats.get("total_employees", 0)
        gender_gap = population_stats.get("gender_gap_percent", 0)
        salary_range_min = population_stats.get("salary_range_min", 0)
        salary_range_max = population_stats.get("salary_range_max", 0)

        # Determine gender gap severity
        gap_severity = "concerning" if gender_gap > 18 else "moderate" if gender_gap > 10 else "minor"
        gap_color = "🔴" if gender_gap > 18 else "🟡" if gender_gap > 10 else "🟢"

        narrative = f"""
👥 **Employee Population Generated Successfully**

📊 **Key Statistics**:
   • Total employees: {total_employees:,}
   • Salary range: £{salary_range_min:,.0f} - £{salary_range_max:,.0f}
   • Gender pay gap: {gap_color} {gender_gap:.1f}% ({gap_severity})

💭 **What this means**: {"This gender pay gap indicates potential salary inequality that requires management attention and intervention." if gender_gap > 12 else "Gender pay gap is within reasonable range but monitoring is recommended."}

➡️ **Next**: Analyzing salary patterns to identify specific inequality issues...
        """.strip()

        return narrative

    def narrate_convergence_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate narrative for median convergence analysis.
        """

        below_median_count = analysis_results.get("below_median_count", 0)
        total_employees = analysis_results.get("total_employees", 200)
        convergence_timeline = analysis_results.get("avg_convergence_years", 0)

        percentage = (below_median_count / total_employees) * 100 if total_employees > 0 else 0

        # Determine severity level
        if percentage > 40:
            severity = "significant salary inequality"
            priority = "HIGH PRIORITY"
            color = "🔴"
            urgency = "immediate"
        elif percentage > 25:
            severity = "moderate salary inequality"
            priority = "MEDIUM PRIORITY"
            color = "🟡"
            urgency = "prompt"
        else:
            severity = "minor salary variations"
            priority = "LOW PRIORITY"
            color = "🟢"
            urgency = "routine"

        narrative = f"""
📊 **Salary Equity Analysis Complete**

{color} **Key Finding**: Found {below_median_count} employees ({percentage:.1f}%) earning below median salary for their level

🎯 **Assessment**: This indicates {severity} requiring {urgency} attention
📈 **Priority Level**: {priority}
⏱️ **Natural convergence timeline**: ~{convergence_timeline:.1f} years without intervention

💡 **Management Recommendation**:
   • Focus on employees >20% below median for immediate action
   • Consider structured salary review process
   • {'Budget for accelerated remediation to reduce compliance risk' if percentage > 30 else 'Monitor progress with regular salary audits'}

➡️ **Next**: Analyzing intervention strategies and associated costs...
        """.strip()

        return narrative

    def narrate_intervention_analysis(self, intervention_results: Dict[str, Any]) -> str:
        """
        Generate narrative for intervention strategy analysis.
        """

        gender_gap_data = intervention_results.get("gender_gap_remediation", {})
        equity_analysis = intervention_results.get("equity_analysis", {})

        # Extract key metrics
        current_gap = gender_gap_data.get("current_gender_gap_percent", 0)
        target_gap = gender_gap_data.get("target_gender_gap_percent", 0)
        recommended_cost = equity_analysis.get("optimal_approach", {}).get("total_investment", 0)
        timeline = equity_analysis.get("optimal_approach", {}).get("timeline_months", 36)

        # Determine approach urgency
        if current_gap > 20:
            urgency = "URGENT"
            approach = "aggressive remediation"
            risk_level = "HIGH compliance and legal risk"
        elif current_gap > 12:
            urgency = "IMPORTANT"
            approach = "structured remediation"
            risk_level = "MEDIUM compliance risk"
        else:
            urgency = "ROUTINE"
            approach = "preventive monitoring"
            risk_level = "LOW compliance risk"

        narrative = f"""
💰 **Intervention Strategy Analysis Complete**

🎯 **Current Situation**:
   • Gender pay gap: {current_gap:.1f}% → Target: {target_gap:.1f}%
   • Risk assessment: {risk_level}
   • Recommended approach: {approach}

💵 **Investment Analysis**:
   • Estimated cost: £{recommended_cost:,.0f}
   • Implementation timeline: {timeline} months
   • Priority level: {urgency}

📋 **Strategic Recommendations**:
   1. {'Immediate budget approval and implementation' if urgency == 'URGENT' else 'Plan phased implementation over ' + str(timeline//12) + ' years'}
   2. {'Engage legal counsel for compliance review' if current_gap > 18 else 'Implement regular monitoring processes'}
   3. Communicate transparently with affected employees

➡️ **Next**: Generating management dashboard with detailed action plan...
        """.strip()

        return narrative

    def narrate_dashboard_generation(self, dashboard_results: Dict[str, Any]) -> str:
        """
        Generate narrative for dashboard generation phase.
        """

        components_count = dashboard_results.get("components_generated", 0)
        dashboard_path = dashboard_results.get("main_dashboard", "")
        auto_opened = dashboard_results.get("auto_opened", True)

        narrative = f"""
📊 **Management Dashboard Generated Successfully**

✅ **Dashboard Components**:
   • Executive summary with key insights
   • Interactive salary equity charts
   • Gap analysis with drill-down capabilities
   • Intervention cost-benefit simulator
   • Priority action matrix
   • Risk assessment indicators

🌐 **Access Information**:
   • Dashboard location: {dashboard_path.split('/')[-1] if dashboard_path else 'management_dashboard.html'}
   • Interactive charts: {components_count} professional visualizations
   • Status: {'Automatically opened in browser' if auto_opened else 'Ready for manual opening'}

💼 **For Management Use**:
   • Present findings to leadership team
   • Use interactive charts for board presentations
   • Export individual charts for reports
   • Reference action priorities for implementation planning

🎯 **Analysis Complete**: All recommendations are now available in management-friendly format
        """.strip()

        return narrative

    def _get_population_narrative_templates(self) -> Dict[str, str]:
        """
        Get narrative templates for population generation.
        """
        return {
            "start": "Generating realistic employee population based on your organization's structure...",
            "salary_generation": "Creating salary distributions that reflect real-world negotiation patterns...",
            "gender_gap_application": "Applying gender pay gap patterns observed in similar organizations...",
            "complete": "Employee population generated successfully with realistic salary inequalities",
        }

    def _get_convergence_narrative_templates(self) -> Dict[str, str]:
        """
        Get narrative templates for convergence analysis.
        """
        return {
            "start": "Analyzing salary equity patterns across all employee levels...",
            "median_calculation": "Calculating fair salary benchmarks for each position level...",
            "gap_identification": "Identifying employees earning significantly below market rate...",
            "timeline_projection": "Estimating time required for natural salary convergence...",
            "complete": "Salary equity analysis complete - priority cases identified",
        }

    def _get_intervention_narrative_templates(self) -> Dict[str, str]:
        """
        Get narrative templates for intervention analysis.
        """
        return {
            "start": "Evaluating management intervention strategies and costs...",
            "cost_analysis": "Calculating budget requirements for different remediation approaches...",
            "timeline_modeling": "Modeling implementation timelines and resource requirements...",
            "roi_calculation": "Analyzing return on investment and risk mitigation benefits...",
            "complete": "Intervention strategy analysis complete with cost-benefit recommendations",
        }

    def _get_dashboard_narrative_templates(self) -> Dict[str, str]:
        """
        Get narrative templates for dashboard generation.
        """
        return {
            "start": "Creating management dashboard with executive-friendly visualizations...",
            "component_generation": "Building interactive charts for salary equity analysis...",
            "summary_creation": "Generating executive summary with key insights and recommendations...",
            "integration": "Assembling comprehensive dashboard for management presentation...",
            "complete": "Management dashboard ready - professional visualizations generated",
        }

    def narrate_visualization_generation(self, viz_data: Dict[str, Any]) -> str:
        """
        Create user-friendly narrative for visualization generation.

        Args:
            viz_data: Visualization generation data including charts_generated, types, location

        Returns:
            User-friendly narrative about visualization generation
        """
        charts_generated = viz_data.get("charts_generated", 0)
        viz_types = viz_data.get("visualization_types", [])
        output_location = viz_data.get("output_location", "images/")

        types_description = ", ".join([t.replace("_", " ").title() for t in viz_types])

        return f"""📊 **Professional Visualizations Generated**

✅ **Charts Created**: {charts_generated} interactive visualizations
📈 **Types**: {types_description}
📁 **Location**: {output_location}

💼 **What this provides**:
   • Executive-ready charts for management presentations
   • Visual analysis of salary equity patterns
   • Interactive drill-down capabilities for detailed exploration
   • Professional formatting suitable for board meetings

➡️ **Next**: Assembling comprehensive management dashboard..."""

    def get_progress_narrative(self, step_name: str, step_data: Dict[str, Any]) -> str:
        """
        Get user-friendly narrative for any analysis step.

        Args:
            step_name: Name of the analysis step
            step_data: Data associated with the step

        Returns:
            User-friendly narrative explaining what's happening
        """

        # Map technical step names to narrative methods
        narrative_mapping = {
            "population_generation": self.narrate_population_generation,
            "median_convergence_analysis": self.narrate_convergence_analysis,
            "intervention_strategy_analysis": self.narrate_intervention_analysis,
            "dashboard_generation": self.narrate_dashboard_generation,
        }

        # Get appropriate narrative method
        narrative_method = narrative_mapping.get(step_name)

        if narrative_method:
            try:
                return narrative_method(step_data)
            except Exception:
                # Fallback to generic narrative
                return self._get_generic_narrative(step_name, step_data)
        else:
            return self._get_generic_narrative(step_name, step_data)

    def _get_generic_narrative(self, step_name: str, step_data: Dict[str, Any]) -> str:
        """
        Generate generic user-friendly narrative for unknown steps.
        """

        friendly_name = step_name.replace("_", " ").title()

        generic_narrative = f"""
⚙️ **{friendly_name} in Progress**

The system is currently working on {friendly_name.lower()} to help identify
salary inequality patterns and provide management recommendations.

This analysis will contribute to the overall salary equity assessment.
        """.strip()

        return generic_narrative

    def create_completion_summary(self, results: Dict[str, Any]) -> str:
        """
        Create final completion summary with key takeaways.
        """

        # Extract key metrics from results
        population_size = results.get("population_size", 200)
        analysis_components = len(results.get("analysis_results", {}))
        dashboard_generated = bool(results.get("dashboard_files"))

        summary = f"""
🎉 **Analysis Complete - Key Insights Ready**

📊 **Analysis Scope**:
   • Analyzed {population_size:,} employees
   • Completed {analysis_components} analysis components
   • Generated {'interactive management dashboard' if dashboard_generated else 'detailed reports'}

🎯 **What You Get**:
   • Clear identification of salary inequality patterns
   • Specific recommendations with cost estimates
   • Interactive visualizations for management presentations
   • Prioritized action plan for implementation

📈 **Next Steps**:
   1. Review the management dashboard for key insights
   2. Present findings to leadership team
   3. Plan implementation based on priority recommendations
   4. Schedule follow-up analysis to track progress

💡 **All analysis results are now available in management-friendly format**
        """.strip()

        return summary
