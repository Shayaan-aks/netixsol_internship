length = int(input("enter the length of the numbers"))
for i in range(length):
    nums = list(map(int, input("Enter numbers separated by spaces: ").split()))

mean = sum(nums) / len(nums)

sorted_nums = sorted(nums)
n = len(sorted_nums)

if n % 2 == 1:
    median = sorted_nums[n // 2]
else:
    median = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2

frequency = {}

for num in nums:
    if num in frequency:
        frequency[num] += 1
    else:
        frequency[num] = 1

highest_frequency = max(frequency.values())

mode = []

for key, value in frequency.items():
    if value == highest_frequency:
        mode.append(key)

minimum = nums[0]
maximum = nums[0]

for num in nums:
    if num < minimum:
        minimum = num

    if num > maximum:
        maximum = num

print("Mean   :", mean)
print("Median :", median)
print("Mode   :", mode)
print("Min    :", minimum)
print("Max    :", maximum)
