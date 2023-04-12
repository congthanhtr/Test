def pickingNumbers(a):
    # Write your code here
    sorted_a = sorted(a)
    break_time = 0
    max_len = 1
    result = 0
    for i in range(1, len(a)):
        # print(sorted_a[i])
        # print(sorted_a[break_time])
        if abs(sorted_a[i] - sorted_a[break_time]) > 1:
            break_time = i
            result = max(result, max_len)
            max_len = 1
        else:
            max_len+=1

    return max(result, max_len)

print(pickingNumbers([4, 6, 5, 3, 3, 1]))