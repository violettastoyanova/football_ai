from db import initialize_database
from chatbot import ChatBot


def main():
    initialize_database()
    bot = ChatBot()

    print("Чатботът стартира.")
    print("Напиши 'помощ' за инструкции.")
    print("Напиши 'изход' за край.\n")

    while True:
        user_input = input(">> ")

        response = bot.parse(user_input)

        if response == "exit":
            print("Програмата приключи.")
            break

        print(response)


if __name__ == "__main__":
    main()
