import cmd
from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList
from classes.linked_list import LinkedList
from typing import List, Tuple
from utils import str_to_ll_type

class LinkedListShell(cmd.Cmd):
    """
    Interactive shell for manipulating linked lists.
    """

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self.prompt = 'LLV> '
        self.ll: SinglyLinkedList | DoublyLinkedList | None = None
        self.operations: List[Tuple[str, List[int | float | str | bool], str]] = []
        print('Welcome to Linked List Visualizer. Type help or ? to list commands.\n')
        self.do_start('')


    def do_start(self, arg):
        ll_type = input("What type of linked list would you like to create? [singly, doubly]: ").lower()  # Using input() within the cmd loop
        if ll_type not in ["singly", "doubly"]:
            print("Invalid linked list type. Please try again. Type 'create singly' or 'create doubly'.")
            return
        self.ll = LinkedList.create(ll_type)
        print(f"Created a new {ll_type} linked list.")


    def do_create(self, arg):
        """Create a new linked list. Usage: create [singly|doubly]"""
        ll_type = arg.lower()
        if ll_type not in ["singly", "doubly"]:
            print("Invalid linked list type. Please try again. Type 'create singly' or 'create doubly'.")
            return
        self.ll = LinkedList.build_from_values(ll_type, [])
        print(f"Created a new {ll_type} linked list.")


    def do_append(self, arg):
        values = [x for x in arg.split(',') if x]
        self.ll.append_values(values)
        status = f"Added {len(values)} node(s) to the end of the linked list."
        for value in values:
            self.append_operations("append", [value], f"Added  value {value} to the end of the linked list.")
        print(status)


    def do_prepend(self, arg):
        values = [x for x in arg.split(',') if x]
        self.ll.prepend_values(values)
        status = f"Added {len(values)} node(s) to the beginning of the linked list."
        for value in values:
            self.append_operations("prepend", [value], status)
        print(status)


    def do_insert(self, arg):
        index, value = arg.split(" ")
        self.ll.insert(int(index), str_to_ll_type(value))
        status = f"Inserted node with value {value} at index {index}."
        self.append_operations("insert", [int(index), value], status)
        print(status)


    def do_replace(self, arg):
        index, value = arg.split(" ")
        self.ll.replace(int(index), value)
        status = f"Replaced node at index {index} with value {value}."
        self.append_operations("replace", [int(index), value], status)
        print(status)


    def do_cycle(self, arg):
        """Create a cycle in the linked list. Usage: cycle [index]"""
        index = int(arg)
        self.ll.create_cycle(index)
        status = f"Created cycle starting at index {index}."
        self.append_operations("cycle", [int(index)], status)
        print(status)


    def do_remove(self, arg):
        index = int(arg)
        self.ll.remove(index)
        status = f"Removed node at index {index}."
        self.append_operations("remove", [int(index)], status)
        print(status)


    def do_has_cycle(self, arg):
        index = self.ll.get_cycle_index()
        if index != -1:
            print(f"Linked list contains a cycle at node {index}")
        else:
            print("Linked list does not contain a cycle.")


    def do_reverse(self, arg):
        self.ll.reverse()
        print("Reversed the linked list.")


    def do_clear(self, arg):
        self.ll.clear()
        self.operations = []
        print("Cleared the linked list.")


    def do_show(self, arg):
        if arg == "operations":
            for operation, values, description in self.operations:
                print(f"{operation} {values} - {description}")
        else:
            self.ll.show()


    def append_operations(self, operation: str, values: list[int | float | str | bool], description: str):
        self.operations.append((operation, values, description))


    def do_quit(self, arg):
        """Exit the shell."""
        print("Goodbye!")
        return True  # Returning True exits the cmdloop

    # Alias for quit
    do_exit = do_quit

if __name__ == '__main__':
    LinkedListShell().cmdloop()
