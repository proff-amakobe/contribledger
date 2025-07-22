import tensorflow as tf
import numpy as np
import time
import copy
from sklearn.model_selection import train_test_split
import subprocess
import json

class TensorFlowFederatedClient:
    def __init__(self, client_id, device_capability='medium'):
        self.client_id = client_id
        self.device_capability = device_capability
        self.model = None
        self.training_params = self._get_device_params()
        self.previous_weights = None
        self.previous_accuracy = 0.0
        
    def _get_device_params(self):
        """Device-specific parameters"""
        params = {
            'high': {'batch_size': 64, 'lr': 0.01, 'epochs': 10},
            'medium': {'batch_size': 32, 'lr': 0.005, 'epochs': 5},
            'low': {'batch_size': 16, 'lr': 0.001, 'epochs': 3}
        }
        return params.get(self.device_capability, params['medium'])
    
    def create_model(self):
        """Create CNN model for CIFAR-10"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.training_params['lr']),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def load_cifar10_data(self, client_data_fraction=0.1):
        """Load and preprocess CIFAR-10 data for this client"""
        (x_train_full, y_train_full), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
        
        # Normalize data
        x_train_full = x_train_full.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0
        
        # Create client-specific data split
        num_samples = int(len(x_train_full) * client_data_fraction)
        client_seed = hash(self.client_id) % 1000
        
        # Create non-IID split by class preference
        np.random.seed(client_seed)
        preferred_classes = np.random.choice(10, size=3, replace=False)  # Each client prefers 3 classes
        
        client_indices = []
        for class_idx in preferred_classes:
            class_indices = np.where(y_train_full.flatten() == class_idx)[0]
            client_indices.extend(np.random.choice(class_indices, min(num_samples//3, len(class_indices)), replace=False))
        
        # Add some random samples from other classes
        remaining_indices = np.setdiff1d(range(len(x_train_full)), client_indices)
        additional_samples = np.random.choice(remaining_indices, min(num_samples//4, len(remaining_indices)), replace=False)
        client_indices.extend(additional_samples)
        
        self.x_train = x_train_full[client_indices]
        self.y_train = y_train_full[client_indices]
        self.x_test = x_test[:1000]  # Small test set
        self.y_test = y_test[:1000]
        
        print(f"📊 {self.client_id}: Loaded {len(self.x_train)} training samples (preferred classes: {preferred_classes})")
        
        return self.x_train, self.y_train, self.x_test, self.y_test
    
    def train_local_model(self, global_weights=None):
        """Train model and calculate real metrics"""
        print(f"🔄 {self.client_id}: Training with TensorFlow...")
        
        if self.model is None:
            self.create_model()
        
        # Store previous weights
        if self.previous_weights is None:
            self.previous_weights = self.model.get_weights()
        
        # Load global weights if provided
        if global_weights is not None:
            self.model.set_weights(global_weights)
        
        # Training
        start_time = time.time()
        
        history = self.model.fit(
            self.x_train, self.y_train,
            batch_size=self.training_params['batch_size'],
            epochs=self.training_params['epochs'],
            validation_data=(self.x_test, self.y_test),
            verbose=0  # Silent training
        )
        
        training_time = time.time() - start_time
        
        # Evaluate
        test_loss, test_accuracy = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        test_accuracy *= 100  # Convert to percentage
        
        print(f"  📈 Test Accuracy: {test_accuracy:.2f}%")
        print(f"  ⏱️  Training Time: {training_time:.2f}s")
        
        # Calculate metrics
        metrics = self._calculate_tf_metrics(training_time, test_accuracy)
        
        return metrics
    
    def _calculate_tf_metrics(self, training_time, current_accuracy):
        """Calculate F-PoC metrics for TensorFlow"""
        current_weights = self.model.get_weights()
        
        # Weight update calculation
        weight_diff_norm = 0.0
        total_params = 0
        
        for i, (current, previous) in enumerate(zip(current_weights, self.previous_weights)):
            diff = current - previous
            weight_diff_norm += np.sum(diff ** 2)
            total_params += diff.size
        
        weight_update_norm = np.sqrt(weight_diff_norm / total_params)
        
        # Convergence speed
        convergence_speed = 1.0 / max(training_time, 0.1)
        
        # Accuracy improvement
        accuracy_improvement = max(0, current_accuracy - self.previous_accuracy)
        
        # Normalize
        normalized_metrics = {
            'weight_update': min(100, max(0, weight_update_norm * 500)),
            'convergence_speed': min(100, max(0, convergence_speed * 20)),
            'accuracy_improvement': min(100, max(0, accuracy_improvement * 3))
        }
        
        # Update for next round
        self.previous_weights = [w.copy() for w in current_weights]
        self.previous_accuracy = current_accuracy
        
        print(f"  📊 Normalized Metrics: W={normalized_metrics['weight_update']:.1f}, C={normalized_metrics['convergence_speed']:.1f}, A={normalized_metrics['accuracy_improvement']:.1f}")
        
        return {
            'normalized_metrics': normalized_metrics,
            'raw_metrics': {
                'weight_update_norm': weight_update_norm,
                'training_time': training_time,
                'accuracy_improvement': accuracy_improvement,
                'current_accuracy': current_accuracy
            },
            'model_weights': current_weights
        }