"""
Analytics and insights module for MCP Atlassian.

This module provides enterprise-grade analytics capabilities for the MCP Atlassian
integration, including cross-product analytics, time tracking analysis,
issue patterns and trends detection, and custom report generation.
"""

import os
import json
import re
import math
import logging
import tempfile
import datetime
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from collections import Counter, defaultdict

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from .auth import with_auth_client, AuthenticatedClient

# Configure logging
logger = logging.getLogger("mcp-atlassian.analytics")


class AnalyticsManager:
    """
    Provides enterprise-grade analytics and insights across Atlassian products.
    
    Includes capabilities for time tracking analysis, issue patterns detection,
    trend identification, and custom report generation.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the AnalyticsManager.
        
        Args:
            data_dir: Directory to store cached data and generated reports
        """
        # Create a directory for cached data and reports
        if data_dir:
            self.data_dir = data_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.data_dir = os.path.join(base_dir, "data", "analytics")
            
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cached data
        self._issue_cache = {}
        self._time_tracking_cache = {}
        
    @with_auth_client("jira")
    def get_project_metrics(self, client: AuthenticatedClient, project_key: str) -> Dict:
        """
        Get comprehensive metrics for a Jira project.
        
        Args:
            client: Authenticated client
            project_key: Project key to analyze
            
        Returns:
            Dict containing project metrics
        """
        # Get all issues in the project
        issues = self._get_all_project_issues(client, project_key)
        
        # Calculate metrics
        issue_types = Counter(issue.get("fields", {}).get("issuetype", {}).get("name", "Unknown") 
                             for issue in issues)
        
        statuses = Counter(issue.get("fields", {}).get("status", {}).get("name", "Unknown") 
                          for issue in issues)
        
        priorities = Counter(issue.get("fields", {}).get("priority", {}).get("name", "Unknown") 
                            for issue in issues)
        
        # Calculate creation velocity (issues per week)
        created_dates = [datetime.datetime.strptime(
                            issue.get("fields", {}).get("created", "2023-01-01T00:00:00.000+0000"),
                            "%Y-%m-%dT%H:%M:%S.%f%z"
                         ).date() 
                         for issue in issues]
        
        if created_dates:
            min_date = min(created_dates)
            max_date = max(created_dates)
            date_range = (max_date - min_date).days
            if date_range > 0:
                velocity_per_week = len(issues) / (date_range / 7)
            else:
                velocity_per_week = len(issues)
        else:
            velocity_per_week = 0
            
        # Calculate resolution time statistics (in days)
        resolution_times = []
        for issue in issues:
            created = issue.get("fields", {}).get("created")
            resolved = issue.get("fields", {}).get("resolutiondate")
            
            if created and resolved:
                created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f%z")
                resolved_date = datetime.datetime.strptime(resolved, "%Y-%m-%dT%H:%M:%S.%f%z")
                resolution_time = (resolved_date - created_date).total_seconds() / (24 * 3600)  # days
                resolution_times.append(resolution_time)
                
        if resolution_times:
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
            median_resolution_time = sorted(resolution_times)[len(resolution_times) // 2]
            p90_resolution_time = sorted(resolution_times)[int(len(resolution_times) * 0.9)]
        else:
            avg_resolution_time = 0
            median_resolution_time = 0
            p90_resolution_time = 0
            
        # Calculate completion rate
        completed_issues = sum(1 for issue in issues 
                             if issue.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key") == "done")
        completion_rate = completed_issues / len(issues) if issues else 0
        
        return {
            "project_key": project_key,
            "total_issues": len(issues),
            "issue_types": dict(issue_types),
            "statuses": dict(statuses),
            "priorities": dict(priorities),
            "velocity_per_week": round(velocity_per_week, 2),
            "resolution_time": {
                "average": round(avg_resolution_time, 2),
                "median": round(median_resolution_time, 2),
                "p90": round(p90_resolution_time, 2),
            },
            "completion_rate": round(completion_rate * 100, 2),
        }
        
    @with_auth_client("jira")    
    def analyze_time_tracking(self, client: AuthenticatedClient, project_key: str) -> Dict:
        """
        Analyze time tracking data for a project.
        
        Args:
            client: Authenticated client
            project_key: Project key to analyze
            
        Returns:
            Dict containing time tracking analysis
        """
        # Get all issues with time tracking information
        jql = f"project = {project_key} AND worklog IS NOT EMPTY"
        response = client.request(
            "GET", 
            f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
            params={
                "jql": jql,
                "maxResults": 1000,
                "fields": "summary,issuetype,created,timetracking,worklog,assignee"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch time tracking data: {response.text}")
            return {"error": "Failed to fetch time tracking data"}
            
        issues = response.json().get("issues", [])
        
        # Process worklog data
        time_by_user = defaultdict(int)
        time_by_issue_type = defaultdict(int)
        time_by_day = defaultdict(int)
        time_by_week = defaultdict(int)
        total_estimated = 0
        total_logged = 0
        estimation_accuracy = []
        
        for issue in issues:
            issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "Unknown")
            
            # Get original estimate and logged time
            time_tracking = issue.get("fields", {}).get("timetracking", {})
            original_estimate_seconds = time_tracking.get("originalEstimateSeconds", 0) or 0
            time_spent_seconds = time_tracking.get("timeSpentSeconds", 0) or 0
            
            total_estimated += original_estimate_seconds
            total_logged += time_spent_seconds
            
            # Calculate estimation accuracy if both values exist
            if original_estimate_seconds > 0 and time_spent_seconds > 0:
                accuracy = time_spent_seconds / original_estimate_seconds
                estimation_accuracy.append({
                    "issue_key": issue.get("key"),
                    "original_estimate": original_estimate_seconds,
                    "time_spent": time_spent_seconds,
                    "accuracy": accuracy
                })
                
            # Aggregate time by issue type
            time_by_issue_type[issue_type] += time_spent_seconds
            
            # Process individual worklog entries
            worklogs = issue.get("fields", {}).get("worklog", {}).get("worklogs", [])
            for worklog in worklogs:
                # Aggregate time by user
                author = worklog.get("author", {}).get("displayName", "Unknown")
                time_spent = worklog.get("timeSpentSeconds", 0)
                time_by_user[author] += time_spent
                
                # Aggregate time by day and week
                started = worklog.get("started", "")
                if started:
                    started_date = datetime.datetime.strptime(started, "%Y-%m-%dT%H:%M:%S.%f%z").date()
                    day_key = started_date.isoformat()
                    week_key = f"{started_date.year}-W{started_date.strftime('%U')}"
                    
                    time_by_day[day_key] += time_spent
                    time_by_week[week_key] += time_spent
        
        # Calculate efficiency metrics
        if total_estimated > 0:
            overall_accuracy = total_logged / total_estimated
        else:
            overall_accuracy = 0
            
        # Convert seconds to hours for all metrics
        time_by_user = {user: time / 3600 for user, time in time_by_user.items()}
        time_by_issue_type = {itype: time / 3600 for itype, time in time_by_issue_type.items()}
        time_by_day = {day: time / 3600 for day, time in time_by_day.items()}
        time_by_week = {week: time / 3600 for week, time in time_by_week.items()}
        
        for item in estimation_accuracy:
            item["original_estimate"] = item["original_estimate"] / 3600
            item["time_spent"] = item["time_spent"] / 3600
            
        # Sort time by day and week chronologically
        time_by_day = dict(sorted(time_by_day.items()))
        time_by_week = dict(sorted(time_by_week.items()))
        
        # Generate insights
        insights = []
        
        # Insight: Overestimation/underestimation pattern
        if estimation_accuracy:
            avg_accuracy = sum(item["accuracy"] for item in estimation_accuracy) / len(estimation_accuracy)
            if avg_accuracy > 1.2:
                insights.append("Tasks are consistently underestimated. Consider adding buffer to estimates.")
            elif avg_accuracy < 0.8:
                insights.append("Tasks are consistently overestimated. Consider reducing estimates for efficiency.")
        
        # Insight: Time distribution
        if time_by_user:
            max_user = max(time_by_user.items(), key=lambda x: x[1])
            total_time = sum(time_by_user.values())
            if max_user[1] / total_time > 0.5:
                insights.append(f"{max_user[0]} is handling more than 50% of the workload. Consider redistributing tasks.")
        
        # Insight: Work pattern
        if time_by_day:
            days = list(time_by_day.keys())
            if len(days) >= 5:
                last_five_days = days[-5:]
                last_five_values = [time_by_day[day] for day in last_five_days]
                if all(v > 1.2 * (sum(last_five_values) / len(last_five_values)) for v in last_five_values[-2:]):
                    insights.append("Work intensity has increased significantly in the last two days. Check for potential burnout.")
        
        # Insight: Weekly pattern
        if time_by_week and len(time_by_week) >= 4:
            weeks = list(time_by_week.keys())
            last_four_weeks = weeks[-4:]
            last_four_values = [time_by_week[week] for week in last_four_weeks]
            trend = sum(last_four_values[i+1] - last_four_values[i] for i in range(3)) / 3
            if trend > 5:
                insights.append("Weekly workload is consistently increasing. Consider capacity planning.")
            elif trend < -5:
                insights.append("Weekly workload is decreasing. Check if project momentum is being maintained.")
        
        return {
            "project_key": project_key,
            "total_issues_with_time_tracking": len(issues),
            "total_time_estimated_hours": round(total_estimated / 3600, 2),
            "total_time_logged_hours": round(total_logged / 3600, 2),
            "overall_estimation_accuracy": round(overall_accuracy, 2),
            "time_by_user": {user: round(hours, 2) for user, hours in time_by_user.items()},
            "time_by_issue_type": {itype: round(hours, 2) for itype, hours in time_by_issue_type.items()},
            "time_by_day": {day: round(hours, 2) for day, hours in time_by_day.items()},
            "time_by_week": {week: round(hours, 2) for week, hours in time_by_week.items()},
            "estimation_accuracy_details": estimation_accuracy,
            "insights": insights
        }
        
    @with_auth_client("jira")
    def detect_issue_patterns(self, client: AuthenticatedClient, project_key: str) -> Dict:
        """
        Detect patterns in issues using clustering and statistical analysis.
        
        Args:
            client: Authenticated client
            project_key: Project key to analyze
            
        Returns:
            Dict containing issue patterns and insights
        """
        # Get all issues with extended fields
        issues = self._get_all_project_issues(client, project_key, fields=[
            "summary", "description", "issuetype", "status", "priority", 
            "assignee", "reporter", "created", "updated", "resolutiondate",
            "comment", "labels", "components", "timetracking", "duedate"
        ])
        
        if not issues:
            return {"error": "No issues found for pattern analysis"}
            
        # Extract features for pattern analysis
        issue_data = []
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Calculate cycle time (resolution time) in days
            created = fields.get("created")
            resolved = fields.get("resolutiondate")
            cycle_time = None
            
            if created and resolved:
                created_date = datetime.datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%f%z")
                resolved_date = datetime.datetime.strptime(resolved, "%Y-%m-%dT%H:%M:%S.%f%z")
                cycle_time = (resolved_date - created_date).total_seconds() / (24 * 3600)  # days
            
            # Calculate comment count
            comments = fields.get("comment", {}).get("comments", [])
            comment_count = len(comments)
            
            # Calculate word count in description
            description = fields.get("description") or ""
            word_count = len(re.findall(r'\w+', description)) if description else 0
            
            # Get time tracking data
            time_tracking = fields.get("timetracking", {})
            original_estimate = time_tracking.get("originalEstimateSeconds", 0) or 0
            time_spent = time_tracking.get("timeSpentSeconds", 0) or 0
            
            # Extract assignee and reporter
            assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
            reporter = fields.get("reporter", {}).get("displayName", "Unknown")
            
            # Get priority level
            priority = fields.get("priority", {}).get("name", "Medium")
            priority_map = {"Highest": 5, "High": 4, "Medium": 3, "Low": 2, "Lowest": 1}
            priority_value = priority_map.get(priority, 3)
            
            # Count labels
            labels = fields.get("labels", [])
            label_count = len(labels)
            
            # Count components
            components = fields.get("components", [])
            component_count = len(components)
            
            # Get issue type
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            
            # Create feature row
            row = {
                "key": issue.get("key"),
                "issue_type": issue_type,
                "priority": priority_value,
                "comment_count": comment_count,
                "word_count": word_count,
                "label_count": label_count,
                "component_count": component_count,
                "original_estimate": original_estimate / 3600 if original_estimate else 0,  # hours
                "time_spent": time_spent / 3600 if time_spent else 0,  # hours
                "cycle_time": cycle_time if cycle_time is not None else 0,
                "assignee": assignee,
                "reporter": reporter
            }
            
            issue_data.append(row)
            
        # Convert to DataFrame
        if not issue_data:
            return {"error": "Failed to extract issue features for pattern analysis"}
            
        df = pd.DataFrame(issue_data)
        
        # Group by assignee and issue type to find specialization patterns
        assignee_specialization = df.groupby(['assignee', 'issue_type']).size().reset_index(name='count')
        assignee_specialization = assignee_specialization.sort_values(['assignee', 'count'], ascending=[True, False])
        
        primary_issue_types = {}
        for assignee in df['assignee'].unique():
            if assignee == "Unassigned":
                continue
                
            assignee_issues = assignee_specialization[assignee_specialization['assignee'] == assignee]
            if not assignee_issues.empty:
                top_issue = assignee_issues.iloc[0]
                total_issues = df[df['assignee'] == assignee].shape[0]
                if total_issues > 0:
                    specialization_ratio = top_issue['count'] / total_issues
                    if specialization_ratio > 0.6:  # 60% or more of one type
                        primary_issue_types[assignee] = {
                            "issue_type": top_issue['issue_type'],
                            "count": int(top_issue['count']),
                            "total": total_issues,
                            "specialization_ratio": round(specialization_ratio, 2)
                        }
        
        # Find cycle time patterns by issue type
        cycle_time_by_type = df[df['cycle_time'] > 0].groupby('issue_type')['cycle_time'].agg(['mean', 'median', 'count']).reset_index()
        cycle_time_by_type = cycle_time_by_type[cycle_time_by_type['count'] >= 5]  # Only include types with enough samples
        cycle_time_by_type = cycle_time_by_type.sort_values('mean', ascending=False)
        
        # Identify outliers in cycle time
        outliers = []
        for issue_type in cycle_time_by_type['issue_type'].unique():
            type_df = df[(df['issue_type'] == issue_type) & (df['cycle_time'] > 0)]
            if len(type_df) >= 5:  # Need enough data for meaningful analysis
                mean = type_df['cycle_time'].mean()
                std = type_df['cycle_time'].std()
                
                # Find outliers (> 2 standard deviations from mean)
                if std > 0:
                    for _, row in type_df[type_df['cycle_time'] > mean + 2*std].iterrows():
                        outliers.append({
                            "key": row['key'],
                            "issue_type": issue_type,
                            "cycle_time": round(float(row['cycle_time']), 2),
                            "average_for_type": round(float(mean), 2),
                            "standard_deviation": round(float(std), 2),
                            "z_score": round(float((row['cycle_time'] - mean) / std), 2)
                        })
        
        # Identify estimation accuracy patterns
        estimation_patterns = []
        estimate_df = df[(df['original_estimate'] > 0) & (df['time_spent'] > 0)]
        
        if not estimate_df.empty:
            estimate_df['accuracy_ratio'] = estimate_df['time_spent'] / estimate_df['original_estimate']
            
            # Group by issue type
            accuracy_by_type = estimate_df.groupby('issue_type')['accuracy_ratio'].agg(['mean', 'count']).reset_index()
            accuracy_by_type = accuracy_by_type[accuracy_by_type['count'] >= 3]  # Only include types with enough samples
            
            for _, row in accuracy_by_type.iterrows():
                pattern_type = "accurate"
                if row['mean'] > 1.3:
                    pattern_type = "underestimated"
                elif row['mean'] < 0.7:
                    pattern_type = "overestimated"
                    
                if pattern_type != "accurate":
                    estimation_patterns.append({
                        "issue_type": row['issue_type'],
                        "pattern": pattern_type,
                        "average_ratio": round(float(row['mean']), 2),
                        "sample_size": int(row['count'])
                    })
        
        # Try to perform clustering if we have enough numerical data
        clustering_results = {}
        if len(df) >= 10:
            try:
                # Select numerical features for clustering
                features = ['comment_count', 'word_count', 'priority', 'cycle_time',
                           'original_estimate', 'time_spent', 'label_count', 'component_count']
                
                # Filter to only include rows with valid cycle times
                cluster_df = df[df['cycle_time'] > 0].copy()
                
                if len(cluster_df) >= 10:
                    # Handle NaN values
                    for feature in features:
                        if feature in cluster_df.columns:
                            cluster_df[feature] = cluster_df[feature].fillna(0)
                    
                    # Normalize the data
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(cluster_df[features])
                    
                    # Determine optimal number of clusters (using simplified method)
                    max_clusters = min(6, len(cluster_df) // 5)  # Limit max clusters based on data size
                    wcss = []
                    for i in range(1, max_clusters + 1):
                        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
                        kmeans.fit(scaled_data)
                        wcss.append(kmeans.inertia_)
                    
                    # Simple elbow method - identify largest drop in WCSS
                    drops = [wcss[i] - wcss[i+1] for i in range(len(wcss)-1)]
                    if drops:
                        optimal_k = drops.index(max(drops)) + 2  # +2 because we start from 1 and need to offset the index
                    else:
                        optimal_k = 2
                    
                    # Apply KMeans with optimal k
                    kmeans = KMeans(n_clusters=optimal_k, init='k-means++', max_iter=300, n_init=10, random_state=42)
                    kmeans.fit(scaled_data)
                    cluster_labels = kmeans.labels_
                    
                    # Add cluster labels to dataframe
                    cluster_df['cluster'] = cluster_labels
                    
                    # Analyze clusters
                    cluster_insights = []
                    for cluster_id in range(optimal_k):
                        cluster_data = cluster_df[cluster_df['cluster'] == cluster_id]
                        
                        # Skip tiny clusters
                        if len(cluster_data) < 3:
                            continue
                        
                        # Calculate cluster statistics
                        common_issue_types = cluster_data['issue_type'].value_counts().head(2).to_dict()
                        avg_cycle_time = cluster_data['cycle_time'].mean()
                        avg_comment_count = cluster_data['comment_count'].mean()
                        avg_word_count = cluster_data['word_count'].mean()
                        
                        cluster_insights.append({
                            "cluster_id": int(cluster_id),
                            "size": int(len(cluster_data)),
                            "percentage": round(len(cluster_data) / len(cluster_df) * 100, 1),
                            "common_issue_types": {k: int(v) for k, v in common_issue_types.items()},
                            "avg_cycle_time": round(float(avg_cycle_time), 2),
                            "avg_comment_count": round(float(avg_comment_count), 2),
                            "avg_word_count": round(float(avg_word_count), 2),
                            "sample_issues": cluster_data['key'].head(5).tolist()
                        })
                    
                    # Generate cluster interpretations
                    for insight in cluster_insights:
                        characteristics = []
                        
                        # Interpret cycle time
                        overall_avg_cycle_time = df[df['cycle_time'] > 0]['cycle_time'].mean()
                        cycle_time_ratio = insight['avg_cycle_time'] / overall_avg_cycle_time if overall_avg_cycle_time else 1
                        
                        if cycle_time_ratio > 1.5:
                            characteristics.append("long cycle time")
                        elif cycle_time_ratio < 0.7:
                            characteristics.append("quick resolution")
                            
                        # Interpret comment count
                        overall_avg_comments = df['comment_count'].mean()
                        if overall_avg_comments > 0:
                            comment_ratio = insight['avg_comment_count'] / overall_avg_comments
                            if comment_ratio > 1.5:
                                characteristics.append("high discussion volume")
                            elif comment_ratio < 0.7:
                                characteristics.append("minimal discussion")
                                
                        # Interpret description length
                        overall_avg_words = df['word_count'].mean()
                        if overall_avg_words > 0:
                            word_ratio = insight['avg_word_count'] / overall_avg_words
                            if word_ratio > 1.5:
                                characteristics.append("detailed descriptions")
                            elif word_ratio < 0.7:
                                characteristics.append("brief descriptions")
                                
                        # Add a summary interpretation
                        if characteristics:
                            insight["interpretation"] = f"Issues with {', '.join(characteristics)}"
                        else:
                            insight["interpretation"] = "No distinctive characteristics identified"
                    
                    clustering_results = {
                        "method": "KMeans",
                        "num_clusters": optimal_k,
                        "insights": cluster_insights
                    }
            except Exception as e:
                logger.error(f"Clustering analysis failed: {str(e)}")
                clustering_results = {"error": str(e)}
        
        return {
            "project_key": project_key,
            "total_issues_analyzed": len(df),
            "assignee_specialization": primary_issue_types,
            "cycle_time_outliers": outliers,
            "estimation_patterns": estimation_patterns,
            "clustering_analysis": clustering_results,
            "cycle_time_by_type": cycle_time_by_type.to_dict(orient='records') if not cycle_time_by_type.empty else []
        }
        
    @with_auth_client("jira")
    def generate_trend_report(self, client: AuthenticatedClient, project_key: str, time_range: str = "6m") -> Dict:
        """
        Generate a trend report showing how metrics have changed over time.
        
        Args:
            client: Authenticated client
            project_key: Project key to analyze
            time_range: Time range to analyze (e.g., "1w", "1m", "3m", "6m", "1y")
            
        Returns:
            Dict containing trend analysis
        """
        # Parse time range
        range_value = int(time_range[:-1])
        range_unit = time_range[-1]
        
        if range_unit == "w":
            start_date = datetime.datetime.now() - datetime.timedelta(weeks=range_value)
        elif range_unit == "m":
            start_date = datetime.datetime.now() - datetime.timedelta(days=range_value * 30)
        elif range_unit == "y":
            start_date = datetime.datetime.now() - datetime.timedelta(days=range_value * 365)
        else:
            return {"error": "Invalid time range format. Use format like '1w', '1m', '6m', '1y'"}
            
        jql = f"project = {project_key} AND created >= '{start_date.strftime('%Y-%m-%d')}'"
        response = client.request(
            "GET", 
            f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
            params={
                "jql": jql,
                "maxResults": 1000,
                "fields": "summary,issuetype,created,updated,status,priority,assignee,resolutiondate"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch trend data: {response.text}")
            return {"error": "Failed to fetch trend data"}
            
        issues = response.json().get("issues", [])
        if not issues:
            return {"message": "No issues found in the specified time range"}
            
        # Convert dates to datetime objects
        for issue in issues:
            fields = issue.get("fields", {})
            if "created" in fields:
                fields["created_date"] = datetime.datetime.strptime(
                    fields["created"], 
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                ).replace(tzinfo=None)
            if "resolutiondate" in fields and fields["resolutiondate"]:
                fields["resolved_date"] = datetime.datetime.strptime(
                    fields["resolutiondate"], 
                    "%Y-%m-%dT%H:%M:%S.%f%z"
                ).replace(tzinfo=None)
                
        # Determine appropriate time buckets based on range
        if range_unit == "w" or (range_unit == "m" and range_value <= 1):
            # For short ranges, use days
            bucket_unit = "day"
            bucket_format = "%Y-%m-%d"
            
            # Create date buckets
            start_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date_buckets = []
            
            current = start_day
            while current <= end_day:
                date_buckets.append(current)
                current += datetime.timedelta(days=1)
        elif range_unit == "m" and range_value <= 3:
            # For medium ranges, use weeks
            bucket_unit = "week"
            bucket_format = "%Y-W%U"
            
            # Create week buckets
            start_week = start_date - datetime.timedelta(days=start_date.weekday())  # First day of the week
            start_week = start_week.replace(hour=0, minute=0, second=0, microsecond=0)
            end_week = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())
            end_week = end_week.replace(hour=0, minute=0, second=0, microsecond=0)
            date_buckets = []
            
            current = start_week
            while current <= end_week:
                date_buckets.append(current)
                current += datetime.timedelta(weeks=1)
        else:
            # For long ranges, use months
            bucket_unit = "month"
            bucket_format = "%Y-%m"
            
            # Create month buckets
            start_month = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_month = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            date_buckets = []
            
            current = start_month
            while current <= end_month:
                date_buckets.append(current)
                
                # Move to next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        
        # Initialize data structures for trend analysis
        created_by_bucket = {bucket.strftime(bucket_format): 0 for bucket in date_buckets}
        resolved_by_bucket = {bucket.strftime(bucket_format): 0 for bucket in date_buckets}
        created_by_type = {}
        status_counts_by_bucket = {}
        
        # Process issues
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Count created issues by bucket
            if "created_date" in fields:
                bucket_key = fields["created_date"].strftime(bucket_format)
                created_by_bucket[bucket_key] = created_by_bucket.get(bucket_key, 0) + 1
                
                # Count by issue type
                issue_type = fields.get("issuetype", {}).get("name", "Unknown")
                if issue_type not in created_by_type:
                    created_by_type[issue_type] = {bucket.strftime(bucket_format): 0 for bucket in date_buckets}
                created_by_type[issue_type][bucket_key] = created_by_type[issue_type].get(bucket_key, 0) + 1
            
            # Count resolved issues by bucket
            if "resolved_date" in fields:
                bucket_key = fields["resolved_date"].strftime(bucket_format)
                resolved_by_bucket[bucket_key] = resolved_by_bucket.get(bucket_key, 0) + 1
        
        # Status distribution over time
        status_counts = {}
        for bucket in date_buckets:
            bucket_key = bucket.strftime(bucket_format)
            status_counts[bucket_key] = {}
            
            # Calculate status distribution at the end of this bucket
            for issue in issues:
                fields = issue.get("fields", {})
                created_date = fields.get("created_date")
                
                if created_date and created_date <= bucket:
                    status = fields.get("status", {}).get("name", "Unknown")
                    
                    # Check if it was resolved before the end of this bucket
                    resolved_date = fields.get("resolved_date", None)
                    
                    current_status = status
                    if resolved_date and resolved_date <= bucket:
                        current_status = "Done"
                    
                    status_counts[bucket_key][current_status] = status_counts[bucket_key].get(current_status, 0) + 1
                    
        # Calculate velocity metrics
        velocity_trend = []
        for i, bucket in enumerate(date_buckets):
            if i > 0:  # Skip first bucket as we need previous data
                bucket_key = bucket.strftime(bucket_format)
                prev_bucket_key = date_buckets[i-1].strftime(bucket_format)
                
                created = created_by_bucket.get(bucket_key, 0)
                resolved = resolved_by_bucket.get(bucket_key, 0)
                
                # Calculate total issues and backlog growth
                total_created_to_date = sum(created_by_bucket.get(date_buckets[j].strftime(bucket_format), 0) 
                                          for j in range(i+1))
                total_resolved_to_date = sum(resolved_by_bucket.get(date_buckets[j].strftime(bucket_format), 0) 
                                           for j in range(i+1))
                backlog_size = total_created_to_date - total_resolved_to_date
                backlog_growth = backlog_size - (total_created_to_date - total_resolved_to_date - 
                                              (created - resolved))
                
                velocity_trend.append({
                    "period": bucket_key,
                    "created": created,
                    "resolved": resolved,
                    "net_change": resolved - created,
                    "backlog_size": backlog_size,
                    "backlog_growth": backlog_growth
                })
                
        # Generate visualizations
        chart_files = {}
        try:
            # Create dates for plotting
            if bucket_unit == "day":
                x_dates = [bucket.strftime("%m-%d") for bucket in date_buckets]
            elif bucket_unit == "week":
                x_dates = [f"W{bucket.strftime('%U')}" for bucket in date_buckets]
            else:
                x_dates = [bucket.strftime("%b %Y") for bucket in date_buckets]
                
            # Velocity chart
            plt.figure(figsize=(12, 6))
            created_values = [created_by_bucket.get(bucket.strftime(bucket_format), 0) for bucket in date_buckets]
            resolved_values = [resolved_by_bucket.get(bucket.strftime(bucket_format), 0) for bucket in date_buckets]
            
            plt.bar(x_dates, created_values, color='blue', alpha=0.6, label='Created')
            plt.bar(x_dates, resolved_values, color='green', alpha=0.6, label='Resolved')
            
            plt.title(f"Issue Velocity for {project_key} ({time_range})")
            plt.xlabel("Time Period")
            plt.ylabel("Number of Issues")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            
            # Save chart to file
            velocity_chart_path = os.path.join(self.data_dir, f"{project_key}_velocity_{time_range}.png")
            plt.savefig(velocity_chart_path)
            plt.close()
            chart_files["velocity_chart"] = velocity_chart_path
            
            # Status distribution chart (stacked area)
            plt.figure(figsize=(12, 6))
            
            # Extract all unique statuses
            all_statuses = set()
            for bucket_data in status_counts.values():
                all_statuses.update(bucket_data.keys())
                
            # Create data for stacked area chart
            status_data = {status: [] for status in all_statuses}
            for bucket in date_buckets:
                bucket_key = bucket.strftime(bucket_format)
                bucket_status_counts = status_counts.get(bucket_key, {})
                
                for status in all_statuses:
                    status_data[status].append(bucket_status_counts.get(status, 0))
            
            # Plot stacked area
            plt.stackplot(x_dates, 
                         [status_data[status] for status in all_statuses],
                         labels=list(all_statuses),
                         alpha=0.7)
            
            plt.title(f"Issue Status Distribution for {project_key} ({time_range})")
            plt.xlabel("Time Period")
            plt.ylabel("Number of Issues")
            plt.xticks(rotation=45)
            plt.legend(loc='upper left')
            plt.tight_layout()
            
            # Save chart to file
            status_chart_path = os.path.join(self.data_dir, f"{project_key}_status_{time_range}.png")
            plt.savefig(status_chart_path)
            plt.close()
            chart_files["status_chart"] = status_chart_path
            
            # Issue type distribution chart
            plt.figure(figsize=(12, 6))
            
            # Get the top 5 issue types by total count
            issue_type_totals = {
                issue_type: sum(counts.values()) 
                for issue_type, counts in created_by_type.items()
            }
            top_types = sorted(issue_type_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            top_type_names = [t[0] for t in top_types]
            
            # Plot lines for top issue types
            for issue_type in top_type_names:
                type_counts = [created_by_type[issue_type].get(bucket.strftime(bucket_format), 0) 
                              for bucket in date_buckets]
                plt.plot(x_dates, type_counts, marker='o', label=issue_type)
            
            plt.title(f"Issue Types Over Time for {project_key} ({time_range})")
            plt.xlabel("Time Period")
            plt.ylabel("Number of Issues Created")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            
            # Save chart to file
            type_chart_path = os.path.join(self.data_dir, f"{project_key}_types_{time_range}.png")
            plt.savefig(type_chart_path)
            plt.close()
            chart_files["type_chart"] = type_chart_path
            
        except Exception as e:
            logger.error(f"Error generating trend charts: {str(e)}")
            
        # Identify trends and insights
        insights = []
        
        # Velocity trends
        if len(velocity_trend) >= 3:
            recent_periods = velocity_trend[-3:]
            
            # Check for velocity changes
            created_trend = [period["created"] for period in recent_periods]
            resolved_trend = [period["resolved"] for period in recent_periods]
            
            created_change = (created_trend[-1] - created_trend[0]) / max(created_trend[0], 1)
            resolved_change = (resolved_trend[-1] - resolved_trend[0]) / max(resolved_trend[0], 1)
            
            if created_change > 0.5:
                insights.append(f"Issue creation has increased by {int(created_change*100)}% over the last three periods.")
            elif created_change < -0.3:
                insights.append(f"Issue creation has decreased by {int(abs(created_change)*100)}% over the last three periods.")
                
            if resolved_change > 0.5:
                insights.append(f"Issue resolution has increased by {int(resolved_change*100)}% over the last three periods.")
            elif resolved_change < -0.3:
                insights.append(f"Issue resolution has decreased by {int(abs(resolved_change)*100)}% over the last three periods.")
                
            # Check for backlog growth
            recent_backlog_change = sum(period["backlog_growth"] for period in recent_periods)
            if recent_backlog_change > 10:
                insights.append(f"Backlog has grown significantly by {recent_backlog_change} issues in the recent periods.")
            elif recent_backlog_change < -10:
                insights.append(f"Team is making good progress, reducing backlog by {abs(recent_backlog_change)} issues in the recent periods.")
        
        # Status distribution insights
        if len(date_buckets) >= 2:
            first_bucket_key = date_buckets[0].strftime(bucket_format)
            last_bucket_key = date_buckets[-1].strftime(bucket_format)
            
            first_status = status_counts.get(first_bucket_key, {})
            last_status = status_counts.get(last_bucket_key, {})
            
            # Calculate percentage of issues in progress
            in_progress_statuses = ['In Progress', 'In Review', 'Testing']
            first_in_progress = sum(first_status.get(status, 0) for status in in_progress_statuses)
            last_in_progress = sum(last_status.get(status, 0) for status in in_progress_statuses)
            
            first_total = sum(first_status.values()) or 1  # Avoid division by zero
            last_total = sum(last_status.values()) or 1
            
            first_in_progress_pct = first_in_progress / first_total
            last_in_progress_pct = last_in_progress / last_total
            
            if last_in_progress_pct > first_in_progress_pct + 0.2:
                insights.append(f"The percentage of issues in progress has increased significantly from {int(first_in_progress_pct*100)}% to {int(last_in_progress_pct*100)}%.")
            elif last_in_progress_pct < first_in_progress_pct - 0.2:
                insights.append(f"The percentage of issues in progress has decreased from {int(first_in_progress_pct*100)}% to {int(last_in_progress_pct*100)}%.")
        
        # Issue type insights
        issue_type_changes = {}
        for issue_type in created_by_type.keys():
            # Skip if not enough periods
            if len(date_buckets) < 2:
                continue
                
            first_bucket_key = date_buckets[0].strftime(bucket_format)
            last_bucket_key = date_buckets[-1].strftime(bucket_format)
            
            first_count = created_by_type[issue_type].get(first_bucket_key, 0)
            last_count = created_by_type[issue_type].get(last_bucket_key, 0)
            
            # Calculate relative change
            if first_count > 0:
                change_pct = (last_count - first_count) / first_count
                issue_type_changes[issue_type] = change_pct
        
        # Find significant changes in issue types
        significant_changes = [(issue_type, change) for issue_type, change in issue_type_changes.items() 
                              if abs(change) > 0.5 and issue_type_totals.get(issue_type, 0) >= 5]
        
        for issue_type, change in significant_changes:
            if change > 0:
                insights.append(f"{issue_type} creation has increased by {int(change*100)}% from the first to the latest period.")
            else:
                insights.append(f"{issue_type} creation has decreased by {int(abs(change)*100)}% from the first to the latest period.")
                
        return {
            "project_key": project_key,
            "time_range": time_range,
            "total_issues": len(issues),
            "velocity_trend": velocity_trend,
            "created_by_period": created_by_bucket,
            "resolved_by_period": resolved_by_bucket,
            "issue_type_trends": created_by_type,
            "status_distribution": status_counts,
            "insights": insights,
            "chart_files": chart_files
        }
        
    def generate_custom_report(self, **kwargs) -> Dict:
        """
        Generate a custom report combining multiple analytics.
        
        Args:
            **kwargs: Parameters for the report
            
        Returns:
            Dict containing the custom report
        """
        report_type = kwargs.get("report_type", "comprehensive")
        project_key = kwargs.get("project_key")
        
        if not project_key:
            return {"error": "Project key is required"}
            
        report = {
            "project_key": project_key,
            "report_type": report_type,
            "generated_at": datetime.datetime.now().isoformat(),
        }
        
        # Generate report based on type
        if report_type == "comprehensive":
            # Project metrics
            metrics = self.get_project_metrics(project_key)
            if "error" not in metrics:
                report["project_metrics"] = metrics
                
            # Time tracking analysis
            time_tracking = self.analyze_time_tracking(project_key)
            if "error" not in time_tracking:
                report["time_tracking"] = time_tracking
                
            # Issue patterns
            patterns = self.detect_issue_patterns(project_key)
            if "error" not in patterns:
                report["issue_patterns"] = patterns
                
            # Trend analysis
            trends = self.generate_trend_report(project_key, "3m")
            if "error" not in trends:
                report["trends"] = trends
                
        elif report_type == "velocity":
            # Focus on velocity and trends
            metrics = self.get_project_metrics(project_key)
            if "error" not in metrics:
                report["project_metrics"] = {
                    "total_issues": metrics["total_issues"],
                    "velocity_per_week": metrics["velocity_per_week"],
                    "completion_rate": metrics["completion_rate"]
                }
                
            # Detailed trend analysis
            trends_1m = self.generate_trend_report(project_key, "1m")
            trends_3m = self.generate_trend_report(project_key, "3m")
            trends_6m = self.generate_trend_report(project_key, "6m")
            
            report["trends"] = {
                "short_term": trends_1m if "error" not in trends_1m else {"error": trends_1m.get("error")},
                "medium_term": trends_3m if "error" not in trends_3m else {"error": trends_3m.get("error")},
                "long_term": trends_6m if "error" not in trends_6m else {"error": trends_6m.get("error")}
            }
            
        elif report_type == "efficiency":
            # Focus on time tracking and efficiency
            time_tracking = self.analyze_time_tracking(project_key)
            if "error" not in time_tracking:
                report["time_tracking"] = time_tracking
                
            # Get resolution time metrics
            metrics = self.get_project_metrics(project_key)
            if "error" not in metrics:
                report["resolution_metrics"] = {
                    "resolution_time": metrics["resolution_time"],
                    "completion_rate": metrics["completion_rate"]
                }
                
            # Get issue patterns related to efficiency
            patterns = self.detect_issue_patterns(project_key)
            if "error" not in patterns:
                report["efficiency_patterns"] = {
                    "cycle_time_outliers": patterns.get("cycle_time_outliers", []),
                    "estimation_patterns": patterns.get("estimation_patterns", []),
                    "cycle_time_by_type": patterns.get("cycle_time_by_type", [])
                }
                
        elif report_type == "quality":
            # Focus on issue patterns and issue type distribution
            metrics = self.get_project_metrics(project_key)
            if "error" not in metrics:
                report["issue_distribution"] = {
                    "issue_types": metrics["issue_types"],
                    "priorities": metrics["priorities"]
                }
                
            # Get trend data for bug reporting
            trends = self.generate_trend_report(project_key, "3m")
            if "error" not in trends and "issue_type_trends" in trends:
                bug_trends = {
                    period: count 
                    for period, count in trends["issue_type_trends"].get("Bug", {}).items()
                }
                report["bug_trends"] = bug_trends
                
            # Calculate bug ratio over time
            if "error" not in trends and "created_by_period" in trends:
                bug_ratio = {}
                for period, total in trends["created_by_period"].items():
                    if total > 0:
                        bug_count = bug_trends.get(period, 0)
                        bug_ratio[period] = round(bug_count / total, 3)
                report["bug_ratio_trend"] = bug_ratio
        
        # Add executive summary
        summary = []
        
        if "project_metrics" in report:
            metrics = report["project_metrics"]
            summary.append(f"Project contains {metrics.get('total_issues', 0)} issues with a weekly velocity of {metrics.get('velocity_per_week', 0)} issues.")
            summary.append(f"Current completion rate is {metrics.get('completion_rate', 0)}%.")
            
        if "time_tracking" in report:
            tracking = report["time_tracking"]
            estimation_accuracy = tracking.get("overall_estimation_accuracy", 0)
            if estimation_accuracy > 0:
                if estimation_accuracy > 1.2:
                    summary.append(f"Tasks are consistently underestimated (accuracy ratio: {round(estimation_accuracy, 2)}).")
                elif estimation_accuracy < 0.8:
                    summary.append(f"Tasks are consistently overestimated (accuracy ratio: {round(estimation_accuracy, 2)}).")
                else:
                    summary.append(f"Estimation accuracy is good (accuracy ratio: {round(estimation_accuracy, 2)}).")
                    
        if "trends" in report:
            if "velocity_trend" in report["trends"]:
                trends = report["trends"]
                if len(trends["velocity_trend"]) >= 2:
                    recent = trends["velocity_trend"][-1]
                    previous = trends["velocity_trend"][-2]
                    
                    created_change = recent["created"] - previous["created"]
                    resolved_change = recent["resolved"] - previous["resolved"]
                    
                    if created_change > 0:
                        summary.append(f"Issue creation has increased by {created_change} issues in the most recent period.")
                    elif created_change < 0:
                        summary.append(f"Issue creation has decreased by {abs(created_change)} issues in the most recent period.")
                        
                    if resolved_change > 0:
                        summary.append(f"Issue resolution has increased by {resolved_change} issues in the most recent period.")
                    elif resolved_change < 0:
                        summary.append(f"Issue resolution has decreased by {abs(resolved_change)} issues in the most recent period.")
                        
        # Add insights if available
        all_insights = []
        
        if "time_tracking" in report and "insights" in report["time_tracking"]:
            all_insights.extend(report["time_tracking"]["insights"])
            
        if "trends" in report and "insights" in report["trends"]:
            all_insights.extend(report["trends"]["insights"])
            
        if all_insights:
            report["key_insights"] = all_insights
            
        report["executive_summary"] = summary
        
        return report
    
    @with_auth_client("confluence")
    def publish_report_to_confluence(self, client: AuthenticatedClient, report: Dict, space_key: str, title: str) -> Dict:
        """
        Publish an analytics report to Confluence.
        
        Args:
            client: Authenticated client
            report: The report to publish
            space_key: Confluence space key
            title: Page title
            
        Returns:
            Dict containing the result of the operation
        """
        # Create markdown content for the report
        content = f"# {title}\n\n"
        content += f"*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        # Add executive summary
        content += "## Executive Summary\n\n"
        if "executive_summary" in report:
            for item in report["executive_summary"]:
                content += f"- {item}\n"
        else:
            content += "*No executive summary available*\n"
            
        content += "\n"
        
        # Add key insights
        if "key_insights" in report and report["key_insights"]:
            content += "## Key Insights\n\n"
            for insight in report["key_insights"]:
                content += f"- {insight}\n"
            content += "\n"
            
        # Add project metrics
        if "project_metrics" in report:
            metrics = report["project_metrics"]
            content += "## Project Metrics\n\n"
            content += f"- **Total Issues:** {metrics.get('total_issues', 0)}\n"
            content += f"- **Weekly Velocity:** {metrics.get('velocity_per_week', 0)}\n"
            content += f"- **Completion Rate:** {metrics.get('completion_rate', 0)}%\n\n"
            
            # Issue type distribution
            if "issue_types" in metrics:
                content += "### Issue Type Distribution\n\n"
                content += "| Issue Type | Count |\n"
                content += "|------------|-------|\n"
                for issue_type, count in metrics["issue_types"].items():
                    content += f"| {issue_type} | {count} |\n"
                content += "\n"
                
            # Resolution time
            if "resolution_time" in metrics:
                resolution = metrics["resolution_time"]
                content += "### Resolution Time (days)\n\n"
                content += f"- **Average:** {resolution.get('average', 0)}\n"
                content += f"- **Median:** {resolution.get('median', 0)}\n"
                content += f"- **90th Percentile:** {resolution.get('p90', 0)}\n\n"
                
        # Add time tracking analysis
        if "time_tracking" in report:
            tracking = report["time_tracking"]
            content += "## Time Tracking Analysis\n\n"
            content += f"- **Total Time Estimated:** {tracking.get('total_time_estimated_hours', 0)} hours\n"
            content += f"- **Total Time Logged:** {tracking.get('total_time_logged_hours', 0)} hours\n"
            content += f"- **Overall Estimation Accuracy:** {tracking.get('overall_estimation_accuracy', 0)}\n\n"
            
            # Time by user
            if "time_by_user" in tracking:
                content += "### Time by User (hours)\n\n"
                content += "| User | Hours Logged |\n"
                content += "|------|-------------|\n"
                for user, hours in tracking["time_by_user"].items():
                    content += f"| {user} | {hours} |\n"
                content += "\n"
                
            # Time by issue type
            if "time_by_issue_type" in tracking:
                content += "### Time by Issue Type (hours)\n\n"
                content += "| Issue Type | Hours Logged |\n"
                content += "|------------|-------------|\n"
                for issue_type, hours in tracking["time_by_issue_type"].items():
                    content += f"| {issue_type} | {hours} |\n"
                content += "\n"
                
        # Add trend analysis
        if "trends" in report:
            trends = report["trends"]
            content += "## Trend Analysis\n\n"
            
            # Velocity trend
            if "velocity_trend" in trends:
                content += "### Velocity Trend\n\n"
                content += "| Period | Created | Resolved | Net Change | Backlog Size |\n"
                content += "|--------|---------|----------|------------|-------------|\n"
                for period in trends["velocity_trend"]:
                    content += f"| {period['period']} | {period['created']} | {period['resolved']} | {period['net_change']} | {period['backlog_size']} |\n"
                content += "\n"
                
            # Add embedded charts if available
            if "chart_files" in trends:
                content += "### Trend Charts\n\n"
                
                # Upload chart images and embed them
                for chart_name, chart_path in trends["chart_files"].items():
                    try:
                        # Upload the chart as an attachment
                        attachment_result = client.request(
                            "POST",
                            f"{os.environ.get('CONFLUENCE_URL')}/rest/api/content/{page_id}/child/attachment",
                            headers={"X-Atlassian-Token": "no-check"},
                            files={
                                "file": (os.path.basename(chart_path), open(chart_path, "rb"), "image/png")
                            }
                        )
                        
                        if attachment_result.status_code in (200, 201):
                            # Get the attachment ID
                            attachment_id = attachment_result.json()["results"][0]["id"]
                            
                            # Add the chart to the content
                            chart_title = chart_name.replace("_", " ").title()
                            content += f"#### {chart_title}\n\n"
                            content += f"![{chart_title}](/wiki/download/attachments/{page_id}/{os.path.basename(chart_path)})\n\n"
                    except Exception as e:
                        logger.error(f"Failed to upload chart {chart_name}: {str(e)}")
                        content += f"*Chart {chart_name} could not be uploaded: {str(e)}*\n\n"
                        
        # Issue patterns
        if "issue_patterns" in report:
            patterns = report["issue_patterns"]
            content += "## Issue Patterns\n\n"
            
            # Assignee specialization
            if "assignee_specialization" in patterns and patterns["assignee_specialization"]:
                content += "### Assignee Specialization\n\n"
                content += "| Assignee | Primary Issue Type | Percentage |\n"
                content += "|----------|-------------------|------------|\n"
                for assignee, data in patterns["assignee_specialization"].items():
                    content += f"| {assignee} | {data['issue_type']} | {int(data['specialization_ratio'] * 100)}% |\n"
                content += "\n"
                
            # Estimation patterns
            if "estimation_patterns" in patterns and patterns["estimation_patterns"]:
                content += "### Estimation Patterns\n\n"
                content += "| Issue Type | Pattern | Accuracy Ratio | Sample Size |\n"
                content += "|------------|---------|----------------|-------------|\n"
                for pattern in patterns["estimation_patterns"]:
                    content += f"| {pattern['issue_type']} | {pattern['pattern']} | {pattern['average_ratio']} | {pattern['sample_size']} |\n"
                content += "\n"
                
            # Cycle time by issue type
            if "cycle_time_by_type" in patterns and patterns["cycle_time_by_type"]:
                content += "### Cycle Time by Issue Type (days)\n\n"
                content += "| Issue Type | Average | Median | Count |\n"
                content += "|------------|---------|--------|-------|\n"
                for cycle in patterns["cycle_time_by_type"]:
                    content += f"| {cycle['issue_type']} | {round(cycle['mean'], 2)} | {round(cycle['median'], 2)} | {int(cycle['count'])} |\n"
                content += "\n"
                
        # Create the page in Confluence
        try:
            create_result = client.request(
                "POST",
                f"{os.environ.get('CONFLUENCE_URL')}/rest/api/content",
                json={
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "body": {
                        "storage": {
                            "value": self._markdown_to_storage_format(content),
                            "representation": "storage"
                        }
                    }
                }
            )
            
            if create_result.status_code in (200, 201):
                page_data = create_result.json()
                page_id = page_data["id"]
                page_url = page_data["_links"]["base"] + page_data["_links"]["webui"]
                
                return {
                    "success": True,
                    "page_id": page_id,
                    "page_url": page_url,
                    "message": f"Report published successfully to {title}"
                }
            else:
                logger.error(f"Failed to create page: {create_result.text}")
                return {
                    "success": False,
                    "error": f"Failed to create page: {create_result.status_code}",
                    "details": create_result.text
                }
        except Exception as e:
            logger.error(f"Error publishing report: {str(e)}")
            return {
                "success": False,
                "error": f"Error publishing report: {str(e)}"
            }
            
    def _get_all_project_issues(self, client: AuthenticatedClient, project_key: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """Helper method to get all issues for a project with pagination."""
        if project_key in self._issue_cache:
            return self._issue_cache[project_key]
            
        all_issues = []
        start_at = 0
        max_results = 100
        fields_param = ",".join(fields) if fields else "*navigable"
        
        while True:
            response = client.request(
                "GET", 
                f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
                params={
                    "jql": f"project = {project_key}",
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": fields_param
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch project issues: {response.text}")
                return []
                
            data = response.json()
            issues = data.get("issues", [])
            all_issues.extend(issues)
            
            if len(issues) < max_results or start_at + len(issues) >= data.get("total", 0):
                # No more issues to fetch
                break
                
            start_at += len(issues)
            
        # Cache the results to avoid repeated API calls
        self._issue_cache[project_key] = all_issues
        return all_issues
        
    def _markdown_to_storage_format(self, markdown: str) -> str:
        """
        Simple converter for markdown to Confluence storage format.
        For a full implementation, a specialized library would be better.
        """
        # This is a very simplified conversion
        html = markdown.replace("# ", "<h1>").replace("\n# ", "\n<h1>")
        html = html.replace("## ", "<h2>").replace("\n## ", "\n<h2>")
        html = html.replace("### ", "<h3>").replace("\n### ", "\n<h3>")
        html = html.replace("#### ", "<h4>").replace("\n#### ", "\n<h4>")
        
        # Close heading tags
        html = html.replace("<h1>", "<h1>").replace("\n", "</h1>\n", 1)
        html = html.replace("<h2>", "<h2>").replace("\n", "</h2>\n", 1)
        html = html.replace("<h3>", "<h3>").replace("\n", "</h3>\n", 1)
        html = html.replace("<h4>", "<h4>").replace("\n", "</h4>\n", 1)
        
        # Convert lists
        html = html.replace("\n- ", "\n<li>").replace("\n<li>", "</li>\n<li>", 1)
        html = "<ul>" + html + "</ul>"
        
        # Convert tables
        if "|" in html:
            lines = html.split("\n")
            in_table = False
            table_html = ""
            
            for i, line in enumerate(lines):
                if line.startswith("|") and line.endswith("|"):
                    if not in_table:
                        in_table = True
                        table_html += "<table>"
                        
                    # Skip separator line
                    if "-|-" in line:
                        continue
                        
                    cells = line.strip("|").split("|")
                    row_html = "<tr>"
                    
                    for cell in cells:
                        if i == 0 or (i == 2 and "-|-" in lines[1]):  # Header row
                            row_html += f"<th>{cell.strip()}</th>"
                        else:
                            row_html += f"<td>{cell.strip()}</td>"
                            
                    row_html += "</tr>"
                    table_html += row_html
                elif in_table:
                    in_table = False
                    table_html += "</table>"
                    html = html.replace(table_html, table_html)
                    
            if in_table:
                table_html += "</table>"
                
        # Convert bold, italic, code
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        html = html.replace("*", "<em>").replace("*", "</em>")
        html = html.replace("`", "<code>").replace("`", "</code>")
        
        # Convert links
        import re
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Convert images
        html = re.sub(r'!\[([^\]]+)\]\(([^)]+)\)', r'<img src="\2" alt="\1"/>', html)
        
        # Wrap in proper Confluence storage format
        return html


# Create a global instance
analytics_manager = AnalyticsManager()