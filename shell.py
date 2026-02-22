import cmd
from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList
from classes.linked_list import LinkedList


class LinkedListShell(cmd.Cmd):
    """
    Interactive shell for manipulating linked lists.
    """

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self.prompt = 'LLV> '
        self.ll: SinglyLinkedList | DoublyLinkedList | None = None
        print('Welcome to Linked List Visualizer. Type help or ? to list commands.\n')
        self.do_entry('')


    def do_entry(self, arg):
        ll_type = input("What type of linked list would you like to create? [singly, doubly]: ")  # Using input() within the cmd loop
        if ll_type not in ["singly", "doubly"]:
            print("Invalid linked list type. Please try again. Type 'create singly' or 'create doubly'.")
            return
        self.ll = LinkedList.create(ll_type)
        print(f"Created a new {ll_type} linked list.")


    def do_greet(self, args):
        """Greet the user. Usage: greet [name]"""
        name = args if args else 'stranger'
        print(f"Hello, {name}!")


    def do_create(self, arg):
        """Create a new linked list. Usage: create [singly|doubly]"""
        ll_type = arg.lower()
        if ll_type not in ["singly", "doubly"]:
            print("Invalid linked list type. Please try again. Type 'create singly' or 'create doubly'.")
            return
        self.ll = LinkedList.build_from_values(ll_type, [])
        print(f"Created a new {ll_type} linked list.")


    def do_append(self, arg):
        values = arg.split(",")
        self.ll.append_values(values)


    def do_prepend(self, arg):
        values = arg.split(",")
        self.ll.prepend_values(values)


    def do_insert(self, arg):
        index, value = arg.split(" ")
        self.ll.insert(int(index), value)


    def do_cycle(self, arg):
        """Create a cycle in the linked list. Usage: cycle [index]"""
        index = int(arg)
        self.ll.create_cycle(index)
        print(f"Created a cycle at index {index}.")


    def do_has_cycle(self, arg):
        index = self.ll.get_cycle_index()
        if index != -1:
            print(f"Linked list contains a cycle at node {index}")
        else:
            print("Linked list does not contain a cycle.")


    def do_remove(self, arg):
        index = int(arg)
        self.ll.remove(index)
        print(f"Removed node at index {index}.")


    def do_replace(self, arg):
        index, value = arg.split(" ")
        self.ll.replace(int(index), value)
        print(f"Replaced node at index {index} with value {value}.")


    def do_reverse(self, arg):
        self.ll.reverse()
        print("Reversed the linked list.")


    def do_clear(self, arg):
        self.ll.clear()
        print("Cleared the linked list.")


    def do_show(self, arg):
        self.ll.show()


    def do_quit(self, arg):
        """Exit the shell."""
        print("Goodbye!")
        return True  # Returning True exits the cmdloop

    # Alias for quit
    do_exit = do_quit

if __name__ == '__main__':
    LinkedListShell().cmdloop()
