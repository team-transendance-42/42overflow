#A coroutine is: A function that can be suspended and resumed.concurrency: multiple tasks in progress
#but only one runs at a time (in one thread)
#a pausable function controlled by an event loop
#async def f():
    #...
#Coroutines only switch when:they hit await
#async def bad():
#    while True:
#        pass
#This freezes everything.
#No await → no switching.

#That async def marks it as a coroutine function.
#But Calling it does not execute it
#It returns a coroutine object

#Coroutine function starts with async
#async def f():
#    print("A")
#    await sleep(2) # doesnt block program, only pause exec of this func
#    print("B")
    
#runs until await
#pauses there
#resumes later from the same point
#A coroutine is not “just a function”.
#It is closer to:
#A function + saved execution state + scheduler hooks
#When it pauses, Python stores:
#where it stopped (instruction pointer)
#local variables
#current state of execution
#Then it can continue later exactly from that point.

#What is the event loop?
#Coroutines don’t run by themselves.
#They are controlled by the event loop:
#The event loop is a scheduler for coroutines.
#It does:
#runs coroutine A until it hits await
#switches to coroutine B
#switches to C
#repeats

#Why coroutines exist (the real reason)
#They solve a specific problem:
#Handling many waiting operations efficiently (I/O concurrency)
#Example:
#HTTP requests
#database calls
#file/network I/O
#Without coroutines:
#each request blocks a thread
#threads are expensive
#With coroutines:
#one thread
#thousands of concurrent tasks
#no blocking during waiting

import asyncio

#run: python3 12_corotine.py
async def work():
    print("step 1")
    await asyncio.sleep(2)
    print("step 2")

async def a():
    print("A1")
    await asyncio.sleep(1)
    print("A2")

async def b():
    print("B1")
    await asyncio.sleep(1)
    print("B2")
    
#All start immediately:
#A starts
#B starts
#work starts
#Then they run until first await:
#A1
#B1
#step 1
#Then they wait in parallel.
#Then finish:
#A2
#B2
#step 2
async def main():
	await asyncio.gather(a(), b(), work()) # Run these coroutines at the same time and wait for all of them to finish.

asyncio.run(main()) #run(starts event loop, runs ONE main coroutine, shuts down loop)
