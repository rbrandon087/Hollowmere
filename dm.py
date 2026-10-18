print("Hollowmere: The Narrator Awakens")
while True:
        print("1. Horror")
        print("2. Fantasy")
        print("3. Horror and Fantasy")
        choice = input("Choose a genre (1, 2, or 3): ")

        if choice == "1":
            genre = "Horror"
            print("Welcome to the world of horror! Prepare to be scared.")
            break
        elif choice == "2":
            genre = "Fantasy"
            print("Welcome to the world of fantasy! Get ready for an epic adventure.")
            break
        elif choice == "3":
            genre = "Horror and Fantasy"
            print("Welcome to the world of horror and fantasy! Brace yourself for a thrilling journey.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue

name = input("What is your name, adventurer? ")

print(f"Welcome {name}, to the world of {genre}! Your journey begins now.")