t = int(input())
ans_row = []
for _ in range(t):
    n, m = map(int, input().split())
    if m == 1:
        ans_row.append([0, n, m])
    elif n < m:
        ans_row.append([n + 1, n, m])
    elif n == m:
        ans_row.append([n, n, m])
    else:
        ans_row.append([m, n, m])
for case in ans_row:
    ans = case[0]
    n = case[1]
    m = case[2]
    print(ans)
    if m == 1:
        for _ in range(n):
            print(0)   
    elif n < m:
        for i in range(n):
            row = []
            for j in range(m):
                if j < n + 1:
                    row.append((i + j + 1) % (n + 1))
                else:
                    row.append(j)
            print(*row)
    else:
        for i in range(n):
            row = []
            for j in range(m):
                row.append((i + j + 1) % m)
            print(*row)
