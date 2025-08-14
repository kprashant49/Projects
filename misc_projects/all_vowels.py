def all_vowels(string):
 return	len({char for char in string if char in 'aeiou'}) == 5

if __name__ == '__main__':
	print(all_vowels(input("Hi, please enter your string! ")))