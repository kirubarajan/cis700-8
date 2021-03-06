# -*- coding: utf-8 -*-
"""Text-Adventure-Game.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/interactive-fiction-class/interactive-fiction-class.github.io/blob/master/homeworks/text-adventure-game/Text_Adventure_Game.ipynb

# Text adventure game

This Python notebook builds a simple text advenutre game inspired by the [Adventuron Classroom](https://adventuron.io/classroom/) design by Chris Ainsley of Adventuron Software Limited.

The main components are:
1. __The parser__, which interprets the player's commands.
2. __The game__, which represents the world (a collection of __locations__ and __items__), and describes what the player sees.
3. __The data__, which you input to create your own unique game.

## The Game Class
The game keeps track of the state of the world, and describes what the player sees as they move through different locations.
"""

class Game:
  """The Game class represents the world.  Internally, we use a 
     graph of Location objects and Item objects, which can be at a 
     Location or in the player's inventory.  Each locations has a set of
     exits which are the directions that a player can move to get to an
     adjacent location. The player can move from one location to another
     location by typing a command like "Go North".
  """

  def __init__(self, start_at):
    # start_at is the location in the game where the player starts
    self.curr_location = start_at
    self.curr_location.has_been_visited = True
    # inventory is the set of objects that the player has collected/
    self.inventory = {}
    # Print the special commands associated with items in the game (helpful 
    # for debugging and for novice players).
    self.print_commands = True

  def describe(self):
    """Describe the current game state by first describing the current 
       location, then listing any exits, and then describing any objects
       in the current location."""
    self.describe_current_location()
    self.describe_exits()
    self.describe_items()

  def describe_current_location(self):
    """Describe the current location by printing its description field."""
    print(self.curr_location.description)

  def describe_exits(self):
    """List the directions that the player can take to exit from the current
       location."""
    exits = []
    for exit in self.curr_location.connections.keys():
      exits.append(exit.capitalize())
    if len(exits) > 0:
      print("Exits: ", end = '')
      print(*exits, sep = ", ",)
  
  def describe_items(self):
    """Describe what objects are in the current location."""
    if len(self.curr_location.items) > 0:
      print("You see: ")
      for item_name in self.curr_location.items:
        item = self.curr_location.items[item_name]
        print(item.description)
        if self.print_commands:
          special_commands = item.get_commands()
          for cmd in special_commands:
            print('\t', cmd)

  def add_to_inventory(self, item):
    """Add an item to the player's inventory."""
    self.inventory[item.name] = item
  
  def is_in_inventory(self,item):
    return item.name in self.inventory

  def get_items_in_scope(self):
    """Returns a list of items in the current location and in the inventory"""
    items_in_scope = []
    for item_name in self.curr_location.items:
      items_in_scope.append(self.curr_location.items[item_name])
    for item_name in self.inventory:
      items_in_scope.append(self.inventory[item_name])
    return items_in_scope

"""## Locations

Locations Locations are the places in the game that a player can visit.  They contain connects to other locations and items that the player can interact with.
"""

class Location:
  """Locations are the places in the game that a player can visit.
     Internally they are represented nodes in a graph.  Each location stores
     a description of the location, any items in the location, its connections
     to adjacent locations, and any blocks that prevent movement to an adjacent
     location.  The connections is a dictionary whose keys are directions and
     whose values are the location that is the result of traveling in that 
     direction.  The travel_descriptions also has directions as keys, and its 
     values are an optional short desciption of traveling to that location.
  """
  def __init__(self, name, description, end_game=False):
    # A short name for the location
    self.name = name
    # A description of the location
    self.description = description
    # True if entering this location should end the game
    self.end_game = end_game
    # Dictionary mapping from directions to other Location objects
    self.connections = {}
    # Dictionary mapping from directions to text description of the path there
    self.travel_descriptions = {}
    # Dictionary mapping from item name to Item objects present in this location
    self.items = {}
    # Dictionary mapping from direction to Block object in that direction
    self.blocks = {}
    # Flag that gets set to True once this location has been visited by player
    self.has_been_visited = False

  def add_connection(self, direction, connected_location, travel_description=""):
    """Add a connection from the current location to a connected location.
       Direction is a string that the player can use to get to the connected
       location.  If the direction is a cardinal direction, then we also 
       automatically make a connection in the reverse direction."""
    self.connections[direction] = connected_location
    self.travel_descriptions[direction] = travel_description
    if direction == 'north':
      connected_location.connections["south"] = self
      connected_location.travel_descriptions["south"] = ""
    if direction == 'south':
      connected_location.connections["north"] = self
      connected_location.travel_descriptions["north"] = ""
    if direction == 'east':
      connected_location.connections["west"] = self
      connected_location.travel_descriptions["west"] = ""
    if direction == 'west':
      connected_location.connections["east"] = self
      connected_location.travel_descriptions["east"] = ""
    if direction == 'up':
      connected_location.connections["down"] = self
      connected_location.travel_descriptions["down"] = ""
    if direction == 'down':
      connected_location.connections["up"] = self
      connected_location.travel_descriptions["up"] = ""
    if direction == 'in':
      connected_location.connections["out"] = self
      connected_location.travel_descriptions["out"] = ""
    if direction == 'out':
      connected_location.connections["in"] = self
      connected_location.travel_descriptions["in"] = ""


  def add_item(self, name, item):
    """Put an item in this location."""
    self.items[name] = item

  def remove_item(self, item):
    """Remove an item from this location (for instance, if the player picks it
       up and puts it in their inventory)."""
    self.items.pop(item.name)


  def is_blocked(self, direction, game):
    """Check to if there is an obstacle in this direction."""
    if not direction in self.blocks:
        return False
    (block_description, preconditions) = self.blocks[direction]
    if check_preconditions(preconditions, game):
      # All the preconditions have been met.  You may pass.
      return False
    else: 
      # There are still obstalces to overcome or puzzles to solve.
      return True

  def get_block_description(self, direction):
    """Check to if there is an obstacle in this direction."""
    if not direction in self.blocks:
      return ""
    else:
      (block_description, preconditions) = self.blocks[direction]
      return block_description

  def add_block(self, blocked_direction, block_description, preconditions):
    """Create an obstacle that prevents a player from moving in the blocked 
       location until the preconditions are all met."""
    self.blocks[blocked_direction] = (block_description, preconditions)

"""## Checking Preconditions 
In text adventure games it's common to block a player's progress by creating blocks that prevent them from moving to a location.  For instance, a drawbridge might have a troll that you need to get rig of before you can cross into the castle, or a locked door might prevent you from entering a building until you have a key.  

This is a function that you can modify to include other preconditions.
"""

def check_preconditions(preconditions, game, print_failure_reasons=True):
  """Checks whether the player has met all of the specified preconditions"""
  all_conditions_met = True
  for check in preconditions: 
    if check == "inventory_contains":
      item = preconditions[check]
      if not game.is_in_inventory(item):
        all_conditions_met = False
        if print_failure_reasons:
          print("You don't have the %s" % item.name)
    if check == "in_location":
      location = preconditions[check]
      if not game.curr_location == location:
        all_conditions_met = False
        if print_failure_reasons:
          print("You aren't in the correct location")
    if check == "location_has_item":
      item = preconditions[check]
      if not item.name in game.curr_location.items:
        all_conditions_met = False
        if print_failure_reasons:
          print("The %s isn't in this location" % item.name)
    if check == "location_has_item_silent":
      item = preconditions[check]
      if not item.name in game.curr_location.items:
        all_conditions_met = False
    # todo - add other types of preconditions
  return all_conditions_met

"""## Items
Items are objects that a player can get, or scenery that a player can examine. We could also implement people as items.
"""

class Item:
  """Items are objects that a player can get, or scenery that a player can
     examine."""
  def __init__(self,
               name,
               description,
               examine_text="",
               take_text="",
               start_at=None,
               gettable=True,
               end_game=False):
    # The name of the object
    self.name = name
    # The default description of the object.
    self.description = description
    # The detailed description of the player examines the object.
    self.examine_text = examine_text
    # Text that displays when player takes an object.
    self.take_text = take_text if take_text else ("You take the %s." % self.name)
    # Indicates whether a player can get the object and put it in their inventory.
    self.gettable = gettable
    # True if entering this location should end the game.
    self.end_game = end_game
    # The location in the Game where the object starts.
    if start_at:
      start_at.add_item(name, self)
    self.commands = {}


  def get_commands(self):
    """Returns a list of special commands associated with this object"""
    return self.commands.keys()

  def add_action(self, command_text, function, arguments, preconditions={}):
    """Add a special action associated with this item"""
    self.commands[command_text] = (function, arguments, preconditions)

  def do_action(self, command_text, game):
    """Perform a special action associated with this item"""
    end_game = False  # Switches to True if this action ends the game.
    if command_text in self.commands:
      function, arguments, preconditions = self.commands[command_text]
      if check_preconditions(preconditions, game):
        end_game = function(game, arguments)
    else:
      print("Cannot perform the action %s" % command_text)
    return end_game

"""## The Parser
The parser is the module that handles the natural language understanding in the game.  The players enter commands in text, and the parser interprets them and performs the actions that the player intends.  This is the module with the most potential for improvement using modern natural language processing.  The implementation that I have given below only uses simple keyword matching.
"""

class Parser:
  """The Parser is the class that handles the player's input.  The player 
     writes commands, and the parser performs natural language understanding
     in order to interpret what the player intended, and how that intent
     is reflected in the simulated world. 
  """
  def __init__(self, game):
    # A list of all of the commands that the player has issued.
    self.command_history = []
    # A pointer to the game.
    self.game = game

  def get_player_intent(self,command):
    command = command.lower()
    if "," in command:
      # Let the player type in a comma separted sequence of commands
      return "sequence"
    elif self.get_direction(command):
      # Check for the direction intent
      return "direction"
    elif command.lower() == "look" or command.lower() == "l":
      # when the user issues a "look" command, re-describe what they see
      return "redescribe"
    elif "examine " in command or command.lower().startswith("x "):
      return "examine"
    elif  "take " in command or "get " in command:
      return "take"
    elif "drop " in command:
      return "drop"
    elif "inventory" in command or command.lower() == "i":
      return "inventory"
    else: 
      for item in self.game.get_items_in_scope():
        special_commands = item.get_commands()
        for special_command in special_commands:
          if command == special_command.lower():
            return "special"

  def parse_command(self, command):
    # add this command to the history
    self.command_history.append(command)

    # By default, none of the intents end the game. The following are ways this
    # flag can be changed to True.
    # * Going to a certain place.
    # * Entering a certain special command
    # * Picking up a certain object.

    end_game = False

    # Intents are functions that can be executed
    intent = self.get_player_intent(command)
    if intent == "direction":
      end_game = self.go_in_direction(command)
    elif intent == "redescribe":
      self.game.describe()
    elif intent == "examine":
      self.examine(command)
    elif intent == "take":
      end_game = self.take(command)
    elif intent == "drop":
      self.drop(command)
    elif intent == "inventory":
      self.check_inventory(command)
    elif intent == "special":
      end_game = self.run_special_command(command)
    elif intent == "sequence":
      end_game = self.execute_sequence(command)
    else:
      print("I'm not sure what you want to do.")
    return end_game

  ### Intent Functions ###

  def go_in_direction(self, command):
    """ The user wants to in some direction """
    direction = self.get_direction(command)

    if direction:
      if direction in self.game.curr_location.connections:
        if self.game.curr_location.is_blocked(direction, self.game):
          # check to see whether that direction is blocked.
          print(self.game.curr_location.get_block_description(direction))
        else:
          # if it's not blocked, then move there 
          self.game.curr_location = self.game.curr_location.connections[direction]

          # If moving to this location ends the game, only describe the location
          # and not the available items or actions.
          if self.game.curr_location.end_game:
            self.game.describe_current_location()
          else:
            self.game.describe()
      else:
        print("You can't go %s from here." % direction.capitalize())
    return self.game.curr_location.end_game

  def check_inventory(self,command):
    """ The player wants to check their inventory"""
    if len(self.game.inventory) == 0:
      print("You don't have anything.")
    else:
      descriptions = []
      for item_name in self.game.inventory:
        item = self.game.inventory[item_name]
        descriptions.append(item.description)
      print("You have: ", end = '')
      print(*descriptions, sep = ", ",)
  

  def examine(self, command):
    """ The player wants to examine something """
    command = command.lower()
    matched_item = False
    # check whether any of the items at this location match the command
    for item_name in self.game.curr_location.items:
      if item_name in command:
        item = self.game.curr_location.items[item_name]
        if item.examine_text:
          print(item.examine_text)
          matched_item = True
        break
    # check whether any of the items in the inventory match the command
    for item_name in self.game.inventory:
      if item_name in command:
        item = self.game.inventory[item_name]
        if item.examine_text:
          print(item.examine_text)
          matched_item = True
    # fail
    if not matched_item:
      print("You don't see anything special.")


  def take(self, command):
    """ The player wants to put something in their inventory """
    command = command.lower()
    matched_item = False

    # This gets set to True if posession of this object ends the game.
    end_game = False

    # check whether any of the items at this location match the command
    for item_name in self.game.curr_location.items:
      if item_name in command:
        item = self.game.curr_location.items[item_name]
        if item.gettable:
          self.game.add_to_inventory(item)
          self.game.curr_location.remove_item(item)
          print(item.take_text)
          end_game = item.end_game
        else:
          print("You cannot take the %s." % item_name)
        matched_item = True
        break
    # check whether any of the items in the inventory match the command
    if not matched_item:
      for item_name in self.game.inventory:
        if item_name in command:
          print("You already have the %s." % item_name)
          matched_item = True
    # fail
    if not matched_item:
      print("You can't find it.")

    return end_game

  def drop(self, command):
    """ The player wants to remove something from their inventory """
    command = command.lower()
    matched_item = False
    # check whether any of the items in the inventory match the command
    if not matched_item:
      for item_name in self.game.inventory:
        if item_name in command:
          matched_item = True
          item = self.game.inventory[item_name]
          self.game.curr_location.add_item(item_name, item)
          self.game.inventory.pop(item_name)
          print("You drop the %s." % item_name)
          break
    # fail
    if not matched_item:
      print("You don't have that.")


  def run_special_command(self, command):
    """Run a special command associated with one of the items in this location
       or in the player's inventory"""
    for item in self.game.get_items_in_scope():
        special_commands = item.get_commands()
        for special_command in special_commands:
          if command == special_command.lower():
            return item.do_action(special_command, self.game)

  def execute_sequence(self, command):
    for cmd in command.split(","):
      cmd = cmd.strip()
      self.parse_command(cmd)

  def get_direction(self, command):
    command = command.lower()
    if command == "n" or "north" in command:
      return "north" 
    if command == "s" or "south" in command:
      return "south"
    if command == "e" or "east" in command: 
      return "east"
    if command == "w" or "west" in command:
      return "west"
    if command == "up":
      return "up"
    if command == "down":
      return "down"
    if command.startswith("go out"):
      return "out"
    if command.startswith("go in"):
      return "in"
    for exit in self.game.curr_location.connections.keys():
      if command == exit.lower() or command == "go " + exit.lower():
        return exit
    return None

"""## Special functions
Many times we want to add special behavior to items in the game.  For instance, we might want to be able to _pick a rose_ from a _rosebush_, or the _eat_ a _fish_.  In this implementation we do this in a pretty generic way by allowing the game developer to call ```Item.add_action(cmd,function,argment,preconditions)``` where ```function``` is any Python function. Some example of functions are defined below.

These functions should return True if the game is ended by the action, False otherwise.
"""

def add_item_to_inventory(game, *args):
  """ Add a newly created Item and add it to your inventory."""
  (item, action_description, already_done_description) = args[0]
  if(not game.is_in_inventory(item)):
    print(action_description)
    game.add_to_inventory(item)
  else:
    print(already_done_description)
  return False

def describe_something(game, *args):
  """Describe some aspect of the Item"""
  (description) = args[0]
  print(description)
  return False

def destroy_item(game, *args):
  """Removes an Item from the game by setting its location is set to None."""
  (item, action_description) = args[0]
  if game.is_in_inventory(item):
    game.inventory.pop(item.name)
    print(action_description)
  elif item.name in game.curr_location.items:
    game.curr_location.remove_item(item)
    print(action_description)
  return False

def create_item(game, *args):
  item, description = args[0]
  game.curr_location.add_item(item.name, item)  
  print(description)

def create_item_location(game, *args):
  item, description, location = args[0]
  location.add_item(item.name, item)  
  print(description)

def end_game(game, *args):
  """Ends the game."""
  end_message = args[0]
  print(end_message)
  return True

def perform_multiple_actions(game, *args):
  actions = args[0]
  for func, arg in actions: 
    func(game, arg)
  return False

"""## Game Data

Here's where you can define the locations and items in your game.  To get you started, I defined a super-simple fishing game, which contains the first 3 locations of __Action Castle__ by Jared A. Sorensen, which is part of the awesome book [Parsley](http://www.memento-mori.com/parsely-products/parsely-pdf).  

You can play through the whole game with the following commands:
1. take pole
2. go out
3. south 
4. catch fish with pole
5. eat fish
"""

lit_lamp = Item("lit lamp", "a lit lamp", "IT IS VERY BRIGHT", start_at=None)

def build_game():
  # Locations
  cottage = Location("Cottage", "You are standing in a small cottage. ")
  garden_path = Location("Garden Path", "You are standing on a lush garden path. There is a cottage here.")
  fishing_pond = Location("Fishing Pond", "You are at the edge of a small fishing pond.")
  winding_path = Location("Winding Path", "You are walking along a winding path. There is a tall tree here.")
  tall_tree = Location("Top of Tall Tree", "You are at the top of a tall tree.")
  drawbridge = Location("Drawbridge", "You are standing on one side of a drawbridge leading to ACTION CASTLE. There is a mean troll here.")
  courtyard = Location("Courtyard", "You are in the courtyard of ACTION CASTLE.")
  tower_stairs = Location("Tower Stairs", "You are climbing the stairs to the tower. There is a door with a lock on it.")
  tower = Location("Tower", "You are inside a tower.")
  dungeon_stairs = Location("Dungeon Stairs", "You are climbing the stairs down to the dungeon. It is too dark to see!")
  dungeon = Location("Dungeon", "You are in the dungeon.")
  great_feasting_hall = Location("Great Feeding Hall", "You stand inside the Great Feasting Hall.")
  throne_room = Location("Throne Room", "This is the throne room of ACTION CASTLE. There is an ornate golden throne here.")

  # Connections
  cottage.add_connection("out", garden_path)

  garden_path.add_connection("in", cottage)
  garden_path.add_connection("north", winding_path)
  garden_path.add_connection("south", fishing_pond)

  fishing_pond.add_connection("north", garden_path)

  winding_path.add_connection("up", tall_tree)
  winding_path.add_connection("south", garden_path)
  winding_path.add_connection("east", drawbridge)

  tall_tree.add_connection("down", winding_path)

  drawbridge.add_connection("west", winding_path)
  drawbridge.add_connection("east", courtyard) # blocked

  courtyard.add_connection("up", tower_stairs)
  courtyard.add_connection("down", dungeon_stairs) # blocked
  courtyard.add_connection("west", drawbridge)
  courtyard.add_connection("east", great_feasting_hall) #blocked

  tower_stairs.add_connection("down", courtyard)
  tower_stairs.add_connection("up", tower)

  tower.add_connection("down", tower_stairs)

  dungeon_stairs.add_connection("down", dungeon) # blocked
  dungeon_stairs.add_connection("up", courtyard)

  dungeon.add_connection("up", dungeon_stairs)

  great_feasting_hall.add_connection("west", courtyard)
  great_feasting_hall.add_connection("east", throne_room)

  throne_room.add_connection("west", great_feasting_hall)

  # Items that you can pick up
  fishing_pole = Item("pole", "a fishing pole", "A SIMPLE FISHING POLE.", start_at=cottage)
  potion = Item("potion", "a poisonous potion", "IT'S BRIGHT GREEN AND STEAMING.", start_at=cottage, take_text='As you near the potion, the fumes cause you to faint and lose the game. THE END.', end_game=True)
  rosebush = Item("rosebush", "a rosebush", "THE ROSEBUSH CONTAINS A SINGLE RED ROSE.  IT IS BEAUTIFUL.", start_at=garden_path)
  rose = Item("rose", "a red rose", "IT SMELLS GOOD.",  start_at=None)
  fish = Item("fish", "a dead fish", "IT SMELLS TERRIBLE.", start_at=None)
  dead_branch = Item("branch", 'a dead branch', "it's a stout dead dead branch", start_at=tall_tree)
  troll = Item("troll", 'a troll', "IT IS WARTY GREEN AND HUNGRY", start_at=drawbridge, gettable=False)
  unconscious_troll= Item("unconscious troll", "an unconscious troll is in the pond", "HIS EYES ARE IN THE BACK OF HIS HEAD.", start_at=None, gettable=False)
  key = Item("key", "a key", "its a key that unlocks something", start_at=None)
  candle = Item("candle", "a strange candle is here", "the candle is covered in strange ruins", start_at=great_feasting_hall)
  lit_candle = Item("lit candle", "a lit candle is here", "the candle gives off a strange, acrid-smelling smoke", start_at=None)

  # Sceneary (not things that you can pick up)
  pond = Item("pond", "a small fishing pond", "THERE ARE FISH IN THE POND.", start_at=fishing_pond, gettable=False)
  crown = Item("crown", "A simple crown", "THERE IS A CROWN", start_at=None)
  guard = Item("guard", "a guard carrying a sword and a key", "HE LOOKS AT YOU SUSPICIOUSLY.", start_at=courtyard, gettable=False)
  unconscious_guard = Item("unconscious guard", "an unconscious guard is slumpped against the wall", "HE HAS BITS OF BRANCH ON HIS UNIFORM.", start_at=None, gettable=False)
  ghost = Item("ghost", "a ghost is lurking", "The ghost has bony, claw-like ﬁngers and wears a crown.", start_at=dungeon, gettable=False)
  princess = Item("princess", "the princess is here", "the princess is sad, beautiful and lonely. she awaits her prince.", start_at=tower, gettable=False)
  married_princess = Item("married princess", "the married princess is here", "the princess is married to you now", start_at=None, gettable=False)
  revelers = Item("revelers", "a group of revelers are celebrating their new king", "the revelers are very happy", start_at=None, gettable=False)
  courtiers_guards_subjects = Item("courtiers, guards and other subjects", "the room is full of of courtiers, guards and other subjects", "they are very happy", start_at=None, gettable=False)
  throne = Item("throne", "there is an ornate golden throne here.", "the throne is ornate", start_at=throne_room, gettable=False)
  talking_princess = Item("princess", "the princess is now talking", "the princess is sad, beautiful and lonely and friendly. she awaits her prince.", start_at=None, gettable=False)
  open_door = Item("door", "Door to the Courtyard", "", start_at=None, gettable=False)

  # add blocks
  drawbridge.add_block("east", "There is a Troll blocking the path",  preconditions={"location_has_item":unconscious_troll})
  courtyard.add_block("east", "There is a Guard blocking the path",  preconditions={"location_has_item":unconscious_guard})
  tower_stairs.add_block("up", "The door is locked.", preconditions={"location_has_item_silent": open_door})
  dungeon_stairs.add_block("down", "The dungeon is too dark to proceed.", preconditions={"inventory_contains": lit_lamp})

  # Add special functions to your items
  troll.add_action("hit troll with branch", end_game, ("You have failed to attack the troll. GAME OVER"), preconditions={"inventory_contains":dead_branch})
  troll.add_action("give fish to troll", perform_multiple_actions, 
    [(destroy_item, (fish, "You feed the fish to troll.")),
    (destroy_item, (troll, "The troll slumps over, unconscious.")),
    (create_item, (unconscious_troll, "The troll's unconscious body lies on the ground.")),
    ], preconditions={"inventory_contains":fish , "location_has_item": troll})

  key.add_action("unlock door", create_item, (open_door, "The door has opened."), preconditions={ "in_location": tower_stairs})
  
  princess.add_action("give rose to princess", perform_multiple_actions, 
      [(destroy_item, (princess,"The princess opens up.",)),
    (create_item, (talking_princess,"The princess will now talk to you.")),], preconditions={"inventory_contains": rose})

  guard.add_action("hit guard with branch", perform_multiple_actions, 
    ([(destroy_item, (dead_branch,"You swing your branch against the guard. It shatters to pieces.")),
    (destroy_item, (guard,"The guard slumps over, unconscious. ")),
    (describe_something, ("His sword has fallen, but you may not take it.")),
    (create_item, (unconscious_guard, "The guard's unconscious body lies on the ground.")),
    (create_item, (key, "His key falls from his hand.")),
    ]), preconditions={"inventory_contains":dead_branch , "location_has_item": guard})

  crown.add_action("wear crown", perform_multiple_actions, (
      [(destroy_item, (unconscious_guard,"The guard wakes up.")),
    (create_item, (guard,"The guard kneels on the foor to hail his new king.")),]), preconditions={"location_has_item": married_princess})

  rosebush.add_action("pick rose",  add_item_to_inventory, (rose, "You pick the lone rose from the rosebush.", "You already picked the rose."))
  rose.add_action("smell rose",  describe_something, ("It smells sweet."))
  pond.add_action("catch fish",  describe_something, ("You reach into the pond and try to catch a fish with your hands, but they are too fast."))
  pond.add_action("catch fish with pole",  add_item_to_inventory, (fish, "You dip your hook into the pond and catch a fish.","You weren't able to catch another fish."), preconditions={"inventory_contains":fishing_pole})
  fish.add_action("eat fish",  end_game, ("That's disgusting! It's raw! And definitely not sashimi-grade! But you've won this version of the game. THE END."))
  dead_branch.add_action("jump", end_game, ("You have jumped from the tall tree fatally to your end."))

  candle.add_action("translate runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  candle.add_action("decipher runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  candle.add_action("read runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  lit_candle.add_action("translate runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  lit_candle.add_action("decipher runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  lit_candle.add_action("read runes", describe_something, ("The candle says 'The runes seem to be a spell of exorcism.'"))
  candle.add_action("light candle", perform_multiple_actions, ([
    (destroy_item, (candle, "You light the candle.")),
    (create_item, (lit_candle, "The candle is giving off a strange, acrid-smelling smoke.")),
    (destroy_item, (ghost, "The ghost flees!")),
    (create_item, (crown, "The ghost drops a golden crown."))
  ]), preconditions={"inventory_contains": candle, 'in_location': dungeon})

  talking_princess.add_action("talk to princess about ghost", describe_something, ("She says: 'My father haunts the dungeon as a restless spirit.'"))
  talking_princess.add_action("talk to princess about crown", describe_something, ("She says: 'Only the rightful heir to the throne may wear it.'"))
  talking_princess.add_action("talk to princess about herself", describe_something, ("She says: 'I cannot leave this tower until I am married!'"))
  talking_princess.add_action("talk to princess about throne", describe_something, ("She says: 'Only the king may sit on the throne.'"))
  talking_princess.add_action("kiss princess", describe_something, ("Not until we're wed"), preconditions={"location_has_item": talking_princess})
  talking_princess.add_action("marry princess", perform_multiple_actions, ([
    (destroy_item, (talking_princess, "The princess says: 'My father’s crown! You have put his soul at rest and may now succeed him!'")),
    (create_item, (married_princess, "The princess accepts your proposal and places the crown on your head.")),
    (create_item_location, (revelers, "Revelers flood the Great Feasting Hall.", great_feasting_hall)),
    (create_item_location, (courtiers_guards_subjects, "Courtiers, guards and other subjects cheer for you in the Throne Room.", throne_room))
  ]), preconditions={"inventory_contains": crown})

  throne.add_action("sit on throne", end_game, ("You sit on the ornate golden throne. The people cheer for the new ruler of... ACTION CASTLE!"), preconditions={"location_has_item": courtiers_guards_subjects})

  return Game(cottage)

"""# Play the game
This small snippet of code is what you need to run the game.  Behold! The magestic prompt!
"""

def game_loop():
  game = build_game()
  parser = Parser(game)
  game.describe()

  lamp = Item("lamp", "a lamp", "a simple lamp", start_at=None)
  lamp.add_action("light lamp", perform_multiple_actions, 
    ([(destroy_item, (lamp, "You light your lamp.")), (add_item_to_inventory, (lit_lamp, "You can see in dark places now.", "The lamp is already lit."))]), preconditions={"inventory_contains": lamp})

  game.add_to_inventory(lamp)

  command = ""
  while not (command.lower() == "exit" or command.lower == "q"):
    command = input(">")
    end_game = parser.parse_command(command)
    if end_game:
      return

game_loop()
print('THE GAME HAS ENDED.')

"""# Visualize your game
The code below allows you to create a directed graph that shows the locations in your game and how they are connected.  You can also save a PDF of your graph to your Google Drive with the `save_to_drive` method.  The output file will be called `game-visualization.pdf`.
"""

#!pip install graphviz
from graphviz import Digraph
from IPython.display import Image
import queue

def DFS(game, graph):
  """Do a depth-first-search traversal of the locations in the game
     starting at the start location, and create a GraphViz graph 
     to vizualize the connections between the locations, and the items
     that are located at each location."""
  start_location = game.curr_location
  frontier = queue.Queue()
  frontier.put(start_location)
  visited = {}
  visited[start_location.name] = True

  while not frontier.empty():
    current_location = frontier.get()
    game.curr_location = current_location
    name = current_location.name
    description = current_location.description
    items = current_location.items
    items_html = describe_items(current_location)
    html = "<<b>%s</b><br />%s<br />%s>" % (name, description, items_html)
    # Create a new node in the graph for this location
    graph.node(name, label=html)  

    connections = current_location.connections
    for direction in connections.keys():
      next_location = connections[direction]
      if not current_location.is_blocked(direction, game):
        # Create an edge between the current location and its successor
        graph.edge(name, next_location.name, label=direction.capitalize())
      else:
        # Create a dotted edge for connected locations that are blocked
        block_description = "%s\n%s" % (direction.capitalize(), current_location.get_block_description(direction))
        graph.edge(name, next_location.name, label=block_description, style="dotted")
      if not next_location.name in visited:
        visited[next_location.name] = True
        frontier.put(next_location)

def describe_items(location, print_commands=True):
    """Describe what objects are in the current location."""
    items_html = ""
    if len(location.items.keys()) > 0:
      items_html = "You see: "
    for item_name in location.items:
      item = location.items[item_name]
      items_html += item.description
      if print_commands:
        special_commands = item.get_commands()
        for cmd in special_commands:
          items_html += "<br/><i>%s</i>" % cmd
    return items_html

def save_to_drive(graph):
  from google.colab import drive
  drive.mount('/content/drive/')
  graph.render('/content/drive/My Drive/game-visualization', view=True)  

graph = Digraph(node_attr={'color': 'lightblue2', 'style': 'filled'})
game = build_game()
DFS(game, graph)
#save_to_drive(graph)
graph