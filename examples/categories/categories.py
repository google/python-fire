"""
This module demonstrates the use of categories in Fire.
Categories seperate GROUPS and COMMANDS into logical groups.
The effect is that the CLI is more organized and easier to navigate,
but only visually, as the command structure is not modified.
"""

import os
import fire

class GroupDemoClass:
  def __init__(self):
    pass

  def test1(self):
    print("test1")

  def test2(self):
    print("test2")

  def test3(self):
    print("test3")

class CategoryDemo:
  # Groups category is "uncategorized" -> will be displayed as "GROUPS" in the CLI
  group1 = GroupDemoClass()

  # Groups category is "GroupA"
  group2 = GroupDemoClass()
  group2.__fire_category__ = "A"
  group3 = GroupDemoClass()
  group3.__fire_category__ = "A"

  # Groups category is "GroupB"
  group4 = GroupDemoClass()
  group4.__fire_category__ = "B"
  group5 = GroupDemoClass()
  group5.__fire_category__ = "B"

  def __init__(self):
    self.greeting = "Hello, World!"

  @fire.helptext.CommandCategory("hello")
  def greet(self):
    print(self.greeting)

  @fire.helptext.CommandCategory("hello")
  def greet2(self):
    print(self.greeting)

  @fire.helptext.CommandCategory("bye")
  def farewell(self):
    print("Goodbye, World!")

  @fire.helptext.CommandCategory("bye")
  def farewell2(self):
    print("Goodbye, World!")
  
  @fire.helptext.CommandCategory("bye")
  @classmethod
  def farewell3(cls):
    print("Goodbye, World!")

  def test3(self):
    print("test3")

  def test4(self):
    print("test4")

  @classmethod
  def test5(cls):
    print("test5")

  @classmethod
  def test6(cls):
    print("test6")

def main():
  os.environ["PAGER"] = "cat"
  fire.Fire(CategoryDemo())

if __name__ == "__main__":
  main()