# COMP0064: MSc Information Security Dissertation
## Project title: Privacy-Preserving Threshold E-Voting Resilient to Voter Dropout

This is the code that accompanies the above MSc dissertation.

### Running the code

Run the program (on Windows) with:
```
$ python main.py 
```

The following command line arguments can be provided to choose the protocol variant and number of voters:
```
  -h, --help  show this help message and exit
  -o          Run original protocol
  -dr         Run dropout resilient protocol
  -e          Run the efficient variant with a threshold of 1
  -g          Run the generic variant with a variable threshold
  -n N        Set the number of voters (default is 10)
  -t T        Set the threshold- only for generic variants (default is simple majority)
```

For example to run the original efficient protocol with 10 voters, the following arguments are used:
```
$ python main.py -o -e -n 10
```



On Linux replace 'python', with 'python3' in the above commands
```
$ python3 main.py -o -e -n 10
```

## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
