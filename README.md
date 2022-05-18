# mem\_trace\_anal

For ananlyzing memory trace and plotting graph

The row file was obtained through a modified valgrind.
The contents of the row file are as follows:

```
readi 0x04935caf 6 
write 0x1ffefff6d0 4 
readi 0x04935cbe 5 
write 0x1ffefff6b8 8 
readi 0x048e7670 4 
readi 0x048e767c 8 
readd 0x04c0ea48 4 
readi 0x048a4f97 4 
readd 0x04a44460 8 
readi 0x048a4fbc 5 
readd 0x04c0e770 8 
readi 0x04a57cc0 4 
readd 0x1ffefff738 8 
write 0x04c0ea38 8 
```

Each row contains operation(readi/readd/write), memory address and length.
* readi: read instruction
* readd: read data
* write: wirte on memory

## execute code with 'run.sh'
`./run.sh -i [log_file] -o [output_directory]`
