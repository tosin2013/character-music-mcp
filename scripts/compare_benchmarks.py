#!/usr/bin/env python3
"""
Benchmark Comparison Tool

Compares current benchmark results with baseline/historical results to detect
performance regressions and improvements.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BenchmarkComparison:
    """Comparison between two benchmark results"""
    benchmark_name: str
    current_time: float
    baseline_time: float
    time_change_percent: float
    current_memory: float
    baseline_memory: float
    memory_change_percent: float
    regression_detected: bool
    improvement_detected: bool
    status: str  # "improved", "regressed", "stable"


@dataclass
class ComparisonReport:
    """Complete comparison report"""
    timestamp: str
    current_file: str
    baseline_file: str
    total_benchmarks: int
    regressions: int
    improvements: int
    stable: int
    comparisons: List[BenchmarkComparison]
    
    @property
    def regression_rate(self) -> float:
        return self.regressions / self.total_benchmarks if self.total_benchmarks > 0 else 0.0
    
    @property
    def improvement_rate(self) -> float:
        return self.improvements / self.total_benchmarks if self.total_benchmarks > 0 else 0.0


class BenchmarkComparator:
    """Compares benchmark results and detects regressions"""
    
    def __init__(self):
        # Thresholds for detecting significant changes
        self.regression_threshold = 0.20  # 20% slower is a regression
        self.improvement_threshold = 0.10  # 10% faster is an improvement
        self.memory_regression_threshold = 0.25  # 25% more memory is a regression
        self.memory_improvement_threshold = 0.15  # 15% less memory is an improvement
    
    def load_benchmark_results(self, filepath: str) -> Dict[str, Any]:
        """Load benchmark results from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Benchmark file not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in benchmark file {filepath}: {e}")
            return {}
    
    def extract_benchmark_data(self, results: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract benchmark data into comparable format"""
        benchmark_data = {}
        
        if "results" in results:
            for result in results["results"]:
                benchmark_data[result["name"]] = {
                    "execution_time": result.get("execution_time", 0.0),
                    "memory_usage_mb": result.get("memory_usage_mb", 0.0),
                    "success_rate": result.get("success_rate", 0.0),
                    "threshold_met": result.get("threshold_met", False)
                }
        
        return benchmark_data
    
    def compare_benchmarks(self, current_data: Dict[str, Dict[str, float]], 
                          baseline_data: Dict[str, Dict[str, float]]) -> List[BenchmarkComparison]:
        """Compare current benchmarks with baseline"""
        comparisons = []
        
        for benchmark_name in current_data:
            if benchmark_name not in baseline_data:
                print(f"⚠️ Benchmark {benchmark_name} not found in baseline")
                continue
            
            current = current_data[benchmark_name]
            baseline = baseline_data[benchmark_name]
            
            # Calculate time change
            time_change = 0.0
            if baseline["execution_time"] > 0:
                time_change = ((current["execution_time"] - baseline["execution_time"]) / 
                              baseline["execution_time"]) * 100
            
            # Calculate memory change
            memory_change = 0.0
            if baseline["memory_usage_mb"] > 0:
                memory_change = ((current["memory_usage_mb"] - baseline["memory_usage_mb"]) / 
                               baseline["memory_usage_mb"]) * 100
            
            # Determine regression/improvement status
            time_regression = time_change > (self.regression_threshold * 100)
            time_improvement = time_change < -(self.improvement_threshold * 100)
            memory_regression = memory_change > (self.memory_regression_threshold * 100)
            memory_improvement = memory_change < -(self.memory_improvement_threshold * 100)
            
            regression_detected = time_regression or memory_regression
            improvement_detected = time_improvement or memory_improvement
            
            if regression_detected:
                status = "regressed"
            elif improvement_detected:
                status = "improved"
            else:
                status = "stable"
            
            comparison = BenchmarkComparison(
                benchmark_name=benchmark_name,
                current_time=current["execution_time"],
                baseline_time=baseline["execution_time"],
                time_change_percent=time_change,
                current_memory=current["memory_usage_mb"],
                baseline_memory=baseline["memory_usage_mb"],
                memory_change_percent=memory_change,
                regression_detected=regression_detected,
                improvement_detected=improvement_detected,
                status=status
            )
            
            comparisons.append(comparison)
        
        return comparisons
    
    def generate_comparison_report(self, current_file: str, baseline_file: str) -> ComparisonReport:
        """Generate complete comparison report"""
        print(f"📊 Comparing benchmarks: {current_file} vs {baseline_file}")
        
        # Load benchmark data
        current_results = self.load_benchmark_results(current_file)
        baseline_results = self.load_benchmark_results(baseline_file)
        
        if not current_results or not baseline_results:
            print("❌ Cannot compare - missing benchmark data")
            return ComparisonReport(
                timestamp=datetime.now().isoformat(),
                current_file=current_file,
                baseline_file=baseline_file,
                total_benchmarks=0,
                regressions=0,
                improvements=0,
                stable=0,
                comparisons=[]
            )
        
        # Extract comparable data
        current_data = self.extract_benchmark_data(current_results)
        baseline_data = self.extract_benchmark_data(baseline_results)
        
        # Perform comparisons
        comparisons = self.compare_benchmarks(current_data, baseline_data)
        
        # Calculate summary statistics
        regressions = len([c for c in comparisons if c.status == "regressed"])
        improvements = len([c for c in comparisons if c.status == "improved"])
        stable = len([c for c in comparisons if c.status == "stable"])
        
        report = ComparisonReport(
            timestamp=datetime.now().isoformat(),
            current_file=current_file,
            baseline_file=baseline_file,
            total_benchmarks=len(comparisons),
            regressions=regressions,
            improvements=improvements,
            stable=stable,
            comparisons=comparisons
        )
        
        return report
    
    def print_comparison_report(self, report: ComparisonReport) -> None:
        """Print detailed comparison report"""
        print("\n" + "=" * 80)
        print("📈 BENCHMARK COMPARISON REPORT")
        print("=" * 80)
        
        print(f"Current Results: {report.current_file}")
        print(f"Baseline Results: {report.baseline_file}")
        print(f"Comparison Time: {report.timestamp}")
        print()
        
        print(f"📊 Summary:")
        print(f"   Total Benchmarks: {report.total_benchmarks}")
        print(f"   Regressions: {report.regressions} ({report.regression_rate:.1%})")
        print(f"   Improvements: {report.improvements} ({report.improvement_rate:.1%})")
        print(f"   Stable: {report.stable}")
        print()
        
        # Print detailed results
        print("📋 Detailed Results:")
        print("-" * 80)
        
        for comparison in report.comparisons:
            if comparison.status == "regressed":
                status_icon = "🔴"
            elif comparison.status == "improved":
                status_icon = "🟢"
            else:
                status_icon = "🟡"
            
            print(f"{status_icon} {comparison.benchmark_name}")
            print(f"   Time: {comparison.current_time:.3f}s → {comparison.baseline_time:.3f}s "
                  f"({comparison.time_change_percent:+.1f}%)")
            print(f"   Memory: {comparison.current_memory:.1f}MB → {comparison.baseline_memory:.1f}MB "
                  f"({comparison.memory_change_percent:+.1f}%)")
            
            if comparison.regression_detected:
                print(f"   ⚠️ REGRESSION DETECTED")
            elif comparison.improvement_detected:
                print(f"   ✨ IMPROVEMENT DETECTED")
            print()
        
        # Overall assessment
        if report.regressions > 0:
            print("🚨 PERFORMANCE REGRESSIONS DETECTED!")
            print(f"   {report.regressions} benchmark(s) show significant performance degradation")
        elif report.improvements > 0:
            print("🎉 PERFORMANCE IMPROVEMENTS DETECTED!")
            print(f"   {report.improvements} benchmark(s) show significant performance improvements")
        else:
            print("✅ PERFORMANCE STABLE")
            print("   No significant performance changes detected")
        
        print("=" * 80)
    
    def save_comparison_report(self, report: ComparisonReport, filepath: str) -> None:
        """Save comparison report to JSON file"""
        report_data = {
            "timestamp": report.timestamp,
            "current_file": report.current_file,
            "baseline_file": report.baseline_file,
            "summary": {
                "total_benchmarks": report.total_benchmarks,
                "regressions": report.regressions,
                "improvements": report.improvements,
                "stable": report.stable,
                "regression_rate": report.regression_rate,
                "improvement_rate": report.improvement_rate
            },
            "comparisons": [
                {
                    "benchmark_name": c.benchmark_name,
                    "current_time": c.current_time,
                    "baseline_time": c.baseline_time,
                    "time_change_percent": c.time_change_percent,
                    "current_memory": c.current_memory,
                    "baseline_memory": c.baseline_memory,
                    "memory_change_percent": c.memory_change_percent,
                    "regression_detected": c.regression_detected,
                    "improvement_detected": c.improvement_detected,
                    "status": c.status
                }
                for c in report.comparisons
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Comparison report saved to: {filepath}")
    
    def find_baseline_file(self, current_file: str) -> Optional[str]:
        """Find appropriate baseline file for comparison"""
        current_path = Path(current_file)
        
        # Look for baseline files in common locations
        baseline_candidates = [
            current_path.parent / "baseline_benchmark_results.json",
            current_path.parent / "previous_benchmark_results.json",
            Path("benchmarks") / "baseline_results.json",
            Path(".") / "baseline_benchmark_results.json"
        ]
        
        for candidate in baseline_candidates:
            if candidate.exists():
                return str(candidate)
        
        return None


def main():
    """Main comparison execution"""
    parser = argparse.ArgumentParser(description="Compare benchmark results")
    parser.add_argument("current_file", help="Current benchmark results file")
    parser.add_argument("--baseline", "-b", help="Baseline benchmark results file")
    parser.add_argument("--output", "-o", default="benchmark_comparison.json",
                       help="Output file for comparison report")
    parser.add_argument("--fail-on-regression", action="store_true",
                       help="Exit with error code if regressions detected")
    
    args = parser.parse_args()
    
    comparator = BenchmarkComparator()
    
    # Determine baseline file
    baseline_file = args.baseline
    if not baseline_file:
        baseline_file = comparator.find_baseline_file(args.current_file)
        if not baseline_file:
            print("❌ No baseline file found. Use --baseline to specify one.")
            return False
    
    # Generate comparison report
    report = comparator.generate_comparison_report(args.current_file, baseline_file)
    
    # Print and save report
    comparator.print_comparison_report(report)
    comparator.save_comparison_report(report, args.output)
    
    # Check for regressions
    if args.fail_on_regression and report.regressions > 0:
        print(f"\n❌ Exiting with error due to {report.regressions} regression(s)")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)