import numpy as np
import subprocess
import json
import time
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

class FederatedLearningClientCLI:
    def __init__(self, client_id, blockchain_endpoint="http://localhost:1317"):
        self.client_id = client_id
        self.blockchain_endpoint = blockchain_endpoint
        self.model = LogisticRegression()
        self.previous_accuracy = 0.0
        
    def generate_local_data(self, n_samples=1000):
        """Generate synthetic local dataset"""
        X, y = make_classification(
            n_samples=n_samples, 
            n_features=20, 
            n_informative=10,
            n_redundant=5,
            random_state=hash(self.client_id) % 1000
        )
        return X, y
    
    def train_local_model(self, X, y):
        """Train model on local data and compute metrics"""
        start_time = time.time()
        
        # Store previous weights for comparison
        try:
            prev_weights = self.model.coef_.copy() if hasattr(self.model, 'coef_') else None
        except:
            prev_weights = None
            
        # Train model
        self.model.fit(X, y)
        training_time = time.time() - start_time
        
        # Calculate metrics
        accuracy = accuracy_score(y, self.model.predict(X))
        
        # Calculate weight update magnitude
        if prev_weights is not None:
            weight_change = np.linalg.norm(self.model.coef_ - prev_weights)
        else:
            weight_change = np.linalg.norm(self.model.coef_)
            
        return {
            'accuracy': accuracy,
            'training_time': training_time,
            'weight_change': weight_change
        }
    
    def normalize_metrics(self, metrics, global_stats=None):
        """Normalize metrics to 0-100 scale"""
        normalized = {
            'weight_update': min(100, int(metrics['weight_change'] * 10)),
            'convergence_speed': max(1, min(100, int(100 / max(0.1, metrics['training_time'])))),
            'accuracy_improvement': min(100, int((metrics['accuracy'] - self.previous_accuracy) * 1000 + 50))
        }
        
        # Ensure values are in 0-100 range
        for key in normalized:
            normalized[key] = max(0, min(100, normalized[key]))
            
        self.previous_accuracy = metrics['accuracy']
        return normalized
    
    def calculate_contribution_score(self, normalized_metrics):
        """Calculate contribution score using the formula"""
        score = (
            0.35 * normalized_metrics['weight_update'] +
            0.30 * normalized_metrics['convergence_speed'] +
            0.35 * normalized_metrics['accuracy_improvement']
        )
        return int(score)
    
    def submit_contribution_via_cli(self, normalized_metrics, contribution_score):
        """Submit contribution using CLI command"""
        try:
            # Use the exact CLI command that exists
            cmd = [
                "contribledgerd", "tx", "contrib", "submit-contribution",
                self.client_id,  # userID
                str(normalized_metrics['weight_update']),
                str(normalized_metrics['convergence_speed']),
                str(normalized_metrics['accuracy_improvement']),
                str(contribution_score),
                "--from", "alice",
                "--chain-id", "contribledger",
                "--yes",
                "--keyring-backend", "test",
                "--output", "json"
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get('code') == 0:
                    print(f"✅ Transaction successful: {response.get('txhash')}")
                    return response
                else:
                    print(f"❌ Transaction failed: {response.get('raw_log')}")
                    return None
            else:
                print(f"❌ CLI Error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting via CLI: {e}")
            return None
    
    def training_round(self):
        """Execute a complete training round"""
        print(f"Client {self.client_id}: Starting training round...")
        
        # Generate and train on local data
        X, y = self.generate_local_data()
        metrics = self.train_local_model(X, y)
        
        # Normalize metrics and calculate score
        normalized_metrics = self.normalize_metrics(metrics)
        contribution_score = self.calculate_contribution_score(normalized_metrics)
        
        print(f"Client {self.client_id}: Metrics = {normalized_metrics}, Score = {contribution_score}")
        
        # Submit to blockchain via CLI
        result = self.submit_contribution_via_cli(normalized_metrics, contribution_score)
        
        if result:
            print(f"Client {self.client_id}: ✅ Contribution submitted successfully")
        else:
            print(f"Client {self.client_id}: ❌ Failed to submit contribution")
            
        return {
            'metrics': normalized_metrics,
            'score': contribution_score,
            'model_weights': self.model.coef_.tolist() if hasattr(self.model, 'coef_') else None
        }

# Example usage
if __name__ == "__main__":
    client = FederatedLearningClientCLI("client001")
    result = client.training_round()
    print(f"Training round completed: {result}")