a = "MONKEY"
b = "MONEY"

n = len(a)
m = len(b)

dp = [[0] * (m + 1) for i in range(n + 1)]

# First row
for i in range(n + 1):
    dp[i][0] = i

# First column
for j in range(m + 1):
    dp[0][j] = j

# Fill DP table
for i in range(1, n + 1):
    for j in range(1, m + 1):

        if a[i - 1] == b[j - 1]:
            dp[i][j] = dp[i - 1][j - 1]

        else:
            dp[i][j] = min(
                dp[i - 1][j],
                dp[i][j - 1],
                dp[i - 1][j - 1]
            ) + 1

print("Edit Distance =", dp[n][m])