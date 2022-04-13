# Ruby is a popular, general-purpose programming language.
# You may have heard of it in connection to Ruby on Rails, one of the most popular web development frameworks in any programming language.
# Although much of Ruby's popularity comes from this connection, 
# Ruby has many uses, including web scraping, static site generation, command-line tools, automation, DevOps, and data processing.


#Find sum of Two Numbers
#-----------------------------------------------------------------------
def sum_eq_n?(arr, n)
    return true if arr.empty? && n == 0
    arr.product(arr).reject { |a,b| a == b }.any? { |a,b| a + b == n }
  end

# find the missing number in an arithmetic sequence
#-----------------------------------------------------------------------
differences = [2, 2, 4]
differences.max_by { |n| differences.count(n) }
# 2is the increase between numbers in the sequence
def find_missing(sequence)
    consecutive     = sequence.each_cons(2)
    differences     = consecutive.map { |a,b| b - a }
    sequence        = differences.max_by { |n| differences.count(n) }
    missing_between = consecutive.find { |a,b| (b - a) != sequence }
    missing_between.first + sequence
  end
  find_missing([2,4,6,10])
  # Should be 8

#Find out if a given string follows a pattern of VOWEL to NON-VOWEL characters.
#-----------------------------------------------------------------------
  def alternating_characters?(s)
    type = [/[aeiou]/, /[^aeiou]/].cycle
    if s.start_with?(/[^aeiou]/)
      type.next
    end
    s.chars.all? { |ch| ch.match?(type.next) }
  end
  alternating_characters?("ateciyu")
  # Should be true

#find out the “Power Set” of a given array.
#The power Set is a set of all the subsets that can be created from the array.
#-----------------------------------------------------------------------
#Recursion:
  def get_numbers(list, index = 0, taken = [])
    return [taken] if index == list.size
    get_numbers(list, index+1, taken) +
    get_numbers(list, index+1, taken + [list[index]])
  end
  get_numbers([1,2,3])

  #Stack:
  def get_numbers_stack(list)
    stack  = [[0, []]]
    output = []
  
    until stack.empty?
      index, taken = stack.pop
  
      next output << taken if index == list.size
  
      stack.unshift [index + 1, taken]
      stack.unshift [index + 1, taken + [list[index]]]
    end
  
    output
  end