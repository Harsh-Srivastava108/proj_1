import random

def get_choices():
        p_choice=input("enter the input(rock,paper,scissors):")
        options=["rock","paper","scissors"]
        c_choice=random.choice(options)
        choices={"p_choice":p_choice,"c_choice":c_choice}
        return choices



def checkwin(p_choice,c_choice):
        if(p_choice==c_choice):
            return "its a tie!"
        
        if(p_choice=="rock"):
               if(c_choice=="paper"):
                      return "c wins"
               else:
                      return "p wins"
        elif(p_choice=="paper"):
               if(c_choice=="rock"):
                      return "p wins"
               else:
                      return "c wins"
        elif(p_choice=="scissors"):
               if(c_choice=="rock"):
                      return "c wins"
               else:
                      return "p wins"


choices=get_choices()         
print(choices)
result = checkwin(choices["p_choice"], choices["c_choice"])
print(result)