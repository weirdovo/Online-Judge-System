a = set(map(int, input().split()))
b = set(map(int, input().split()))
a = a.union(b)
print(*(x for x in a))