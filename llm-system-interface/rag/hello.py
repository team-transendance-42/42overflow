import random

# python3 llm-system-interface/rag/hello.py 
print("hello, world")

def main():
	secret = random.randint(1, 10)
	attempts = 0

	print("guess a num between 1 and 10")

	while True:
		guess = int(input("Your guess: "))
		attempts += 1

		if guess < secret:
			print("too low")
		elif guess > secret:
			print("too high")
		else:
			print(f"Correct! You got it in {attempts} tries.") #“formatted string literal”: print the value of attempts
			break

#If this file is being run directly, then __name__ is set to "__main__", so Python calls main().
#If this file is imported from another file, __name__ is set to the module’s name instead, so main() does not run automatically.
if __name__ == "__main__":
	main()


