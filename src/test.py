from parse_command import parse, kwarg_parser, exhaust_parser, command_parser


cmd = "git -rerferf asdv pull --asd asdf"
print(parse(command_parser, cmd))
