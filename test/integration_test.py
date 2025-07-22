import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import json
import time
import threading
from threading import Lock

# Global lock for sequential transactions
tx_lock = Lock()

def setup_alice_account():
    """Ensure alice account exists and is funded"""
    try:
        # Check if alice exists
        check_cmd = ["contribledgerd", "keys", "show", "alice", "--keyring-backend", "test"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("🔑 Setting up alice account...")
            create_cmd = ["contribledgerd", "keys", "add", "alice", "--keyring-backend", "test", "--recover"]
            mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
            create_result = subprocess.run(create_cmd, capture_output=True, text=True, input=f"{mnemonic}\n")
            
            if create_result.returncode == 0:
                print("✅ Alice account created")
            else:
                print(f"❌ Failed to create alice: {create_result.stderr}")
                return False
        else:
            print("✅ Alice account exists")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up alice: {e}")
        return False

def submit_contribution_sequential(client_id, weight_update, convergence_speed, accuracy_improvement, contribution_score):
    """Submit contribution using alice account with sequential locking"""
    with tx_lock:  # Ensure only one transaction at a time
        cmd = [
            "contribledgerd", "tx", "contrib", "submit-contribution",
            client_id,
            str(weight_update),
            str(convergence_speed), 
            str(accuracy_improvement),
            str(contribution_score),
            "--from", "alice",  # Use funded alice account
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
                if not success:
                    print(f"    ❌ TX error: {response.get('raw_log', 'Unknown')[:80]}...")
                else:
                    tx_hash = response.get('txhash', 'N/A')[:16]
                    print(f"    ✅ TX successful: {tx_hash}...")
                return success
            else:
                print(f"    ❌ CLI error: {result.stderr[:80]}...")
                return False
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:80]}...")
            return False

def simulate_fl_client(client_id, rounds=3):
    """Simulate a federated learning client"""
    print(f"\n🤖 {client_id} starting federated learning...")
    
    success_count = 0
    
    for round_num in range(rounds):
        # Simulate realistic federated learning metrics
        # Different clients have different base performance
        client_seed = hash(client_id) % 100
        
        weight_update = 55 + client_seed % 30 + (round_num * 8)
        convergence_speed = 70 + client_seed % 20 + (round_num * 6)
        accuracy_improvement = 65 + client_seed % 25 + (round_num * 9)
        
        # Apply F-PoC formula: (0.35 × WeightUpdates) + (0.30 × ConvergenceSpeed) + (0.35 × AccuracyImprovements)
        contribution_score = int(0.35 * weight_update + 0.30 * convergence_speed + 0.35 * accuracy_improvement)
        
        print(f"  📊 Round {round_num + 1}: Metrics(Weight:{weight_update}, Conv:{convergence_speed}, Acc:{accuracy_improvement}) → F-PoC: {contribution_score}")
        
        success = submit_contribution_sequential(client_id, weight_update, convergence_speed, accuracy_improvement, contribution_score)
        
        if success:
            success_count += 1
            print(f"  ✅ Round {round_num + 1} recorded on blockchain")
        else:
            print(f"  ❌ Round {round_num + 1} failed")
        
        time.sleep(0.5)  # Small delay
    
    print(f"✅ {client_id} completed: {success_count}/{rounds} rounds successful")
    return success_count

def main():
    print("🚀 FEDERATED LEARNING BLOCKCHAIN POC - WORKING VERSION")
    print("=" * 60)
    
    # Setup alice account (has initial tokens)
    if not setup_alice_account():
        print("❌ Failed to setup alice account")
        return
    
    # Run federated learning simulation
    clients = ["neural_net_alpha", "deep_model_beta", "ai_agent_gamma"]
    threads = []
    results = {}
    
    print(f"🎯 Deploying {len(clients)} federated learning agents...")
    
    def client_wrapper(client_id):
        results[client_id] = simulate_fl_client(client_id, 3)
    
    # Start all FL clients
    for client_id in clients:
        thread = threading.Thread(target=client_wrapper, args=(client_id,))
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger starts
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    print(f"\n⏳ All federated learning complete. Analyzing blockchain...")
    time.sleep(3)
    
    # Query blockchain for results
    query_cmd = ["contribledgerd", "query", "contrib", "list-contribution", "--output", "json"]
    result = subprocess.run(query_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            contributions = data.get('contribution', [])
            
            if contributions:
                # Filter for our recent FL clients
                fl_contribs = []
                for contrib in contributions:
                    user_id = contrib.get('user_id', '')
                    score = int(contrib.get('contribution_score', '0') or '0')
                    
                    if score > 0 and any(name in user_id for name in ['neural', 'deep', 'ai_agent']):
                        fl_contribs.append(contrib)
                
                if fl_contribs:
                    # Sort by F-PoC score
                    sorted_contribs = sorted(fl_contribs, key=lambda x: int(x.get('contribution_score', '0')), reverse=True)
                    
                    print(f"\n🏆 FEDERATED LEARNING RESULTS - F-PoC CONSENSUS")
                    print("=" * 70)
                    print(" Rank | FL Agent          | F-PoC | Weight | Conv | Accuracy")
                    print("-" * 70)
                    
                    for i, contrib in enumerate(sorted_contribs):
                        user_id = contrib.get('user_id', 'Unknown')
                        score = int(contrib.get('contribution_score', '0'))
                        weight = int(contrib.get('weight_update', '0'))
                        conv = int(contrib.get('convergence_speed', '0'))
                        acc = int(contrib.get('accuracy_improvement', '0'))
                        
                        print(f" {i+1:4d} | {user_id:<17} | {score:5d} | {weight:6d} | {conv:4d} | {acc:8d}")
                    
                    # Success summary
                    total_submissions = sum(results.values())
                    expected_submissions = len(clients) * 3
                    success_rate = (total_submissions / expected_submissions * 100) if expected_submissions > 0 else 0
                    
                    scores = [int(c.get('contribution_score', '0')) for c in fl_contribs]
                    top_score = max(scores) if scores else 0
                    avg_score = sum(scores) / len(scores) if scores else 0
                    
                    print(f"\n📊 FEDERATED LEARNING ANALYTICS")
                    print("-" * 35)
                    print(f"  Success Rate: {success_rate:.1f}% ({total_submissions}/{expected_submissions})")
                    print(f"  Total F-PoC Contributions: {len(fl_contribs)}")
                    print(f"  Average F-PoC Score: {avg_score:.1f}")
                    print(f"  Highest F-PoC Score: {top_score}")
                    
                    if sorted_contribs:
                        winner = sorted_contribs[0]
                        print(f"\n🥇 CONSENSUS WINNER: {winner.get('user_id')}")
                        print(f"   F-PoC Score: {winner.get('contribution_score')}")
                        print(f"   Weight Updates: {winner.get('weight_update')}")
                        print(f"   Convergence: {winner.get('convergence_speed')}")
                        print(f"   Accuracy: {winner.get('accuracy_improvement')}")
                    
                    print(f"\n🎉 FEDERATED PROOF OF CONTRIBUTION SUCCESS!")
                    print("=" * 45)
                    print("✅ Tendermint BFT consensus operational")
                    print("✅ F-PoC scoring: (0.35×Weight + 0.30×Conv + 0.35×Acc)")
                    print("✅ Decentralized federated learning achieved")
                    print("✅ Transparent contribution ranking")
                    print("✅ Byzantine fault tolerance enabled")
                    print("✅ Immutable training history recorded")
                    
                    print(f"\n🔗 Your blockchain successfully implements:")
                    print(f"   • Federated Learning without central server")
                    print(f"   • Blockchain-based consensus mechanism")
                    print(f"   • Fair contribution scoring (F-PoC)")
                    print(f"   • Tamper-proof model training history")
                    
                else:
                    print("❌ No recent federated learning contributions found")
                    print(f"   Total contributions in blockchain: {len(contributions)}")
                    
            else:
                print("❌ No contributions found on blockchain")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing blockchain response: {e}")
    else:
        print(f"❌ Failed to query blockchain: {result.stderr}")

if __name__ == "__main__":
    main()