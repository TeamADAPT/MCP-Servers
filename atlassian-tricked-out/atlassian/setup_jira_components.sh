#!/bin/bash

# Script to set up Jira components for Echo Resonance project
echo "Setting up Jira components for the Echo Resonance project..."

# Create teams as components
echo "Creating team components..."
for component in $(cat team_components.json | jq -c '.[]'); do
  name=$(echo $component | jq -r '.name')
  description=$(echo $component | jq -r '.description')
  echo "Creating component: $name - $description"
done

# Create categories as components
echo "Creating category components..."
for category in $(cat project_categories.json | jq -c '.[]'); do
  name=$(echo $category | jq -r '.name')
  description=$(echo $category | jq -r '.description')
  echo "Creating component: $name - $description"
done

echo "Component setup prepared!"
