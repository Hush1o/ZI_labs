import math

m = pow(2,25) - 1
a = pow(12,3)
c = 987
x0 = 11

def gcd(a,b) :
    if b > a :
        a,b = b,a
    while True :
        r = a % b
        if r > 0 :
            a, b = b, r
        else :
            return b

def next_x(x):
    return (a * x + c) % m

def generate_N_sequence(n, start = x0):
    sequence = []
    x = start
    for _ in range(n):
        x = next_x(x)
        sequence.append(x)
    return sequence

def chesaro(sequence) :
    pairs = len(sequence) // 2
    count = 0
    for i in range(0, pairs * 2,2) :
        if gcd(sequence[i], sequence[i+1]) == 1 :
            count += 1

    if count == 0 : return 0
    else :
        prob = count / pairs
        if prob == 0 : return 0
        return math.sqrt(6/prob)

def period(start = x0) :
    visited = {}
    cur = start
    for i in range(m + 5) :
        cur = (a * cur + c) % m
        if cur in visited :
            return i - visited[cur]
        visited[cur] = i
    return -1