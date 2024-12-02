import hashlib
from qiskit import QuantumCircuit, Aer, execute
import numpy as np
import random

# STEP1: Create a random bit string and a random basis sequence
#Z basis: |0> and |1>, Computational basis
#X basis: |+> and |->, Hadamard basis
def create_random_bit_and_basis(length):
    # Random bits(0 and 1)
    bits = np.random.randint(2, size=length)
    # Random basis(0 for Z basis, 1 for X basis
    basis = np.random.randint(2, size=length)
    return bits, basis

# STEP2: Encode the bit string using the basis sequence
def encode_bit_sequence(bit_sequence, basis_sequence, length):
    qc = QuantumCircuit(length, length)

    for i in range(length):
        if basis_sequence[i] == 0:
            qc.x(i)
        elif basis_sequence[i] == 1:
            if bit_sequence[i] == 0:
                qc.h(i)
            else: 
                qc.x(i) # default basis is |0> so we need to flip the bit
                qc.h(i)
    return qc

# STEP3: Measure the qubits
def bob_measure(prepared_circuit, bob_basis_sequence, length):
    qc = prepared_circuit.copy() # Copy the circuit Alice prepared

    for i in range(length):
        if bob_basis_sequence[i] == 1:
            qc.h(i) # Apply Hadamard gate to change to Z basis

        qc.measure(i, i)

    simulator = Aer.get_backend('qasm_simulator')
    job = execute(qc, simulator, shots=1)
    result = job.result()
    measured_bit_sequence = list(result.get_counts().keys())[0]

    return measured_bit_sequence

#STEP4: Compare the basis sequence
def basis_matching(alice_basis_sequence, bob_basis_sequence):
    matching_basis = [i for i in range(length) if alice_basis_sequence[i] == bob_basis_sequence[i]]
    alice_shared_key = [alice_basis_sequence[i] for i in matching_basis]
    bob_shared_key = [bob_basis_sequence[i] for i in matching_basis]
    return matching_basis, alice_shared_key, bob_shared_key

#STEP5: Error correction
def error_correction(alice_key, bob_key, check_fraction = 0.2):
    '''
    Check if the shared key is correct
    check_fraction: Fraction of the key to check, default is 0.2
    '''
    num_check_bits = round(check_fraction * len(bob_key))
    check_indices = random.sample(range(len(bob_key)), num_check_bits)

    mismatch = 0
    for i in check_indices:
        if bob_key[i] != alice_key[i]:
            mismatch += 1
    
    error_rate = mismatch / num_check_bits

    # Clean the key
    bob_clear_key = [bob_key[i] for i in range(len(bob_key)) if i not in check_indices]
    alice_clear_key = [alice_key[i] for i in range(len(alice_key)) if i not in check_indices]

    return error_rate, bob_clear_key, alice_clear_key, check_indices

# STEP6: Privacy Amplification

def privacy_amplification(bob_clear_key, alice_clear_key, final_key_length):
    '''
    clear_key: The key after error correction
    final_key_length: The length of the final key
    '''
    #hash function(random matrix)
    random_matrix = np.random.randint(2, size=(final_key_length, len(bob_clear_key)))
    bob_final_key = np.dot(random_matrix, bob_clear_key) % 2
    alice_final_key = np.dot(random_matrix, alice_clear_key) % 2

    return bob_final_key, alice_final_key

# STEP7: Key Confirmation
def key_confirmation(alice_final_key, bob_final_key):
    '''
    Check if the shared key is correct
    '''
    # Convert keys to strings for hashing
    alice_key_str = ''.join(map(str, alice_final_key))
    bob_key_str = ''.join(map(str, bob_final_key))

    # Compute hashes
    alice_hash = hashlib.sha256(alice_key_str.encode()).hexdigest()
    bob_hash = hashlib.sha256(bob_key_str.encode()).hexdigest()
    
    return alice_hash == bob_hash, alice_hash, bob_hash


length = 136 # Length of the bit string
bit_sequence, alice_basis_sequence = create_random_bit_and_basis(length)

print("Bit sequence: ", bit_sequence)

qc = encode_bit_sequence(bit_sequence, alice_basis_sequence, length)

#Generate random basis sequence for Bob
bob_basis_sequence = np.random.randint(2, size=length)
measured_bit_sequence = bob_measure(qc, bob_basis_sequence, length)

matching_basis, alice_shared_key, bob_shared_key = basis_matching(alice_basis_sequence, bob_basis_sequence)
error_rate, bob_clear_key, alice_clear_key, check_indices = error_correction(alice_shared_key, bob_shared_key)


print(f"Alice's Basis Sequence: {alice_basis_sequence}")
print(f"Bob's Basis Sequence: {bob_basis_sequence}")
print(f"Bob's Measured Bits: {measured_bit_sequence}")
print(f"Matching Indices: {matching_basis}")
print(f"Shared Key: {alice_shared_key}") # Alice and Bob can use this key for secure communication
print(f'Error rate:{error_rate}')
print(f'Check indices: {check_indices}')
print(f'Bob clear key: {bob_clear_key}')
print(f'Alice clear key: {alice_clear_key}')

final_key_length = 10

# Perform privacy amplification
bob_final_key, alice_final_key = privacy_amplification(bob_clear_key, alice_clear_key, final_key_length)

print(f"Bob Final Key (Privacy Amplification): {bob_final_key}")
print(f"Alice Final Key (Privacy Amplification): {alice_final_key}")

key_match, alice_hash, bob_hash = key_confirmation(alice_final_key, bob_final_key)

if key_match:
    print("Key matched!")
else:
    print("Key did not match!")