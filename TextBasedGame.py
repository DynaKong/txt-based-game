#Dominic Klatik

import pygame

pygame.mixer.init()
footsteps_sound = pygame.mixer.Sound("footsteps_shortened.wav")

def loop_ambient(filename):
    try:
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Failed to load sound: {e}")

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gpt_room_description(room_name, items, inventory):
    prompt = (
        f"You are the eerie narrator of a dark fantasy text adventure game. "
        f"The player has entered the {room_name}."
        f"Describe the room in a creepy, immersive way. "
        f"Items in the room: {', '.join(items) if items else 'none'}. "
        f"The player/s current inventory: {', '.join(inventory) if inventory else 'empty'}. "
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a spooky game narrator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.9,
        )
        import re
        full_response = response.choices[0].message.content.strip()
        sentences=re.split(r'(?<=[.!?]) +', full_response)
        if len(sentences) > 1:
            return ' '.join(sentences[:-1]) if not sentences [-1].endswith(('.', '!', '?')) else full_response
        else:
            return full_response
    except Exception as e:
        return f"(The game shudders-an error occured tallking to the shadows: {e})"

def get_gpt_ending(inventory):
    prompt = (
        f"The player has just defeated an ancient witch in a dark fantasy adventure. "
        f"They used the following items during their quest: {', '.join(inventory)}. "
        f"Write a short, eering and poetic ending narration that reflects on the battle, "
        f"keep it under 150 words."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a gothic game narrator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.85
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(The hut creaks... something went wrong: {e})"

def greet_player():
    print('\nYou stumble upon what you believe to be an abandoned hut, with signs signaling to beware of the witch.' 
          '\nYou venture forth, with your sense of adventure and courage and are shocked at the size of the hut.' 
          '\nYou hear the sound of a witch cackle coming from the cellar and know you are ill-equipped.' 
          '\nMaybe you can find some items in her home to help you on your quest to defeat her..')

def display_map(currentRoom):
    print("\nMap of the Witch's Hut:")
    print("-"*35)

    def mark(name):
        return f">>{name}<<" if currentRoom == name else f" {name} "

    print(f" {mark('Bathroom')} - {mark('Bedroom')}")
    print("          |")
    print(f"          |               {mark('Cellar')}")
    print("          |                    |")
    print(f"{mark('Library')} - {mark('Entryway')} - {mark('Kitchen')}")
    print("          |")
    print(f"{mark('Livingroom')} - {mark('Hidden Closet')}")
    print('-'*35)

def show_instructions():
    print("Witch Text Adventure Game")
    print("Collect 6 items to win the game, or be beaten by the Witch.")
    print("Move commands:  South,  North,  East,  West")
    print("Add to Inventory: get item")
    print('Type "exit" at any time to leave the game')

print('-' * 70)

room_description_cache = {}
def main():
    loop_ambient("dungeon_ambience.wav")
    greet_player()
    show_instructions()
    rooms = {
        'Entryway': {'South': 'Living Room', 'West': 'Library', 'East': 'Kitchen', 'North': 'Bathroom'},
        'Library': {'East': 'Entryway', 'Item': 'Spell Book'},
        'Bathroom': {'South': 'Entryway', 'East': 'Bedroom', 'Item': 'Mirror Shard'},
        'Bedroom': {'West': 'Bathroom', 'Item': 'Cloak'},
        'Living Room': {'North': 'Entryway', 'East': 'Hidden Closet','Item': 'Music Box'},
        'Hidden Closet': {'West': 'Living Room', 'Item': 'Silent Boots'},
        'Kitchen': {'West': 'Entryway', 'North': 'Cellar', 'Item': 'HP Potion'},
        'Cellar': {'South': 'Kitchen', 'Item': 'The Witch'}
        }
    currentRoom = 'Entryway'
    inventory = []

    def get_item(currentRoom):
        if 'Item' in rooms[currentRoom]:
            item = rooms[currentRoom]['Item']
            print('You found a', item)
            inventory.append(item)
            del rooms[currentRoom]['Item']
        else:
            print('No items are here')
        if currentRoom in room_description_cache:
            del room_description_cache[currentRoom]

    while True:
        print('You are in the', currentRoom)
        if currentRoom not in room_description_cache:
            items = [rooms[currentRoom]['Item']] if 'Item' in rooms[currentRoom] else []
            room_description_cache[currentRoom] = get_gpt_room_description(currentRoom, items, inventory)
        print (room_description_cache[currentRoom])
        print('-' * 70)
        print('Inventory:', inventory)
        print ('-' * 70)
        action = input('What would you like to do? (move, get item, exit): ').lower()
        if action == 'move':
            footsteps_sound.play()
            direction = input('Which direction? (North, South, East, West): ').capitalize()
            if direction in rooms[currentRoom]:
                if rooms[currentRoom][direction] == 'Cellar' and len(inventory) <6:
                    print('\nHow could you ever hope to defeat her without all of the items? '
                            '\nGAME OVER')
                    break
                if rooms[currentRoom][direction] == 'Cellar' and len(inventory) >= 6:
                    print("You descend into the cellar...")
                    print(get_gpt_ending(inventory))
                    break
                currentRoom = rooms[currentRoom][direction]
                print('You moved to', currentRoom)
            else:
                print("You can't go that way")
        elif action == 'get item':
            (get_item(currentRoom))
        elif action == 'map':
            display_map(currentRoom)
        elif action == 'exit':
            print('Very well, good luck next time!')
            break
if __name__ == "__main__":
    main()