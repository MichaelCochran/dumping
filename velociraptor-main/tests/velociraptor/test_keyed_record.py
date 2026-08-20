from velociraptor.types.keyed_record import *
import itertools

class TestKeyedRecord:
    def setup_method(self, method):
        self.x = KeyedRecord('a', '1', 'Test')
        self.y = KeyedRecord('b', '2', 'Test')
        self.z = KeyedRecord('a', '1', 'Test')
        self.n = KeyedRecord(None, None, None)

    def test_keyed_record_eq(self):
        assert(self.x == self.x)
        assert(self.x is self.x)
        assert(self.x != self.y)
        assert(self.x is not self.y)
        assert(self.x == self.z)
        assert(self.x is not self.z)
        assert(self.x != self.n)
        assert(self.x is not self.n)
        assert(self.n == NullKeyedRecord)
        assert(self.n is not NullKeyedRecord)

    def test_keyed_record_lt(self):
        expected = [KeyedRecord(*x) for x in itertools.product(['a', 'b', None], ['1', '2', None], ['x', 'y', None])]
        actual = sorted([KeyedRecord(*x) for x in itertools.product(['b', None, 'a'], [None, '1', '2'], ['y', 'x', None])])

        assert(expected == actual)

        # Test that sorting a list of NullKeyedRecords is successful
        nullelementlist = [self.n] * 3
        assert(len(sorted(nullelementlist)) == 3)
