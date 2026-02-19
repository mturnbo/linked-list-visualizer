import cmd
from classes.singly_linked_list import SinglyLinkedList
from classes.doubly_linked_list import DoublyLinkedList
from classes.linked_list import LinkedList


class LinkedListShell(cmd.Cmd):
    # intro = 'Welcome to Linked List Visualizer. Type help or ? to list commands.\n'
    # prompt = '(LLV) '

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        self.prompt = 'LLV > '
        self.ll: SinglyLinkedList | DoublyLinkedList | None = None
        print('Welcome to Linked List Visualizer. Type help or ? to list commands.\n')


    def do_greet(self, args):
        """Greet the user. Usage: greet [name]"""
        name = args if args else 'stranger'
        print(f"Hello, {name}!")


    def do_create(self, arg):
        """Create a new linked list. Usage: create [singly|doubly]"""
        ll_type = arg.lower()
        self.ll = LinkedList.build_from_values(ll_type, [])
        print(f"Created a new {ll_type} linked list.")


    def do_append(self, arg):
        self.ll.append(arg)

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
