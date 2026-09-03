from classes.node import Node
from classes.linked_list import LinkedList

def find_merge_node(head1, head2):
    node_addresses_1 = {}
    node_addresses_2 = {}

    current_node = head1
    while current_node:
        # node_addresses_1[id(current_node)] = current_node.value
        current_node = current_node.next

    current_node = head2
    while current_node:
        node_addresses_2[id(current_node)] = current_node.value
        current_node = current_node.next

    print(node_addresses_1)
    print(node_addresses_2)


if __name__ == '__main__':
    ll1 = LinkedList.build_from_values("singly", [1, 2, 3, 4, 5])
    ll2 = LinkedList.build_from_values("singly", [6, 7, 8, 9, 10])

    new_node = Node(99)
    ll1.tail.next = new_node
    ll1.tail = new_node
    ll1.size += 1
    ll1.show()
    print(ll1.get_addresses())


    ll2.tail.next = new_node
    ll2.tail = new_node
    ll2.size += 1
    ll2.show()
    print(ll2.get_addresses())

    find_merge_node(ll1.head, ll2.head)




