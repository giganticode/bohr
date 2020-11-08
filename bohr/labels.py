# This is automatically generated code. Do not edit manually.
class Label(object):
    pass


class TangledCommit(Label):
    pass


class NonTangledCommit(Label):
    pass


class Bugless(Label):
    pass


class Minor(Label):
    pass


class Major(Label):
    pass


class Critical(Label):
    pass


class BugFix(Label):
    pass


class NonBugFix(Label):
    pass


class BogusFix(NonBugFix):
    pass


class DocFix(BogusFix):
    pass


class TestFix(BogusFix):
    pass


TangledCommit = TangledCommit()
NonTangledCommit = NonTangledCommit()
Bugless = Bugless()
Minor = Minor()
Major = Major()
Critical = Critical()
BugFix = BugFix()
NonBugFix = NonBugFix()
BogusFix = BogusFix()
DocFix = DocFix()
TestFix = TestFix()
