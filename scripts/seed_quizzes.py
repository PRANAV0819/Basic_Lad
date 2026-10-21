import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assignments.models import ReadinessModule, SubjectCategory, Assignment, Question, QuestionOption
from adminpanel.models import Admin

def run_seed():
    admin = Admin.objects.first()
    
    # 0. Delete empty orphan test "gfg"
    Assignment.objects.filter(title='gfg', questions__isnull=True).delete()

    # Get modules
    core_mod = ReadinessModule.objects.filter(code='CORE_SUBJECTS').first()
    coding_mod = ReadinessModule.objects.filter(code='CODING_DSA').first()
    apt_mod = ReadinessModule.objects.filter(code='APTITUDE').first()
    lr_mod = ReadinessModule.objects.filter(code='LOGICAL_REASONING').first()
    comm_mod = ReadinessModule.objects.filter(code='COMMUNICATION_SKILLS').first()

    tests_data = [
        # ==========================================
        # 1. CORE SUBJECTS
        # ==========================================
        {
            "module": core_mod,
            "subject": "Data Structures and Algorithms (DSA)",
            "topic": "Time Complexity, Trees & Heaps",
            "title": "DSA Core Assessment: Complexity & Tree Structures",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Assess your understanding of asymptotic notation, tree balancing, and heap properties commonly tested in technical screening rounds.",
            "questions": [
                {
                    "text": "What is the worst-case time complexity of QuickSort, and when does it typically occur?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Worst case is O(N^2) when the chosen pivot is always the smallest or largest element, such as in an already sorted array with first/last element pivoting.",
                    "options": [
                        ("A", "O(N log N), when the array is randomly shuffled", False),
                        ("B", "O(N^2), when the pivot divides the array into extremely unbalanced partitions (e.g. 0 and N-1 elements)", True),
                        ("C", "O(N), when all elements in the array are distinct", False),
                        ("D", "O(log N), when using three-way partitioning", False),
                    ]
                },
                {
                    "text": "Which of the following operations on a Min-Heap of size N runs in O(log N) time?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Extract-Min (removing the root) and Insert both take O(log N) because of heapify. Finding min takes O(1). Building heap takes O(N).",
                    "options": [
                        ("A", "Finding the minimum element", False),
                        ("B", "Building the entire heap from an unsorted array", False),
                        ("C", "Extract-Min (deleting the root element) and restoring the heap property", True),
                        ("D", "Checking if the heap is empty", False),
                    ]
                },
                {
                    "text": "In an AVL tree with N nodes, what is the maximum height of the tree?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The height of an AVL tree with N nodes is strictly bounded by approximately 1.44 * log2(N), guaranteeing O(log N) search, insertion, and deletion.",
                    "options": [
                        ("A", "O(N)", False),
                        ("B", "Approximately 1.44 * log2(N)", True),
                        ("C", "O(N^1/2)", False),
                        ("D", "Exactly log2(N) in all configurations", False),
                    ]
                },
                {
                    "text": "Which data structure is optimal for implementing an LRU (Least Recently Used) Cache with O(1) get and put operations?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A combination of a Hash Map (for O(1) key lookup) and a Doubly Linked List (for O(1) removal and node repositioning) is optimal.",
                    "options": [
                        ("A", "Hash Map combined with a Doubly Linked List", True),
                        ("B", "Binary Search Tree combined with an Array", False),
                        ("C", "Single Stack with a Queue", False),
                        ("D", "Min-Heap with an Adjacency List", False),
                    ]
                },
                {
                    "text": "Consider the recurrence relation: T(N) = 2T(N/2) + O(N). According to the Master Theorem, what is the asymptotic time complexity?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Here a=2, b=2, and f(N) = O(N). Since log_b(a) = log_2(2) = 1, f(N) matches Theta(N^1). By Case 2 of Master Theorem, T(N) = Theta(N log N).",
                    "options": [
                        ("A", "O(N)", False),
                        ("B", "O(N log N)", True),
                        ("C", "O(N^2)", False),
                        ("D", "O(2^N)", False),
                    ]
                }
            ]
        },
        {
            "module": core_mod,
            "subject": "Object-Oriented Programming (OOP)",
            "topic": "Polymorphism, Inheritance & SOLID Principles",
            "title": "OOP Core Assessment: Architecture, Inheritance & Principles",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Test your grasp of runtime polymorphism, abstract classes, diamond problem, and object-oriented design principles.",
            "questions": [
                {
                    "text": "How does C++ or Java implement runtime polymorphism (dynamic method dispatch)?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Runtime polymorphism is implemented using Virtual Method Tables (vtables) and virtual pointers (vptrs) resolved at execution time.",
                    "options": [
                        ("A", "Through compile-time macro expansion", False),
                        ("B", "Using Virtual Tables (vtable) and Virtual Pointers (vptr) resolved at runtime", True),
                        ("C", "By duplicating class bytecodes at link time", False),
                        ("D", "Using static type casting on the call stack", False),
                    ]
                },
                {
                    "text": "What is the 'Diamond Problem' in object-oriented programming?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The diamond problem occurs in multiple inheritance when a class inherits from two classes that both inherit from the same common base class, causing ambiguity.",
                    "options": [
                        ("A", "An ambiguity that arises when two child classes inherit from a common base class, and another class inherits from both child classes", True),
                        ("B", "A memory leak caused by unreferenced circular references in garbage collection", False),
                        ("C", "A deadlock between two synchronized threads accessing singleton objects", False),
                        ("D", "Overriding private static methods in a derived class", False),
                    ]
                },
                {
                    "text": "What does the Liskov Substitution Principle (LSP) in SOLID design state?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "LSP states that objects of a superclass should be replaceable with objects of a subclass without affecting the correctness or validity of the program.",
                    "options": [
                        ("A", "Every class must have only a single reason to change", False),
                        ("B", "Subtypes must be substitutable for their base types without altering program correctness", True),
                        ("C", "Clients should not be forced to depend upon interfaces they do not use", False),
                        ("D", "High-level modules should not depend upon low-level modules directly", False),
                    ]
                },
                {
                    "text": "What is the primary difference between an Abstract Class and an Interface in Java?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "An abstract class can maintain state (instance fields) and constructors, whereas interfaces cannot store non-static state and support multiple inheritance.",
                    "options": [
                        ("A", "An abstract class can maintain instance state and constructors; a class can implement multiple interfaces but extend only one class", True),
                        ("B", "Interfaces can have private constructors while abstract classes cannot", False),
                        ("C", "Abstract classes cannot have concrete methods under any circumstances", False),
                        ("D", "Interfaces require manual heap memory deallocation", False),
                    ]
                },
                {
                    "text": "Which design pattern ensures a class has only one instance while providing a global access point to it?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The Singleton pattern restricts instantiation of a class to one single instance and provides a global access method.",
                    "options": [
                        ("A", "Factory Pattern", False),
                        ("B", "Singleton Pattern", True),
                        ("C", "Observer Pattern", False),
                        ("D", "Adapter Pattern", False),
                    ]
                }
            ]
        },
        {
            "module": core_mod,
            "subject": "Database Management Systems (DBMS)",
            "topic": "SQL, Normalization & ACID Transactions",
            "title": "DBMS Core Assessment: Normal Forms, Transactions & Indexing",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Comprehensive evaluation of relational schema design, ACID properties, isolation levels, and B+ Tree indexing.",
            "questions": [
                {
                    "text": "What distinguishes Boyce-Codd Normal Form (BCNF) from Third Normal Form (3NF)?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "In BCNF, for every non-trivial functional dependency X -> Y, X must be a super key. In 3NF, Y can also be a prime attribute.",
                    "options": [
                        ("A", "3NF eliminates transitive dependencies; BCNF requires that for every X -> Y, X must be a super key without exception", True),
                        ("B", "BCNF allows multi-valued dependencies whereas 3NF strictly forbids them", False),
                        ("C", "3NF requires tables to have no primary key", False),
                        ("D", "BCNF guarantees lossless join but cannot guarantee zero redundancy", False),
                    ]
                },
                {
                    "text": "In relational database transactions, which ACID property ensures that partially completed transactions leave no permanent trace in case of a crash?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Atomicity ensures 'all-or-nothing' execution. If a transaction fails midway, rollback ensures no partial updates persist.",
                    "options": [
                        ("A", "Consistency", False),
                        ("B", "Isolation", False),
                        ("C", "Atomicity", True),
                        ("D", "Durability", False),
                    ]
                },
                {
                    "text": "Why are B+ Trees preferred over Binary Search Trees or B-Trees for database disk indexing?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "B+ Trees store all actual record pointers/data in leaf nodes linked sequentially, enabling highly efficient range queries and fewer disk I/O operations.",
                    "options": [
                        ("A", "B+ Trees store all data records in leaf nodes linked as a doubly-linked list, optimizing range scans and minimizing disk I/O", True),
                        ("B", "B+ Trees have an average height of O(N)", False),
                        ("C", "B+ Trees require zero memory for internal nodes", False),
                        ("D", "Binary search trees are not deterministic", False),
                    ]
                },
                {
                    "text": "Which SQL transaction isolation level prevents 'Dirty Reads', 'Non-Repeatable Reads', and 'Phantom Reads'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Serializable is the highest isolation level. It prevents dirty reads, non-repeatable reads, and phantom reads.",
                    "options": [
                        ("A", "Read Committed", False),
                        ("B", "Read Uncommitted", False),
                        ("C", "Repeatable Read", False),
                        ("D", "Serializable", True),
                    ]
                },
                {
                    "text": "What is the result of an INNER JOIN between Table A (5 rows, values {1,1,2,2,3}) and Table B (3 rows, values {1,2,2}) on the value column?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Value 1: 2 rows in A * 1 row in B = 2 rows. Value 2: 2 rows in A * 2 rows in B = 4 rows. Value 3: 0 rows match. Total = 2 + 4 = 6 rows.",
                    "options": [
                        ("A", "3 rows", False),
                        ("B", "5 rows", False),
                        ("C", "6 rows", True),
                        ("D", "15 rows", False),
                    ]
                }
            ]
        },
        {
            "module": core_mod,
            "subject": "Operating Systems (OS)",
            "topic": "Process Scheduling, Deadlocks & Virtual Memory",
            "title": "OS Core Assessment: Synchronization, Paging & Scheduling",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Assess process management, deadlock prevention, semaphores, Belady's anomaly, and page replacement strategies.",
            "questions": [
                {
                    "text": "Which condition is NOT one of the four Coffman conditions necessary for a Deadlock to occur?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Preemption eliminates deadlock. The four Coffman conditions are Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
                    "options": [
                        ("A", "Mutual Exclusion", False),
                        ("B", "Preemption of resources by the operating system kernel", True),
                        ("C", "Hold and Wait", False),
                        ("D", "Circular Wait", False),
                    ]
                },
                {
                    "text": "What is Belady's Anomaly in operating systems virtual memory management?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Belady's Anomaly occurs in FIFO page replacement where increasing the number of page frames causes more page faults to occur.",
                    "options": [
                        ("A", "Page fault rate increases as the number of page frames allocated increases, observed in FIFO page replacement", True),
                        ("B", "Thrashing caused by low CPU utilization in multi-threaded programs", False),
                        ("C", "Processes starving because of Round Robin quantum length", False),
                        ("D", "Memory fragmentation caused by paging", False),
                    ]
                },
                {
                    "text": "What is the difference between a Binary Semaphore and a Mutex?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A Mutex includes ownership semantics—only the thread that locked it can unlock it. A Semaphore is a signaling mechanism that can be signaled by any thread.",
                    "options": [
                        ("A", "A Mutex has ownership semantics (only the locking thread can unlock it); a semaphore is a signaling mechanism without ownership", True),
                        ("B", "A Semaphore can only be used on single-core processors", False),
                        ("C", "A Mutex can take arbitrary integer values whereas a semaphore is always binary", False),
                        ("D", "There is no functional or architectural difference", False),
                    ]
                },
                {
                    "text": "In Shortest Remaining Time First (SRTF) scheduling, if a new process arrives with CPU burst 2 ms while the current process has 4 ms remaining, what happens?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "SRTF is the preemptive version of SJF. Because the newly arrived process (2 ms) is shorter than remaining burst (4 ms), the CPU preempts the current process.",
                    "options": [
                        ("A", "The running process is preempted and the new process is allocated the CPU", True),
                        ("B", "The running process continues to run to completion", False),
                        ("C", "Both processes execute concurrently in time slices", False),
                        ("D", "The operating system terminates both processes", False),
                    ]
                },
                {
                    "text": "What causes 'Thrashing' in an Operating System?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Thrashing occurs when the sum of working set sizes of all active processes exceeds available physical memory, causing processes to spend more time paging than executing.",
                    "options": [
                        ("A", "A deadlock between multiple CPU cores", False),
                        ("B", "When a process spends more time page swapping than executing due to insufficient allocated frames", True),
                        ("C", "Corrupted disk sectors in swap space", False),
                        ("D", "Overclocking the GPU", False),
                    ]
                }
            ]
        },
        {
            "module": core_mod,
            "subject": "Computer Networks and Cloud Computing (CN&CC)",
            "topic": "OSI Model, TCP/IP, Routing & Security",
            "title": "Computer Networks: Protocols, Subnetting & Architecture",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Assess OSI layers, TCP three-way handshake, CIDR subnetting, DNS hierarchy, and TLS/HTTPS security mechanisms.",
            "questions": [
                {
                    "text": "During the TCP 3-Way Handshake connection establishment, what flags are sent in sequence?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Step 1: Client sends SYN. Step 2: Server responds with SYN-ACK. Step 3: Client acknowledges with ACK.",
                    "options": [
                        ("A", "SYN -> SYN-ACK -> ACK", True),
                        ("B", "ACK -> SYN -> SYN-ACK", False),
                        ("C", "SYN -> ACK -> DATA", False),
                        ("D", "FIN -> ACK -> FIN-ACK", False),
                    ]
                },
                {
                    "text": "In a /26 IPv4 subnet (CIDR notation), how many usable host IP addresses are available?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "32 - 26 = 6 host bits. Total IPs = 2^6 = 64. Subtracting 2 (network ID and broadcast address) gives 62 usable host addresses.",
                    "options": [
                        ("A", "64", False),
                        ("B", "62", True),
                        ("C", "30", False),
                        ("D", "126", False),
                    ]
                },
                {
                    "text": "At which layer of the OSI model does the Address Resolution Protocol (ARP) operate?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "ARP maps IP addresses (Layer 3) to MAC addresses (Layer 2), operating at the Data Link Layer / Network interface boundary.",
                    "options": [
                        ("A", "Application Layer", False),
                        ("B", "Transport Layer", False),
                        ("C", "Data Link Layer (Layer 2)", True),
                        ("D", "Session Layer", False),
                    ]
                },
                {
                    "text": "Why does HTTPS use both asymmetric and symmetric encryption?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Asymmetric encryption (RSA/ECC) securely exchanges a shared session key during handshake; symmetric encryption (AES) encrypts bulk data fast and efficiently.",
                    "options": [
                        ("A", "Asymmetric is used for key exchange during TLS handshake; symmetric is used for bulk data transfer due to its computational speed", True),
                        ("B", "Symmetric encryption is used for certificates; asymmetric is used for payloads", False),
                        ("C", "Asymmetric encryption is required by IP routers", False),
                        ("D", "To prevent DNS spoofing only", False),
                    ]
                },
                {
                    "text": "Which routing algorithm is prone to the 'Count-to-Infinity' problem, and how is it mitigated?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Distance Vector routing (Bellman-Ford) suffers from count-to-infinity, mitigated using Split Horizon and Poison Reverse techniques.",
                    "options": [
                        ("A", "Distance Vector Routing, mitigated using Split Horizon and Poison Reverse", True),
                        ("B", "Link State Routing, mitigated using Dijkstra shortest path", False),
                        ("C", "BGP Path Vector, mitigated using Autonomous System loop checks", False),
                        ("D", "OSPF, mitigated using designated routers", False),
                    ]
                }
            ]
        },

        # ==========================================
        # 2. CODING & DSA
        # ==========================================
        {
            "module": coding_mod,
            "subject": "Programming Fundamentals – C/C++ or Python",
            "topic": "Pointers, Memory Allocation & Code Output",
            "title": "Programming Fundamentals & Code Tracing Quiz",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Evaluate fundamental concepts in memory referencing, scope, pointer arithmetic, and language syntax.",
            "questions": [
                {
                    "text": "In C++, what will be the output of the following code snippet?",
                    "code": "int a = 10;\nint &ref = a;\nref = 20;\ncout << a;",
                    "type": "CODE",
                    "marks": 2,
                    "solution": "A reference in C++ is an alias to the original variable. Modifying 'ref' directly modifies 'a', so 20 is output.",
                    "options": [
                        ("A", "10", False),
                        ("B", "20", True),
                        ("C", "Garbage value", False),
                        ("D", "Compilation error", False),
                    ]
                },
                {
                    "text": "What happens when you allocate memory using malloc() in C but fail to call free() before terminating the process?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "During process execution it creates a memory leak (unusable heap space). Modern OSes reclaim the process address space upon process termination.",
                    "options": [
                        ("A", "It causes a Memory Leak during program execution; modern OSes reclaim the virtual memory after process termination", True),
                        ("B", "It corrupts the CPU cache immediately", False),
                        ("C", "The compiler issues a fatal syntax error", False),
                        ("D", "It automatically calls free() when the variable goes out of scope", False),
                    ]
                },
                {
                    "text": "In Python, what is the output of `[i * 2 for i in range(5) if i % 2 == 0]`?",
                    "code": "result = [i * 2 for i in range(5) if i % 2 == 0]\nprint(result)",
                    "type": "CODE",
                    "marks": 2,
                    "solution": "Range(5) is [0, 1, 2, 3, 4]. Even values are 0, 2, 4. Multiplied by 2 gives [0, 4, 8].",
                    "options": [
                        ("A", "[0, 2, 4, 6, 8]", False),
                        ("B", "[0, 4, 8]", True),
                        ("C", "[2, 6]", False),
                        ("D", "[0, 1, 2, 3, 4]", False),
                    ]
                },
                {
                    "text": "Which of the following describes the difference between Deep Copy and Shallow Copy?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A shallow copy duplicates the outer object and copies references; a deep copy duplicates the object and recursively copies all nested objects.",
                    "options": [
                        ("A", "Shallow copy copies references to nested objects, whereas deep copy recursively clones nested objects into distinct memory", True),
                        ("B", "Deep copy is only available in compiled languages", False),
                        ("C", "Shallow copy creates new objects on disk while deep copy uses RAM", False),
                        ("D", "There is no difference in modern memory-managed languages", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Arrays & Strings",
            "topic": "Sliding Window, Two Pointers & Prefix Sums",
            "title": "Arrays & Strings: Two Pointers & Sliding Window",
            "difficulty": "MEDIUM",
            "time_limit": 25,
            "passing_percentage": 50,
            "description": "Solve quintessential array and string interview problems: Kadane's algorithm, palindromes, and sliding window maximum.",
            "questions": [
                {
                    "text": "What is the time and auxiliary space complexity of Kadane's Algorithm for finding the maximum contiguous subarray sum?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Kadane's algorithm maintains a running sum in a single pass: O(N) time and O(1) auxiliary space.",
                    "options": [
                        ("A", "O(N^2) Time, O(1) Space", False),
                        ("B", "O(N) Time, O(1) Space", True),
                        ("C", "O(N log N) Time, O(N) Space", False),
                        ("D", "O(N) Time, O(N) Space", False),
                    ]
                },
                {
                    "text": "When checking whether a string is a palindrome ignoring non-alphanumeric characters, which technique is optimal?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Two-pointer approach (one pointer at head, one at tail moving toward the center) runs in O(N) time and O(1) space.",
                    "options": [
                        ("A", "Two Pointers starting at both ends moving inwards with O(N) time and O(1) space", True),
                        ("B", "Recursion with O(N^2) stack space", False),
                        ("C", "Sorting the string and comparing with reverse in O(N log N)", False),
                        ("D", "Using a 2D dynamic programming table", False),
                    ]
                },
                {
                    "text": "Which data structure enables finding the maximum in every sliding window of size K in an array of size N in O(N) total time?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A Monotonic Decreasing Deque stores indices of candidates, allowing amortized O(1) per element, totaling O(N) time.",
                    "options": [
                        ("A", "Monotonic Deque (Double-ended queue)", True),
                        ("B", "Max-Heap in O(N log K)", False),
                        ("C", "Simple Array in O(N * K)", False),
                        ("D", "Stack with single push/pop", False),
                    ]
                },
                {
                    "text": "In the KMP (Knuth-Morris-Pratt) pattern searching algorithm, what does the Pi (LPS) table represent?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The LPS (Longest Proper Prefix which is also Suffix) table tells the algorithm how many characters can be skipped upon mismatch.",
                    "options": [
                        ("A", "Length of the longest proper prefix that is also a suffix for each prefix of the pattern", True),
                        ("B", "The frequency of each character in the pattern string", False),
                        ("C", "The ASCII hash values of the text", False),
                        ("D", "The edit distance between text and pattern", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Linked Lists",
            "topic": "Fast-Slow Pointers, Reversal & Cycles",
            "title": "Linked Lists: Traversal, Cycles & Reversal",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Test mastery of single/doubly linked lists, Floyd's tortoise-and-hare cycle detection, and pointer updates.",
            "questions": [
                {
                    "text": "How does Floyd's Tortoise and Hare algorithm detect a cycle in a Singly Linked List?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Slow pointer moves 1 step, fast pointer moves 2 steps. If a cycle exists, they will inevitably meet inside the loop in O(N) time and O(1) space.",
                    "options": [
                        ("A", "Slow moves 1 step and Fast moves 2 steps; if they meet, a cycle exists", True),
                        ("B", "Both pointers move 1 step and count node visits in a hash set", False),
                        ("C", "Reverse the linked list and check if head equals tail", False),
                        ("D", "Check if node value exceeds N", False),
                    ]
                },
                {
                    "text": "To reverse a singly linked list in-place iteratively, how many pointer variables are required at minimum?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Three pointers: 'prev', 'curr', and 'next_node' (to hold the rest of the list before reversing the link curr->next = prev).",
                    "options": [
                        ("A", "1 pointer", False),
                        ("B", "2 pointers", False),
                        ("C", "3 pointers (prev, current, next)", True),
                        ("D", "An entire auxiliary array of pointers", False),
                    ]
                },
                {
                    "text": "What is the time complexity to find the middle node of a linked list of length N using two pointers?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The fast pointer traverses the list in N/2 iterations, which is O(N) time in a single pass.",
                    "options": [
                        ("A", "O(N) Time and O(1) Space", True),
                        ("B", "O(N^2) Time and O(1) Space", False),
                        ("C", "O(log N) Time", False),
                        ("D", "O(N) Time and O(N) Space", False),
                    ]
                },
                {
                    "text": "In a Doubly Linked List, what is the time complexity to delete a node when a direct pointer to that node is already given?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Because each node has direct pointers to both prev and next, updating their pointers takes O(1) time without any traversal.",
                    "options": [
                        ("A", "O(1)", True),
                        ("B", "O(N)", False),
                        ("C", "O(log N)", False),
                        ("D", "O(N^2)", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Stacks & Queues",
            "topic": "Monotonic Stack, Parentheses & Buffer",
            "title": "Stacks & Queues: Applications & Monotonic Patterns",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Assess stack evaluation, balanced parenthesis validation, monotonic stack algorithms, and queue implementation.",
            "questions": [
                {
                    "text": "What is the optimal data structure to find the 'Next Greater Element' for all elements in an array in O(N) time?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A Monotonic Decreasing Stack stores elements whose next greater element is yet to be found. Each element is pushed and popped at most once.",
                    "options": [
                        ("A", "Monotonic Stack", True),
                        ("B", "Priority Queue", False),
                        ("C", "Binary Search Tree", False),
                        ("D", "Circular Queue", False),
                    ]
                },
                {
                    "text": "What is the amortized time complexity of the dequeue (pop) operation when implementing a Queue using Two Stacks?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Each element is pushed once to Stack 1, moved once to Stack 2, and popped once from Stack 2. Amortized time per element is O(1).",
                    "options": [
                        ("A", "O(1) Amortized", True),
                        ("B", "O(N) in all cases", False),
                        ("C", "O(log N)", False),
                        ("D", "O(N^2)", False),
                    ]
                },
                {
                    "text": "In evaluating an Arithmetic Postfix Expression (Reverse Polish Notation), which data structure is used?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A Stack pushes operands and pops the top two operands upon encountering an operator.",
                    "options": [
                        ("A", "Stack", True),
                        ("B", "Queue", False),
                        ("C", "Adjacency Matrix", False),
                        ("D", "Hash Map", False),
                    ]
                },
                {
                    "text": "How does a circular queue of capacity C determine whether it is full?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "(rear + 1) % capacity == front indicates the queue has filled its available slots.",
                    "options": [
                        ("A", "(rear + 1) % capacity == front", True),
                        ("B", "front == rear == 0", False),
                        ("C", "rear == capacity", False),
                        ("D", "front == -1", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Trees & Graphs",
            "topic": "DFS, BFS, Dijkstra & Topological Sort",
            "title": "Trees & Graphs: Traversals, Shortest Paths & DAGs",
            "difficulty": "HARD",
            "time_limit": 30,
            "passing_percentage": 50,
            "description": "Advanced technical assessment on BFS/DFS traversal, Dijkstra shortest path, Kahn's algorithm, and BST properties.",
            "questions": [
                {
                    "text": "Which tree traversal of a Binary Search Tree (BST) visits nodes in strictly ascending sorted order?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Inorder traversal visits Left subtree -> Current Node -> Right subtree, producing sorted output for any valid BST.",
                    "options": [
                        ("A", "Preorder traversal", False),
                        ("B", "Inorder traversal", True),
                        ("C", "Postorder traversal", False),
                        ("D", "Level order traversal", False),
                    ]
                },
                {
                    "text": "What is the time complexity of Dijkstra's Shortest Path Algorithm implemented with a Min-Heap (Priority Queue) on a graph with V vertices and E edges?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "With a binary min-heap, extracting min takes O(V log V) and updating edge weights takes O(E log V), yielding O((V + E) log V).",
                    "options": [
                        ("A", "O(V^2)", False),
                        ("B", "O((V + E) log V)", True),
                        ("C", "O(E + V)", False),
                        ("D", "O(V * E)", False),
                    ]
                },
                {
                    "text": "Which condition allows Topological Sorting of a graph?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Topological sort is strictly defined only on Directed Acyclic Graphs (DAGs). A graph with cycles cannot be topologically sorted.",
                    "options": [
                        ("A", "The graph must be a Directed Acyclic Graph (DAG)", True),
                        ("B", "The graph must be undirected and bipartite", False),
                        ("C", "The graph must be strongly connected", False),
                        ("D", "All edge weights must be positive", False),
                    ]
                },
                {
                    "text": "How can you detect a cycle in a Directed Graph using Depth-First Search (DFS)?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "By tracking nodes currently in the recursion stack (back-edges). If a neighbor is already visited and in the recursion stack, a cycle exists.",
                    "options": [
                        ("A", "By detecting a Back-Edge to a vertex currently active in the recursion call stack", True),
                        ("B", "By checking if total edges exceed vertices", False),
                        ("C", "By running BFS and checking queue size", False),
                        ("D", "By calculating the determinant of the adjacency matrix", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Searching & Sorting",
            "topic": "Binary Search, MergeSort & QuickSort",
            "title": "Searching & Sorting: Divide-and-Conquer Algorithms",
            "difficulty": "MEDIUM",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Test understanding of binary search boundary conditions, sorting stability, and divide-and-conquer mechanics.",
            "questions": [
                {
                    "text": "What does it mean for a sorting algorithm to be 'Stable'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "A stable sorting algorithm preserves the original relative order of elements that have equal sorting keys.",
                    "options": [
                        ("A", "It never crashes regardless of input size", False),
                        ("B", "It preserves the relative order of elements that have equal comparison keys", True),
                        ("C", "It uses O(1) auxiliary space", False),
                        ("D", "It achieves O(N log N) worst-case time", False),
                    ]
                },
                {
                    "text": "Which of the following sorting algorithms is inherently stable and guarantees O(N log N) worst-case time?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Merge Sort guarantees O(N log N) worst-case time and preserves relative order of equal keys (stable).",
                    "options": [
                        ("A", "QuickSort", False),
                        ("B", "HeapSort", False),
                        ("C", "MergeSort", True),
                        ("D", "SelectionSort", False),
                    ]
                },
                {
                    "text": "When implementing Binary Search on a sorted array, which expression prevents integer overflow when computing the midpoint?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "mid = low + (high - low) / 2 prevents overflow that occurs if (low + high) exceeds the 32-bit integer limit.",
                    "options": [
                        ("A", "mid = (low + high) / 2", False),
                        ("B", "mid = low + (high - low) / 2", True),
                        ("C", "mid = (high - low) * 2", False),
                        ("D", "mid = (low + high) >> 2", False),
                    ]
                },
                {
                    "text": "What is the worst-case auxiliary space complexity of standard Merge Sort for an array of size N?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Merge Sort requires an auxiliary array of size O(N) to merge the divided sub-arrays.",
                    "options": [
                        ("A", "O(1)", False),
                        ("B", "O(log N)", False),
                        ("C", "O(N)", True),
                        ("D", "O(N^2)", False),
                    ]
                }
            ]
        },
        {
            "module": coding_mod,
            "subject": "Recursion and Dynamic Programming",
            "topic": "Memoization, Tabulation & Classic DP",
            "title": "Recursion & DP: 0/1 Knapsack, LCS & Subproblems",
            "difficulty": "HARD",
            "time_limit": 30,
            "passing_percentage": 50,
            "description": "Master Dynamic Programming principles: overlapping subproblems, optimal substructure, memoization, and state transitions.",
            "questions": [
                {
                    "text": "What two key properties must a problem have to be solvable using Dynamic Programming?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Dynamic Programming requires Overlapping Subproblems (subproblems are computed repeatedly) and Optimal Substructure (optimal solution formed from optimal subproblem solutions).",
                    "options": [
                        ("A", "Overlapping Subproblems and Optimal Substructure", True),
                        ("B", "Greedy Choice Property and Infinite Recursion", False),
                        ("C", "Independent Subproblems and Disjoint Sets", False),
                        ("D", "Binary Decision Trees and Randomized Pivots", False),
                    ]
                },
                {
                    "text": "In the classic 0/1 Knapsack Problem with N items and maximum weight capacity W, what is the standard DP time complexity?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Standard 2D table approach computes states for each item (1..N) and capacity (0..W), taking O(N * W) pseudo-polynomial time.",
                    "options": [
                        ("A", "O(2^N)", False),
                        ("B", "O(N * W)", True),
                        ("C", "O(N log W)", False),
                        ("D", "O(N + W)", False),
                    ]
                },
                {
                    "text": "What is the recurrence relation for Longest Common Subsequence (LCS) of strings S1 and S2 at indices i and j when S1[i] == S2[j]?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "When characters match, LCS(i, j) = 1 + LCS(i-1, j-1).",
                    "options": [
                        ("A", "LCS(i, j) = 1 + LCS(i-1, j-1)", True),
                        ("B", "LCS(i, j) = max(LCS(i-1, j), LCS(i, j-1))", False),
                        ("C", "LCS(i, j) = LCS(i-1, j) + LCS(i, j-1)", False),
                        ("D", "LCS(i, j) = 2 * LCS(i-1, j-1)", False),
                    ]
                },
                {
                    "text": "What is the primary difference between Top-Down Memoization and Bottom-Up Tabulation in Dynamic Programming?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Top-down uses recursion and caches subproblem outputs; bottom-up iteratively fills a table from base cases without recursion stack overhead.",
                    "options": [
                        ("A", "Top-down uses recursion with a lookup cache; bottom-up iteratively fills a table starting from the smallest base cases", True),
                        ("B", "Top-down always uses O(1) space whereas bottom-up requires O(2^N)", False),
                        ("C", "Bottom-up cannot solve NP-complete problems", False),
                        ("D", "There is no difference in memory or call stack behavior", False),
                    ]
                }
            ]
        },

        # ==========================================
        # 3. APTITUDE (15% Weight)
        # ==========================================
        {
            "module": apt_mod,
            "subject": "Percentages, Ratios and Proportions",
            "topic": "Percentages, Profit & Loss, Successive Discounts",
            "title": "Aptitude: Percentages, Profit, Loss & Ratios",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Essential campus placement quantitative aptitude covering marked prices, discounts, cost-price equations, and ratios.",
            "questions": [
                {
                    "text": "A shopkeeper marks an article 40% above its cost price and offers a discount of 25%. What is his net profit or loss percentage?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Let CP = 100. Marked Price = 140. Selling Price = 140 * 0.75 = 105. Profit = 105 - 100 = 5%.",
                    "options": [
                        ("A", "15% Profit", False),
                        ("B", "5% Profit", True),
                        ("C", "5% Loss", False),
                        ("D", "10% Profit", False),
                    ]
                },
                {
                    "text": "If two successive discounts of 20% and 10% are given on an article, what is the single equivalent discount percentage?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Equivalent discount = d1 + d2 - (d1 * d2)/100 = 20 + 10 - (200/100) = 30 - 2 = 28%.",
                    "options": [
                        ("A", "30%", False),
                        ("B", "28%", True),
                        ("C", "25%", False),
                        ("D", "32%", False),
                    ]
                },
                {
                    "text": "The ratio of boys to girls in a college is 5 : 3. If there are 150 more boys than girls, what is the total number of students?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Difference = 5x - 3x = 2x = 150 => x = 75. Total students = 8x = 8 * 75 = 600.",
                    "options": [
                        ("A", "450", False),
                        ("B", "500", False),
                        ("C", "600", True),
                        ("D", "750", False),
                    ]
                },
                {
                    "text": "A mixture of 60 liters of milk and water contains milk and water in the ratio 2 : 1. How much water must be added so that the ratio becomes 1 : 2?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Milk = (2/3)*60 = 40L, Water = (1/3)*60 = 20L. New ratio requires Milk/Water = 1/2 => 40 / (20 + W) = 1/2 => 20 + W = 80 => W = 60 liters.",
                    "options": [
                        ("A", "40 liters", False),
                        ("B", "60 liters", True),
                        ("C", "80 liters", False),
                        ("D", "50 liters", False),
                    ]
                }
            ]
        },
        {
            "module": apt_mod,
            "subject": "Time and Work",
            "topic": "Work Rates, Alternate Days & Pipes",
            "title": "Aptitude: Time, Work & Cisterns",
            "difficulty": "MEDIUM",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Standard work rate problems, multi-worker coordination, efficiency ratios, and inlet/outlet pipe calculations.",
            "questions": [
                {
                    "text": "A can finish a work in 12 days and B can finish the same work in 24 days. If they work together, how many days will they take to complete the work?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Combined rate = 1/12 + 1/24 = (2 + 1)/24 = 3/24 = 1/8. Total days = 8 days.",
                    "options": [
                        ("A", "6 days", False),
                        ("B", "8 days", True),
                        ("C", "10 days", False),
                        ("D", "18 days", False),
                    ]
                },
                {
                    "text": "A is twice as efficient as B and together they can complete a task in 14 days. In how many days can A alone complete the task?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Efficiency of A = 2 units/day, B = 1 unit/day. Combined = 3 units/day. Total work = 3 * 14 = 42 units. A alone = 42 / 2 = 21 days.",
                    "options": [
                        ("A", "21 days", True),
                        ("B", "28 days", False),
                        ("C", "42 days", False),
                        ("D", "16 days", False),
                    ]
                },
                {
                    "text": "Pipe A can fill a tank in 6 hours and Pipe B can empty it in 8 hours. If both pipes are opened simultaneously, in how many hours will the tank be full?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Net fill rate = 1/6 - 1/8 = (4 - 3)/24 = 1/24 per hour. Time to fill = 24 hours.",
                    "options": [
                        ("A", "14 hours", False),
                        ("B", "20 hours", False),
                        ("C", "24 hours", True),
                        ("D", "48 hours", False),
                    ]
                },
                {
                    "text": "12 men can complete a project in 18 days working 8 hours a day. How many days will 16 men take to complete the same project working 9 hours a day?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "M1 * D1 * H1 = M2 * D2 * H2 => 12 * 18 * 8 = 16 * D2 * 9 => 1728 = 144 * D2 => D2 = 1728 / 144 = 12 days.",
                    "options": [
                        ("A", "10 days", False),
                        ("B", "12 days", True),
                        ("C", "14 days", False),
                        ("D", "16 days", False),
                    ]
                }
            ]
        },
        {
            "module": apt_mod,
            "subject": "Time, Speed and Distance",
            "topic": "Average Speed, Relative Velocity, Trains & Boats",
            "title": "Aptitude: Speed, Distance, Trains & Boats",
            "difficulty": "MEDIUM",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Problems on relative speed of moving trains, harmonic mean for average speed, and upstream/downstream boat speeds.",
            "questions": [
                {
                    "text": "A student travels to college at 20 km/h and returns home along the same route at 30 km/h. What is his average speed for the round trip?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "For equal distances, Average Speed = (2 * S1 * S2) / (S1 + S2) = (2 * 20 * 30) / (20 + 30) = 1200 / 50 = 24 km/h.",
                    "options": [
                        ("A", "25 km/h", False),
                        ("B", "24 km/h", True),
                        ("C", "23.5 km/h", False),
                        ("D", "26 km/h", False),
                    ]
                },
                {
                    "text": "A train 180 meters long is traveling at a speed of 54 km/h. How many seconds will it take to pass an electric pole?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Convert speed to m/s: 54 * (5/18) = 15 m/s. Time = Distance / Speed = 180 / 15 = 12 seconds.",
                    "options": [
                        ("A", "10 seconds", False),
                        ("B", "12 seconds", True),
                        ("C", "15 seconds", False),
                        ("D", "18 seconds", False),
                    ]
                },
                {
                    "text": "A boat can travel with a speed of 13 km/h in still water. If the speed of the stream is 4 km/h, what is the time taken by the boat to travel 68 km downstream?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Downstream speed = Speed of boat + Speed of stream = 13 + 4 = 17 km/h. Time = 68 / 17 = 4 hours.",
                    "options": [
                        ("A", "3 hours", False),
                        ("B", "4 hours", True),
                        ("C", "5 hours", False),
                        ("D", "6 hours", False),
                    ]
                },
                {
                    "text": "Two trains 140 m and 160 m long are running towards each other on parallel tracks at 40 km/h and 50 km/h. How long will they take to pass each other from the moment they meet?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Total distance = 140 + 160 = 300 m. Relative speed = 40 + 50 = 90 km/h = 90 * (5/18) = 25 m/s. Time = 300 / 25 = 12 seconds.",
                    "options": [
                        ("A", "10 seconds", False),
                        ("B", "12 seconds", True),
                        ("C", "14 seconds", False),
                        ("D", "15 seconds", False),
                    ]
                }
            ]
        },
        {
            "module": apt_mod,
            "subject": "Probability and Permutations",
            "topic": "Permutations, Combinations & Probability",
            "title": "Aptitude: Permutations, Combinations & Probability",
            "difficulty": "HARD",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Solve counting and probability problems: letter arrangements, selecting committees, dice roll distributions, and card decks.",
            "questions": [
                {
                    "text": "In how many distinct ways can the letters of the word 'LEADER' be arranged?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Total letters = 6. The letter 'E' repeats 2 times. Distinct arrangements = 6! / 2! = 720 / 2 = 360.",
                    "options": [
                        ("A", "720", False),
                        ("B", "360", True),
                        ("C", "120", False),
                        ("D", "180", False),
                    ]
                },
                {
                    "text": "Out of 7 men and 4 women, a committee of 5 is to be formed. In how many ways can this be done so that the committee includes exactly 3 men and 2 women?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Ways to choose 3 men from 7: 7C3 = 35. Ways to choose 2 women from 4: 4C2 = 6. Total ways = 35 * 6 = 210.",
                    "options": [
                        ("A", "140", False),
                        ("B", "210", True),
                        ("C", "420", False),
                        ("D", "105", False),
                    ]
                },
                {
                    "text": "Two fair six-sided dice are rolled simultaneously. What is the probability that the sum of the numbers appearing on the dice is 8?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Sample space = 36. Favorable outcomes for sum 8: (2,6), (3,5), (4,4), (5,3), (6,2) -> 5 outcomes. Probability = 5/36.",
                    "options": [
                        ("A", "1/6", False),
                        ("B", "5/36", True),
                        ("C", "7/36", False),
                        ("D", "1/9", False),
                    ]
                },
                {
                    "text": "A card is drawn from a well-shuffled pack of 52 cards. What is the probability of getting either a King or a Heart?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Kings = 4, Hearts = 13, King of Hearts = 1. Total favorable = 4 + 13 - 1 = 16. Probability = 16 / 52 = 4/13.",
                    "options": [
                        ("A", "17/52", False),
                        ("B", "4/13", True),
                        ("C", "1/4", False),
                        ("D", "9/26", False),
                    ]
                }
            ]
        },
        {
            "module": apt_mod,
            "subject": "Number Systems",
            "topic": "Divisibility, Unit Digits, LCM & HCF",
            "title": "Aptitude: Number Systems, LCM, HCF & Remainders",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Essential aptitude fundamentals on unit digit cycles, divisibility tests, remainders, and LCM/HCF relations.",
            "questions": [
                {
                    "text": "What is the unit digit of the expression 7^105?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The unit digit cycle for powers of 7 has period 4: 7^1=7, 7^2=9, 7^3=3, 7^4=1. 105 mod 4 = 1. Hence, the unit digit is 7.",
                    "options": [
                        ("A", "1", False),
                        ("B", "7", True),
                        ("C", "9", False),
                        ("D", "3", False),
                    ]
                },
                {
                    "text": "The HCF and LCM of two numbers are 11 and 7700 respectively. If one of the numbers is 275, find the other number.",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Product of two numbers = HCF * LCM => 275 * X = 11 * 7700 => X = (11 * 7700) / 275 = 84700 / 275 = 308.",
                    "options": [
                        ("A", "280", False),
                        ("B", "308", True),
                        ("C", "312", False),
                        ("D", "324", False),
                    ]
                },
                {
                    "text": "Which digit must replace '*' in the number 97215*6 so that it is completely divisible by 11?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Divisibility by 11: (Sum of odd-position digits) - (Sum of even-position digits) must be 0 or a multiple of 11. Odd positions from right: 6 + 5 + 2 + 9 = 22. Even positions: * + 1 + 7 = 8 + *. Difference = 22 - (8 + *) = 14 - *. For difference = 11, * = 3.",
                    "options": [
                        ("A", "1", False),
                        ("B", "3", True),
                        ("C", "5", False),
                        ("D", "7", False),
                    ]
                },
                {
                    "text": "How many trailing zeroes are there in the decimal representation of 100! (100 factorial)?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Count factors of 5 in 100!: floor(100/5) + floor(100/25) = 20 + 4 = 24 trailing zeroes.",
                    "options": [
                        ("A", "20", False),
                        ("B", "24", True),
                        ("C", "25", False),
                        ("D", "22", False),
                    ]
                }
            ]
        },

        # ==========================================
        # 4. LOGICAL REASONING (15% Weight)
        # ==========================================
        {
            "module": lr_mod,
            "subject": "Number and Letter Series",
            "topic": "Sequence Patterns, Differences & Alpha Shifts",
            "title": "Logical Reasoning: Number & Alphanumeric Series",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Crack common patterns tested in placement reasoning rounds: prime series, differences of differences, and letter shifts.",
            "questions": [
                {
                    "text": "Find the missing number in the sequence: 2, 6, 12, 20, 30, 42, ?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Patterns: n*(n+1) -> 1*2=2, 2*3=6, 3*4=12, 4*5=20, 5*6=30, 6*7=42, 7*8=56. (Or differences +4, +6, +8, +10, +12, +14). 42 + 14 = 56.",
                    "options": [
                        ("A", "50", False),
                        ("B", "56", True),
                        ("C", "60", False),
                        ("D", "64", False),
                    ]
                },
                {
                    "text": "Find the next term in the letter series: B, E, I, N, T, ?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Letter positions in alphabet: B(2) + 3 = E(5); E(5) + 4 = I(9); I(9) + 5 = N(14); N(14) + 6 = T(20); T(20) + 7 = 27 = A (wrapping 1).",
                    "options": [
                        ("A", "Y", False),
                        ("B", "Z", False),
                        ("C", "A", True),
                        ("D", "B", False),
                    ]
                },
                {
                    "text": "Find the odd one out from the following group: 27, 64, 125, 144, 216",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "27 = 3^3, 64 = 4^3, 125 = 5^3, 216 = 6^3 are all perfect cubes. 144 is 12^2, not a cube of an integer.",
                    "options": [
                        ("A", "64", False),
                        ("B", "125", False),
                        ("C", "144", True),
                        ("D", "216", False),
                    ]
                },
                {
                    "text": "Identify the missing element in the alphanumeric sequence: A2C, B4D, C8E, D16F, ?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "First letter: A -> B -> C -> D -> E. Middle number doubles: 2 -> 4 -> 8 -> 16 -> 32. Last letter: C -> D -> E -> F -> G. Combined: E32G.",
                    "options": [
                        ("A", "E32G", True),
                        ("B", "E24G", False),
                        ("C", "F32G", False),
                        ("D", "E32H", False),
                    ]
                }
            ]
        },
        {
            "module": lr_mod,
            "subject": "Coding-Decoding",
            "topic": "Shift Ciphers, Number Substitutions & Matrices",
            "title": "Logical Reasoning: Coding-Decoding & Symbol Operations",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Decode substitution ciphers, reverse alphabet mappings, and fictitious language statements.",
            "questions": [
                {
                    "text": "If in a certain code, 'COMPUTER' is written as 'RFUVQNPC', how will 'MEDICINE' be written in that same code?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Reverse the word COMPUTER -> RETUPMOC. Invert/shift each inner letter by +1, keeping first and last characters matched. MEDICINE reversed is ENICIDEM. Shifting intermediate letters by +1 gives EOJDJEFM.",
                    "options": [
                        ("A", "EOJDJEFM", True),
                        ("B", "MFEJDINE", False),
                        ("C", "EMDJIFEM", False),
                        ("D", "EOJDEJFM", False),
                    ]
                },
                {
                    "text": "If 'DELHI' is coded as 73541 and 'CALCUTTA' is coded as 82589662, how will 'CALICUT' be coded?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Direct character substitution: C=8, A=2, L=5, I=1, C=8, U=9, T=6. Result: 8251896.",
                    "options": [
                        ("A", "8251896", True),
                        ("B", "8258961", False),
                        ("C", "8521896", False),
                        ("D", "8251968", False),
                    ]
                },
                {
                    "text": "In a fictitious language: 'pit dar na' means 'you are good', 'dar tok pa' means 'good and bad', and 'tim na tok' means 'they are bad'. What word represents 'they'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Comparing (1) and (2): 'dar' = 'good'. Comparing (1) and (3): 'na' = 'are'. Comparing (2) and (3): 'tok' = 'bad'. In statement (3) 'tim na tok' ('they are bad'), 'tim' must mean 'they'.",
                    "options": [
                        ("A", "na", False),
                        ("B", "tok", False),
                        ("C", "tim", True),
                        ("D", "dar", False),
                    ]
                },
                {
                    "text": "If '+' means multiplication, '-' means division, '*' means addition, and '/' means subtraction, what is the value of: 20 + 5 - 10 * 6 / 4?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Substitute operators: 20 * 5 / 10 + 6 - 4. Following BODMAS: 20 * (5/10) = 20 * 0.5 = 10. Then 10 + 6 - 4 = 12.",
                    "options": [
                        ("A", "10", False),
                        ("B", "12", True),
                        ("C", "15", False),
                        ("D", "18", False),
                    ]
                }
            ]
        },
        {
            "module": lr_mod,
            "subject": "Seating Arrangements",
            "topic": "Circular Tables, Linear Rows & Puzzles",
            "title": "Logical Reasoning: Seating Arrangements & Puzzles",
            "difficulty": "HARD",
            "time_limit": 20,
            "passing_percentage": 50,
            "description": "Tackle challenging analytical arrangement puzzles commonly presented in campus aptitude rounds.",
            "questions": [
                {
                    "text": "Eight friends A, B, C, D, E, F, G, and H are sitting in a circle facing the center. B is between G and D. H is third to the left of B and second to the right of A. C is between A and G. Who is sitting directly opposite to A?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Placing in circular order facing center: A, C, G, B, D, F/E, H... tracing opposite positions shows D is directly opposite to A.",
                    "options": [
                        ("A", "B", False),
                        ("B", "D", True),
                        ("C", "G", False),
                        ("D", "H", False),
                    ]
                },
                {
                    "text": "Five people P, Q, R, S, and T are standing in a line facing North. S is between T and Q. Q is to the immediate left of R. P is to the immediate left of T. Who is standing in the exact middle of the line?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Arranging left to right: P, T, S, Q, R. The middle person is S.",
                    "options": [
                        ("A", "P", False),
                        ("B", "T", False),
                        ("C", "S", True),
                        ("D", "Q", False),
                    ]
                },
                {
                    "text": "Six books P, Q, R, S, T, and U are stacked one above another. R is just above S. T is between P and U. P is not at the top. If U is at the bottom, which book is at the top?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "U is at bottom (position 1). T is between P and U -> position 2 is T, position 3 is P. Remaining are R and S (R above S). Therefore position 4 is S, position 5 is R, or R at position 6 (top). R is at the top.",
                    "options": [
                        ("A", "R", True),
                        ("B", "S", False),
                        ("C", "P", False),
                        ("D", "Q", False),
                    ]
                },
                {
                    "text": "In a row of 40 children facing North, Rohan is 18th from the left end. What is his position from the right end?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Position from right = Total + 1 - Position from left = 40 + 1 - 18 = 23rd.",
                    "options": [
                        ("A", "22nd", False),
                        ("B", "23rd", True),
                        ("C", "24th", False),
                        ("D", "21st", False),
                    ]
                }
            ]
        },
        {
            "module": lr_mod,
            "subject": "Blood Relations",
            "topic": "Family Trees, Direct & Coded Relations",
            "title": "Logical Reasoning: Blood Relations & Family Trees",
            "difficulty": "MEDIUM",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Evaluate multi-generational deductions, photograph descriptions, and coded relationship equations.",
            "questions": [
                {
                    "text": "Pointing towards a gentleman in a photograph, a woman said: 'His only brother is the father of my daughter's father.' How is the gentleman related to the woman's husband?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'My daughter's father' = woman's husband. 'Father of my husband' = woman's father-in-law. 'The gentleman's brother' = woman's father-in-law. Therefore, the gentleman is the Uncle (Paternal Uncle) of the husband.",
                    "options": [
                        ("A", "Father", False),
                        ("B", "Paternal Uncle", True),
                        ("C", "Grandfather", False),
                        ("D", "Brother-in-law", False),
                    ]
                },
                {
                    "text": "A is the father of C, but C is not his son. B is the sister of C. What is C to B?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "If A is father of C and C is not son, C must be the daughter. Since B is sister of C, C is B's sister.",
                    "options": [
                        ("A", "Brother", False),
                        ("B", "Sister", True),
                        ("C", "Daughter", False),
                        ("D", "Cousin", False),
                    ]
                },
                {
                    "text": "If 'P + Q' means P is the father of Q; 'P - Q' means P is the sister of Q; 'P * Q' means P is the brother of Q. Which expression represents that 'M is the aunt of N'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Aunt means sister of the father. If M - K means M is sister of K, and K + N means K is father of N, then M is the aunt of N. Hence M - K + N.",
                    "options": [
                        ("A", "M - K + N", True),
                        ("B", "M + K * N", False),
                        ("C", "M * K - N", False),
                        ("D", "K + M - N", False),
                    ]
                },
                {
                    "text": "Introducing a boy, a girl says, 'He is the son of the daughter of the father of my uncle.' How is the boy related to the girl?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'Father of my uncle' = my grandfather. 'Daughter of my grandfather' = my mother (or maternal aunt). 'Son of my mother' = my brother. Thus the boy is her brother.",
                    "options": [
                        ("A", "Brother", True),
                        ("B", "Uncle", False),
                        ("C", "Cousin only", False),
                        ("D", "Nephew", False),
                    ]
                }
            ]
        },
        {
            "module": lr_mod,
            "subject": "Syllogisms",
            "topic": "Deductive Logic, Venn Diagrams & Validity",
            "title": "Logical Reasoning: Syllogisms & Deductive Logic",
            "difficulty": "MEDIUM",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Verify validity of logical deductions using standard syllogism principles, Venn diagrams, and complementary pairs.",
            "questions": [
                {
                    "text": "Statements: (1) All poets are dreamers. (2) All painters are dreamers. Conclusions: I. All painters are poets. II. Some dreamers are not painters.",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Both poets and painters are subsets of dreamers, but they may or may not overlap. Conclusion I does not necessarily follow. Neither does II (since all dreamers could be painters). Neither follows.",
                    "options": [
                        ("A", "Only Conclusion I follows", False),
                        ("B", "Only Conclusion II follows", False),
                        ("C", "Either I or II follows", False),
                        ("D", "Neither Conclusion I nor II follows", True),
                    ]
                },
                {
                    "text": "Statements: (1) All mangoes are golden. (2) No golden things are cheap. Conclusions: I. All mangoes are cheap. II. Golden mangoes are not cheap.",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Since all mangoes are golden, and no golden things are cheap, no mangoes can be cheap. Hence II ('Golden mangoes are not cheap') definitely follows.",
                    "options": [
                        ("A", "Only Conclusion I follows", False),
                        ("B", "Only Conclusion II follows", True),
                        ("C", "Both I and II follow", False),
                        ("D", "Neither follows", False),
                    ]
                },
                {
                    "text": "Which pair of conclusions forms an 'Either-Or' complementary pair in standard categorical syllogism?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'Some A are B' (Particular Affirmative - I) and 'No A is B' (Universal Negative - E) are exact contradictories with identical subject and predicate.",
                    "options": [
                        ("A", "'Some A are B' and 'No A is B'", True),
                        ("B", "'All A are B' and 'No A is B'", False),
                        ("C", "'All A are B' and 'Some A are B'", False),
                        ("D", "'Some A are B' and 'Some A are not B'", False),
                    ]
                },
                {
                    "text": "Statements: (1) Some cats are dogs. (2) No dog is an elephant. Conclusion: Some cats are not elephants.",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "The cats that are dogs cannot be elephants because no dog is an elephant. Hence, those cats are definitely not elephants. The conclusion follows.",
                    "options": [
                        ("A", "The conclusion definitely follows", True),
                        ("B", "The conclusion does not follow", False),
                        ("C", "The conclusion is invalid in all interpretations", False),
                        ("D", "Insufficient information", False),
                    ]
                }
            ]
        },
        {
            "module": lr_mod,
            "subject": "Direction Sense",
            "topic": "Compass Bearings, Displacements & Shadows",
            "title": "Logical Reasoning: Direction Sense & Navigation",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Calculate shortest geometric distance, turns relative to cardinal bearings, and shadow directions.",
            "questions": [
                {
                    "text": "A person walks 8 km towards North, then turns right and walks 6 km. What is the shortest displacement from his starting point, and in which direction is he?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Using Pythagoras theorem: sqrt(8^2 + 6^2) = sqrt(64 + 36) = sqrt(100) = 10 km. Since he went North then East, he is in the North-East direction.",
                    "options": [
                        ("A", "14 km, North", False),
                        ("B", "10 km, North-East", True),
                        ("C", "10 km, South-East", False),
                        ("D", "12 km, North-West", False),
                    ]
                },
                {
                    "text": "One morning after sunrise, Suresh was standing facing a pole. The shadow of the pole fell exactly to his right. Which direction was Suresh facing?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "In the morning, the sun is in the East, so shadows fall towards the West. If the shadow is to his right, West is to his right. A person who has West to their right is facing South.",
                    "options": [
                        ("A", "East", False),
                        ("B", "West", False),
                        ("C", "South", True),
                        ("D", "North", False),
                    ]
                },
                {
                    "text": "A man is facing North-West. He turns 90 degrees in the clockwise direction, then 180 degrees in the anticlockwise direction. Which direction is he facing now?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Initial: NW (315° or -45° from North). +90° clockwise = NE (45°). Then -180° = SW (225°). He is facing South-East (or South-East from 45° - 180° = -135° = South-East).",
                    "options": [
                        ("A", "South-East", True),
                        ("B", "South-West", False),
                        ("C", "North-East", False),
                        ("D", "South", False),
                    ]
                },
                {
                    "text": "Starting from point A, Rahul travels 3 km East to B, then turns South and walks 4 km to C. How far is he from point A?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "Displacement = sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5 km.",
                    "options": [
                        ("A", "7 km", False),
                        ("B", "5 km", True),
                        ("C", "6 km", False),
                        ("D", "12 km", False),
                    ]
                }
            ]
        },

        # ==========================================
        # 5. COMMUNICATION SKILLS (10% Weight)
        # ==========================================
        {
            "module": comm_mod,
            "subject": "Verbal Communication",
            "topic": "Grammar, Professional Email & Fluency",
            "title": "Verbal Communication: Corporate English & Grammar",
            "difficulty": "EASY",
            "time_limit": 15,
            "passing_percentage": 50,
            "description": "Essential placement verbal ability: subject-verb agreement, formal tone, commonly confused words, and idiom usage.",
            "questions": [
                {
                    "text": "Choose the grammatically correct sentence adhering to subject-verb agreement:",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'Neither the manager nor the team members were...' When subjects are connected by neither/nor, the verb agrees with the closer subject (team members = plural -> were).",
                    "options": [
                        ("A", "Neither the manager nor the team members was present at the review.", False),
                        ("B", "Neither the manager nor the team members were present at the review.", True),
                        ("C", "Neither the manager or the team members were present at the review.", False),
                        ("D", "Neither the manager nor the team members has been present at the review.", False),
                    ]
                },
                {
                    "text": "Which sentence correctly uses the word 'affect' or 'effect'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'Affect' is typically a verb (to influence), while 'effect' is typically a noun (the result). 'The new policy will affect employee productivity' is correct.",
                    "options": [
                        ("A", "The new deployment will effect all database connections.", False),
                        ("B", "The new policy will affect employee productivity positively.", True),
                        ("C", "The medicine had no affect on the symptoms.", False),
                        ("D", "What is the primary affect of this decision?", False),
                    ]
                },
                {
                    "text": "In a professional business email, which sign-off is most appropriate when writing to a corporate recruiter?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'Sincerely' or 'Best regards' followed by full name and contact information is the industry standard for professional business correspondence.",
                    "options": [
                        ("A", "Cheers,", False),
                        ("B", "Catch you later,", False),
                        ("C", "Best regards,", True),
                        ("D", "Yours affectionately,", False),
                    ]
                },
                {
                    "text": "What is the meaning of the idiom 'to beat around the bush'?",
                    "type": "MCQ",
                    "marks": 2,
                    "solution": "'To beat around the bush' means to avoid discussing what is important, speaking evasively or ambiguously.",
                    "options": [
                        ("A", "To reach a swift decision", False),
                        ("B", "To avoid talking about the main topic directly", True),
                        ("C", "To work hard in physical labor", False),
                        ("D", "To resolve a conflict quickly", False),
                    ]
                }
            ]
        }
    ]

    created_tests_count = 0
    created_questions_count = 0

    for t_data in tests_data:
        mod = t_data["module"]
        subj_name = t_data["subject"]
        
        # Find or create corresponding SubjectCategory
        cat = None
        if mod:
            cat = SubjectCategory.objects.filter(module=mod, name__icontains=subj_name.split()[0]).first()
            if not cat:
                cat = SubjectCategory.objects.create(
                    module=mod,
                    name=subj_name,
                    description=t_data["description"][:100],
                    topics=t_data["topic"],
                    order=SubjectCategory.objects.filter(module=mod).count() + 1
                )

        # Check if an assignment with this title already exists
        assignment = Assignment.objects.filter(title=t_data["title"]).first()
        if not assignment:
            assignment = Assignment.objects.create(
                title=t_data["title"],
                module=mod,
                subject_category=cat,
                subject=subj_name,
                topic=t_data["topic"],
                difficulty=t_data["difficulty"],
                time_limit=t_data["time_limit"],
                passing_percentage=t_data["passing_percentage"],
                description=t_data["description"],
                created_by=admin,
                created_by_name="Administrator" if not admin else admin.username,
                assessment_type="SUBJECT",
                exam_type="SUBJECT",
                status="PUBLISHED",
                max_attempts=3,
                show_solutions_after_submission=True,
                negative_marking=0.25
            )
            created_tests_count += 1
        else:
            assignment.module = mod
            assignment.subject_category = cat
            assignment.subject = subj_name
            assignment.status = "PUBLISHED"
            assignment.save()

        # Create questions if none exist
        if assignment.questions.count() == 0:
            for q_idx, q_info in enumerate(t_data["questions"], 1):
                question = Question.objects.create(
                    assignment=assignment,
                    question_text=q_info["text"],
                    code_snippet=q_info.get("code", ""),
                    question_type=q_info.get("type", "MCQ"),
                    marks=q_info["marks"],
                    solution=q_info["solution"],
                    order=q_idx
                )
                created_questions_count += 1

                for opt_label, opt_text, is_corr in q_info["options"]:
                    QuestionOption.objects.create(
                        question=question,
                        option_label=opt_label,
                        option_text=opt_text,
                        is_correct=is_corr
                    )

            assignment.recalculate_total_marks()

    print(f"SUCCESS: Seeded {created_tests_count} new tests and {created_questions_count} questions.")

if __name__ == '__main__':
    run_seed()
