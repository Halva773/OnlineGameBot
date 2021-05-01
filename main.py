def gap(g, m, n):
    get_primes(m, n)  # m < n
    for i in range(1, len(primes)):
        if primes[i] - primes[i - 1] == g:
            return [primes[i - 1], primes[i]]
    return None
primes = []
def get_primes(m, n):
    numbers = set(range(n, 1, -1))
    while numbers:
        p = numbers.pop()
        if m <= p <= n:
            primes.append(p)
        numbers.difference_update(set(range(p * 2, n + 1, p)))


print(gap(2, 100, 110))
