# This is automatically generated code. Do not edit manually.

from enum import auto

from bohr.labeling.labelset import Label


class CommitLabel(Label):
    MinorBugFix = auto()
    MajorBugFix = auto()
    CriticalBugFix = auto()
    OtherSeverityLevelBugFix = auto()
    BugFix = MinorBugFix | MajorBugFix | CriticalBugFix | OtherSeverityLevelBugFix
    DocAdd = auto()
    DocSpellingFix = auto()
    DocChange = DocAdd | DocSpellingFix
    TestFix = auto()
    Refactoring = auto()
    CopyChangeAdd = auto()
    Feature = auto()
    InitialCommit = auto()
    VersionBump = auto()
    NonBugFix = DocChange | TestFix | Refactoring | CopyChangeAdd | Feature | InitialCommit | VersionBump
    Commit = BugFix | NonBugFix
    Label = Commit

    def parent(self):
        return None


class SStuBBugFix(Label):
    WrongIdentifier = auto()
    WrongNumericLiteral = auto()
    WrongModifier = auto()
    WrongBooleanLiteral = auto()
    WrongFunctionName = auto()
    TooFewArguments = auto()
    TooManyArguments = auto()
    WrongFunction = WrongFunctionName | TooFewArguments | TooManyArguments
    WrongBinaryOperator = auto()
    WrongUnaryOperator = auto()
    WrongOperator = WrongBinaryOperator | WrongUnaryOperator
    MissingThrowsException = auto()
    SStuB = WrongIdentifier | WrongNumericLiteral | WrongModifier | WrongBooleanLiteral | WrongFunction | WrongOperator | MissingThrowsException
    BugFix = SStuB

    def parent(self):
        return CommitLabel.BugFix


class TangledCommit(Label):
    Tangled = auto()
    NonTangled = auto()
    Commit = Tangled | NonTangled

    def parent(self):
        return CommitLabel.Commit


class SnippetLabel(Label):
    LongMethod = auto()
    LongParameterList = auto()
    Smelly = LongMethod | LongParameterList
    NonSmelly = auto()
    Snippet = Smelly | NonSmelly
    Label = Snippet

    def parent(self):
        return CommitLabel.Label
