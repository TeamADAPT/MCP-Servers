"""
AI-powered capabilities for MCP Atlassian.

This module provides enterprise-grade AI capabilities for the MCP Atlassian integration,
including smart issue classification, content suggestion mechanisms,
sentiment analysis for tickets, and predictive SLA management.
"""

import os
import re
import json
import time
import logging
import datetime
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from collections import Counter, defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import joblib

from .auth import with_auth_client, AuthenticatedClient

# Configure logging
logger = logging.getLogger("mcp-atlassian.ai_capabilities")

# Initialize NLTK resources if not already downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)


class AICapabilitiesManager:
    """
    Provides enterprise-grade AI capabilities for Atlassian products.
    
    Includes smart issue classification, content suggestion mechanisms,
    sentiment analysis for tickets, and predictive SLA management.
    """
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the AICapabilitiesManager.
        
        Args:
            models_dir: Directory to store trained models
        """
        # Create a directory for trained models
        if models_dir:
            self.models_dir = models_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.models_dir = os.path.join(base_dir, "data", "models")
            
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Cache for trained models
        self._classifier_models = {}
        self._sla_prediction_models = {}
        self._vectorizers = {}
        
    @with_auth_client("jira")
    def train_issue_classifier(self, client: AuthenticatedClient, project_key: str, model_type: str = "issue_type") -> Dict:
        """
        Train a classifier model for automatic issue classification.
        
        Args:
            client: Authenticated client
            project_key: Project key to use for training
            model_type: Type of classifier to train (issue_type, priority, component)
            
        Returns:
            Dict containing training results
        """
        # Get training data from Jira
        jql = f"project = {project_key} ORDER BY created DESC"
        response = client.request(
            "GET", 
            f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
            params={
                "jql": jql,
                "maxResults": 500,  # Get a good sample size
                "fields": "summary,description,issuetype,priority,components,labels"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch training data: {response.text}")
            return {"error": "Failed to fetch training data"}
            
        issues = response.json().get("issues", [])
        if len(issues) < 20:
            return {"error": "Insufficient training data. Need at least 20 issues."}
            
        # Prepare training data based on model type
        X_text = []
        y_labels = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Combine summary and description for text features
            summary = fields.get("summary", "")
            description = fields.get("description", "") or ""
            combined_text = f"{summary}\n{description}"
            
            # Skip if text is too short
            if len(combined_text.strip()) < 10:
                continue
                
            X_text.append(combined_text)
            
            # Get target label based on model type
            if model_type == "issue_type":
                label = fields.get("issuetype", {}).get("name", "Unknown")
            elif model_type == "priority":
                label = fields.get("priority", {}).get("name", "Medium")
            elif model_type == "component":
                components = fields.get("components", [])
                # Use the first component if available, otherwise 'None'
                label = components[0].get("name", "None") if components else "None"
            else:
                return {"error": f"Unsupported model type: {model_type}"}
                
            y_labels.append(label)
            
        # Check if we have enough data after filtering
        if len(X_text) < 20:
            return {"error": "Insufficient training data after filtering. Need at least 20 issues with good text content."}
            
        # Check if we have at least 2 unique labels
        unique_labels = set(y_labels)
        if len(unique_labels) < 2:
            return {"error": f"Need at least 2 unique {model_type} values for classification"}
            
        # Create vectorizer and transform text data
        vectorizer = TfidfVectorizer(
            max_features=5000, 
            min_df=2, 
            max_df=0.8,
            ngram_range=(1, 2)
        )
        X_tfidf = vectorizer.fit_transform(X_text)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_tfidf, y_labels, test_size=0.2, random_state=42, stratify=y_labels if len(unique_labels) > 1 else None
        )
        
        # Train classifier
        if len(unique_labels) > 2:  # Multiclass
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
        else:  # Binary
            clf = LogisticRegression(random_state=42)
            
        clf.fit(X_train, y_train)
        
        # Evaluate classifier
        accuracy = clf.score(X_test, y_test)
        
        # Calculate class distribution
        class_distribution = Counter(y_labels)
        
        # Save models
        model_name = f"{project_key}_{model_type}_classifier"
        model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
        vectorizer_path = os.path.join(self.models_dir, f"{model_name}_vectorizer.joblib")
        
        joblib.dump(clf, model_path)
        joblib.dump(vectorizer, vectorizer_path)
        
        # Store in cache
        self._classifier_models[model_name] = clf
        self._vectorizers[model_name] = vectorizer
        
        # Get feature importance
        feature_importance = None
        if hasattr(clf, 'feature_importances_'):
            # For Random Forest
            feature_names = vectorizer.get_feature_names_out()
            importance = clf.feature_importances_
            feature_importance = sorted(
                [(feature_names[i], importance[i]) for i in range(len(feature_names))],
                key=lambda x: x[1],
                reverse=True
            )[:20]  # Top 20 features
        elif hasattr(clf, 'coef_'):
            # For LogisticRegression
            feature_names = vectorizer.get_feature_names_out()
            importance = clf.coef_[0]
            feature_importance = sorted(
                [(feature_names[i], importance[i]) for i in range(len(feature_names))],
                key=lambda x: abs(x[1]),
                reverse=True
            )[:20]  # Top 20 features
            
        return {
            "model_type": model_type,
            "project_key": project_key,
            "training_data_size": len(X_text),
            "accuracy": round(accuracy, 3),
            "class_distribution": {label: count for label, count in class_distribution.items()},
            "model_path": model_path,
            "top_features": feature_importance
        }
        
    @with_auth_client("jira")
    def classify_issue(self, client: AuthenticatedClient, project_key: str, 
                      text: str, model_type: str = "issue_type") -> Dict:
        """
        Classify an issue using a trained model.
        
        Args:
            client: Authenticated client
            project_key: Project key associated with the model
            text: Issue text to classify (summary + description)
            model_type: Type of classifier to use
            
        Returns:
            Dict containing classification results
        """
        model_name = f"{project_key}_{model_type}_classifier"
        
        # Load model from cache or disk
        clf = self._classifier_models.get(model_name)
        vectorizer = self._vectorizers.get(model_name)
        
        if clf is None or vectorizer is None:
            # Try to load from disk
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            vectorizer_path = os.path.join(self.models_dir, f"{model_name}_vectorizer.joblib")
            
            try:
                clf = joblib.load(model_path)
                vectorizer = joblib.load(vectorizer_path)
                
                # Update cache
                self._classifier_models[model_name] = clf
                self._vectorizers[model_name] = vectorizer
            except FileNotFoundError:
                return {
                    "error": f"No trained model found for {project_key} {model_type}",
                    "recommendation": f"Train a model first using train_issue_classifier"
                }
                
        # Preprocess and vectorize text
        X_tfidf = vectorizer.transform([text])
        
        # Get prediction and probabilities
        prediction = clf.predict(X_tfidf)[0]
        
        probabilities = None
        if hasattr(clf, 'predict_proba'):
            proba = clf.predict_proba(X_tfidf)[0]
            classes = clf.classes_
            probabilities = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}
            
        # Get alternative suggestions (top 3)
        alternatives = []
        if probabilities:
            alternatives = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[1:4]
            alternatives = [{"label": label, "confidence": conf} for label, conf in alternatives]
            
        return {
            "model_type": model_type,
            "project_key": project_key,
            "input_text": text[:100] + "..." if len(text) > 100 else text,
            "predicted_label": prediction,
            "confidence": round(float(max(probabilities.values())), 3) if probabilities else None,
            "all_probabilities": probabilities,
            "alternative_suggestions": alternatives
        }
        
    @with_auth_client("jira")
    def suggest_content(self, client: AuthenticatedClient, project_key: str, 
                       query: str, content_type: str = "description") -> Dict:
        """
        Suggest content for issues based on similar existing issues.
        
        Args:
            client: Authenticated client
            project_key: Project key to search for similar content
            query: Query text (e.g. issue summary)
            content_type: Type of content to suggest (description, comment, solution)
            
        Returns:
            Dict containing suggested content
        """
        # Get recent issues from the project
        jql = f"project = {project_key} ORDER BY created DESC"
        response = client.request(
            "GET", 
            f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
            params={
                "jql": jql,
                "maxResults": 100,
                "fields": "summary,description,comment,resolution,issuetype"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch issues for content suggestion: {response.text}")
            return {"error": "Failed to fetch issues for content suggestion"}
            
        issues = response.json().get("issues", [])
        if not issues:
            return {"error": "No issues found for content suggestion"}
            
        # Process issues to extract relevant content
        issue_data = []
        for issue in issues:
            fields = issue.get("fields", {})
            
            summary = fields.get("summary", "")
            
            # Get content based on content_type
            if content_type == "description":
                content = fields.get("description", "")
            elif content_type == "comment":
                comments = fields.get("comment", {}).get("comments", [])
                # Get the most relevant comment (longest)
                content = max(comments, key=lambda c: len(c.get("body", "")), default={}).get("body", "") if comments else ""
            elif content_type == "solution":
                # Look for resolution or a comment containing solution keywords
                resolution = fields.get("resolution", {}).get("description", "")
                
                # Try to find a solution comment
                solution_comment = ""
                comments = fields.get("comment", {}).get("comments", [])
                for comment in comments:
                    body = comment.get("body", "").lower()
                    if any(kw in body for kw in ["solution", "resolve", "fixed", "implemented", "workaround"]):
                        solution_comment = comment.get("body", "")
                        break
                        
                content = resolution if len(resolution) > len(solution_comment) else solution_comment
            else:
                return {"error": f"Unsupported content type: {content_type}"}
                
            # Only include issues that have the requested content
            if content and len(content.strip()) > 30:  # Minimum content length
                issue_data.append({
                    "key": issue.get("key"),
                    "summary": summary,
                    "content": content,
                    "issue_type": fields.get("issuetype", {}).get("name", "Unknown")
                })
                
        if not issue_data:
            return {"error": f"No issues found with substantial {content_type} content"}
            
        # Create vectorizer for text similarity
        vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        
        # Create document corpus and vectorize
        summaries = [item["summary"] for item in issue_data]
        summaries_matrix = vectorizer.fit_transform(summaries)
        
        # Vectorize query
        query_vector = vectorizer.transform([query])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, summaries_matrix).flatten()
        
        # Rank results by similarity
        ranked_indices = similarity_scores.argsort()[::-1]
        
        # Get top 3 suggestions
        suggestions = []
        for idx in ranked_indices[:3]:
            if similarity_scores[idx] > 0.1:  # Minimum similarity threshold
                suggestion = {
                    "issue_key": issue_data[idx]["key"],
                    "similarity": round(float(similarity_scores[idx]), 3),
                    "summary": issue_data[idx]["summary"],
                    "content": issue_data[idx]["content"],
                    "issue_type": issue_data[idx]["issue_type"]
                }
                suggestions.append(suggestion)
                
        if not suggestions:
            return {"message": "No relevant content suggestions found"}
            
        return {
            "project_key": project_key,
            "query": query,
            "content_type": content_type,
            "suggestions": suggestions
        }
        
    @with_auth_client("jira")
    def analyze_sentiment(self, client: AuthenticatedClient, text: str = None, 
                         issue_key: str = None) -> Dict:
        """
        Analyze sentiment in text or Jira issue comments.
        
        Args:
            client: Authenticated client
            text: Text to analyze (optional if issue_key is provided)
            issue_key: Jira issue key to analyze comments from (optional if text is provided)
            
        Returns:
            Dict containing sentiment analysis results
        """
        if not text and not issue_key:
            return {"error": "Either text or issue_key must be provided"}
            
        # If issue_key is provided, fetch comments from the issue
        comments = []
        if issue_key:
            response = client.request(
                "GET", 
                f"{os.environ.get('JIRA_URL')}/rest/api/2/issue/{issue_key}/comment"
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch comments: {response.text}")
                return {"error": f"Failed to fetch comments for issue {issue_key}"}
                
            comments_data = response.json().get("comments", [])
            comments = [comment.get("body", "") for comment in comments_data]
            
            # Also get the issue description
            issue_response = client.request(
                "GET", 
                f"{os.environ.get('JIRA_URL')}/rest/api/2/issue/{issue_key}",
                params={"fields": "description,summary"}
            )
            
            if issue_response.status_code == 200:
                fields = issue_response.json().get("fields", {})
                description = fields.get("description", "")
                summary = fields.get("summary", "")
                
                if description:
                    comments.insert(0, description)
                if summary:
                    comments.insert(0, summary)
                    
        # Analyze sentiment in the provided text or comments
        if text:
            sentiment = self._analyze_text_sentiment(text)
            result = {
                "overall_sentiment": sentiment["compound_category"],
                "sentiment_score": round(sentiment["compound"], 3),
                "sentiment_details": {
                    "positive": round(sentiment["pos"], 3),
                    "negative": round(sentiment["neg"], 3),
                    "neutral": round(sentiment["neu"], 3)
                }
            }
        else:
            # Analyze each comment
            comment_sentiments = []
            for i, comment in enumerate(comments):
                sentiment = self._analyze_text_sentiment(comment)
                comment_sentiments.append({
                    "text_type": "Description" if i == 0 else "Summary" if i == 1 else f"Comment {i-1}",
                    "text_preview": comment[:100] + "..." if len(comment) > 100 else comment,
                    "sentiment": sentiment["compound_category"],
                    "score": round(sentiment["compound"], 3),
                    "details": {
                        "positive": round(sentiment["pos"], 3),
                        "negative": round(sentiment["neg"], 3),
                        "neutral": round(sentiment["neu"], 3)
                    }
                })
                
            # Calculate overall sentiment
            if comment_sentiments:
                avg_compound = sum(cs["score"] for cs in comment_sentiments) / len(comment_sentiments)
                overall_category = "positive" if avg_compound >= 0.05 else "negative" if avg_compound <= -0.05 else "neutral"
                
                # Count sentiment categories
                sentiment_counts = Counter(cs["sentiment"] for cs in comment_sentiments)
                
                result = {
                    "issue_key": issue_key,
                    "overall_sentiment": overall_category,
                    "average_sentiment_score": round(avg_compound, 3),
                    "sentiment_distribution": {
                        "positive": sentiment_counts.get("positive", 0),
                        "neutral": sentiment_counts.get("neutral", 0),
                        "negative": sentiment_counts.get("negative", 0)
                    },
                    "comment_sentiments": comment_sentiments
                }
            else:
                result = {
                    "issue_key": issue_key,
                    "message": "No comments or text to analyze"
                }
                
        return result
        
    @with_auth_client("jira")
    def train_sla_predictor(self, client: AuthenticatedClient, project_key: str) -> Dict:
        """
        Train a model to predict SLA breaches based on historical data.
        
        Args:
            client: Authenticated client
            project_key: Project key to use for training
            
        Returns:
            Dict containing training results
        """
        # Get historical SLA data
        # This requires a custom field for SLA or resolution time data
        jql = f"project = {project_key} AND resolution IS NOT EMPTY ORDER BY resolved DESC"
        response = client.request(
            "GET", 
            f"{os.environ.get('JIRA_URL')}/rest/api/2/search",
            params={
                "jql": jql,
                "maxResults": 500,
                "fields": "summary,description,created,resolutiondate,issuetype,priority,reporter,assignee,components,labels,customfield_10000"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch SLA training data: {response.text}")
            return {"error": "Failed to fetch SLA training data"}
            
        issues = response.json().get("issues", [])
        if len(issues) < 30:
            return {"error": f"Insufficient training data. Need at least 30 resolved issues in {project_key}."}
            
        # Prepare training data
        X_data = []
        y_data = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Calculate resolution time in hours
            created_str = fields.get("created")
            resolved_str = fields.get("resolutiondate")
            
            if not created_str or not resolved_str:
                continue
                
            created = datetime.datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            resolved = datetime.datetime.strptime(resolved_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            
            resolution_time_hours = (resolved - created).total_seconds() / 3600
            
            # Extract features
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            priority = fields.get("priority", {}).get("name", "Medium")
            
            # Convert priority to numeric
            priority_map = {"Highest": 5, "High": 4, "Medium": 3, "Low": 2, "Lowest": 1}
            priority_value = priority_map.get(priority, 3)
            
            # Text length features
            summary = fields.get("summary", "")
            description = fields.get("description", "") or ""
            summary_length = len(summary.split())
            description_length = len(description.split()) if description else 0
            
            # Categorical features (one-hot encoded)
            assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
            reporter = fields.get("reporter", {}).get("displayName", "Unknown")
            
            # Component and label counts
            components = fields.get("components", [])
            labels = fields.get("labels", [])
            component_count = len(components)
            label_count = len(labels)
            
            # Custom SLA field (if available)
            sla_met = fields.get("customfield_10000", True)  # Assume True if not specified
            
            # Create feature vector
            features = {
                "issue_type": issue_type,
                "priority_value": priority_value,
                "summary_length": summary_length,
                "description_length": description_length,
                "component_count": component_count,
                "label_count": label_count,
                "has_assignee": 1 if assignee != "Unassigned" else 0
            }
            
            # Add to training data
            X_data.append(features)
            
            # Target variable: Did the issue meet SLA?
            # For this example, we'll use a simplified approach:
            # - High priority issues should be resolved within 24 hours
            # - Medium priority issues should be resolved within 48 hours
            # - Low priority issues should be resolved within 72 hours
            if sla_met is not True:  # If we have actual SLA data
                y_data.append(1 if sla_met else 0)
            else:
                # Estimate SLA based on priority and resolution time
                if priority_value == 5:  # Highest
                    y_data.append(1 if resolution_time_hours <= 8 else 0)
                elif priority_value == 4:  # High
                    y_data.append(1 if resolution_time_hours <= 24 else 0)
                elif priority_value == 3:  # Medium
                    y_data.append(1 if resolution_time_hours <= 48 else 0)
                else:  # Low or Lowest
                    y_data.append(1 if resolution_time_hours <= 72 else 0)
                    
        # Convert feature dictionaries to proper format
        import pandas as pd
        X_df = pd.DataFrame(X_data)
        
        # One-hot encode categorical features
        X_df = pd.get_dummies(X_df, columns=["issue_type"])
        
        # Check if we have enough data after preprocessing
        if len(X_df) < 30:
            return {"error": "Insufficient training data after preprocessing"}
            
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X_df, y_data, test_size=0.2, random_state=42)
        
        # Train model
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        
        # Evaluate model
        accuracy = clf.score(X_test, y_test)
        
        # Calculate class distribution
        sla_met_count = sum(y_data)
        sla_breached_count = len(y_data) - sla_met_count
        
        # Save model and preprocessing info
        model_name = f"{project_key}_sla_predictor"
        model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
        
        # Save column names to ensure correct feature order during prediction
        column_names = X_df.columns.tolist()
        
        model_info = {
            "model": clf,
            "columns": column_names,
            "training_date": datetime.datetime.now().isoformat()
        }
        
        joblib.dump(model_info, model_path)
        
        # Store in cache
        self._sla_prediction_models[model_name] = model_info
        
        # Feature importance
        feature_importance = None
        if hasattr(clf, 'feature_importances_'):
            importance = clf.feature_importances_
            feature_importance = sorted(
                [(column_names[i], importance[i]) for i in range(len(column_names))],
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 features
            
        return {
            "project_key": project_key,
            "training_data_size": len(X_df),
            "accuracy": round(accuracy, 3),
            "class_distribution": {
                "met_sla": sla_met_count,
                "breached_sla": sla_breached_count
            },
            "model_path": model_path,
            "top_features": feature_importance
        }
        
    @with_auth_client("jira")
    def predict_sla(self, client: AuthenticatedClient, issue_key: str = None, 
                   issue_data: Optional[Dict] = None) -> Dict:
        """
        Predict SLA breach risk for an issue.
        
        Args:
            client: Authenticated client
            issue_key: Jira issue key to predict (if issue_data not provided)
            issue_data: Issue data for prediction (optional)
            
        Returns:
            Dict containing SLA prediction results
        """
        if not issue_key and not issue_data:
            return {"error": "Either issue_key or issue_data must be provided"}
            
        # If issue_key is provided, fetch issue data
        if issue_key:
            response = client.request(
                "GET", 
                f"{os.environ.get('JIRA_URL')}/rest/api/2/issue/{issue_key}",
                params={"fields": "summary,description,issuetype,priority,components,labels,assignee,project"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch issue data: {response.text}")
                return {"error": f"Failed to fetch data for issue {issue_key}"}
                
            issue_data = response.json()
            
        # Extract project key
        if issue_key:
            project_key = issue_key.split("-")[0]
        else:
            project_key = issue_data.get("fields", {}).get("project", {}).get("key")
            
        if not project_key:
            return {"error": "Unable to determine project key"}
            
        # Load SLA prediction model
        model_name = f"{project_key}_sla_predictor"
        model_info = self._sla_prediction_models.get(model_name)
        
        if not model_info:
            # Try to load from disk
            model_path = os.path.join(self.models_dir, f"{model_name}.joblib")
            
            try:
                model_info = joblib.load(model_path)
                self._sla_prediction_models[model_name] = model_info
            except FileNotFoundError:
                return {
                    "error": f"No trained SLA prediction model found for {project_key}",
                    "recommendation": f"Train a model first using train_sla_predictor"
                }
                
        clf = model_info["model"]
        columns = model_info["columns"]
        
        # Extract features from issue
        fields = issue_data.get("fields", {})
        
        issue_type = fields.get("issuetype", {}).get("name", "Unknown")
        priority = fields.get("priority", {}).get("name", "Medium")
        
        # Convert priority to numeric
        priority_map = {"Highest": 5, "High": 4, "Medium": 3, "Low": 2, "Lowest": 1}
        priority_value = priority_map.get(priority, 3)
        
        # Text length features
        summary = fields.get("summary", "")
        description = fields.get("description", "") or ""
        summary_length = len(summary.split())
        description_length = len(description.split()) if description else 0
        
        # Component and label counts
        components = fields.get("components", [])
        labels = fields.get("labels", [])
        component_count = len(components)
        label_count = len(labels)
        
        # Has assignee
        assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
        has_assignee = 1 if assignee != "Unassigned" else 0
        
        # Create feature dictionary
        features = {
            "priority_value": priority_value,
            "summary_length": summary_length,
            "description_length": description_length,
            "component_count": component_count,
            "label_count": label_count,
            "has_assignee": has_assignee
        }
        
        # One-hot encode issue_type
        for col in columns:
            if col.startswith("issue_type_"):
                type_value = col.replace("issue_type_", "")
                features[col] = 1 if issue_type == type_value else 0
                
        # Create DataFrame with the same columns as training data
        import pandas as pd
        X_pred = pd.DataFrame([features])
        
        # Ensure all columns from training are present (with 0s if missing)
        for col in columns:
            if col not in X_pred.columns:
                X_pred[col] = 0
                
        # Reorder columns to match training data
        X_pred = X_pred[columns]
        
        # Make prediction
        prediction = clf.predict(X_pred)[0]
        
        # Get probability if available
        probability = None
        if hasattr(clf, 'predict_proba'):
            probability = clf.predict_proba(X_pred)[0][1]  # Probability of class 1 (SLA met)
            
        # Determine SLA hours based on priority
        sla_hours = {
            5: 8,    # Highest
            4: 24,   # High
            3: 48,   # Medium
            2: 72,   # Low
            1: 120   # Lowest
        }.get(priority_value, 48)
        
        # Calculate risk factors
        risk_factors = []
        
        if not has_assignee:
            risk_factors.append("No assignee")
            
        if description_length < 10:
            risk_factors.append("Insufficient description")
            
        if priority_value >= 4 and component_count == 0:
            risk_factors.append("High priority with no components specified")
            
        # Calculate recommended action
        if prediction == 1:  # SLA likely to be met
            if probability is not None and probability < 0.7:
                recommended_action = "Monitor - SLA may be met but with moderate risk"
            else:
                recommended_action = "Standard handling - SLA likely to be met"
        else:  # SLA breach risk
            if has_assignee:
                recommended_action = "Escalate to assignee - High risk of SLA breach"
            else:
                recommended_action = "Immediate assignment needed - High risk of SLA breach"
                
        return {
            "issue_key": issue_key if issue_key else "N/A",
            "project_key": project_key,
            "sla_prediction": "Will Meet SLA" if prediction == 1 else "At Risk of SLA Breach",
            "confidence": round(float(max(probability, 1-probability)), 3) if probability is not None else None,
            "target_sla_hours": sla_hours,
            "risk_factors": risk_factors,
            "recommended_action": recommended_action
        }
        
    def _analyze_text_sentiment(self, text: str) -> Dict:
        """Helper method to analyze sentiment in text."""
        if not text or len(text.strip()) == 0:
            return {
                "compound": 0,
                "pos": 0,
                "neg": 0,
                "neu": 1,
                "compound_category": "neutral"
            }
            
        # Get sentiment scores
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        
        # Determine sentiment category based on compound score
        if sentiment["compound"] >= 0.05:
            sentiment["compound_category"] = "positive"
        elif sentiment["compound"] <= -0.05:
            sentiment["compound_category"] = "negative"
        else:
            sentiment["compound_category"] = "neutral"
            
        return sentiment


# Create a global instance
ai_capabilities_manager = AICapabilitiesManager()