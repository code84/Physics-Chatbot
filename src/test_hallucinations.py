import time
from retrieve import setup_rag_pipeline

def run_test_suite():
    print("Initializing RAG Engine for Automated Testing...\n")
    chain, _ = setup_rag_pipeline()
    
    # 20 Test Questions (Mix of Physics, Out-of-Scope, and Nonsense)
    test_suite = [
        {"q": "What is Newton's First Law?", "type": "Physics"},
        {"q": "How do you calculate kinetic energy?", "type": "Physics"},
        {"q": "What is the formula for gravitational force?", "type": "Physics"},
        {"q": "Define Hooke's Law.", "type": "Physics"},
        {"q": "What is the speed of light in a vacuum?", "type": "Physics"},
        {"q": "Explain the conservation of momentum.", "type": "Physics"},
        {"q": "What is Coulomb's Law?", "type": "Physics"},
        {"q": "Describe Ohm's Law.", "type": "Physics"},
        {"q": "What is a magnetic field?", "type": "Physics"},
        {"q": "Explain the Doppler effect.", "type": "Physics"},
        
        # Out-of-Scope Questions (Testing Guardrails)
        {"q": "How do I bake a chocolate cake?", "type": "Out-of-Scope"},
        {"q": "What is the capital of France?", "type": "Out-of-Scope"},
        {"q": "Write a Python script for a calculator.", "type": "Out-of-Scope"},
        {"q": "Who won the World Cup in 2022?", "type": "Out-of-Scope"},
        {"q": "What is the best way to invest in stocks?", "type": "Out-of-Scope"},
        {"q": "How do I fix a leaky faucet?", "type": "Out-of-Scope"},
        {"q": "Write a poem about the ocean.", "type": "Out-of-Scope"},
        {"q": "What is the plot of the movie Inception?", "type": "Out-of-Scope"},
        {"q": "How do you train a dog to sit?", "type": "Out-of-Scope"},
        {"q": "Give me a recipe for scrambled eggs.", "type": "Out-of-Scope"}
    ]

    passed_tests = 0
    total_tests = len(test_suite)

    print("--- STARTING EVALUATION SUITE ---\n")

    for i, test in enumerate(test_suite):
        print(f"Test {i+1}/{total_tests}: {test['q']}")
        try:
            response = chain.invoke(test['q'])
            
            # Validation Logic
            if test['type'] == "Out-of-Scope":
                # The prompt rule says it must firmly refuse
                if "I am a physics assistant" in response or "cannot answer" in response:
                    print("✅ PASS: Correctly refused out-of-scope question.")
                    passed_tests += 1
                else:
                    print(f"❌ FAIL: Hallucinated an answer: {response[:50]}...")
            else:
                # Physics questions should not be refused
                if "I am a physics assistant" not in response:
                    print("✅ PASS: Answered physics question.")
                    passed_tests += 1
                else:
                    print("❌ FAIL: Refused a valid physics question.")
                    
        except Exception as e:
            print(f"❌ ERROR on question: {e}")
            
        time.sleep(1) # Prevent hitting API rate limits

    precision = (passed_tests / total_tests) * 100
    print("\n--- EVALUATION COMPLETE ---")
    print(f"Total Questions: {total_tests}")
    print(f"Passed Guardrails: {passed_tests}")
    print(f"System Precision: {precision}%")

if __name__ == "__main__":
    run_test_suite()