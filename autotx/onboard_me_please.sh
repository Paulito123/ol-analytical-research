#!/usr/bin/expect -f

set timeout -1

set auth [lindex $argv 0]
set mnem [lindex $argv 1]

spawn txs create-account -c 1 -a $auth

expect "Enter your 0L mnemonic:\r"
send -- "$mnem\r"

expect eof