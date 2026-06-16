def test_alter_field_and_index_together(self):
    """Fields are altered after deleting some index_together."""
    initial_author = ModelState(
        "testapp",
        "Author",
        [
            ("id", models.AutoField(primary_key=True)),
            ("name", models.CharField(max_length=200)),
            ("age", models.IntegerField(db_index=True)),
        ],
        {
            "index_together": {("name",)},
        },
    )
    author_reversed_constraints = ModelState(
        "testapp",
        "Author",
        [
            ("id", models.AutoField(primary_key=True)),
            ("name", models.CharField(max_length=200, unique=True)),
            ("age", models.IntegerField()),
        ],
        {
            "index_together": {("age",)},
        },
    )
    changes = self.get_changes([initial_author], [author_reversed_constraints])

    self.assertNumberMigrations(changes, "testapp", 1)
    self.assertOperationTypes(
        changes,
        "testapp",
        0,
        [
            "AlterIndexTogether",
            "AlterField",
            "AlterField",
            "AlterIndexTogether",
        ],
    )
    self.assertOperationAttributes(
        changes,
        "testapp",
        0,
        0,
        name="author",
        index_together=set(),
    )
    self.assertOperationAttributes(
        changes,
        "testapp",
        0,
        1,
        model_name="author",
        name="age",
    )
    self.assertOperationAttributes(
        changes,
        "testapp",
        0,
        2,
        model_name="author",
        name="name",
    )
    self.assertOperationAttributes(
        changes,
        "testapp",
        0,
        3,
        name="author",
        index_together={("age",)},
    )
