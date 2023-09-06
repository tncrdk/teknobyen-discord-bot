from parse_command import parse, command_parser

command = "git pull"
print(parse(command_parser, command))
