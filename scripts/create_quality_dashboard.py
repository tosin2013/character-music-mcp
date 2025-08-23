#!/usr/bin/env python3
"""
Real-time Quality Dashboard Creator

Creates interactive dashboards for monitoring test coverage, performance metrics,
and overall code quality with real-time updates and historical trends.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse
from jinja2 import Template


class QualityDashboardCreator:
    """Creates comprehensive quality monitoring dashboards"""
    
    def __init__(self, output_dir: str = "dashboard"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Dashboard templates
        self.main_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Character Music MCP - Quality Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f8fafc; color: #334155; line-height: 1.6; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); 
            color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .refresh-info { 
            background: rgba(255, 255, 255, 0.1); padding: 10px 15px; 
            border-radius: 8px; margin-top: 15px; font-size: 0.9em;
        }
        .metrics-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 20px; margin-bottom: 30px; 
        }
        .metric-card { 
            background: white; padding: 25px; border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 20px rgba(0,0,0,0.12); 
        }
        .metric-card h3 { 
            color: #64748b; font-size: 0.85em; text-transform: uppercase; 
            letter-spacing: 1px; margin-bottom: 12px; font-weight: 600;
        }
        .metric-value { 
            font-size: 2.8em; font-weight: 800; margin-bottom: 8px; 
            display: flex; align-items: center; gap: 10px;
        }
        .metric-value.excellent { color: #059669; }
        .metric-value.good { color: #0891b2; }
        .metric-value.warning { color: #d97706; }
        .metric-value.critical { color: #dc2626; }
        .metric-trend { 
            font-size: 0.9em; color: #64748b; display: flex; 
            align-items: center; gap: 5px; margin-bottom: 10px;
        }
        .trend-up { color: #059669; }
        .trend-down { color: #dc2626; }
        .trend-stable { color: #64748b; }
        .metric-subtitle { color: #94a3b8; font-size: 0.9em; }
        .section { 
            background: white; padding: 30px; border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 30px;
            border: 1px solid #e2e8f0;
        }
        .section h2 { 
            color: #1e293b; margin-bottom: 25px; padding-bottom: 15px; 
            border-bottom: 2px solid #f1f5f9; font-size: 1.5em; font-weight: 600;
        }
        .chart-container { 
            position: relative; height: 400px; margin: 20px 0; 
            background: #fafbfc; border-radius: 8px; padding: 15px;
        }
        .alerts-container { 
            display: grid; gap: 15px; 
        }
        .alert { 
            padding: 15px 20px; border-radius: 8px; border-left: 4px solid;
            display: flex; align-items: center; gap: 12px;
        }
        .alert.critical { 
            background: #fef2f2; border-color: #dc2626; color: #991b1b; 
        }
        .alert.warning { 
            background: #fffbeb; border-color: #d97706; color: #92400e; 
        }
        .alert.info { 
            background: #eff6ff; border-color: #2563eb; color: #1d4ed8; 
        }
        .alert-icon { font-size: 1.2em; }
        .alert-content { flex: 1; }
        .alert-time { font-size: 0.85em; opacity: 0.8; }
        .status-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
        }
        .status-item { 
            padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;
            background: white;
        }
        .status-item h4 { color: #374151; margin-bottom: 10px; font-weight: 600; }
        .status-badge { 
            padding: 6px 12px; border-radius: 20px; font-size: 0.8em; 
            font-weight: 600; text-transform: uppercase; display: inline-block;
        }
        .status-badge.passing { background: #d1fae5; color: #065f46; }
        .status-badge.failing { background: #fee2e2; color: #991b1b; }
        .status-badge.warning { background: #fef3c7; color: #92400e; }
        .progress-bar { 
            width: 100%; height: 8px; background: #f1f5f9; border-radius: 4px; 
            overflow: hidden; margin: 10px 0;
        }
        .progress-fill { 
            height: 100%; transition: width 0.3s ease; border-radius: 4px;
        }
        .progress-fill.excellent { background: #059669; }
        .progress-fill.good { background: #0891b2; }
        .progress-fill.warning { background: #d97706; }
        .progress-fill.critical { background: #dc2626; }
        .timestamp { 
            text-align: center; color: #94a3b8; font-size: 0.9em; 
            margin-top: 40px; padding-top: 20px; border-top: 1px solid #f1f5f9;
        }
        .auto-refresh { 
            position: fixed; top: 20px; right: 20px; background: white; 
            padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0; font-size: 0.9em;
        }
        .refresh-toggle { 
            margin-left: 10px; padding: 5px 10px; background: #3b82f6; 
            color: white; border: none; border-radius: 4px; cursor: pointer;
        }
        .refresh-toggle:hover { background: #2563eb; }
        .refresh-toggle.disabled { background: #94a3b8; cursor: not-allowed; }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .metrics-grid { grid-template-columns: 1fr; }
            .metric-value { font-size: 2.2em; }
            .header h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="auto-refresh">
        <span id="refresh-status">Auto-refresh: ON</span>
        <button class="refresh-toggle" onclick="toggleAutoRefresh()">Toggle</button>
        <span id="last-update">Last: {{ timestamp }}</span>
    </div>

    <div class="container">
        <div class="header">
            <h1>🎵 Character Music MCP Quality Dashboard</h1>
            <p>Real-time monitoring of test coverage, performance, and code quality</p>
            <div class="refresh-info">
                <strong>Live Dashboard</strong> • Updates every 5 minutes • 
                Last updated: {{ timestamp }}
            </div>
        </div>

        <div class="metrics-grid">
            {% for metric in key_metrics %}
            <div class="metric-card">
                <h3>{{ metric.title }}</h3>
                <div class="metric-value {{ metric.status_class }}">
                    {{ metric.value }}{{ metric.unit }}
                    <span style="font-size: 0.4em;">{{ metric.icon }}</span>
                </div>
                <div class="metric-trend">
                    <span class="trend-{{ metric.trend_direction }}">
                        {{ metric.trend_icon }} {{ metric.trend_text }}
                    </span>
                </div>
                <div class="metric-subtitle">{{ metric.subtitle }}</div>
                <div class="progress-bar">
                    <div class="progress-fill {{ metric.status_class }}" 
                         style="width: {{ metric.progress_percent }}%"></div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="section">
            <h2>📊 Performance Trends</h2>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>📈 Coverage Trends</h2>
            <div class="chart-container">
                <canvas id="coverageChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>🚨 Active Alerts</h2>
            <div class="alerts-container">
                {% if alerts %}
                    {% for alert in alerts %}
                    <div class="alert {{ alert.severity }}">
                        <div class="alert-icon">{{ alert.icon }}</div>
                        <div class="alert-content">
                            <strong>{{ alert.title }}</strong>
                            <div>{{ alert.message }}</div>
                        </div>
                        <div class="alert-time">{{ alert.time_ago }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="alert info">
                        <div class="alert-icon">✅</div>
                        <div class="alert-content">
                            <strong>All Systems Operational</strong>
                            <div>No active alerts or issues detected</div>
                        </div>
                    </div>
                {% endif %}
            </div>
        </div>

        <div class="section">
            <h2>🔍 System Status</h2>
            <div class="status-grid">
                {% for status in system_status %}
                <div class="status-item">
                    <h4>{{ status.component }}</h4>
                    <span class="status-badge {{ status.status }}">{{ status.status_text }}</span>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #64748b;">
                        {{ status.details }}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="timestamp">
            Dashboard generated at {{ timestamp }} • 
            <a href="javascript:location.reload()" style="color: #3b82f6;">Refresh Now</a>
        </div>
    </div>

    <script>
        // Auto-refresh functionality
        let autoRefreshEnabled = true;
        let refreshInterval;

        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const status = document.getElementById('refresh-status');
            const button = document.querySelector('.refresh-toggle');
            
            if (autoRefreshEnabled) {
                status.textContent = 'Auto-refresh: ON';
                button.textContent = 'Disable';
                button.classList.remove('disabled');
                startAutoRefresh();
            } else {
                status.textContent = 'Auto-refresh: OFF';
                button.textContent = 'Enable';
                button.classList.add('disabled');
                clearInterval(refreshInterval);
            }
        }

        function startAutoRefresh() {
            refreshInterval = setInterval(() => {
                if (autoRefreshEnabled) {
                    location.reload();
                }
            }, 300000); // 5 minutes
        }

        function updateLastRefresh() {
            const now = new Date();
            document.getElementById('last-update').textContent = 
                'Last: ' + now.toLocaleTimeString();
        }

        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: {{ performance_chart.labels | tojson }},
                datasets: [
                    {
                        label: 'Character Analysis (s)',
                        data: {{ performance_chart.character_analysis | tojson }},
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Complete Workflow (s)',
                        data: {{ performance_chart.workflow | tojson }},
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Performance Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time (seconds)'
                        }
                    }
                }
            }
        });

        // Coverage Chart
        const coverageCtx = document.getElementById('coverageChart').getContext('2d');
        const coverageChart = new Chart(coverageCtx, {
            type: 'line',
            data: {
                labels: {{ coverage_chart.labels | tojson }},
                datasets: [
                    {
                        label: 'Test Coverage (%)',
                        data: {{ coverage_chart.coverage | tojson }},
                        borderColor: '#059669',
                        backgroundColor: 'rgba(5, 150, 105, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Success Rate (%)',
                        data: {{ coverage_chart.success_rate | tojson }},
                        borderColor: '#dc2626',
                        backgroundColor: 'rgba(220, 38, 38, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Quality Metrics Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Percentage (%)'
                        }
                    }
                }
            }
        });

        // Start auto-refresh
        startAutoRefresh();
        
        // Update timestamp every minute
        setInterval(updateLastRefresh, 60000);
    </script>
</body>
</html>
        """
    
    def load_quality_metrics(self) -> Dict[str, Any]:
        """Load current quality metrics from various sources"""
        metrics = {
            "test_coverage": 0.0,
            "test_success_rate": 0.0,
            "performance_score": 0.0,
            "documentation_score": 0.0,
            "security_score": 0.0,
            "code_quality_score": 0.0
        }
        
        # Load from quality metrics file
        quality_file = Path("quality_metrics.json")
        if quality_file.exists():
            try:
                with open(quality_file, 'r') as f:
                    data = json.load(f)
                
                for name, metric_data in data.items():
                    if name in metrics:
                        metrics[name] = metric_data.get("current_value", 0.0)
            except Exception as e:
                print(f"⚠️ Failed to load quality metrics: {e}")
        
        # Load from test reports
        test_reports = list(Path(".").glob("*test_report*.json"))
        if test_reports:
            latest_report = max(test_reports, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest_report, 'r') as f:
                    data = json.load(f)
                metrics["test_success_rate"] = data.get("overall_success_rate", 0.0) * 100
            except Exception:
                pass
        
        # Load from coverage reports
        coverage_file = Path("coverage.xml")
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                coverage_elem = root.find(".")
                if coverage_elem is not None:
                    line_rate = float(coverage_elem.get("line-rate", 0))
                    metrics["test_coverage"] = line_rate * 100
            except Exception:
                pass
        
        return metrics
    
    def load_performance_data(self) -> Dict[str, Any]:
        """Load performance metrics and trends"""
        performance_data = {
            "current": {},
            "trends": {},
            "history": []
        }
        
        # Load from performance metrics file
        perf_file = Path("performance_metrics.json")
        if perf_file.exists():
            try:
                with open(perf_file, 'r') as f:
                    data = json.load(f)
                
                # Group by metric name
                metric_groups = {}
                for metric in data:
                    name = metric["name"]
                    if name not in metric_groups:
                        metric_groups[name] = []
                    metric_groups[name].append(metric)
                
                # Get current values and trends
                for name, metrics in metric_groups.items():
                    if metrics:
                        latest = metrics[-1]
                        performance_data["current"][name] = {
                            "value": latest["value"],
                            "unit": latest["unit"],
                            "timestamp": latest["timestamp"]
                        }
                        
                        # Calculate trend
                        if len(metrics) >= 5:
                            recent_values = [m["value"] for m in metrics[-5:]]
                            older_values = [m["value"] for m in metrics[-10:-5]] if len(metrics) >= 10 else recent_values
                            
                            recent_avg = sum(recent_values) / len(recent_values)
                            older_avg = sum(older_values) / len(older_values)
                            
                            if older_avg > 0:
                                trend_percent = ((recent_avg - older_avg) / older_avg) * 100
                                performance_data["trends"][name] = trend_percent
                
                performance_data["history"] = data
                
            except Exception as e:
                print(f"⚠️ Failed to load performance data: {e}")
        
        return performance_data
    
    def load_alerts(self) -> List[Dict[str, Any]]:
        """Load active alerts from various sources"""
        alerts = []
        
        # Load quality alerts
        quality_alerts_file = Path("quality_alerts.json")
        if quality_alerts_file.exists():
            try:
                with open(quality_alerts_file, 'r') as f:
                    data = json.load(f)
                
                for alert in data:
                    alerts.append({
                        "severity": alert.get("severity", "info"),
                        "title": alert.get("metric_name", "Unknown"),
                        "message": alert.get("message", ""),
                        "timestamp": alert.get("timestamp", ""),
                        "type": "quality"
                    })
            except Exception:
                pass
        
        # Load performance alerts
        perf_alerts_file = Path("performance_alerts.json")
        if perf_alerts_file.exists():
            try:
                with open(perf_alerts_file, 'r') as f:
                    data = json.load(f)
                
                for alert in data:
                    alerts.append({
                        "severity": alert.get("severity", "info"),
                        "title": alert.get("metric_name", "Unknown"),
                        "message": alert.get("message", ""),
                        "timestamp": alert.get("timestamp", ""),
                        "type": "performance"
                    })
            except Exception:
                pass
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return alerts[:10]  # Return last 10 alerts
    
    def format_metric_for_display(self, name: str, value: float, 
                                 trend: Optional[float] = None) -> Dict[str, Any]:
        """Format metric for dashboard display"""
        # Determine status class based on value and thresholds
        thresholds = {
            "test_coverage": {"excellent": 90, "good": 80, "warning": 70},
            "test_success_rate": {"excellent": 95, "good": 90, "warning": 80},
            "performance_score": {"excellent": 90, "good": 80, "warning": 70},
            "documentation_score": {"excellent": 95, "good": 85, "warning": 75},
            "security_score": {"excellent": 95, "good": 90, "warning": 80},
            "code_quality_score": {"excellent": 90, "good": 80, "warning": 70}
        }
        
        metric_thresholds = thresholds.get(name, {"excellent": 90, "good": 80, "warning": 70})
        
        if value >= metric_thresholds["excellent"]:
            status_class = "excellent"
        elif value >= metric_thresholds["good"]:
            status_class = "good"
        elif value >= metric_thresholds["warning"]:
            status_class = "warning"
        else:
            status_class = "critical"
        
        # Format trend
        trend_direction = "stable"
        trend_icon = "➡️"
        trend_text = "Stable"
        
        if trend is not None:
            if trend > 2:
                trend_direction = "up"
                trend_icon = "📈"
                trend_text = f"+{trend:.1f}%"
            elif trend < -2:
                trend_direction = "down"
                trend_icon = "📉"
                trend_text = f"{trend:.1f}%"
        
        # Metric-specific formatting
        titles = {
            "test_coverage": "Test Coverage",
            "test_success_rate": "Test Success Rate",
            "performance_score": "Performance Score",
            "documentation_score": "Documentation Quality",
            "security_score": "Security Score",
            "code_quality_score": "Code Quality"
        }
        
        icons = {
            "test_coverage": "🧪",
            "test_success_rate": "✅",
            "performance_score": "⚡",
            "documentation_score": "📚",
            "security_score": "🔒",
            "code_quality_score": "🎯"
        }
        
        subtitles = {
            "test_coverage": "Line coverage percentage",
            "test_success_rate": "Passing tests percentage",
            "performance_score": "Benchmark success rate",
            "documentation_score": "Documentation completeness",
            "security_score": "Security scan results",
            "code_quality_score": "Code quality metrics"
        }
        
        return {
            "title": titles.get(name, name.replace("_", " ").title()),
            "value": f"{value:.1f}",
            "unit": "%",
            "icon": icons.get(name, "📊"),
            "status_class": status_class,
            "trend_direction": trend_direction,
            "trend_icon": trend_icon,
            "trend_text": trend_text,
            "subtitle": subtitles.get(name, ""),
            "progress_percent": min(100, max(0, value))
        }
    
    def format_alerts_for_display(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format alerts for dashboard display"""
        formatted_alerts = []
        
        for alert in alerts:
            # Calculate time ago
            try:
                alert_time = datetime.fromisoformat(alert["timestamp"])
                time_diff = datetime.now() - alert_time
                
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours}h ago"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes}m ago"
                else:
                    time_ago = "Just now"
            except:
                time_ago = "Unknown"
            
            # Alert icons
            icons = {
                "critical": "🚨",
                "warning": "⚠️",
                "info": "ℹ️"
            }
            
            formatted_alerts.append({
                "severity": alert["severity"],
                "title": alert["title"],
                "message": alert["message"],
                "time_ago": time_ago,
                "icon": icons.get(alert["severity"], "📢")
            })
        
        return formatted_alerts
    
    def generate_chart_data(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data for performance and coverage trends"""
        chart_data = {
            "performance_chart": {
                "labels": [],
                "character_analysis": [],
                "workflow": []
            },
            "coverage_chart": {
                "labels": [],
                "coverage": [],
                "success_rate": []
            }
        }
        
        # Process performance history
        if "history" in performance_data:
            # Group by date
            daily_data = {}
            
            for metric in performance_data["history"]:
                try:
                    date = datetime.fromisoformat(metric["timestamp"]).date()
                    date_str = date.strftime("%m/%d")
                    
                    if date_str not in daily_data:
                        daily_data[date_str] = {}
                    
                    daily_data[date_str][metric["name"]] = metric["value"]
                except:
                    continue
            
            # Sort by date and extract data
            sorted_dates = sorted(daily_data.keys())[-14:]  # Last 14 days
            
            for date_str in sorted_dates:
                data = daily_data[date_str]
                chart_data["performance_chart"]["labels"].append(date_str)
                chart_data["performance_chart"]["character_analysis"].append(
                    data.get("character_analysis_time", 0)
                )
                chart_data["performance_chart"]["workflow"].append(
                    data.get("complete_workflow_time", 0)
                )
        
        # Generate sample coverage data (would be loaded from actual metrics)
        import random
        for i in range(14):
            date = datetime.now() - timedelta(days=13-i)
            chart_data["coverage_chart"]["labels"].append(date.strftime("%m/%d"))
            chart_data["coverage_chart"]["coverage"].append(
                random.uniform(75, 95)  # Sample data
            )
            chart_data["coverage_chart"]["success_rate"].append(
                random.uniform(85, 100)  # Sample data
            )
        
        return chart_data
    
    def get_system_status(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get system component status"""
        status_items = []
        
        # Test Suite Status
        test_success = metrics.get("test_success_rate", 0)
        if test_success >= 95:
            test_status = "passing"
            test_status_text = "Passing"
            test_details = f"{test_success:.1f}% tests passing"
        elif test_success >= 80:
            test_status = "warning"
            test_status_text = "Warning"
            test_details = f"{test_success:.1f}% tests passing"
        else:
            test_status = "failing"
            test_status_text = "Failing"
            test_details = f"{test_success:.1f}% tests passing"
        
        status_items.append({
            "component": "Test Suite",
            "status": test_status,
            "status_text": test_status_text,
            "details": test_details
        })
        
        # Coverage Status
        coverage = metrics.get("test_coverage", 0)
        if coverage >= 80:
            coverage_status = "passing"
            coverage_status_text = "Good"
            coverage_details = f"{coverage:.1f}% line coverage"
        elif coverage >= 60:
            coverage_status = "warning"
            coverage_status_text = "Low"
            coverage_details = f"{coverage:.1f}% line coverage"
        else:
            coverage_status = "failing"
            coverage_status_text = "Critical"
            coverage_details = f"{coverage:.1f}% line coverage"
        
        status_items.append({
            "component": "Code Coverage",
            "status": coverage_status,
            "status_text": coverage_status_text,
            "details": coverage_details
        })
        
        # Performance Status
        perf_score = metrics.get("performance_score", 0)
        if perf_score >= 80:
            perf_status = "passing"
            perf_status_text = "Good"
            perf_details = f"{perf_score:.1f}% benchmarks passing"
        elif perf_score >= 60:
            perf_status = "warning"
            perf_status_text = "Degraded"
            perf_details = f"{perf_score:.1f}% benchmarks passing"
        else:
            perf_status = "failing"
            perf_status_text = "Poor"
            perf_details = f"{perf_score:.1f}% benchmarks passing"
        
        status_items.append({
            "component": "Performance",
            "status": perf_status,
            "status_text": perf_status_text,
            "details": perf_details
        })
        
        # Security Status
        security_score = metrics.get("security_score", 0)
        if security_score >= 95:
            security_status = "passing"
            security_status_text = "Secure"
            security_details = "No critical vulnerabilities"
        elif security_score >= 80:
            security_status = "warning"
            security_status_text = "Minor Issues"
            security_details = "Some non-critical issues found"
        else:
            security_status = "failing"
            security_status_text = "Vulnerable"
            security_details = "Critical issues detected"
        
        status_items.append({
            "component": "Security",
            "status": security_status,
            "status_text": security_status_text,
            "details": security_details
        })
        
        return status_items
    
    def create_dashboard(self) -> str:
        """Create the complete quality dashboard"""
        print("📊 Creating quality dashboard...")
        
        # Load all data
        metrics = self.load_quality_metrics()
        performance_data = self.load_performance_data()
        alerts = self.load_alerts()
        
        # Format metrics for display
        key_metrics = []
        for name, value in metrics.items():
            trend = performance_data["trends"].get(name)
            formatted_metric = self.format_metric_for_display(name, value, trend)
            key_metrics.append(formatted_metric)
        
        # Format alerts
        formatted_alerts = self.format_alerts_for_display(alerts)
        
        # Generate chart data
        chart_data = self.generate_chart_data(performance_data)
        
        # Get system status
        system_status = self.get_system_status(metrics)
        
        # Prepare template data
        template_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "key_metrics": key_metrics,
            "alerts": formatted_alerts,
            "system_status": system_status,
            "performance_chart": chart_data["performance_chart"],
            "coverage_chart": chart_data["coverage_chart"]
        }
        
        # Render template
        template = Template(self.main_template)
        html_content = template.render(**template_data)
        
        # Save dashboard
        dashboard_file = self.output_dir / "index.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Quality dashboard created: {dashboard_file}")
        
        # Create API endpoint for data
        api_data = {
            "timestamp": template_data["timestamp"],
            "metrics": {metric["title"]: {
                "value": float(metric["value"]),
                "status": metric["status_class"],
                "trend": metric["trend_text"]
            } for metric in key_metrics},
            "alerts_count": len(formatted_alerts),
            "system_health": "good" if all(s["status"] == "passing" for s in system_status) else "warning"
        }
        
        api_file = self.output_dir / "api.json"
        with open(api_file, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2)
        
        return str(dashboard_file)


def main():
    """Main dashboard creation"""
    parser = argparse.ArgumentParser(description="Create quality dashboard")
    parser.add_argument("--output", "-o", default="dashboard",
                       help="Output directory for dashboard")
    parser.add_argument("--watch", "-w", action="store_true",
                       help="Watch for changes and auto-regenerate")
    parser.add_argument("--interval", "-i", type=int, default=300,
                       help="Update interval in seconds (for watch mode)")
    
    args = parser.parse_args()
    
    creator = QualityDashboardCreator(args.output)
    
    if args.watch:
        print(f"🔄 Starting dashboard watch mode (interval: {args.interval}s)")
        try:
            while True:
                dashboard_file = creator.create_dashboard()
                print(f"📊 Dashboard updated: {dashboard_file}")
                
                import time
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard watch stopped by user")
    else:
        dashboard_file = creator.create_dashboard()
        print(f"🎉 Dashboard created successfully!")
        print(f"📂 Open: {dashboard_file}")


if __name__ == "__main__":
    main()