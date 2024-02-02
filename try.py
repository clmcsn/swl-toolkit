from itertools import product, chain

def new_code(A,B):
    # Use itertools.product to generate all combinations
    cA = product(*A)
    cB = [tuple(B[j][i] for j in range(len(B))) for i in range(len(B[0]))]
    cC = [tuple(C[j][i] for j in range(len(C))) for i in range(len(C[0]))]
    result = product(cA, cB)
    result = product(result, cC)
    result = [tuple(chain(*x)) for x in result]
    return result

# Example usage:
A = [[1, 2], ['a', 'b']]
B = [[2, 3], [4, 5]]
C = [[1, 2, 3], ['a', 'b', 'c']]

result = new_code(A, B)
print(result)
