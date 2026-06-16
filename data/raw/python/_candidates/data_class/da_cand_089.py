class ReturnsContract(Contract):
    """Contract to check the output of a callback

    general form:
    @returns request(s)/item(s) [min=1 [max]]

    e.g.:
    @returns request
    @returns request 2
    @returns request 2 10
    @returns request 0 10
    """

    name = "returns"
    object_type_verifiers = {
        "request": lambda x: isinstance(x, Request),
        "requests": lambda x: isinstance(x, Request),
        "item": is_item,
        "items": is_item,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if len(self.args) not in [1, 2, 3]:
            raise ValueError(
                f"Incorrect argument quantity: expected 1, 2 or 3, got {len(self.args)}"
            )
        self.obj_name = self.args[0] or None
        self.obj_type_verifier = self.object_type_verifiers[self.obj_name]

        try:
            self.min_bound = int(self.args[1])
        except IndexError:
            self.min_bound = 1

        try:
            self.max_bound = int(self.args[2])
        except IndexError:
            self.max_bound = float("inf")

    def post_process(self, output):
        occurrences = 0
        for x in output:
            if self.obj_type_verifier(x):
                occurrences += 1

        assertion = self.min_bound <= occurrences <= self.max_bound

        if not assertion:
            if self.min_bound == self.max_bound:
                expected = self.min_bound
            else:
                expected = f"{self.min_bound}..{self.max_bound}"

            raise ContractFail(
                f"Returned {occurrences} {self.obj_name}, expected {expected}"
            )
