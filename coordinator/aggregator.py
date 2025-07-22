import requests
import numpy as np
import json
import time
from typing import List, Dict

class ModelAggregator:
    def __init__(self, blockchain_endpoint="http://localhost:1317"):
        self.blockchain_endpoint = blockchain_endpoint
        self.global_model_weights = None
        
    def fetch_contributions(self, min_score=0):
        """Fetch contributions from blockchain using the generated API"""
        try:
            # Use the generated REST endpoint for listing contributions
            response = requests.get(f"{self.blockchain_endpoint}/contribledger/contrib/contribution")
            data = response.json()
            
            contributions = []
            # The response structure will be different based on generated code
            if 'contribution' in data:
                for contrib in data['contribution']:
                    if int(contrib['contributionScore']) >= min_score:
                        contributions.append(contrib)
            elif 'Contribution' in data:  # Alternative field name
                for contrib in data['Contribution']:
                    if int(contrib['contributionScore']) >= min_score:
                        contributions.append(contrib)
                        
            # Sort by contribution score (descending)
            contributions.sort(key=lambda x: int(x['contributionScore']), reverse=True)
            return contributions
        except Exception as e:
            print(f"Error fetching contributions: {e}")
            return []
    
    def select_top_contributors(self, contributions, top_k=5):
        """Select top K contributors based on score"""
        return contributions[:top_k]
    
    def aggregate_models(self, selected_contributions, client_weights):
        """Aggregate model weights using federated averaging"""
        if not selected_contributions or not client_weights:
            return None
            
        # Weight by contribution score
        total_score = sum(int(c['contributionScore']) for c in selected_contributions)
        
        aggregated_weights = None
        for contrib in selected_contributions:
            user_id = contrib['userID']
            if user_id in client_weights:
                weight = int(contrib['contributionScore']) / total_score
                
                if aggregated_weights is None:
                    aggregated_weights = np.array(client_weights[user_id]) * weight
                else:
                    aggregated_weights += np.array(client_weights[user_id]) * weight
                    
        return aggregated_weights.tolist() if aggregated_weights is not None else None
    
    def compute_model_hash(self, weights):
        """Compute hash of model weights for blockchain storage"""
        import hashlib
        weights_str = json.dumps(weights, sort_keys=True)
        return hashlib.sha256(weights_str.encode()).hexdigest()
    
    def coordination_round(self, client_weights: Dict[str, List[float]], top_k=5):
        """Execute a coordination round"""
        print("Starting coordination round...")
        
        # Fetch contributions
        contributions = self.fetch_contributions()
        print(f"Fetched {len(contributions)} contributions")
        
        if not contributions:
            print("No contributions found")
            return None
            
        # Select top contributors
        selected = self.select_top_contributors(contributions, top_k)
        print(f"Selected top {len(selected)} contributors")
        
        # Aggregate models
        aggregated_weights = self.aggregate_models(selected, client_weights)
        
        if aggregated_weights:
            model_hash = self.compute_model_hash(aggregated_weights)
            print(f"Aggregated model hash: {model_hash}")
            
            self.global_model_weights = aggregated_weights
            
            return {
                'global_weights': aggregated_weights,
                'model_hash': model_hash,
                'contributors': [c['userID'] for c in selected],
                'total_score': sum(int(c['contributionScore']) for c in selected)
            }
        else:
            print("Failed to aggregate models")
            return None

# Example usage
if __name__ == "__main__":
    aggregator = ModelAggregator()
    
    # Mock client weights for testing
    mock_weights = {
        "client001": [0.1, 0.2, 0.3, 0.4],
        "client002": [0.2, 0.3, 0.4, 0.5],
        "client003": [0.3, 0.4, 0.5, 0.6]
    }
    
    result = aggregator.coordination_round(mock_weights)
    if result:
        print(f"Coordination completed: {result}")