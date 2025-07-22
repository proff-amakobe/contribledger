import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
import time
import copy
import subprocess
import json

class SimpleNN(nn.Module):
    """Simple neural network for CIFAR-10/MNIST"""
    def __init__(self, input_size=32*32*3, hidden_size=128, num_classes=10):
        super(SimpleNN, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, 64)
        self.fc3 = nn.Linear(64, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class ConvNet(nn.Module):
    """Convolutional Neural Network for image classification"""
    def __init__(self, num_classes=10):
        super(ConvNet, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 64 * 4 * 4)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

class RealMLFederatedClient:
    def __init__(self, client_id, dataset='cifar10', model_type='simple', device_capability='medium'):
        self.client_id = client_id
        self.dataset = dataset
        self.model_type = model_type
        self.device_capability = device_capability
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model based on type
        if dataset == 'cifar10':
            if model_type == 'simple':
                self.model = SimpleNN(input_size=32*32*3, num_classes=10)
            else:
                self.model = ConvNet(num_classes=10)
        elif dataset == 'mnist':
            self.model = SimpleNN(input_size=28*28*1, num_classes=10)
        
        self.model.to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        
        # Device-specific training parameters
        self.training_params = self._get_device_params()
        
        # Store training history
        self.training_history = []
        self.previous_weights = None
        self.previous_accuracy = 0.0
        
    def _get_device_params(self):
        """Simulate different device capabilities"""
        params = {
            'high': {'batch_size': 64, 'lr': 0.01, 'epochs': 5, 'data_samples': 2000},
            'medium': {'batch_size': 32, 'lr': 0.005, 'epochs': 3, 'data_samples': 1000},
            'low': {'batch_size': 16, 'lr': 0.001, 'epochs': 2, 'data_samples': 500}
        }
        return params.get(self.device_capability, params['medium'])
    
    def load_data(self, client_data_fraction=0.1, non_iid_alpha=0.5):
        """Load realistic federated data with non-IID distribution"""
        if self.dataset == 'cifar10':
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ])
            
            full_dataset = torchvision.datasets.CIFAR10(
                root='./data', train=True, download=True, transform=transform
            )
            test_dataset = torchvision.datasets.CIFAR10(
                root='./data', train=False, download=True, transform=transform
            )
            
        elif self.dataset == 'mnist':
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
            
            full_dataset = torchvision.datasets.MNIST(
                root='./data', train=True, download=True, transform=transform
            )
            test_dataset = torchvision.datasets.MNIST(
                root='./data', train=False, download=True, transform=transform
            )
        
        # Create non-IID data distribution for this client
        train_indices = self._create_non_iid_split(full_dataset, non_iid_alpha)
        test_indices = list(range(min(1000, len(test_dataset))))  # Small test set
        
        self.train_dataset = Subset(full_dataset, train_indices)
        self.test_dataset = Subset(test_dataset, test_indices)
        
        self.train_loader = DataLoader(
            self.train_dataset, 
            batch_size=self.training_params['batch_size'], 
            shuffle=True
        )
        self.test_loader = DataLoader(
            self.test_dataset, 
            batch_size=32, 
            shuffle=False
        )
        
        print(f"📊 {self.client_id}: Loaded {len(self.train_dataset)} training samples, {len(self.test_dataset)} test samples")
    
    def _create_non_iid_split(self, dataset, alpha):
        """Create non-IID data split using Dirichlet distribution"""
        num_classes = 10
        num_samples = self.training_params['data_samples']
        
        # Get labels
        if hasattr(dataset, 'targets'):
            labels = np.array(dataset.targets)
        else:
            labels = np.array([dataset[i][1] for i in range(len(dataset))])
        
        # Create Dirichlet distribution for non-IID split
        client_seed = hash(self.client_id) % 1000
        np.random.seed(client_seed)
        
        proportions = np.random.dirichlet([alpha] * num_classes)
        
        # Sample data according to proportions
        selected_indices = []
        for class_idx in range(num_classes):
            class_indices = np.where(labels == class_idx)[0]
            num_class_samples = int(proportions[class_idx] * num_samples)
            
            if len(class_indices) > 0 and num_class_samples > 0:
                selected_class_indices = np.random.choice(
                    class_indices, 
                    min(num_class_samples, len(class_indices)), 
                    replace=False
                )
                selected_indices.extend(selected_class_indices)
        
        # Pad if necessary
        if len(selected_indices) < num_samples:
            remaining_indices = np.setdiff1d(range(len(dataset)), selected_indices)
            additional_needed = num_samples - len(selected_indices)
            if len(remaining_indices) > 0:
                additional = np.random.choice(
                    remaining_indices, 
                    min(additional_needed, len(remaining_indices)), 
                    replace=False
                )
                selected_indices.extend(additional)
        
        return selected_indices[:num_samples]
    
    def train_local_model(self, global_weights=None):
        """Train model locally and compute real metrics"""
        print(f"🔄 {self.client_id}: Starting training round...")
        
        # Store previous weights for comparison
        if self.previous_weights is None and global_weights is not None:
            self.previous_weights = copy.deepcopy(global_weights)
        elif self.previous_weights is None:
            self.previous_weights = copy.deepcopy(self.model.state_dict())
        
        # Load global weights if provided
        if global_weights is not None:
            self.model.load_state_dict(global_weights)
        
        # Training setup
        optimizer = optim.SGD(
            self.model.parameters(), 
            lr=self.training_params['lr'], 
            momentum=0.9,
            weight_decay=1e-4
        )
        
        self.model.train()
        start_time = time.time()
        total_loss = 0.0
        num_batches = 0
        
        # Training loop
        for epoch in range(self.training_params['epochs']):
            epoch_loss = 0.0
            for batch_idx, (data, target) in enumerate(self.train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            total_loss += epoch_loss
            print(f"  Epoch {epoch+1}/{self.training_params['epochs']}: Loss = {epoch_loss/len(self.train_loader):.4f}")
        
        training_time = time.time() - start_time
        avg_loss = total_loss / num_batches
        
        # Evaluate model
        accuracy = self.evaluate_model()
        
        # Calculate real metrics
        metrics = self._calculate_real_metrics(training_time, accuracy)
        
        return metrics
    
    def evaluate_model(self):
        """Evaluate model on test set"""
        self.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in self.test_loader:
                data, target = data.to(self.device), target.to(self.device)
                outputs = self.model(data)
                _, predicted = torch.max(outputs.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
        
        accuracy = 100 * correct / total
        print(f"  📈 {self.client_id}: Test Accuracy = {accuracy:.2f}%")
        return accuracy
    
    def _calculate_real_metrics(self, training_time, current_accuracy):
        """Calculate real F-PoC metrics from actual training"""
        current_weights = self.model.state_dict()
        
        # 1. Weight Update Magnitude (L2 norm of weight differences)
        weight_update_norm = 0.0
        param_count = 0
        
        for name, param in current_weights.items():
            if name in self.previous_weights:
                diff = param - self.previous_weights[name]
                weight_update_norm += torch.norm(diff).item() ** 2
                param_count += param.numel()
        
        weight_update_norm = np.sqrt(weight_update_norm) / np.sqrt(param_count)
        
        # 2. Convergence Speed (inverse of training time, normalized)
        # Faster training = higher score
        convergence_speed = 1.0 / max(training_time, 0.1)  # Avoid division by zero
        
        # 3. Accuracy Improvement
        accuracy_improvement = max(0, current_accuracy - self.previous_accuracy)
        
        # Normalize metrics to 0-100 scale using realistic ranges
        normalized_metrics = {
            'weight_update': min(100, max(0, weight_update_norm * 1000)),  # Scale weight norms
            'convergence_speed': min(100, max(0, convergence_speed * 10)),  # Scale speed
            'accuracy_improvement': min(100, max(0, accuracy_improvement * 2))  # Scale accuracy diff
        }
        
        # Store for next round
        self.previous_weights = copy.deepcopy(current_weights)
        self.previous_accuracy = current_accuracy
        
        print(f"  📊 Raw Metrics: Weight Δ={weight_update_norm:.4f}, Speed={convergence_speed:.2f}, Acc Δ={accuracy_improvement:.2f}%")
        print(f"  📊 Normalized: W={normalized_metrics['weight_update']:.1f}, C={normalized_metrics['convergence_speed']:.1f}, A={normalized_metrics['accuracy_improvement']:.1f}")
        
        return {
            'raw_metrics': {
                'weight_update_norm': weight_update_norm,
                'training_time': training_time,
                'accuracy_improvement': accuracy_improvement,
                'current_accuracy': current_accuracy
            },
            'normalized_metrics': normalized_metrics,
            'model_weights': current_weights
        }
    
    def calculate_f_poc_score(self, normalized_metrics):
        """Calculate F-PoC score using the established formula"""
        score = (
            0.35 * normalized_metrics['weight_update'] +
            0.30 * normalized_metrics['convergence_speed'] +
            0.35 * normalized_metrics['accuracy_improvement']
        )
        return int(score)
    
    def submit_to_blockchain(self, normalized_metrics, f_poc_score):
        """Submit real ML metrics to blockchain"""
        cmd = [
            "contribledgerd", "tx", "contrib", "submit-contribution",
            self.client_id,
            str(int(normalized_metrics['weight_update'])),
            str(int(normalized_metrics['convergence_speed'])),
            str(int(normalized_metrics['accuracy_improvement'])),
            str(f_poc_score),
            "--from", "alice",
            "--chain-id", "contribledger",
            "--yes",
            "--keyring-backend", "test",
            "--output", "json",
            "--gas", "200000",
            "--fees", "1000stake"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                response = json.loads(result.stdout)
                success = response.get('code', 1) == 0
                if success:
                    print(f"  ✅ {self.client_id}: F-PoC score {f_poc_score} recorded on blockchain")
                else:
                    print(f"  ❌ {self.client_id}: Blockchain error: {response.get('raw_log', 'Unknown')[:50]}...")
                return success
            else:
                print(f"  ❌ {self.client_id}: CLI error: {result.stderr[:50]}...")
                return False
        except Exception as e:
            print(f"  ❌ {self.client_id}: Exception: {str(e)[:50]}...")
            return False
    
    def federated_learning_round(self, round_num, global_weights=None):
        """Execute one complete federated learning round"""
        print(f"\n🔄 {self.client_id} - Round {round_num}")
        print("-" * 40)
        
        # Train local model
        metrics = self.train_local_model(global_weights)
        
        # Calculate F-PoC score
        f_poc_score = self.calculate_f_poc_score(metrics['normalized_metrics'])
        
        print(f"  🏆 F-PoC Score: {f_poc_score}")
        
        # Submit to blockchain
        success = self.submit_to_blockchain(metrics['normalized_metrics'], f_poc_score)
        
        return {
            'success': success,
            'f_poc_score': f_poc_score,
            'metrics': metrics,
            'model_weights': metrics['model_weights']
        }

# Example usage
if __name__ == "__main__":
    # Create a real ML federated client
    client = RealMLFederatedClient(
        client_id="real_ml_client_001",
        dataset='cifar10',
        model_type='conv',
        device_capability='medium'
    )
    
    # Load data
    client.load_data(non_iid_alpha=0.1)  # Highly non-IID
    
    # Run a training round
    result = client.federated_learning_round(1)
    print(f"Round completed: {result}")