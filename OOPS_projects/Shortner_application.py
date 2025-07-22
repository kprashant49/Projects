from Shortner import *


myshortner = DictionaryShortner({1:"mike",2:"tom",3:"john",4:"kim"})
myshortner.print_original_items()
myshortner.print_shortened_items()

myshortner = ListAndCharShortner([1,2,3,4,5,6,7,8,9,10])
myshortner.print_original_items()
myshortner.print_shortened_items()

myshortner = ListAndCharShortner("Sliced")
myshortner.print_original_items()
myshortner.print_shortened_items()