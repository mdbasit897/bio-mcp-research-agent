"""
Load testing for the biomedical research agent
"""
import pytest
import asyncio
import time
import json
import concurrent.futures
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import run_research_agent


class LoadTestConfig:
    """Configuration for load testing scenarios"""
    
    def __init__(self):
        self.scenarios = {
            "light_load": {
                "concurrent_users": 1,
                "requests_per_user": 5,
                "expected_max_time": 10
            },
            "moderate_load": {
                "concurrent_users": 5,
                "requests_per_user": 10,
                "expected_max_time": 30
            },
            "heavy_load": {
                "concurrent_users": 10,
                "requests_per_user": 20,
                "expected_max_time": 60
            },
            "stress_test": {
                "concurrent_users": 20,
                "requests_per_user": 30,
                "expected_max_time": 120
            }
        }


class LoadTestExecutor:
    """Load test executor utility"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = []
    
    async def execute_user_task(self, user_id: int, task_id: int) -> Dict:
        """Execute a single user task"""
        start_time = time.time()
        
        try:
            with patch('agent.client') as mock_client, \
                 patch('agent.stdio_client') as mock_stdio, \
                 patch('agent.ClientSession') as mock_session_class, \
                 patch('agent.os.makedirs') as mock_makedirs:
                
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = f"User {user_id}, Task {task_id}"
                mock_response.choices[0].message.tool_calls = None
                mock_client.chat.completions.create.return_value = mock_response
                
                mock_session = Mock()
                mock_session.initialize = AsyncMock()
                mock_session_class.return_value = mock_session
                
                await run_research_agent(f"load test user {user_id} task {task_id}")
                
                end_time = time.time()
                return {
                    "user_id": user_id,
                    "task_id": task_id,
                    "success": True,
                    "execution_time": end_time - start_time,
                    "error": None
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                "user_id": user_id,
                "task_id": task_id,
                "success": False,
                "execution_time": end_time - start_time,
                "error": str(e)
            }
    
    async def execute_user_scenario(self, user_id: int, scenario_name: str) -> List[Dict]:
        """Execute all tasks for a single user"""
        config = self.config.scenarios[scenario_name]
        tasks = []
        
        for task_id in range(config["requests_per_user"]):
            task = asyncio.create_task(self.execute_user_task(user_id, task_id))
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
    
    async def run_load_test(self, scenario_name: str) -> Dict:
        """Run a complete load test scenario"""
        config = self.config.scenarios[scenario_name]
        self.results = []
        
        print(f"Starting {scenario_name} load test with {config['concurrent_users']} users, "
              f"{config['requests_per_user']} requests each")
        
        start_time = time.time()
        
        # Create tasks for all concurrent users
        user_tasks = []
        for user_id in range(config["concurrent_users"]):
            task = asyncio.create_task(
                self.execute_user_scenario(user_id, scenario_name)
            )
            user_tasks.append(task)
        
        # Wait for all users to complete
        all_results = await asyncio.gather(*user_tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Flatten results
        self.results = []
        for user_results in all_results:
            self.results.extend(user_results)
        
        # Calculate metrics
        successful_tasks = [r for r in self.results if r["success"]]
        failed_tasks = [r for r in self.results if not r["success"]]
        
        execution_times = [r["execution_time"] for r in successful_tasks]
        
        metrics = {
            "scenario": scenario_name,
            "total_tasks": len(self.results),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(successful_tasks) / len(self.results) if self.results else 0,
            "total_time": total_time,
            "avg_task_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "max_task_time": max(execution_times) if execution_times else 0,
            "min_task_time": min(execution_times) if execution_times else 0,
            "requests_per_second": len(successful_tasks) / total_time if total_time > 0 else 0,
            "config": config
        }
        
        print(f"Completed {scenario_name}: {metrics['success_rate']:.1%} success rate, "
              f"{metrics['requests_per_second']:.1f} req/s")
        
        return metrics


class TestLoadTesting:
    """Load testing for the research agent"""

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_light_load_scenario(self):
        """Test light load scenario"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        metrics = await executor.run_load_test("light_load")
        
        # Validate light load performance
        assert metrics["success_rate"] >= 0.95  # 95% success rate
        assert metrics["total_time"] < metrics["config"]["expected_max_time"]
        assert metrics["avg_task_time"] < 5.0  # Average task time < 5 seconds
        assert metrics["requests_per_second"] > 0.5

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_moderate_load_scenario(self):
        """Test moderate load scenario"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        metrics = await executor.run_load_test("moderate_load")
        
        # Validate moderate load performance
        assert metrics["success_rate"] >= 0.90  # 90% success rate
        assert metrics["total_time"] < metrics["config"]["expected_max_time"]
        assert metrics["avg_task_time"] < 8.0  # Average task time < 8 seconds
        assert metrics["requests_per_second"] > 1.5

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_heavy_load_scenario(self):
        """Test heavy load scenario"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        metrics = await executor.run_load_test("heavy_load")
        
        # Validate heavy load performance
        assert metrics["success_rate"] >= 0.80  # 80% success rate
        assert metrics["total_time"] < metrics["config"]["expected_max_time"]
        assert metrics["avg_task_time"] < 10.0  # Average task time < 10 seconds
        assert metrics["requests_per_second"] > 3.0

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_stress_test_scenario(self):
        """Test stress scenario (system limits)"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        metrics = await executor.run_load_test("stress_test")
        
        # Validate stress test results
        # Stress tests may have lower success rates due to system limits
        assert metrics["success_rate"] >= 0.60  # 60% success rate minimum
        assert metrics["total_time"] < metrics["config"]["expected_max_time"]
        # Monitor system behavior under stress

    @pytest.mark.performance
    async def test_concurrent_user_behavior(self):
        """Test behavior with concurrent users"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # Test with moderate concurrent users
        metrics = await executor.run_load_test("moderate_load")
        
        # Validate concurrent user handling
        assert metrics["success_rate"] >= 0.90
        
        # Check that tasks are distributed reasonably
        execution_times = [r["execution_time"] for r in self.results if r["success"]]
        time_variance = max(execution_times) - min(execution_times)
        
        # Time variance shouldn't be too extreme
        assert time_variance < 15.0  # No more than 15 seconds difference between fastest and slowest

    @pytest.mark.performance
    async def test_memory_under_load(self):
        """Test memory usage under load"""
        import psutil
        
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Run moderate load test
        metrics = await executor.run_load_test("moderate_load")
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Validate memory behavior under load
        assert memory_increase < 100  # Memory increase should be reasonable
        assert metrics["success_rate"] >= 0.90

    @pytest.mark.performance
    async def test_error_handling_under_load(self):
        """Test error handling under load conditions"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # Run heavy load test to trigger potential errors
        metrics = await executor.run_load_test("heavy_load")
        
        # Analyze error patterns
        failed_tasks = [r for r in self.results if not r["success"]]
        
        if failed_tasks:
            # Log error patterns for analysis
            error_types = {}
            for task in failed_tasks:
                error_type = task["error"].split(":")[0] if ":" in task["error"] else task["error"]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print(f"Error types under load: {error_types}")
            
            # Ensure errors are not concentrated on specific users/tasks
            user_error_counts = {}
            for task in failed_tasks:
                user_id = task["user_id"]
                user_error_counts[user_id] = user_error_counts.get(user_id, 0) + 1
            
            max_user_errors = max(user_error_counts.values()) if user_error_counts else 0
            total_users = config.scenarios["heavy_load"]["concurrent_users"]
            
            # No single user should have more than 50% of errors
            assert max_user_errors <= (len(failed_tasks) * 0.5)


class TestLoadTestScalability:
    """Test scalability of the research agent under load"""

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_scalability_analysis(self):
        """Test how the system scales with increasing load"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        scalability_results = []
        
        # Test different load levels
        for scenario_name in ["light_load", "moderate_load", "heavy_load"]:
            metrics = await executor.run_load_test(scenario_name)
            scalability_results.append(metrics)
        
        # Analyze scalability
        light_metrics = next(m for m in scalability_results if m["scenario"] == "light_load")
        moderate_metrics = next(m for m in scalability_results if m["scenario"] == "moderate_load")
        heavy_metrics = next(m for m in scalability_results if m["scenario"] == "heavy_load")
        
        # Calculate scalability ratios
        light_to_moderate_ratio = moderate_metrics["requests_per_second"] / light_metrics["requests_per_second"]
        moderate_to_heavy_ratio = heavy_metrics["requests_per_second"] / moderate_metrics["requests_per_second"]
        
        # Validate scalability (should be somewhat linear, not perfect)
        assert light_to_moderate_ratio >= 0.5  # At least 50% scaling efficiency
        assert moderate_to_heavy_ratio >= 0.3  # At least 30% scaling efficiency
        
        # Success rate should not degrade too much
        assert heavy_metrics["success_rate"] >= 0.80

    @pytest.mark.performance
    @pytest.mark.slow
    async def test_bottleneck_identification(self):
        """Test identification of performance bottlenecks"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # Run stress test to identify bottlenecks
        metrics = await executor.run_load_test("stress_test")
        
        # Analyze performance characteristics
        successful_tasks = [r for r in self.results if r["success"]]
        execution_times = [r["execution_time"] for r in successful_tasks]
        
        # Calculate performance percentiles
        sorted_times = sorted(execution_times)
        p50 = sorted_times[int(len(sorted_times) * 0.5)]
        p90 = sorted_times[int(len(sorted_times) * 0.9)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        
        # Identify potential bottlenecks
        bottlenecks = []
        
        if p95 > p50 * 2:
            bottlenecks.append("High variance in task completion times")
        
        if metrics["avg_task_time"] > 10:
            bottlenecks.append("High average task time")
        
        if metrics["requests_per_second"] < 2:
            bottlenecks.append("Low request throughput")
        
        print(f"Potential bottlenecks identified: {bottlenecks}")
        
        # Ensure system is still functional despite bottlenecks
        assert metrics["success_rate"] >= 0.60


class TestLoadTestResilience:
    """Test resilience under various load conditions"""

    @pytest.mark.performance
    async def test_load_balancing_simulation(self):
        """Test load balancing simulation"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # Simulate uneven load distribution
        uneven_users = [1, 1, 1, 2, 2, 3, 3, 3, 3]  # User 1: 2 tasks, User 2: 2 tasks, User 3: 5 tasks
        
        results = []
        for user_id in uneven_users:
            for task_id in range(1):  # Single task per uneven request
                result = await executor.execute_user_task(user_id, task_id)
                results.append(result)
        
        # Analyze load distribution
        user_task_counts = {}
        for result in results:
            user_id = result["user_id"]
            user_task_counts[user_id] = user_task_counts.get(user_id, 0) + 1
        
        print(f"Uneven load distribution: {user_task_counts}")
        
        # Ensure all users can complete their tasks
        assert all(result["success"] for result in results)

    @pytest.mark.performance
    async def test_recovery_after_load_spike(self):
        """Test system recovery after load spikes"""
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # First, run a heavy load test
        print("Running initial heavy load...")
        initial_metrics = await executor.run_load_test("heavy_load")
        
        # Then run a light load test to see if system has recovered
        print("Testing recovery with light load...")
        recovery_metrics = await executor.run_load_test("light_load")
        
        # Compare performance
        initial_rps = initial_metrics["requests_per_second"]
        recovery_rps = recovery_metrics["requests_per_second"]
        
        # System should recover to good performance
        assert recovery_rps >= initial_rps * 1.2  # Recovery should be at least 20% better than initial
        assert recovery_metrics["success_rate"] >= 0.95

    @pytest.mark.performance
    async def test_memory_leak_detection(self):
        """Test memory leak detection under load"""
        import psutil
        
        config = LoadTestConfig()
        executor = LoadTestExecutor(config)
        
        # Monitor memory over multiple load cycles
        memory_snapshots = []
        
        for cycle in range(3):
            # Record memory before load test
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Run load test
            metrics = await executor.run_load_test("moderate_load")
            
            # Record memory after load test
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            memory_snapshots.append({
                "cycle": cycle + 1,
                "initial_memory": initial_memory,
                "final_memory": final_memory,
                "memory_increase": memory_increase,
                "success_rate": metrics["success_rate"]
            })
            
            # Force garbage collection between cycles
            import gc
            gc.collect()
            
            # Wait a bit for memory to settle
            await asyncio.sleep(1)
        
        # Analyze memory trends
        memory_increases = [snapshot["memory_increase"] for snapshot in memory_snapshots]
        
        # Check for memory leaks (memory should not grow continuously)
        avg_increase = sum(memory_increases) / len(memory_increases)
        max_increase = max(memory_increases)
        
        print(f"Memory increases per cycle: {memory_increases}")
        print(f"Average increase: {avg_increase:.1f}MB, Max increase: {max_increase:.1f}MB")
        
        # Memory growth should be minimal
        assert max_increase < 50  # Less than 50MB increase per cycle
        assert avg_increase < 20  # Average less than 20MB per cycle