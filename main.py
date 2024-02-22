numbers = input("Enter a list of numbers separated by spaces ")

numList = [int(num) for num in numbers.split()]




def classify_numbers(numList):
    evenNumbers = []
    oddNumbers = []
    for num in numList:
        if num % 2 == 0:
            evenNumbers.append(num)
        else:
            oddNumbers.append(num)
    return evenNumbers, oddNumbers


evenNumbers, oddNumbers = classify_numbers(numList)

print(evenNumbers)
print(oddNumbers)
