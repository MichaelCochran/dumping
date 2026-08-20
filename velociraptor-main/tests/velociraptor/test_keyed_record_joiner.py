from velociraptor.types.keyed_record_joiner import *

class TestKeyedRecordJoiner:

    def setup_method(self, method):
        self.left_dict : dict[str, KeyedRecord] = {
           'l01': KeyedRecord('01', 'a',  'Left01a 1:1'),
           'l02': KeyedRecord('02', 'b',  'Left02b 1:1'),
           'l03': KeyedRecord(None, 'c',  'Left03c LeftOnly NoPK'),
           'l04': KeyedRecord('04', None, 'Left04d RightOnly NoFK'),
           'l05': KeyedRecord('_a', 'e',  'Left05e LeftOnly'),
           'l06': KeyedRecord('06', '_1', 'Left06f RightOnly'),
           'l07': KeyedRecord('_b', '_2', 'Left07g NoMatch'),
           'l08': KeyedRecord('08', 'h',  'Left08h RightOnly Multiple'),
           'l09': KeyedRecord('09', 'i',  'Left09i 1:M LeftOnly'),
           'l10': KeyedRecord('10', 'j',  'Left10j 1:M LeftOnly Multiple'),
           'l11': KeyedRecord(None, 'k',  'Left11k 1:M LeftOnly NoPK'),
           'l12': KeyedRecord('12', None, 'Left12l RightOnly Multiple NoFK'),
           'l13': KeyedRecord('13', 'm',  'Left13m 1:M RightOnly Multiple NoFK'),
           'l14': KeyedRecord('14', 'n',  'Left14n RightOnly Multiple NoPK'),
           'l15': KeyedRecord('15', 'o',  'Left15o M:M Both a'),
           'l16': KeyedRecord('15', 'o',  'Left15o M:M Both b'),
           'l17': KeyedRecord('15', 'o',  'Left15o M:M Both c'),
           'l18': KeyedRecord('16', 'p',  'Left16p M:M RightOnly SameFK a'),
           'l19': KeyedRecord('16', 'p',  'Left16p M:M RightOnly SameFK b'),
           'l20': KeyedRecord('16', 'p',  'Left16p M:M RightOnly SameFK c'),
           'l21': KeyedRecord('17', 's',  'Left17s M:M RightOnly DiffFK a'),
           'l22': KeyedRecord('17', 't',  'Left17t M:M RightOnly DiffFK b'),
           'l23': KeyedRecord('17', 'u',  'Left17u M:M RightOnly DiffFK c'),
           'l24': KeyedRecord(None, None, 'Left18v None None')
        }

        self.right_dict : dict[str, KeyedRecord] = {
           'r01': KeyedRecord('a',  '01', 'Right01a 1:1'),
           'r02': KeyedRecord('b',  '02', 'Right02b 1:1'),
           'r03': KeyedRecord('c',  '03', 'Right03c LeftOnly NoPK'),
           'r04': KeyedRecord('d',  '04', 'Right04d RightOnly NoFK'),
           'r05': KeyedRecord('e',  '05', 'Right05e LeftOnly'),
           'r06': KeyedRecord('f',  '06', 'Right06f RightOnly'),
           'r07': KeyedRecord('g',  '07', 'Right07g NoMatch'),
           'r08': KeyedRecord('h1', '08', 'Right08h RightOnly Multiple 1'),
           'r09': KeyedRecord('h2', '08', 'Right08h RightOnly Multiple 2'),
           'r10': KeyedRecord('h3', '08', 'Right08h RightOnly Multiple 3'),
           'r11': KeyedRecord('i',  '9a', 'Right09i 1:M LeftOnly 1'),
           'r12': KeyedRecord('i',  '9b', 'Right09i 1:M LeftOnly 2'),
           'r13': KeyedRecord('i',  '9c', 'Right09i 1:M LeftOnly 3'),
           'r14': KeyedRecord('j',  '10', 'Right10j 1:M LeftOnly Multiple 1'),
           'r15': KeyedRecord('j',  '10', 'Right10j 1:M LeftOnly Multiple 2'),
           'r16': KeyedRecord('j',  '10', 'Right10j 1:M LeftOnly Multiple 3'),
           'r17': KeyedRecord('k',  '11', 'Right11k 1:M LeftOnly NoPK 1'),
           'r18': KeyedRecord('k',  '11', 'Right11k 1:M LeftOnly NoPK 2'),
           'r19': KeyedRecord('k',  '11', 'Right11k 1:M LeftOnly NoPK 3'),
           'r20': KeyedRecord('l',  '12', 'Right12l RightOnly Multiple NoFK 1'),
           'r21': KeyedRecord('l',  '12', 'Right12l RightOnly Multiple NoFK 2'),
           'r22': KeyedRecord('l',  '12', 'Right12l RightOnly Multiple NoFK 3'),
           'r23': KeyedRecord('m',  None, 'Right13m 1:M RightOnly Multiple NoFK 1'),
           'r24': KeyedRecord('m',  None, 'Right13m 1:M RightOnly Multiple NoFK 2'),
           'r25': KeyedRecord('m',  None, 'Right13m 1:M RightOnly Multiple NoFK 3'),
           'r26': KeyedRecord(None, '14', 'Right14n RightOnly Multiple NoPK 1'),
           'r27': KeyedRecord(None, '14', 'Right14n RightOnly Multiple NoPK 2'),
           'r28': KeyedRecord(None, '14', 'Right14n RightOnly Multiple NoPK 3'),
           'r29': KeyedRecord('o',  '15', 'Right15o M:M Both 1'),
           'r30': KeyedRecord('o',  '15', 'Right15o M:M Both 2'),
           'r31': KeyedRecord('o',  '15', 'Right15o M:M Both 3'),
           'r32': KeyedRecord('p',  '16', 'Right16p M:M RightOnly DiffPK 1'),
           'r33': KeyedRecord('q',  '16', 'Right16q M:M RightOnly DiffPK 2'),
           'r34': KeyedRecord(None, '16', 'Right16r M:M RightOnly DiffPK 3'),
           'r35': KeyedRecord('s',  '17', 'Right17s M:M RightOnly DiffFK 1'),
           'r36': KeyedRecord('t',  '17', 'Right17t M:M RightOnly DiffFK 2'),
           'r37': KeyedRecord(None, '17', 'Right17u M:M RightOnly DiffFK 3'),
           'r38': KeyedRecord(None, None, 'Right18v None None')
        }

        self.expectedMapping = [
           ('l01', 'r01', MatchType.ONE_TO_ONE, MatchType.ONE_TO_ONE, False, False),
           ('l02', 'r02', MatchType.ONE_TO_ONE, MatchType.ONE_TO_ONE, False, False),
           ('l03', 'r03', MatchType.ONE_TO_ONE, MatchType.UNMATCHED, False, False),
           ('l04', 'r04', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l05', 'r05', MatchType.ONE_TO_ONE, MatchType.UNMATCHED, False, False),
           ('l06', 'r06', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           (None,  'r07', MatchType.UNMATCHED, MatchType.UNMATCHED, False, False),
           ('l07', None,  MatchType.UNMATCHED, MatchType.UNMATCHED, False, False),
           ('l08', 'r08', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l08', 'r09', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l08', 'r10', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l09', 'r11', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l09', 'r12', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l09', 'r13', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l10', 'r14', MatchType.ONE_TO_MANY, MatchType.ONE_TO_ONE, False, True),
           ('l10', 'r15', MatchType.ONE_TO_MANY, MatchType.ONE_TO_ONE, False, True),
           ('l10', 'r16', MatchType.ONE_TO_MANY, MatchType.ONE_TO_ONE, False, True),
           ('l11', 'r17', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l11', 'r18', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l11', 'r19', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l12', 'r20', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, True),
           ('l12', 'r21', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, True),
           ('l12', 'r22', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, True),
           ('l13', 'r23', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l13', 'r24', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l13', 'r25', MatchType.ONE_TO_MANY, MatchType.UNMATCHED, False, True),
           ('l14', 'r26', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l14', 'r27', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l14', 'r28', MatchType.UNMATCHED, MatchType.ONE_TO_ONE, False, False),
           ('l15', 'r29', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l16', 'r29', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l17', 'r29', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l15', 'r30', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l16', 'r30', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l17', 'r30', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l15', 'r31', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l16', 'r31', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l17', 'r31', MatchType.ONE_TO_MANY, MatchType.ONE_TO_MANY, True, True),
           ('l18', 'r32', MatchType.ONE_TO_ONE, MatchType.ONE_TO_MANY, True, False),
           ('l18', 'r33', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l18', 'r34', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l19', 'r32', MatchType.ONE_TO_ONE, MatchType.ONE_TO_MANY, True, False),
           ('l19', 'r33', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l19', 'r34', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l20', 'r32', MatchType.ONE_TO_ONE, MatchType.ONE_TO_MANY, True, False),
           ('l20', 'r33', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l20', 'r34', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l21', 'r35', MatchType.ONE_TO_ONE, MatchType.ONE_TO_MANY, True, False),
           ('l21', 'r36', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l21', 'r37', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l22', 'r35', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l22', 'r36', MatchType.ONE_TO_ONE, MatchType.ONE_TO_MANY, True, False),
           ('l22', 'r37', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l23', 'r35', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l23', 'r36', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l23', 'r37', MatchType.UNMATCHED, MatchType.ONE_TO_MANY, True, False),
           ('l24', None,  MatchType.UNMATCHED, MatchType.UNMATCHED, False, False),
           (None,  'r38', MatchType.UNMATCHED, MatchType.UNMATCHED, False, False)
        ]

    def helper_test_join(self,
                         left: dict[str, KeyedRecord],
                         right: dict[str, KeyedRecord],
                         expectedMapping: list):

        print("** Expected ************************")

        expected = list[MatchedPair]()
        for i, match in enumerate(expectedMapping):
            mp = MatchedPair(left[match[0]] if match[0] is not None else NullKeyedRecord,
                            right[match[1]] if match[1] is not None else NullKeyedRecord)
            mp.l_result.match_type = match[2]
            mp.r_result.match_type = match[3]
            mp.l_result.is_pk_duplicate = match[4]
            mp.r_result.is_pk_duplicate = match[5]
            expected.append(mp)
        expected.sort()

        print(*expected, sep='\n')


        print("** Actual **************************")

        actual = KeyedRecordJoiner.join(list(left.values()), list(right.values()))
        actual.sort()

        print(*actual, sep='\n')

        assert(len(expected) == len(actual))
        for e, a in zip(expected, actual):
            assert(e == a)

    def test_join_normal(self):
      self.helper_test_join(self.left_dict, self.right_dict, self.expectedMapping)

    def test_join_swap_left_right(self):
      self.helper_test_join(self.right_dict, self.left_dict, [(sub[1], sub[0], sub[3], sub[2], sub[5], sub[4]) for sub in self.expectedMapping])

    def test_join_reversed(self):
      self.helper_test_join(dict(reversed(self.left_dict.items())), dict(reversed(self.right_dict.items())), self.expectedMapping)

    def test_join_swap_left_right_reversed(self):
      self.helper_test_join(dict(reversed(self.right_dict.items())), dict(reversed(self.left_dict.items())), [(sub[1], sub[0], sub[3], sub[2], sub[5], sub[4]) for sub in self.expectedMapping])