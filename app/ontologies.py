class Medication:
    @classmethod
    def get_children(cls) -> list:
        def collect_descendants(cls) -> list:
            subclasses = cls.__subclasses__()
            descendants = []
            for subclass in subclasses:
                descendants.append(subclass)
                descendants.extend(collect_descendants(subclass))
            return descendants
        all_descendants = collect_descendants(cls)
        return all_descendants   
    # Class-level attribute (shared by all instances)
    _shared_lists = {}

    @classmethod
    def get_shared_lists(cls):
        """Provide access to the shared lists."""
        return cls._shared_lists

    @classmethod
    def get_all_lists_as_string(cls):
        """Return all descendant lists as a single formatted string."""
        result = []
        for name, values in cls.get_shared_lists().items():
            result.append(f"{name}: {values}")
        return "\n".join(result)

    def __init__(self, name):
        self.name = name
        # Initialize the list for this instance in the shared dictionary
        super().get_shared_lists()[self.name] = []

    def append_to_list(self, value):
        """Append a value to this instance's list."""
        super().get_shared_lists()[self.name].append(value)
        print(f"Value '{value}' added to the list for instance '{self.name}'.")

    def remove_from_list(self, value):
        """Remove a value from this instance's list."""
        try:
            super().get_shared_lists()[self.name].remove(value)
            print(f"Value '{value}' removed from the list for instance '{self.name}'.")
        except ValueError:
            print(f"Value '{value}' not found in the list for instance '{self.name}'.")

    def get_list(self):
        """Retrieve this instance's list."""
        return super().get_shared_lists()[self.name]

    def __str__(self):
        return self.name
    
    def class_name(self):
        return self.__class__.__name__
    
class Antidiabetics(Medication):
    pass

class Biguanides(Antidiabetics):
    pass

class Insulin(Antidiabetics):
    pass

class GLP1(Antidiabetics):
    pass





    

