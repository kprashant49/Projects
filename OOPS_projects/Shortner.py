class Shortner:
    def __init__(self,items):
        self.original_items = items

    def print_original_items(self):
        print(self.original_items)

class ListAndCharShortner(Shortner):
    def print_shortened_items(self):
        print(self.original_items[0:3])

class DictionaryShortner(Shortner):
    def print_shortened_items(self):
        dict = self.original_items
        counter = 0
        result_dict = {}
        for (k,v) in dict.items():
            if(counter <3):
                result_dict.update({k:v})
                counter +=1
        print(result_dict)