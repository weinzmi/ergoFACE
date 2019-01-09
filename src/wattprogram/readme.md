# wattprogram
this folder is the standard location of all the watt program files.
the list of files will be loaded in watt.py every time, the state "training"
is entered.

the files follow the structure:

```yaml
Prog:
    Seq1:
        Name: Watt program test 0
        Description: this is a test watt program description
        Duration: 10
        Watt: 25
    Seq2:
        Duration: 10
        Watt: 40
    Seq3:
        Duration: 10
        Watt: 50
    Seq4:
        Duration: 10
        Watt: 40
    Seq5:
        Duration: 10
        Watt: 25
    Seq6:
        Duration: 10
        Watt: 50
    ...
```

files can be modified and created by comply to this structure.
