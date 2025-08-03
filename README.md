# dapnet-sendpage

`dapnet-sendpage` is a quick and easy CLI tool for sending calls over the DAPNET pager messaging service.  You need to have a subscriber account at [hampager.de](https://hampager.de), which also means you need to be a licensed amateur radio operator

## Installation

This project relies on the [uv](https://docs.astral.sh/uv/) project manager, so you will need to install this first.  You'll thank me later.

Once you've installed `uv` and cloned this repo to your local machine using `git clone https://github.com/thelovebug/dapnet-sendpage.git` you'll need to run `uv sync` to make sure that your environment has everything it needs to run this script.

Oh, you'll also need Python installed.

## Usage

```shell
uv run sendpage.py --calls "C4LLS1GNS" "Message" [--send]
```

## Detail

### Callsigns/Aliases

```text
--calls "C4LLS1GNS"
```

... is one or more callsigns or aliases, comma-separated, preferably without spaces between.  If you do that, you can omit the "double quotes".

```text
# Good examples
--calls "M7TLB, MI7DJT, M0RWV"
--calls M7TLB,MI7DJT,M0RWV

# Bad examples
--calls M7TLB, MI7DJT,   M0RWV

# the above example is bad because it's not one single block of callsigns
```

### Message

```text
"Message"
```

... is a quote-qualified message of up to, I suppose 300 characters.  If you must use a double quotation mark in your message text, put a \ before it.

```text
# Good examples

"This is my amazingly cool message, ain't it great?"
"The XYL told me today, \"No more radios!\" - help!"

# Bad examples

"The XYL told me today, "No more radios!" - help!"

# This is a bad example as there are unescaped quotes within the message.  Perhaps use single quotes?
```

### The trigger

```shell
--send
```

If you don't specify this particular switch - which is best placed at the end of the command - then it will *show* you what it's going to do, but won't actually send the messages.  This is great if you want to preview who the message is going to, or how many individual calls your message is going to be broken into.

## Setting up the config file

If you haven't already got a `sendpage.json` file in place, then make a copy of `sendpage.json.example` and fill in the details with your own.
)
```json
{
    "user": {
        "mycall": "m1abc"                       // This is your own callsign, case-insensitive
    },
    "dapnetapi": {
        "user": "m1abc",                        // This is the username and password for your SUBSCRIBER account
        "pass": "0123456789ABCDEF0123",         // with DAPNET - the one you log into the hampager.de website with
        "txarea": "all",
        "api": "https://hampager.de/api/calls"  // You can leave this, and the line above alone if you wish
    },
    "aliases": {
        "friends": "M4TE1,M4TE2,M4TE3,M4TE4",   // See below for an explanation of the Aliases functionality
        "enemies": "F0E1,F0E2,F0E3,F0E4"
    }
}
```

### Aliases

The concept of Aliases within this script is very easy.  You create a new key in your `sendpage.json` file under the `"aliases":` node, like in the example above where you have two already specified (that won't work as-is, by the way) - `friends` and `enemies`.

The value for each of those keys determines what callsigns you want to be represented by that key.  So, in our example, `friends` is equivalent to the callsigns `"M4TE1,M4TE2,M4TE3,M4TE4"`.  Thus, if you specify `friends` as one of the callsigns when you run this script, it will replace `friends` with `M4TE1,M4TE2,M4TE3,M4TE4`.

Thus, if you do this:

```shell
python sendpage.py --calls "M7TLB,FRIENDS" "Hello there!" --send
```

The end result would effectively be this:

```shell
python sendpage.py --calls "M7TLB,F0E1,F0E2,F0E3,F0E4" "Hello there!" --send
```

I suppose it's a way of "group texting", but only in one direction.
