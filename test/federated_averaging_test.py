import torch
import numpy as np
from clients.pytorch_fl_client import RealMLFederatedClient
import matplotlib.pyplot as plt
import seaborn as sns

def test_federated_averaging_quality():
    """Test quality of F-PoC weighted federated averaging"""
    print("🧪 Testing F-PoC Weighted Federated Averaging Quality")
    
    # Create multiple clients with different capabilities
    clients = []
    for i in range(4):
        client = RealMLFederatedClient(
            client_id=f"test_client_{i:03d}",
            dataset='cifar10',
            model_type='simple',
            device_capability=['low', 'medium', 'high', 'medium'][i]
        )
        client.load_data(non_iid_alpha=0.1 + i*0.2)  # Different data distributions
        clients.append(client)
    
    # Train each client for multiple rounds
    all_results = []
    
    for round_num in range(1, 4):
        round_results = {}
        round_weights = {}
        
        print(f"\n🔄 Federated Round {round_num}")
        
        for client in clients:
            result = client.train_local_model()
            f_poc_score = client.calculate_f_poc_score(result['normalized_metrics'])
            
            round_results[client.client_id] = {
                'f_poc_score': f_poc_score,
                'metrics': result,
                'accuracy': result['raw_metrics']['current_accuracy']
            }
            round_weights[client.client_id] = result['model_weights']
        
        # Perform federated averaging
        scores = {cid: r['f_poc_score'] for cid, r in round_results.items()}
        global_weights = federated_averaging_weighted(round_weights, scores)
        
        # Test global model performance
        global_accuracy = test_global_model_accuracy(global_weights, clients[0])
        
        print(f"  📊 Round {round_num} Results:")
        for cid, result in round_results.items():
            print(f"    {cid}: F-PoC={result['f_poc_score']:3d}, Accuracy={result['accuracy']:.1f}%")
        print(f"    🌐 Global Model Accuracy: {global_accuracy:.1f}%")
        
        all_results.append({
            'round': round_num,
            'client_results': round_results,
            'global_accuracy': global_accuracy,
            'global_weights': global_weights
        })
        
        # Update clients with global weights for next round
        for client in clients:
            if global_weights:
                client.model.load_state_dict(global_weights)
    
    return all_results

def federated_averaging_weighted(client_weights, client_scores):
    """Perform F-PoC weighted federated averaging"""
    if not client_weights:
        return None
    
    # Normalize scores to weights
    scores = np.array(list(client_scores.values()))
    if np.sum(scores) == 0:
        weights = np.ones(len(scores)) / len(scores)
    else:
        weights = scores / np.sum(scores)
    
    # Weighted average
    client_ids = list(client_weights.keys())
    averaged_state_dict = {}
    
    first_state_dict = client_weights[client_ids[0]]
    
    for param_name in first_state_dict:
        averaged_param = weights[0] * first_state_dict[param_name]
        
        for i, client_id in enumerate(client_ids[1:], 1):
            averaged_param += weights[i] * client_weights[client_id][param_name]
        
        averaged_state_dict[param_name] = averaged_param
    
    return averaged_state_dict

def test_global_model_accuracy(global_weights, reference_client):
    """Test accuracy of global model"""
    if global_weights is None:
        return 0.0
    
    # Load global weights into reference client's model
    reference_client.model.load_state_dict(global_weights)
    
    # Evaluate on test set
    accuracy = reference_client.evaluate_model()
    return accuracy